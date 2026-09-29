import React from 'react';
import { Sparkles, CheckCircle2, Zap } from 'lucide-react';
import { ClaimObject, LegInfo, VersionDiff } from '../types';
import { SourcePopover } from './SourcePopover';
import { getIntentColor } from '../design/tokens';

interface AnswerCanvasProps {
  legs: LegInfo[];
  drafts: Record<string, ClaimObject>;
  finalAnswer: string;
  finalClaims: ClaimObject[];
  citations: string[];
  version: number;
  diff?: VersionDiff;
  readyAtEnd?: number;
  isDrafting: boolean;
  onQuickAction: (action: 'shorter' | 'bullets' | 'simple') => void;
  onSeeDiff: () => void;
}

export const AnswerCanvas: React.FC<AnswerCanvasProps> = ({
  legs,
  drafts,
  finalAnswer,
  finalClaims,
  version,
  readyAtEnd,
  isDrafting,
  onQuickAction,
  onSeeDiff,
}) => {
  // If we have final settled claims, render settled cards
  const hasSettledAnswer = Boolean(finalAnswer);

  return (
    <div className="space-y-4">
      {/* Header bar: Version update or status */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider font-mono">
            Answer Canvas
          </span>
          {version > 1 && (
            <button
              onClick={onSeeDiff}
              className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium bg-emerald-50 dark:bg-emerald-950/60 text-emerald-700 dark:text-emerald-300 border border-emerald-200 dark:border-emerald-800 hover:bg-emerald-100 transition-colors"
            >
              <span>Updated · v{version}</span>
              <span className="underline ml-0.5">See what changed</span>
            </button>
          )}
        </div>

        {isDrafting && (
          <div className="flex items-center gap-1.5 text-xs text-blue-600 dark:text-blue-400 font-mono animate-pulse">
            <Sparkles className="w-3.5 h-3.5" />
            <span>Drafting in parallel...</span>
          </div>
        )}
      </div>

      {/* Main Canvas Body: Intent sections */}
      <div className="space-y-3">
        {legs.length === 0 && !hasSettledAnswer ? (
          /* Empty / waiting placeholder */
          <div className="p-8 text-center border border-dashed border-slate-200 dark:border-slate-800 rounded-2xl">
            <p className="text-sm text-slate-400 dark:text-slate-500">
              Speak or start a demo scenario. Live answer sections will stream into this canvas.
            </p>
          </div>
        ) : hasSettledAnswer ? (
          /* Settled final claims */
          <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-5 shadow-sm space-y-4">
            {finalClaims.length > 0 ? (
              finalClaims.map((claim, idx) => {
                const intentStyle = getIntentColor(idx);
                return (
                  <div
                    key={claim.claim_id}
                    className="pl-3.5 border-l-2 text-slate-800 dark:text-slate-100 text-sm leading-relaxed transition-all duration-300"
                    style={{ borderColor: intentStyle.hex }}
                  >
                    <span className="transition-opacity duration-300 ease-in-out">{claim.text}</span>
                    {claim.citations.map((cite, cIdx) => (
                      <SourcePopover
                        key={cite}
                        citation={cite}
                        index={cIdx}
                        evidenceSpan={claim.evidence_span}
                      />
                    ))}
                  </div>
                );
              })
            ) : (
              <p className="text-sm text-slate-800 dark:text-slate-100 leading-relaxed">
                {finalAnswer}
              </p>
            )}

            {/* "Ready when you stopped" line (SPEC §14.3a item 3) */}
            {readyAtEnd !== undefined && readyAtEnd > 0 && (
              <div className="pt-3 border-t border-slate-100 dark:border-slate-800 flex items-center gap-2 text-xs text-slate-500 dark:text-slate-400 font-mono">
                <CheckCircle2 className="w-4 h-4 text-emerald-500" />
                <span>
                  {Math.round(readyAtEnd * 100)}% of parts were ready before you finished speaking
                </span>
                <span className="text-slate-300 dark:text-slate-700">·</span>
                <span className="text-blue-600 dark:text-blue-400 font-semibold flex items-center gap-1">
                  <Zap className="w-3 h-3 fill-current" /> Instant delivery
                </span>
              </div>
            )}
          </div>
        ) : (
          /* Streaming drafting / ghost sections */
          legs.map((leg, idx) => {
            const draft = drafts[leg.leg_id];
            const intentStyle = getIntentColor(idx);

            return (
              <div
                key={leg.leg_id}
                className={`p-4 rounded-xl border transition-all ${
                  draft
                    ? 'bg-blue-50/40 dark:bg-blue-950/20 border-blue-200 dark:border-blue-900/60 drafting-shimmer'
                    : 'bg-slate-50/50 dark:bg-slate-900/40 border-dashed border-slate-200 dark:border-slate-800'
                }`}
                style={{ borderLeftColor: intentStyle.hex, borderLeftWidth: '3px' }}
              >
                <div className="flex items-center justify-between mb-1.5">
                  <span
                    className="text-xs font-medium px-2 py-0.5 rounded font-mono"
                    style={{ backgroundColor: intentStyle.bg, color: intentStyle.hex }}
                  >
                    {leg.leg_id}: {leg.text.slice(0, 45)}...
                  </span>
                  <span className="text-[11px] font-mono text-slate-400">
                    {draft ? 'Draft verified' : 'Searching leg...'}
                  </span>
                </div>

                {draft ? (
                  <p className="text-xs text-slate-700 dark:text-slate-300 italic">
                    "{draft.text}"
                  </p>
                ) : (
                  <div className="h-4 bg-slate-200 dark:bg-slate-800 rounded w-3/4 animate-pulse mt-1" />
                )}
              </div>
            );
          })
        )}
      </div>

      {/* Quick Actions (Presentation only, zero retrieval) */}
      {hasSettledAnswer && (
        <div className="flex flex-wrap items-center gap-2 pt-1">
          <button
            onClick={() => onQuickAction('shorter')}
            className="px-3 py-1 text-xs rounded-lg border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-800 hover:bg-slate-50 text-slate-700 dark:text-slate-300 font-medium transition-colors"
          >
            Shorter
          </button>
          <button
            onClick={() => onQuickAction('bullets')}
            className="px-3 py-1 text-xs rounded-lg border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-800 hover:bg-slate-50 text-slate-700 dark:text-slate-300 font-medium transition-colors"
          >
            As bullets
          </button>
          <button
            onClick={() => onQuickAction('simple')}
            className="px-3 py-1 text-xs rounded-lg border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-800 hover:bg-slate-50 text-slate-700 dark:text-slate-300 font-medium transition-colors"
          >
            Explain simply
          </button>
          <span className="text-[11px] text-slate-400 dark:text-slate-500 font-mono ml-2">
            No new search needed (instant)
          </span>
        </div>
      )}
    </div>
  );
};
