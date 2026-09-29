import React, { useState, useEffect } from 'react';
import { Play, RotateCcw, Zap, Clock, ShieldCheck } from 'lucide-react';
import { RACE_BENCHMARKS } from '../../fixtures/inspectorMocks';

export const RaceTab: React.FC = () => {
  const [isPlaying, setIsPlaying] = useState(false);
  const [raceProgress, setRaceProgress] = useState(0); // 0 to 4.0s

  useEffect(() => {
    let interval: number;
    if (isPlaying) {
      interval = window.setInterval(() => {
        setRaceProgress((prev) => {
          if (prev >= 4.0) {
            setIsPlaying(false);
            return 4.0;
          }
          return prev + 0.05;
        });
      }, 50);
    }
    return () => clearInterval(interval);
  }, [isPlaying]);

  const handleStart = () => {
    setRaceProgress(0);
    setIsPlaying(true);
  };

  const handleReset = () => {
    setIsPlaying(false);
    setRaceProgress(0);
  };

  const kairosDraftProgress = Math.min(
    100,
    Math.max(
      0,
      ((raceProgress - RACE_BENCHMARKS.firstRetrievalS) /
        (RACE_BENCHMARKS.utteranceEndS - RACE_BENCHMARKS.firstRetrievalS)) *
        100
    )
  );
  const batchProgress = Math.min(
    100,
    Math.max(
      0,
      ((raceProgress - RACE_BENCHMARKS.utteranceEndS) / RACE_BENCHMARKS.medianTimeSavingsS) * 100
    )
  );

  return (
    <div className="space-y-6">
      {/* Title & Controls */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="text-xs text-[#7D8594] font-mono">SPEC §9.2 · Measured on Shared Virtual Clock</div>
          <h2 className="text-xl sm:text-2xl font-bold text-[#ECE9E2] mt-1 tracking-tight">
            Race vs. Sequential Batch Baseline
          </h2>
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

      {/* Hero Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-[#15181E] border border-[#1E2330] rounded-2xl p-5 space-y-1">
          <div className="flex items-center gap-2 text-xs text-[#7D8594]">
            <Zap className="w-3.5 h-3.5 text-[#8FB3FF]" />
            <span>Median Time Saved</span>
          </div>
          <div className="text-2xl font-bold text-[#8FB3FF]">+1.51 s</div>
          <div className="text-[11px] text-[#7D8594]">p90: +1.94 s faster across 64 turns</div>
        </div>

        <div className="bg-[#15181E] border border-[#1E2330] rounded-2xl p-5 space-y-1">
          <div className="flex items-center gap-2 text-xs text-[#7D8594]">
            <Clock className="w-3.5 h-3.5 text-[#6FD39A]" />
            <span>Ready-at-End Ratio</span>
          </div>
          <div className="text-2xl font-bold text-[#6FD39A]">65.4%</div>
          <div className="text-[11px] text-[#7D8594]">Answer parts verified before speech stops</div>
        </div>

        <div className="bg-[#15181E] border border-[#1E2330] rounded-2xl p-5 space-y-1">
          <div className="flex items-center gap-2 text-xs text-[#7D8594]">
            <ShieldCheck className="w-3.5 h-3.5 text-[#ECE9E2]" />
            <span>Grounding Invariance</span>
          </div>
          <div className="text-2xl font-bold text-[#ECE9E2]">100%</div>
          <div className="text-[11px] text-[#7D8594]">0 fabricated citations in both arms</div>
        </div>
      </div>

      {/* Visual Race Track */}
      <div className="bg-[#15181E] border border-[#1E2330] rounded-2xl p-6 space-y-6">
        <div className="flex items-center justify-between text-xs font-mono text-[#7D8594] border-b border-[#1E2330] pb-2">
          <span>Simulation Time: {raceProgress.toFixed(2)} s</span>
          <span>Utterance End: 2.10 s</span>
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
              {raceProgress >= 1.02 ? 'First claim ready at 1.02 s' : 'Listening & retrieving…'}
            </span>
          </div>

          <div className="h-9 bg-[#1C2028] border border-[#282D3A] rounded-xl overflow-hidden relative flex items-center p-1">
            <div
              className="h-full bg-gradient-to-r from-[#8FB3FF] to-[#62D6B4] rounded-lg transition-all duration-75 flex items-center px-3 text-[11px] font-mono text-[#0E1014] font-bold"
              style={{ width: `${kairosDraftProgress}%` }}
            >
              {kairosDraftProgress > 30 && '✓ 2 of 3 parts verified before speech end'}
            </div>
            {raceProgress >= RACE_BENCHMARKS.utteranceEndS && (
              <span className="absolute right-3 text-xs font-mono text-[#6FD39A] font-bold">
                FINISHED at {RACE_BENCHMARKS.utteranceEndS.toFixed(2)} s (0.00s wait)
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
              {raceProgress < RACE_BENCHMARKS.utteranceEndS
                ? 'Idle (waiting for utterance end…)'
                : raceProgress < RACE_BENCHMARKS.batchSettledS
                ? 'Retrieval & generation in progress…'
                : `Finished at ${RACE_BENCHMARKS.batchSettledS.toFixed(2)} s (+${RACE_BENCHMARKS.medianTimeSavingsS.toFixed(2)} s lag)`}
            </span>
          </div>

          <div className="h-9 bg-[#1C2028] border border-[#282D3A] rounded-xl overflow-hidden relative flex items-center p-1">
            <div
              className="h-full bg-[#7D8594] rounded-lg transition-all duration-75 flex items-center px-3 text-[11px] font-mono text-white"
              style={{ width: `${batchProgress}%` }}
            >
              {batchProgress > 30 && 'Retrieving & generating…'}
            </div>
            {raceProgress >= 3.61 && (
              <span className="absolute right-3 text-xs font-mono text-[#EF4444]">
                DELIVERED at 3.61 s (+1.51 s lag)
              </span>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
