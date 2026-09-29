"""WebSocket Live Streaming Endpoint (SPEC §10, §13.3).

Provides live transcript streaming with:
1. Token and Origin validation before connection acceptance.
2. Strict message size (< 4 KB) and schema validation (rejects unknown fields).
3. Per-connection rate limiting, bounded queues, and idle timeout.
4. Real-time pipeline events (decisions, legs, drafts, claims, and version updates).
"""

from __future__ import annotations

import asyncio
import json
import logging
import time

from fastapi import WebSocket, WebSocketDisconnect, status
from pydantic import ValidationError

from kairos.config import load_config
from kairos.controller.features import ControllerFeatureExtractor
from kairos.controller.rules import RuleBasedController
from kairos.decompose.dispatcher import ParallelDispatcher
from kairos.decompose.manager import DecompositionManager
from kairos.grounding.gate import GroundingGate
from kairos.index.store import IndexStore
from kairos.retrieve.hybrid import HybridRetriever
from kairos.schemas import ErrorDetail, ErrorEnvelope, StreamInputChunk
from kairos.security.sanitizer import sanitize_input_text
from kairos.session.delta import DeltaEngine
from kairos.session.store import SessionStore
from kairos.synth.drafting import DraftingManager
from kairos.synth.extractive import ExtractiveSynthesizer
from kairos.synth.rewrite import Speed2Synthesizer

logger = logging.getLogger("kairos.api.stream")


async def handle_stream_websocket(
    websocket: WebSocket,
    session_id: str,
    token: str,
    session_store: SessionStore,
    index_store: IndexStore,
) -> None:
    """Handle live WebSocket transcript streaming session."""
    cfg = load_config()
    secret = cfg.token_secret

    # 1. Validate Origin
    origin = websocket.headers.get("origin")
    allowed = cfg.security.allowed_origins
    if origin and "*" not in allowed and origin not in allowed:
        logger.warning(f"WebSocket rejected: unauthorized origin '{origin}'")
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    # 2. Authenticate session & token
    session = session_store.get_session(session_id, token, secret)
    if session is None:
        logger.warning(f"WebSocket rejected: invalid session or token '{session_id}'")
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    await websocket.accept()
    logger.info(f"WebSocket accepted for session {session_id}")

    # Initialize per-connection pipeline stages
    feature_extractor = ControllerFeatureExtractor(index_store.sparse_index)
    controller = RuleBasedController()
    decomposer = DecompositionManager()
    retriever = HybridRetriever(index_store)
    dispatcher = ParallelDispatcher(retriever)
    synthesizer = ExtractiveSynthesizer()
    gate = GroundingGate()
    drafting_mgr = DraftingManager(synthesizer, gate)
    delta_engine = DeltaEngine(synthesizer)
    speed2_synth = Speed2Synthesizer(gate=gate) if cfg.synthesis.speed2.enabled else None

    prefix_buffer = ""
    turn_decisions: list[str] = []
    has_prior_answer = bool(session.answer)
    window_start = time.time()
    window_count = 0
    conn_start_time = time.time()
    idle_timeout = float(cfg.session.ttl_s)
    max_conn_lifetime = float(cfg.security.ws.max_connection_s)

    try:
        while True:
            # Enforce max connection lifetime (SPEC §13.3)
            now = time.time()
            if now - conn_start_time > max_conn_lifetime:
                logger.info(f"WebSocket session {session_id} exceeded max connection lifetime ({max_conn_lifetime}s).")
                err = ErrorEnvelope(
                    error=ErrorDetail(
                        code="MAX_CONNECTION_LIFETIME_EXCEEDED",
                        message="Connection lifetime exceeded. Please reconnect.",
                        request_id=session_id,
                    )
                )
                await websocket.send_text(json.dumps(err.model_dump()))
                await websocket.close(code=status.WS_1000_NORMAL_CLOSURE)
                return

            # Idle timeout guard
            raw_text = await asyncio.wait_for(websocket.receive_text(), timeout=idle_timeout)

            # Enforce message size limit (Security Rule 5, SPEC §13.3: <= 4096 bytes)
            if len(raw_text.encode("utf-8")) > 4096:
                logger.warning(f"Oversized message received from session {session_id}")
                err = ErrorEnvelope(
                    error=ErrorDetail(
                        code="MESSAGE_TOO_LARGE",
                        message="Message exceeds maximum 4096 bytes limit.",
                        request_id=session_id,
                    )
                )
                await websocket.send_text(json.dumps(err.model_dump()))
                await websocket.close(code=status.WS_1009_MESSAGE_TOO_BIG)
                return

            # Enforce rate limit (max 60 messages per second per connection)
            if now - window_start > 1.0:
                window_start = now
                window_count = 0
            window_count += 1
            if window_count > 60:
                logger.warning(f"Rate limit exceeded on session {session_id}")
                err = ErrorEnvelope(
                    error=ErrorDetail(
                        code="RATE_LIMIT_EXCEEDED",
                        message="Too many messages sent per second.",
                        request_id=session_id,
                    )
                )
                await websocket.send_text(json.dumps(err.model_dump()))
                await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
                return

            # Strict Pydantic parsing (forbids unknown fields)
            try:
                chunk_data = json.loads(raw_text)
                chunk = StreamInputChunk.model_validate(chunk_data)
            except (json.JSONDecodeError, ValidationError) as e:
                logger.warning(f"Malformed stream message: {e}")
                err = ErrorEnvelope(
                    error=ErrorDetail(
                        code="INVALID_MESSAGE_SCHEMA",
                        message=f"Message validation error: {e}",
                        request_id=session_id,
                    )
                )
                await websocket.send_text(json.dumps(err.model_dump()))
                continue

            # Sanitize input chunk text (NFKC, strip control/zero-width, escape delimiters - SPEC §13.3)
            sanitized_text = sanitize_input_text(chunk.text)

            # Update running prefix
            if prefix_buffer:
                prefix_buffer = f"{prefix_buffer} {sanitized_text}".strip()
            else:
                prefix_buffer = sanitized_text.strip()

            # Controller decision
            features = feature_extractor.compute_features(
                prefix_buffer, has_prior_answer=has_prior_answer
            )
            dec = controller.decide(features, chunk.t, has_prior_answer=has_prior_answer)
            turn_decisions.append(dec.decision)

            await websocket.send_text(
                json.dumps(
                    {
                        "event": "controller_decision",
                        "t": chunk.t,
                        "decision": dec.decision,
                        "reason": dec.reason,
                    }
                )
            )

            # If controller triggers retrieval
            if dec.decision == "RETRIEVE":
                active_legs, reissued_ids = decomposer.decompose(prefix_buffer, chunk.t)

                if active_legs:
                    await websocket.send_text(
                        json.dumps(
                            {
                                "event": "subqueries_updated",
                                "t": chunk.t,
                                "legs": [
                                    {
                                        "leg_id": l.leg_id,
                                        "text": l.text,
                                        "first_dispatch_s": l.first_dispatch_s,
                                    }
                                    for l in active_legs
                                ],
                            }
                        )
                    )

                if reissued_ids:
                    results = await dispatcher.dispatch_legs(active_legs, reissued_ids)
                    for leg in active_legs:
                        if leg.leg_id in results:
                            # Speculative answer drafting mid-utterance
                            draft_claim = drafting_mgr.draft_leg(
                                leg,
                                results[leg.leg_id],
                                index_store.chunks_map,
                                t=chunk.t,
                                version=session.current_version,
                            )
                            if draft_claim:
                                await websocket.send_text(
                                    json.dumps(
                                        {
                                            "event": "draft_verified",
                                            "t": chunk.t,
                                            "leg_id": leg.leg_id,
                                            "claim": draft_claim.model_dump(),
                                        }
                                    )
                                )

            # If user has finished speaking (turn final)
            if chunk.is_final:
                # Classify turn type against existing session
                turn_class = delta_engine.classify_turn(prefix_buffer, session)

                if turn_class == "presentation_only":
                    new_ans, claims, diff = delta_engine.handle_presentation_only(session)
                    v = session_store.save_version(
                        session_id, new_ans, claims, session.citations, diff=diff
                    )
                    await websocket.send_text(
                        json.dumps(
                            {
                                "event": "turn_completed",
                                "turn_type": "presentation_only",
                                "answer": new_ans,
                                "version": v,
                                "citations": session.citations,
                                "diff": diff.model_dump(),
                                "metrics": {"retrievals": 0, "ready_at_end": 1.0},
                            }
                        )
                    )
                else:
                    final_legs = list(decomposer.active_legs.values())
                    all_results = dispatcher.get_all_results()
                    committed_claims, drafting_metrics = drafting_mgr.commit_turn(
                        final_legs,
                        all_results,
                        index_store.chunks_map,
                        utterance_end_t=chunk.t,
                        version=session.current_version,
                    )

                    final_answer = " ".join(c.text for c in committed_claims)
                    citations = list(
                        dict.fromkeys(cite for c in committed_claims for cite in c.citations)
                    )

                    is_refinement = turn_class in (
                        "late_constraint",
                        "constraint_on_existing",
                        "contradiction",
                    )
                    v = session_store.save_version(
                        session_id,
                        final_answer,
                        committed_claims,
                        citations,
                        is_refinement=is_refinement,
                    )
                    session.active_legs = {l.leg_id: l for l in final_legs}
                    has_prior_answer = True

                    await websocket.send_text(
                        json.dumps(
                            {
                                "event": "turn_completed",
                                "turn_type": turn_class,
                                "answer": final_answer,
                                "version": v,
                                "citations": citations,
                                "claims": [c.model_dump() for c in committed_claims],
                                "metrics": drafting_metrics,
                            }
                        )
                    )

                    # Stage 5 Speed-2 Grounded Rewrite (SPEC §6.2)
                    if (
                        speed2_synth is not None
                        and cfg.synthesis.speed2.enabled
                        and cfg.synthesis.speed2.run_policy != "off"
                        and committed_claims
                    ):
                        s2_claims, s2_metrics = speed2_synth.rewrite_claims(
                            committed_claims, index_store.chunks_map
                        )
                        if s2_metrics.get("rewrites_accepted", 0) > 0:
                            s2_answer = " ".join(c.text for c in s2_claims)
                            v_s2 = session_store.save_version(
                                session_id, s2_answer, s2_claims, citations
                            )
                            await websocket.send_text(
                                json.dumps(
                                    {
                                        "event": "speed2_completed",
                                        "answer": s2_answer,
                                        "version": v_s2,
                                        "citations": citations,
                                        "claims": [c.model_dump() for c in s2_claims],
                                        "metrics": s2_metrics,
                                    }
                                )
                            )

                # Reset turn state
                prefix_buffer = ""
                turn_decisions.clear()
                decomposer.reset_turn()
                dispatcher.reset_turn()
                drafting_mgr.reset_turn()
                feature_extractor.reset_turn()

    except (TimeoutError, WebSocketDisconnect):
        logger.info(f"WebSocket closed/disconnected for session {session_id}")
    except Exception as e:  # noqa: BLE001
        logger.error(f"Error in stream websocket for session {session_id}: {e}")
        try:
            await websocket.close(code=status.WS_1011_INTERNAL_ERROR)
        except Exception as close_err:  # noqa: BLE001
            logger.debug(f"Error while closing websocket: {close_err}")
