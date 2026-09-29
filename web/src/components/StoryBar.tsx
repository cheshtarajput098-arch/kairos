import React from 'react';
import { Play, Pause, SkipForward } from 'lucide-react';

interface StoryBarProps {
  currentScenarioIndex: number;
  totalScenarios: number;
  title: string;
  description: string;
  isPlaying: boolean;
  onPause: () => void;
  onResume: () => void;
  onNext: () => void;
  onExit: () => void;
}

export const StoryBar: React.FC<StoryBarProps> = ({
  currentScenarioIndex,
  totalScenarios,
  title,
  description,
  isPlaying,
  onPause,
  onResume,
  onNext,
  onExit,
}) => {
  return (
    <div className="h-14 bg-[#12151B] border-b border-[#1E2330] px-6 flex items-center justify-between text-xs text-[#ECE9E2]">
      <div className="flex items-center gap-3 overflow-hidden">
        {/* DEMO badge */}
        <span className="px-2 py-0.5 rounded font-mono text-[10px] font-bold tracking-wider bg-[#F0B455] text-[#0E1014]">
          DEMO
        </span>

        {/* Counter and Title */}
        <span className="font-medium text-[#ECE9E2] shrink-0">
          {currentScenarioIndex + 1} of {totalScenarios} · {title}
        </span>

        {/* Description */}
        <span className="text-[#7D8594] truncate hidden md:inline">
          {description}
        </span>
      </div>

      {/* Progress & Controls */}
      <div className="flex items-center gap-4 shrink-0">
        {/* Step progress lines/dots */}
        <div className="flex items-center gap-1.5">
          {Array.from({ length: totalScenarios }).map((_, i) => (
            <div
              key={i}
              className={`h-1 rounded-full transition-all ${
                i === currentScenarioIndex
                  ? 'w-6 bg-[#ECE9E2]'
                  : i < currentScenarioIndex
                  ? 'w-4 bg-[#7D8594]'
                  : 'w-4 bg-[#1E2330]'
              }`}
            />
          ))}
        </div>

        {/* Pause/Resume button */}
        {isPlaying ? (
          <button
            onClick={onPause}
            className="p-1.5 text-[#A3A9B5] hover:text-[#ECE9E2] rounded transition-colors"
            title="Pause demo"
          >
            <Pause className="w-3.5 h-3.5 fill-current" />
          </button>
        ) : (
          <button
            onClick={onResume}
            className="p-1.5 text-[#A3A9B5] hover:text-[#ECE9E2] rounded transition-colors"
            title="Resume demo"
          >
            <Play className="w-3.5 h-3.5 fill-current" />
          </button>
        )}

        {/* Next button */}
        <button
          onClick={onNext}
          className="p-1.5 text-[#A3A9B5] hover:text-[#ECE9E2] rounded transition-colors"
          title="Next scenario"
        >
          <SkipForward className="w-3.5 h-3.5 fill-current" />
        </button>

        {/* Exit button */}
        <button
          onClick={onExit}
          className="px-2.5 py-1 text-xs text-[#A3A9B5] hover:text-[#ECE9E2] border border-[#1E2330] rounded-md transition-colors"
        >
          Exit
        </button>
      </div>
    </div>
  );
};
