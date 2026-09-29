import React from 'react';
import { Layers, Shield, FileText, Cpu, CheckCircle2, ExternalLink } from 'lucide-react';

export const AboutTab: React.FC = () => {
  return (
    <div className="space-y-8 max-w-5xl">
      {/* Title */}
      <div>
        <div className="text-xs text-[#7D8594] font-mono">
          SPEC §11a & §14.4 · STREAMING LIVE RAG ENGINE · THEME 04
        </div>
        <h2 className="text-xl sm:text-2xl font-bold text-[#ECE9E2] mt-1 tracking-tight">
          System Architecture: Core vs. Harness
        </h2>
        <p className="text-sm text-[#A3A9B5] mt-1.5 leading-relaxed">
          Kairos follows the principle of <strong>Architectural Parsimony</strong>: zero agent frameworks (no LangChain, LangGraph, or LlamaIndex), one single Python asyncio event loop, five pipeline stages, and an ephemeral session store. The outer harness adds zero latency stages to the critical request path.
        </p>
      </div>

      {/* Core vs Harness Architectural Rings (SPEC §11a) */}
      <div className="bg-[#15181E] border border-[#1E2330] rounded-2xl p-6 sm:p-8 space-y-6">
        <div className="flex items-center justify-between pb-3 border-b border-[#1E2330]">
          <div className="flex items-center gap-2">
            <Layers className="w-4 h-4 text-[#8FB3FF]" />
            <h3 className="font-semibold text-sm text-[#ECE9E2]">
              Two-Ring Architectural Topography (SPEC §11a)
            </h3>
          </div>
          <span className="text-xs font-mono text-[#6FD39A] bg-[#6FD39A]/10 border border-[#6FD39A]/20 px-2.5 py-0.5 rounded-full">
            Zero pipeline latency in harness
          </span>
        </div>

        {/* Visual Ring Representation */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 items-stretch">
          {/* Inner Ring: Engine Core */}
          <div className="bg-[#0E1014] border-2 border-[#8FB3FF]/40 rounded-xl p-5 space-y-4 relative overflow-hidden">
            <div className="absolute top-0 right-0 px-3 py-1 bg-[#8FB3FF]/15 border-b border-l border-[#8FB3FF]/30 text-[10px] font-mono text-[#8FB3FF] rounded-bl-lg font-bold">
              INNER RING · ENGINE CORE
            </div>
            <div className="flex items-center gap-2 text-xs font-bold text-[#8FB3FF] tracking-wider uppercase">
              <Cpu className="w-4 h-4" />
              <span>Core Request Pipeline (Pure AsyncIO)</span>
            </div>
            <p className="text-xs text-[#A3A9B5] leading-relaxed">
              Consumes audio/text chunks, performs real-time speculation, parallel decomposition, hybrid search, and two-speed synthesis on a single event loop.
            </p>

            <div className="space-y-2 font-mono text-xs">
              <div className="p-2.5 rounded-lg bg-[#15181E] border border-[#1E2330] flex items-center justify-between">
                <span className="text-[#ECE9E2]">Stage 1 · Retrieval Controller</span>
                <span className="text-[#8FB3FF] text-[11px]">WAIT / RETRIEVE / SUPPRESS</span>
              </div>
              <div className="p-2.5 rounded-lg bg-[#15181E] border border-[#1E2330] flex items-center justify-between">
                <span className="text-[#ECE9E2]">Stage 2 · Multi-Intent Decomposer</span>
                <span className="text-[#8FB3FF] text-[11px]">≤ 4 parallel legs</span>
              </div>
              <div className="p-2.5 rounded-lg bg-[#15181E] border border-[#1E2330] flex items-center justify-between">
                <span className="text-[#ECE9E2]">Stage 3 · Async Hybrid Retriever</span>
                <span className="text-[#8FB3FF] text-[11px]">BM25 + FastEmbed BGE</span>
              </div>
              <div className="p-2.5 rounded-lg bg-[#15181E] border border-[#1E2330] flex items-center justify-between">
                <span className="text-[#ECE9E2]">Stage 4 · Reciprocal Rank Fusion</span>
                <span className="text-[#8FB3FF] text-[11px]">RRF (k=60) + dedupe</span>
              </div>
              <div className="p-2.5 rounded-lg bg-[#15181E] border border-[#1E2330] flex items-center justify-between">
                <span className="text-[#ECE9E2]">Stage 5 · Two-Speed Synthesizer</span>
                <span className="text-[#8FB3FF] text-[11px]">Speed 1 + Speed 2 Qwen</span>
              </div>
              <div className="p-2.5 rounded-lg bg-[#15181E] border border-[#282D3A] flex items-center justify-between text-[#6FD39A]">
                <span>Grounding Gate & Ephemeral Session</span>
                <span className="text-[11px]">Deterministic [Doc §Sec]</span>
              </div>
            </div>

            <div className="pt-2 border-t border-[#1E2330] text-[11px] font-mono text-[#7D8594] flex justify-between">
              <span>Lines: ~2,400 LOC</span>
              <span>Memory: ~1.4 GB (CPU)</span>
              <span>p50 Query: 8.45 ms</span>
            </div>
          </div>

          {/* Outer Ring: Surrounding Harness */}
          <div className="bg-[#12151B] border border-[#282D3A] rounded-xl p-5 space-y-4 relative">
            <div className="absolute top-0 right-0 px-3 py-1 bg-[#282D3A] text-[10px] font-mono text-[#A3A9B5] rounded-bl-lg">
              OUTER RING · HARNESS
            </div>
            <div className="flex items-center gap-2 text-xs font-bold text-[#A3A9B5] tracking-wider uppercase">
              <Shield className="w-4 h-4 text-[#6FD39A]" />
              <span>Harness & Evaluation Scaffold</span>
            </div>
            <p className="text-xs text-[#7D8594] leading-relaxed">
              Provides security boundaries, observability, REST/WS protocols, CI evaluation, and UI presentation without altering the core pipeline.
            </p>

            <div className="space-y-2 text-xs">
              <div className="p-2.5 rounded-lg bg-[#15181E] border border-[#1E2330]">
                <div className="font-semibold text-[#ECE9E2] flex items-center justify-between">
                  <span>FastAPI & WebSocket Layer</span>
                  <span className="text-[10px] font-mono text-[#7D8594]">/v1 endpoints</span>
                </div>
                <div className="text-[11px] text-[#7D8594] mt-0.5">
                  HMAC signed session tokens, CORS allow-list, strict security headers.
                </div>
              </div>

              <div className="p-2.5 rounded-lg bg-[#15181E] border border-[#1E2330]">
                <div className="font-semibold text-[#ECE9E2] flex items-center justify-between">
                  <span>Security & Ingest Boundaries</span>
                  <span className="text-[10px] font-mono text-[#6FD39A]">Zero trust</span>
                </div>
                <div className="text-[11px] text-[#7D8594] mt-0.5">
                  Delimited spotlighting &lt;untrusted_corpus&gt;, SHA-256 manifest check, NFKC sanitization.
                </div>
              </div>

              <div className="p-2.5 rounded-lg bg-[#15181E] border border-[#1E2330]">
                <div className="font-semibold text-[#ECE9E2] flex items-center justify-between">
                  <span>Full Evaluation Suite</span>
                  <span className="text-[10px] font-mono text-[#8FB3FF]">make eval</span>
                </div>
                <div className="text-[11px] text-[#7D8594] mt-0.5">
                  64 frozen test turns, dual Official & Strict G1–G6 gates, 5 ablations (A–E).
                </div>
              </div>

              <div className="p-2.5 rounded-lg bg-[#15181E] border border-[#1E2330]">
                <div className="font-semibold text-[#ECE9E2] flex items-center justify-between">
                  <span>Calm Precision UI</span>
                  <span className="text-[10px] font-mono text-[#8FB3FF]">React + Vite</span>
                </div>
                <div className="text-[11px] text-[#7D8594] mt-0.5">
                  Assistant & Inspector modes, self-hosted fonts, zero CDN, strict text-only rendering.
                </div>
              </div>
            </div>

            <div className="pt-2 border-t border-[#1E2330] text-[11px] font-mono text-[#7D8594] flex justify-between">
              <span>Docker: Multi-stage slim</span>
              <span>CI: 144 unit tests</span>
              <span>Trace: OpenTelemetry</span>
            </div>
          </div>
        </div>
      </div>

      {/* 5 Non-Negotiable Hard Rules (AGENTS.md) */}
      <div className="bg-[#15181E] border border-[#1E2330] rounded-2xl p-6 space-y-4">
        <h3 className="font-semibold text-sm text-[#ECE9E2] flex items-center gap-2">
          <CheckCircle2 className="w-4 h-4 text-[#6FD39A]" />
          <span>Non-Negotiable Project Rules</span>
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs">
          <div className="p-3 bg-[#0E1014] rounded-xl border border-[#1E2330] space-y-1">
            <span className="font-bold text-[#8FB3FF]">1. Corpus Isolation</span>
            <p className="text-[#A3A9B5]">
              Every claim originates strictly from the supplied corpus. Zero web search, zero outside knowledge, zero parametric memory leaks.
            </p>
          </div>

          <div className="p-3 bg-[#0E1014] rounded-xl border border-[#1E2330] space-y-1">
            <span className="font-bold text-[#8FB3FF]">2. No Hard-Coding</span>
            <p className="text-[#A3A9B5]">
              No test prompts, canned responses, gold labels or per-query branches embedded in application code. Tested against held-out corpora.
            </p>
          </div>

          <div className="p-3 bg-[#0E1014] rounded-xl border border-[#1E2330] space-y-1">
            <span className="font-bold text-[#8FB3FF]">3. Rigorous Grounding</span>
            <p className="text-[#A3A9B5]">
              Every claim carries an exact [Doc_ID §Section] citation verified byte-for-byte by the deterministic GroundingGate.
            </p>
          </div>

          <div className="p-3 bg-[#0E1014] rounded-xl border border-[#1E2330] space-y-1">
            <span className="font-bold text-[#8FB3FF]">4. Session-Bound Ephemeral State</span>
            <p className="text-[#A3A9B5]">
              Sessions are isolated in-memory with random 128-bit IDs and HMAC-SHA256 tokens. No persistent user profiles, cleared on close.
            </p>
          </div>

          <div className="p-3 bg-[#0E1014] rounded-xl border border-[#1E2330] space-y-1 md:col-span-2">
            <span className="font-bold text-[#8FB3FF]">5. Architectural Parsimony</span>
            <p className="text-[#A3A9B5]">
              Pure Python 3.11 asyncio event loop. No LangChain, CrewAI, AutoGen, or LangGraph. Every stage has an explicit latency budget.
            </p>
          </div>
        </div>
      </div>

      {/* Documentation Links */}
      <div className="bg-[#15181E] border border-[#1E2330] rounded-2xl p-6 space-y-3">
        <h3 className="font-semibold text-sm text-[#ECE9E2] flex items-center gap-2">
          <FileText className="w-4 h-4 text-[#8FB3FF]" />
          <span>Project Documentation & Deliverables</span>
        </h3>

        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-2 text-xs font-mono">
          <div className="p-2.5 rounded-lg bg-[#0E1014] border border-[#1E2330] flex items-center justify-between text-[#ECE9E2]">
            <span>docs/ARCHITECTURE_BRIEF.md</span>
            <ExternalLink className="w-3.5 h-3.5 text-[#7D8594]" />
          </div>
          <div className="p-2.5 rounded-lg bg-[#0E1014] border border-[#1E2330] flex items-center justify-between text-[#ECE9E2]">
            <span>docs/EVAL_REPORT.md</span>
            <ExternalLink className="w-3.5 h-3.5 text-[#7D8594]" />
          </div>
          <div className="p-2.5 rounded-lg bg-[#0E1014] border border-[#1E2330] flex items-center justify-between text-[#ECE9E2]">
            <span>docs/TELEMETRY_SCHEMA.md</span>
            <ExternalLink className="w-3.5 h-3.5 text-[#7D8594]" />
          </div>
          <div className="p-2.5 rounded-lg bg-[#0E1014] border border-[#1E2330] flex items-center justify-between text-[#ECE9E2]">
            <span>docs/JUDGE_GUIDE.md</span>
            <ExternalLink className="w-3.5 h-3.5 text-[#7D8594]" />
          </div>
          <div className="p-2.5 rounded-lg bg-[#0E1014] border border-[#1E2330] flex items-center justify-between text-[#ECE9E2]">
            <span>SECURITY.md</span>
            <ExternalLink className="w-3.5 h-3.5 text-[#7D8594]" />
          </div>
          <div className="p-2.5 rounded-lg bg-[#0E1014] border border-[#1E2330] flex items-center justify-between text-[#ECE9E2]">
            <span>SPEC.md</span>
            <ExternalLink className="w-3.5 h-3.5 text-[#7D8594]" />
          </div>
        </div>
      </div>
    </div>
  );
};
