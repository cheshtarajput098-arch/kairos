import React from 'react';
import { Timeline } from './Timeline';
import { TelemetryPanel } from './TelemetryPanel';
import { ClaimObject, ControllerDecisionEvent, LegInfo, StreamEvent, VersionDiff } from '../types';
import { getIntentColor } from '../design/tokens';

interface InspectorModeProps {
  decisions: ControllerDecisionEvent[];
  legs: LegInfo[];
  firstRetrievalT: number | null;
  utteranceEndT: number | null;
  currentTime: number;
  events: StreamEvent[];
  readyAtEnd?: number;
  finalAnswer: string;
  finalClaims: ClaimObject[];
  citations: string[];
  version: number;
  diff?: VersionDiff;
}

export const InspectorMode: React.FC<InspectorModeProps> = ({
  decisions,
  legs,
  firstRetrievalT,
  utteranceEndT,
  currentTime,
  events,
  readyAtEnd,
  finalClaims,
  citations,
  version,
  diff,
}) => {
  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* 1. Signature Timeline */}
      <Timeline
        decisions={decisions}
        legs={legs}
        firstRetrievalT={firstRetrievalT}
        utteranceEndT={utteranceEndT}
        currentTime={currentTime}
      />

      {/* 2. Structured Answer & Grounding Panel */}
      <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-5 shadow-sm space-y-4">
        <div className="flex items-center justify-between border-b border-slate-100 dark:border-slate-800 pb-2">
          <span className="text-xs font-mono font-bold uppercase text-slate-800 dark:text-slate-200">
            Grounding & Citation Inspection (v{version})
          </span>
          <span className="text-xs font-mono text-emerald-600 dark:text-emerald-400">
            {citations.length} Verified Sources
          </span>
        </div>

        {finalClaims.length > 0 ? (
          <div className="space-y-3">
            {finalClaims.map((claim, idx) => {
              const intentStyle = getIntentColor(idx);
              return (
                <div
                  key={claim.claim_id}
                  className="p-3 rounded-xl border border-slate-100 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-850/50 space-y-2"
                  style={{ borderLeftColor: intentStyle.hex, borderLeftWidth: '3px' }}
                >
                  <div className="flex items-center justify-between text-xs">
                    <span className="font-mono font-semibold" style={{ color: intentStyle.hex }}>
                      Leg {claim.leg_id} · Claim {claim.claim_id}
                    </span>
                    <div className="flex items-center gap-1">
                      {claim.citations.map((c) => (
                        <span
                          key={c}
                          className="px-2 py-0.5 rounded text-[10px] font-mono bg-blue-100 dark:bg-blue-900/60 text-blue-700 dark:text-blue-300 font-bold"
                        >
                          {c}
                        </span>
                      ))}
                    </div>
                  </div>

                  <p className="text-xs text-slate-800 dark:text-slate-200 leading-relaxed">
                    {claim.text}
                  </p>

                  <div className="text-[11px] text-slate-500 italic bg-white dark:bg-slate-900 p-2 rounded border border-slate-100 dark:border-slate-800">
                    <span className="font-semibold text-slate-400 not-italic">Span: </span>
                    "{claim.evidence_span}"
                  </div>
                </div>
              );
            })}
          </div>
        ) : (
          <div className="text-xs text-slate-400 italic">No committed answer in current session yet.</div>
        )}

        {/* Diff view if v > 1 */}
        {diff && (
          <div className="mt-4 pt-3 border-t border-slate-100 dark:border-slate-800 text-xs font-mono space-y-1">
            <div className="text-[11px] font-bold uppercase text-slate-400">Version Diff</div>
            <div className="flex flex-wrap gap-2 text-[11px]">
              {diff.changed.length > 0 && (
                <span className="text-amber-500">Changed: [{diff.changed.join(', ')}]</span>
              )}
              {diff.unchanged.length > 0 && (
                <span className="text-emerald-500">Unchanged: [{diff.unchanged.join(', ')}]</span>
              )}
              {diff.added.length > 0 && (
                <span className="text-blue-500">Added: [{diff.added.join(', ')}]</span>
              )}
            </div>
          </div>
        )}
      </div>

      {/* 3. Live Telemetry Panel */}
      <TelemetryPanel
        events={events}
        readyAtEnd={readyAtEnd}
        retrievalsCount={legs.length}
      />
    </div>
  );
};
