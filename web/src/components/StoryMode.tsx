import React from 'react';
import { Play, Pause, RotateCcw, FastForward, CheckCircle2 } from 'lucide-react';
import strings from '../strings.en.json';

interface StoryModeProps {
  currentScenarioIndex: number;
  isPlaying: boolean;
  onStartScenario: (index: number) => void;
  onPause: () => void;
  onResume: () => void;
  onReset: () => void;
}

export const SCENARIOS = [
  {
    id: 's1',
    title: 'Scenario 1: Compound Multi-Intent',
    tag: 'Multi-Intent Decomposition',
    caption: strings.storyMode.scenario1.caption,
    chunks: [
      { t: 0.0, text: 'We want to organise a workshop in' },
      { t: 0.8, text: 'Pune for 30 attendees, and need' },
      { t: 1.6, text: 'the cancellation policy plus catering options.' },
    ],
    utteranceEnd: 2.1,
  },
  {
    id: 's2',
    title: 'Scenario 2: Late-Arriving Detail',
    tag: 'In-Place Refinement (v1 → v2)',
    caption: strings.storyMode.scenario2.caption,
    chunks: [
      { t: 0.0, text: 'Explain the travel reimbursement rules' },
      { t: 1.6, text: 'for domestic staff travel.' },
      { t: 2.5, text: 'Actually, the booking was made for an' },
      { t: 3.5, text: 'international trip in foreign currency.' },
    ],
    utteranceEnd: 4.2,
  },
  {
    id: 's3',
    title: 'Scenario 3: Presentation Suppression',
    tag: 'Zero-Retrieval Presentation',
    caption: strings.storyMode.scenario3.caption,
    chunks: [
      { t: 0.0, text: 'What are the venue booking rules in Pune?' },
      { t: 2.0, text: 'Could you reformat that into brief bullet points?' },
    ],
    utteranceEnd: 3.0,
  },
];

export const StoryMode: React.FC<StoryModeProps> = ({
  currentScenarioIndex,
  isPlaying,
  onStartScenario,
  onPause,
  onResume,
  onReset,
}) => {
  const activeScenario = SCENARIOS[currentScenarioIndex] || SCENARIOS[0];

  return (
    <div className="bg-gradient-to-r from-blue-900 to-indigo-900 text-white rounded-2xl p-5 shadow-md space-y-4">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-blue-800 pb-3">
        <div>
          <div className="flex items-center gap-2">
            <span className="px-2 py-0.5 rounded text-[10px] font-mono uppercase bg-blue-700 font-bold tracking-wider">
              Story Mode
            </span>
            <span className="text-sm font-semibold">{activeScenario.title}</span>
          </div>
          <p className="text-xs text-blue-200 mt-1 max-w-xl">
            {activeScenario.caption}
          </p>
        </div>

        {/* Playback Controls */}
        <div className="flex items-center gap-2 self-start sm:self-auto">
          {isPlaying ? (
            <button
              onClick={onPause}
              className="p-2 rounded-lg bg-blue-700 hover:bg-blue-600 text-white transition-colors"
              title="Pause playback"
            >
              <Pause className="w-4 h-4 fill-current" />
            </button>
          ) : (
            <button
              onClick={onResume}
              className="p-2 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white transition-colors"
              title="Play scenario"
            >
              <Play className="w-4 h-4 fill-current" />
            </button>
          )}

          <button
            onClick={() => onStartScenario((currentScenarioIndex + 1) % SCENARIOS.length)}
            className="p-2 rounded-lg bg-blue-800 hover:bg-blue-700 text-blue-200 hover:text-white transition-colors"
            title="Next scenario"
          >
            <FastForward className="w-4 h-4" />
          </button>

          <button
            onClick={onReset}
            className="p-2 rounded-lg bg-blue-800 hover:bg-blue-700 text-blue-200 hover:text-white transition-colors"
            title="Reset"
          >
            <RotateCcw className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Scenario Progress Track */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-2 pt-1">
        {SCENARIOS.map((sc, idx) => {
          const isCurrent = idx === currentScenarioIndex;
          const isDone = idx < currentScenarioIndex;

          return (
            <button
              key={sc.id}
              onClick={() => onStartScenario(idx)}
              className={`p-2.5 rounded-xl text-left border transition-all text-xs ${
                isCurrent
                  ? 'bg-white/10 border-white/40 shadow-sm'
                  : 'bg-black/10 border-transparent hover:bg-white/5 opacity-80'
              }`}
            >
              <div className="flex items-center justify-between text-[11px] font-mono">
                <span className="font-semibold text-blue-200">0{idx + 1}</span>
                {isDone && <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />}
              </div>
              <div className="font-medium mt-1 truncate">{sc.title}</div>
              <div className="text-[10px] text-blue-300 font-mono mt-0.5">{sc.tag}</div>
            </button>
          );
        })}
      </div>
    </div>
  );
};
