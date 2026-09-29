export type DecisionType = 'WAIT' | 'RETRIEVE' | 'NO_RETRIEVAL';

export interface ControllerDecisionEvent {
  event: 'controller_decision';
  t: number;
  decision: DecisionType;
  reason: string;
}

export interface LegInfo {
  leg_id: string;
  text: string;
  first_dispatch_s: number;
}

export interface SubqueriesUpdatedEvent {
  event: 'subqueries_updated';
  t: number;
  legs: LegInfo[];
}

export interface ClaimObject {
  claim_id: string;
  leg_id: string;
  text: string;
  citations: string[];
  evidence_span: string;
  status: 'verified' | 'dropped' | 'uncertain' | 'retracted';
  version: number;
}

export interface DraftVerifiedEvent {
  event: 'draft_verified';
  t: number;
  leg_id: string;
  claim: ClaimObject;
}

export interface VersionDiff {
  added: string[];
  changed: string[];
  retracted: string[];
  unchanged: string[];
  citations_added: string[];
}

export interface TurnCompletedEvent {
  event: 'turn_completed';
  turn_type: 'single' | 'compound' | 'late_constraint' | 'presentation_only' | 'out_of_corpus';
  answer: string;
  version: number;
  citations: string[];
  claims?: ClaimObject[];
  diff?: VersionDiff;
  metrics?: {
    ready_at_end?: number;
    draft_survival_rate?: number;
    rollback_rate?: number;
    rollback_exposure_ms?: number;
    first_verified_rel_end_s?: number;
    retrievals?: number;
  };
}

export interface Speed2CompletedEvent {
  event: 'speed2_completed';
  answer: string;
  version: number;
  citations: string[];
  claims: ClaimObject[];
  metrics: {
    rewrite_pass_rate: number;
    latency_ms: number;
    rewrites_accepted: number;
    rewrites_rejected: number;
  };
}

export type StreamEvent =
  | ControllerDecisionEvent
  | SubqueriesUpdatedEvent
  | DraftVerifiedEvent
  | TurnCompletedEvent
  | Speed2CompletedEvent;

export interface SessionInfo {
  session_id: string;
  token: string;
  expires_at: number;
}

export interface TimelineMarker {
  t: number;
  type: 'decision' | 'draft' | 'utterance_end';
  label: string;
  decision?: DecisionType;
  color?: string;
  reason?: string;
}

export interface DemoChunk {
  t: number;
  text: string;
}

export interface DemoScenario {
  id: string;
  title: string;
  description: string;
  chunks: DemoChunk[];
  utterance_end: number;
  turn_type: string;
}
