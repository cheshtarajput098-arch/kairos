import React from 'react';
import { ControllerDecisionEvent, LegInfo } from '../types';
import { getIntentColor } from '../design/tokens';

interface TimelineProps {
  decisions: ControllerDecisionEvent[];
  legs: LegInfo[];
  firstRetrievalT: number | null;
  utteranceEndT: number | null;
  currentTime: number;
}

export const Timeline: React.FC<TimelineProps> = ({
  decisions,
  legs,
  firstRetrievalT,
  utteranceEndT,
  currentTime,
}) => {
  // Normalize time width: max of utteranceEnd or last decision
  const maxTime = Math.max(utteranceEndT || 4.0, decisions.length > 0 ? decisions[decisions.length - 1].t + 1 : 4.0);

  const getPositionPercent = (t: number) => {
    return Math.min(100, Math.max(0, (t / maxTime) * 100));
  };

  return (
    <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-5 shadow-sm space-y-4">
      <div className="flex items-center justify-between border-b border-slate-100 dark:border-slate-800 pb-2">
        <div className="flex items-center gap-2">
          <span className="text-xs font-mono font-bold uppercase text-purple-600 dark:text-purple-400">
            Pipeline Timeline
          </span>
          <span className="text-xs text-slate-400 font-mono">
            {currentTime.toFixed(1)}s / {maxTime.toFixed(1)}s
          </span>
        </div>

        {/* Lead time pill */}
        {firstRetrievalT !== null && utteranceEndT !== null && utteranceEndT > firstRetrievalT && (
          <span className="px-2.5 py-0.5 rounded-full text-xs font-mono bg-blue-50 dark:bg-blue-900/40 text-blue-600 dark:text-blue-300 font-medium">
            Lead Time: +{(utteranceEndT - firstRetrievalT).toFixed(2)}s
          </span>
        )}
      </div>

      {/* Visual Timeline track */}
      <div className="relative pt-6 pb-2 min-h-[140px] flex flex-col justify-between">
        {/* Shaded Lead Time Area */}
        {firstRetrievalT !== null && utteranceEndT !== null && (
          <div
            className="absolute top-0 bottom-0 bg-blue-50/60 dark:bg-blue-950/30 border-l border-r border-blue-300 dark:border-blue-800 rounded-sm pointer-events-none"
            style={{
              left: `${getPositionPercent(firstRetrievalT)}%`,
              width: `${getPositionPercent(utteranceEndT) - getPositionPercent(firstRetrievalT)}%`,
            }}
          >
            <span className="text-[10px] font-mono text-blue-500 absolute -top-5 left-1">
              Shaded Lead Time
            </span>
          </div>
        )}

        {/* Utterance End vertical marker */}
        {utteranceEndT !== null && (
          <div
            className="absolute top-0 bottom-0 border-l-2 border-dashed border-rose-400 dark:border-rose-600 z-10"
            style={{ left: `${getPositionPercent(utteranceEndT)}%` }}
          >
            <span className="text-[9px] font-mono font-bold text-rose-500 uppercase absolute -top-5 -left-10 bg-rose-50 dark:bg-rose-950/80 px-1 py-0.5 rounded">
              End ({utteranceEndT.toFixed(1)}s)
            </span>
          </div>
        )}

        {/* Track 1: Controller Decisions */}
        <div className="relative h-7 border-b border-slate-100 dark:border-slate-800">
          <span className="text-[10px] font-mono uppercase text-slate-400 absolute -left-2 top-1 w-14">
            Ctrl
          </span>
          <div className="ml-14 relative h-full">
            {decisions.map((dec, i) => {
              const left = getPositionPercent(dec.t);
              const color =
                dec.decision === 'RETRIEVE'
                  ? 'bg-blue-500 text-white'
                  : dec.decision === 'WAIT'
                  ? 'bg-slate-400 text-white'
                  : 'bg-purple-500 text-white';

              return (
                <div
                  key={i}
                  className={`absolute top-0 -translate-x-1/2 px-1.5 py-0.5 rounded text-[10px] font-mono font-semibold cursor-help shadow-sm ${color}`}
                  style={{ left: `${left}%` }}
                  title={`t=${dec.t}s: ${dec.decision} (${dec.reason})`}
                >
                  {dec.decision[0]}
                </div>
              );
            })}
          </div>
        </div>

        {/* Track 2: Retrieval Legs Gantt Bars */}
        <div className="relative space-y-1.5 pt-2">
          <span className="text-[10px] font-mono uppercase text-slate-400 absolute -left-2 top-2 w-14">
            Legs
          </span>
          <div className="ml-14 space-y-1.5">
            {legs.length === 0 ? (
              <div className="h-6 flex items-center text-xs text-slate-400 italic">
                No active query legs dispatched yet
              </div>
            ) : (
              legs.map((leg, i) => {
                const intentStyle = getIntentColor(i);
                const startLeft = getPositionPercent(leg.first_dispatch_s);
                const endRight = utteranceEndT ? getPositionPercent(utteranceEndT) : 95;
                const width = Math.max(5, endRight - startLeft);

                return (
                  <div key={leg.leg_id} className="relative h-6 bg-slate-100 dark:bg-slate-800 rounded">
                    <div
                      className="absolute top-0 bottom-0 rounded px-2 flex items-center text-[11px] font-mono font-medium text-white overflow-hidden shadow-sm"
                      style={{
                        left: `${startLeft}%`,
                        width: `${width}%`,
                        backgroundColor: intentStyle.hex,
                      }}
                    >
                      <span className="truncate">{leg.leg_id}: {leg.text}</span>
                    </div>
                  </div>
                );
              })
            )}
          </div>
        </div>

        {/* Axis markers */}
        <div className="relative ml-14 h-4 pt-1 flex justify-between text-[10px] font-mono text-slate-400 border-t border-slate-200 dark:border-slate-800 mt-2">
          <span>0.0s</span>
          <span>{(maxTime * 0.25).toFixed(1)}s</span>
          <span>{(maxTime * 0.5).toFixed(1)}s</span>
          <span>{(maxTime * 0.75).toFixed(1)}s</span>
          <span>{maxTime.toFixed(1)}s</span>
        </div>
      </div>
    </div>
  );
};
