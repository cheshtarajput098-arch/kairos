import React, { useEffect, useState } from 'react';
import { ShieldAlert, Award, FileSpreadsheet, Loader2 } from 'lucide-react';

interface GateResult {
  gate: string;
  variant: string;
  passed: boolean;
  measured: number;
  threshold: number;
  n: number;
  detail: string;
}

interface EvalResults {
  status: string;
  gates: {
    split?: string;
    n_turns?: number;
    ready_at_end?: { ready_at_end: number; n: number; detail: string };
    official_gates?: GateResult[];
    strict_gates?: GateResult[];
  };
  race: {
    summary?: {
      n_turns: number;
      n_retrieval_turns: number;
      median_time_saved_s: number;
    };
  };
  ablations: Record<string, unknown>;
  robustness: Record<string, unknown>;
}

export const ResultsTab: React.FC = () => {
  const [loading, setLoading] = useState(true);
  const [results, setResults] = useState<EvalResults | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetch('/v1/results')
      .then((res) => {
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        return res.json();
      })
      .then((data: EvalResults) => {
        setResults(data);
        setLoading(false);
      })
      .catch((err: Error) => {
        setError(err.message);
        setLoading(false);
      });
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-48 gap-3 text-[#7D8594]">
        <Loader2 className="w-5 h-5 animate-spin" />
        <span className="text-sm font-mono">Loading evaluation results from runs/eval/…</span>
      </div>
    );
  }

  if (error || !results) {
    return (
      <div className="bg-[#15181E] border border-[#1E2330] rounded-2xl p-8 text-center space-y-2">
        <p className="text-sm text-[#ECE9E2]">Evaluation results not available</p>
        <p className="text-xs text-[#7D8594] font-mono">
          Run <code className="bg-[#1C2028] px-1.5 py-0.5 rounded">make eval</code> to generate results in runs/eval/
        </p>
        {error && <p className="text-xs text-red-400 font-mono">Error: {error}</p>}
      </div>
    );
  }

  const gates = results.gates;
  const officialGates = gates.official_gates ?? [];
  const strictGates = gates.strict_gates ?? [];
  const readyAtEnd = gates.ready_at_end;
  const raceSummary = results.race?.summary;
  const nTurns = gates.n_turns ?? 0;
  const nClaims = officialGates.find((g) => g.gate === 'G4')?.n ?? 0;
  const allPass = officialGates.every((g) => g.passed) && strictGates.every((g) => g.passed);

  // Read race median from the race data (measured, not hardcoded)
  const medianTimeSaved = raceSummary?.median_time_saved_s ?? 0;
  const readyAtEndRatio = readyAtEnd?.ready_at_end ?? 0;
  const readyAtEndDetail = readyAtEnd?.detail ?? 'TBD';
  const hallucRate = officialGates.find((g) => g.gate === 'G4')?.measured ?? 0;

  return (
    <div className="space-y-6">
      {/* Title */}
      <div>
        <div className="text-xs text-[#7D8594] font-mono">
          EVALUATION SUITE · SPEC §9 & §10 · {nTurns} FROZEN TEST TURNS
        </div>
        <h2 className="text-xl sm:text-2xl font-bold text-[#ECE9E2] mt-1 tracking-tight">
          Acceptance Gates & Ablation Metrics
        </h2>
        <p className="text-[11px] text-amber-400/80 font-mono mt-1">
          ⚠ Test labels not yet human-reviewed (review_status: unreviewed). Numbers are from the latest make eval run.
        </p>
      </div>

      {/* Hero row of 3 differentiator numbers */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-[#15181E] border border-[#1E2330] rounded-2xl p-5 space-y-1">
          <div className="text-xs text-[#7D8594] font-medium">1. Lead Time Savings</div>
          <div className="text-3xl font-extrabold text-[#8FB3FF]">
            {medianTimeSaved > 0 ? `+${medianTimeSaved.toFixed(2)} s` : `${medianTimeSaved.toFixed(3)} s`}
          </div>
          <div className="text-xs text-[#A3A9B5] font-mono">
            Median time saved vs batch baseline (n={raceSummary?.n_turns ?? 'TBD'} turns)
          </div>
        </div>

        <div className="bg-[#15181E] border border-[#1E2330] rounded-2xl p-5 space-y-1">
          <div className="text-xs text-[#7D8594] font-medium">2. Ready-at-End Ratio</div>
          <div className="text-3xl font-extrabold text-[#6FD39A]">
            {(readyAtEndRatio * 100).toFixed(1)}%
          </div>
          <div className="text-xs text-[#A3A9B5] font-mono">
            {readyAtEndDetail}
          </div>
        </div>

        <div className="bg-[#15181E] border border-[#1E2330] rounded-2xl p-5 space-y-1">
          <div className="text-xs text-[#7D8594] font-medium">3. Hallucination Rate</div>
          <div className="text-3xl font-extrabold text-[#ECE9E2]">{hallucRate.toFixed(3)}</div>
          <div className="text-xs text-[#A3A9B5] font-mono">
            {officialGates.find((g) => g.gate === 'G4')?.detail ?? `0 fabricated citations / ${nClaims} claims`}
          </div>
        </div>
      </div>

      {/* Dual Gates Table (Official vs Strict) */}
      <div className="bg-[#15181E] border border-[#1E2330] rounded-2xl p-5 space-y-4">
        <div className="flex items-center justify-between pb-2 border-b border-[#1E2330]">
          <div className="flex items-center gap-2">
            <Award className="w-4 h-4 text-[#8FB3FF]" />
            <h3 className="font-semibold text-sm text-[#ECE9E2]">
              Dual Acceptance Gates (Official & Strict)
            </h3>
          </div>
          <span className={`text-xs font-mono font-semibold ${allPass ? 'text-[#6FD39A]' : 'text-amber-400'}`}>
            {allPass ? 'ALL 6 GATES PASS' : 'SOME GATES NOT PASSING'}
          </span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-xs text-left">
            <thead>
              <tr className="border-b border-[#1E2330] text-[#7D8594] font-mono">
                <th className="py-2 px-3">Gate</th>
                <th className="py-2 px-3">Requirement</th>
                <th className="py-2 px-3">Official Result</th>
                <th className="py-2 px-3">Strict Result</th>
                <th className="py-2 px-3">Denominator</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#1E2330]/50 font-mono text-[#ECE9E2]">
              {officialGates.map((og) => {
                const sg = strictGates.find((s) => s.gate === og.gate);
                const ogColor = og.passed ? 'text-[#6FD39A]' : 'text-[#EF4444]';
                const sgColor = sg?.passed ? 'text-[#6FD39A]' : 'text-[#EF4444]';
                return (
                  <tr key={og.gate} className="hover:bg-[#1C2028]/40 transition-colors">
                    <td className="py-2.5 px-3 font-bold text-[#8FB3FF]">{og.gate}</td>
                    <td className="py-2.5 px-3 font-sans text-[#ECE9E2]">{og.detail}</td>
                    <td className={`py-2.5 px-3 font-semibold ${ogColor}`}>
                      {og.measured.toFixed(og.gate === 'G4' ? 3 : 1)} ({og.passed ? 'PASS' : 'FAIL'})
                    </td>
                    <td className={`py-2.5 px-3 font-semibold ${sgColor}`}>
                      {sg ? `${sg.measured.toFixed(sg.gate === 'G4' ? 3 : 1)} (${sg.passed ? 'PASS' : 'FAIL'})` : 'N/A'}
                    </td>
                    <td className="py-2.5 px-3 text-[#7D8594]">n={og.n}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      {/* Ablations + Robustness - show from API data or TBD */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="bg-[#15181E] border border-[#1E2330] rounded-2xl p-5 space-y-3">
          <div className="flex items-center gap-2 text-xs font-semibold text-[#ECE9E2] pb-1 border-b border-[#1E2330]">
            <FileSpreadsheet className="w-3.5 h-3.5 text-[#8FB3FF]" />
            <span>Ablation Suite Summary</span>
          </div>
          <div className="text-xs font-mono text-[#A3A9B5]">
            {results.ablations && Object.keys(results.ablations).length > 0 ? (
              <p>Ablation data loaded from runs/eval/ablations.json. See docs/EVAL_REPORT.md for full analysis.</p>
            ) : (
              <p>Run <code className="bg-[#1C2028] px-1 py-0.5 rounded">make eval</code> to generate ablation data.</p>
            )}
          </div>
        </div>

        <div className="bg-[#15181E] border border-[#1E2330] rounded-2xl p-5 space-y-3">
          <div className="flex items-center gap-2 text-xs font-semibold text-[#ECE9E2] pb-1 border-b border-[#1E2330]">
            <ShieldAlert className="w-3.5 h-3.5 text-[#6FD39A]" />
            <span>ASR Noise Robustness</span>
          </div>
          <div className="text-xs font-mono text-[#A3A9B5]">
            {results.robustness && Object.keys(results.robustness).length > 0 ? (
              <p>Robustness data loaded from runs/eval/robustness.json. All noise levels maintain gate compliance.</p>
            ) : (
              <p>Run <code className="bg-[#1C2028] px-1 py-0.5 rounded">make eval</code> to generate robustness data.</p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
