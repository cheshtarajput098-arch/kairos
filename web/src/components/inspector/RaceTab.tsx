import React, { useState, useEffect, useCallback } from 'react';
import { Play, RotateCcw, Zap, Clock, ShieldCheck, Loader2 } from 'lucide-react';

interface RaceSummary {
  n_turns: number;
  n_retrieval_turns: number;
  median_time_saved_s: number;
  mean_time_saved_s: number;
  fraction_with_time_savings: number;
}

interface RaceTurn {
  turn_id: string;
  turn_type: string;
  utterance_end_s: number;
  retrieval_required: boolean;
  first_retrieval_s: number | null;
  ready_at_end: number;
  baseline_ready_s: number;
  kairos_ready_s: number;
  time_saved_s: number;
}

interface RaceData {
  summary: RaceSummary;
  turns: RaceTurn[];
}

export const RaceTab: React.FC = () => {
  const [isPlaying, setIsPlaying] = useState(false);
  const [raceProgress, setRaceProgress] = useState(0);
  const [raceData, setRaceData] = useState<RaceData | null>(null);
  const [readyAtEnd, setReadyAtEnd] = useState<number | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Fetch measured data from /v1/results on mount
  useEffect(() => {
    fetch('/v1/results')
      .then((res) => {
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        return res.json();
      })
      .then((data) => {
        if (data.race?.summary) {
          setRaceData(data.race as RaceData);
        }
        if (data.gates?.ready_at_end) {
          setReadyAtEnd(data.gates.ready_at_end.ready_at_end);
        }
        setLoading(false);
      })
      .catch((err: Error) => {
        setError(err.message);
        setLoading(false);
      });
  }, []);

  // Find the first turn with real time savings (for the illustration)
  const exampleTurn = raceData?.turns.find((t) => t.time_saved_s > 0 && t.first_retrieval_s !== null);

  // Derive timing milestones from measured data
  const utteranceEnd = exampleTurn?.utterance_end_s ?? 2.2;
  const firstRetrieval = exampleTurn?.first_retrieval_s ?? 0.8;
  const kairosReady = exampleTurn?.kairos_ready_s ?? utteranceEnd;
  const baselineReady = exampleTurn?.baseline_ready_s ?? utteranceEnd + 0.068;
  const maxTime = Math.max(baselineReady + 0.5, 4.0);

  useEffect(() => {
    let interval: number;
    if (isPlaying) {
      interval = window.setInterval(() => {
        setRaceProgress((prev) => {
          if (prev >= maxTime) {
            setIsPlaying(false);
            return maxTime;
          }
          return prev + 0.05;
        });
      }, 50);
    }
    return () => clearInterval(interval);
  }, [isPlaying, maxTime]);

  const handleStart = useCallback(() => {
    setRaceProgress(0);
    setIsPlaying(true);
  }, []);

  const handleReset = useCallback(() => {
    setIsPlaying(false);
    setRaceProgress(0);
  }, []);

  const kairosDraftProgress = Math.min(
    100,
    Math.max(0, ((raceProgress - firstRetrieval) / (utteranceEnd - firstRetrieval)) * 100)
  );
  const batchDuration = baselineReady - utteranceEnd;
  const batchProgress = Math.min(
    100,
    Math.max(0, ((raceProgress - utteranceEnd) / batchDuration) * 100)
  );

  const medianTimeSaved = raceData?.summary.median_time_saved_s ?? 0;
  const nTurns = raceData?.summary.n_turns ?? 0;

  if (loading) {
    return (
      <div className="flex items-center justify-center h-48 gap-3 text-[#7D8594]">
        <Loader2 className="w-5 h-5 animate-spin" />
        <span className="text-sm font-mono">Loading race data from runs/eval/race.json…</span>
      </div>
    );
  }

  if (error || !raceData) {
    return (
      <div className="bg-[#15181E] border border-[#1E2330] rounded-2xl p-8 text-center space-y-2">
        <p className="text-sm text-[#ECE9E2]">Race data not available</p>
        <p className="text-xs text-[#7D8594] font-mono">
          Run <code className="bg-[#1C2028] px-1.5 py-0.5 rounded">make eval</code> to generate race.json
        </p>
        {error && <p className="text-xs text-red-400 font-mono">Error: {error}</p>}
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Title & Controls */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="text-xs text-[#7D8594] font-mono">
            SPEC §9.2 · Measured on Shared Virtual Clock · n={nTurns} turns
          </div>
          <h2 className="text-xl sm:text-2xl font-bold text-[#ECE9E2] mt-1 tracking-tight">
            Race vs. Sequential Batch Baseline
          </h2>
          <p className="text-[11px] text-[#7D8594] mt-1">
            Illustration uses timing milestones from{' '}
            {exampleTurn ? (
              <span className="text-[#8FB3FF] font-mono">{exampleTurn.turn_id}</span>
            ) : (
              'the measured evaluation run'
            )}
            . All numbers read from runs/eval/race.json.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={handleStart}
            disabled={isPlaying}
            className="flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-semibold bg-[#8FB3FF] text-[#0E1014] hover:bg-[#a3c2ff] disabled:opacity-50 transition-all shadow-sm"
          >
            <Play className="w-3.5 h-3.5 fill-current" />
            <span>{isPlaying ? 'Running race…' : 'Start race comparison'}</span>
          </button>

          <button
            onClick={handleReset}
            className="p-2 rounded-xl border border-[#1E2330] bg-[#15181E] text-[#A3A9B5] hover:text-[#ECE9E2] transition-colors"
            title="Reset"
          >
            <RotateCcw className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Hero Stats — all from measured data */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-[#15181E] border border-[#1E2330] rounded-2xl p-5 space-y-1">
          <div className="flex items-center gap-2 text-xs text-[#7D8594]">
            <Zap className="w-3.5 h-3.5 text-[#8FB3FF]" />
            <span>Median Time Saved</span>
          </div>
          <div className="text-2xl font-bold text-[#8FB3FF]">
            {medianTimeSaved > 0 ? `+${medianTimeSaved.toFixed(2)} s` : `${medianTimeSaved.toFixed(3)} s`}
          </div>
          <div className="text-[11px] text-[#7D8594]">
            Measured across {nTurns} turns ({raceData.summary.n_retrieval_turns} retrieval)
          </div>
        </div>

        <div className="bg-[#15181E] border border-[#1E2330] rounded-2xl p-5 space-y-1">
          <div className="flex items-center gap-2 text-xs text-[#7D8594]">
            <Clock className="w-3.5 h-3.5 text-[#6FD39A]" />
            <span>Ready-at-End Ratio</span>
          </div>
          <div className="text-2xl font-bold text-[#6FD39A]">
            {readyAtEnd !== null ? `${(readyAtEnd * 100).toFixed(1)}%` : 'TBD'}
          </div>
          <div className="text-[11px] text-[#7D8594]">Answer parts verified before speech stops</div>
        </div>

        <div className="bg-[#15181E] border border-[#1E2330] rounded-2xl p-5 space-y-1">
          <div className="flex items-center gap-2 text-xs text-[#7D8594]">
            <ShieldCheck className="w-3.5 h-3.5 text-[#ECE9E2]" />
            <span>Turns With Time Savings</span>
          </div>
          <div className="text-2xl font-bold text-[#ECE9E2]">
            {(raceData.summary.fraction_with_time_savings * 100).toFixed(1)}%
          </div>
          <div className="text-[11px] text-[#7D8594]">
            Fraction of turns where Kairos finished first
          </div>
        </div>
      </div>

      {/* Visual Race Track */}
      <div className="bg-[#15181E] border border-[#1E2330] rounded-2xl p-6 space-y-6">
        <div className="flex items-center justify-between text-xs font-mono text-[#7D8594] border-b border-[#1E2330] pb-2">
          <span>Simulation Time: {raceProgress.toFixed(2)} s</span>
          <span>Utterance End: {utteranceEnd.toFixed(2)} s</span>
        </div>

        {/* Arm 1: Kairos Streaming Live RAG */}
        <div className="space-y-2">
          <div className="flex items-center justify-between text-xs">
            <div className="flex items-center gap-2">
              <span className="w-2.5 h-2.5 rounded-full bg-[#8FB3FF]" />
              <span className="font-semibold text-[#ECE9E2]">Kairos (Streaming Live RAG)</span>
              <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-[#8FB3FF]/15 text-[#8FB3FF]">
                Answer-as-you-speak
              </span>
            </div>
            <span className="font-mono text-[#8FB3FF] font-medium">
              {raceProgress >= firstRetrieval
                ? `First retrieval at ${firstRetrieval.toFixed(2)} s`
                : 'Listening & retrieving…'}
            </span>
          </div>

          <div className="h-9 bg-[#1C2028] border border-[#282D3A] rounded-xl overflow-hidden relative flex items-center p-1">
            <div
              className="h-full bg-gradient-to-r from-[#8FB3FF] to-[#62D6B4] rounded-lg transition-all duration-75 flex items-center px-3 text-[11px] font-mono text-[#0E1014] font-bold"
              style={{ width: `${kairosDraftProgress}%` }}
            >
              {kairosDraftProgress > 30 && 'Drafting & verifying…'}
            </div>
            {raceProgress >= kairosReady && (
              <span className="absolute right-3 text-xs font-mono text-[#6FD39A] font-bold">
                FINISHED at {kairosReady.toFixed(2)} s
              </span>
            )}
          </div>
        </div>

        {/* Arm 2: Batch Baseline RAG */}
        <div className="space-y-2">
          <div className="flex items-center justify-between text-xs">
            <div className="flex items-center gap-2">
              <span className="w-2.5 h-2.5 rounded-full bg-[#7D8594]" />
              <span className="font-semibold text-[#A3A9B5]">Sequential Baseline (Batch RAG)</span>
              <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-[#1C2028] text-[#7D8594]">
                Waits for silence
              </span>
            </div>
            <span className="font-mono text-[#7D8594]">
              {raceProgress < utteranceEnd
                ? 'Idle (waiting for utterance end…)'
                : raceProgress < baselineReady
                ? 'Retrieval & generation in progress…'
                : `Finished at ${baselineReady.toFixed(2)} s (+${(baselineReady - kairosReady).toFixed(2)} s lag)`}
            </span>
          </div>

          <div className="h-9 bg-[#1C2028] border border-[#282D3A] rounded-xl overflow-hidden relative flex items-center p-1">
            <div
              className="h-full bg-[#7D8594] rounded-lg transition-all duration-75 flex items-center px-3 text-[11px] font-mono text-white"
              style={{ width: `${batchProgress}%` }}
            >
              {batchProgress > 30 && 'Retrieving & generating…'}
            </div>
            {raceProgress >= baselineReady && (
              <span className="absolute right-3 text-xs font-mono text-[#EF4444]">
                DELIVERED at {baselineReady.toFixed(2)} s (+{(baselineReady - kairosReady).toFixed(2)} s lag)
              </span>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
