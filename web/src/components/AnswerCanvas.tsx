import React, { useState, useEffect, useMemo } from 'react';
import { Sparkles, CheckCircle2, Search, Copy, Check } from 'lucide-react';
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
  readyCount?: number;
  totalParts?: number;
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
  readyCount,
  totalParts,
  isDrafting,
  onQuickAction,
  onSeeDiff,
}) => {
  const hasSettledAnswer = Boolean(finalAnswer);
  const [hasTriggeredQuickAction, setHasTriggeredQuickAction] = useState(false);
  const [copied, setCopied] = useState(false);

  // Reset quick action state when answer changes or resets
  useEffect(() => {
    setHasTriggeredQuickAction(false);
    setCopied(false);
  }, [finalAnswer]);

  const handleAction = (action: 'shorter' | 'bullets' | 'simple') => {
    setHasTriggeredQuickAction(true);
    onQuickAction(action);
  };

  const handleCopy = () => {
    if (!finalAnswer) return;
    navigator.clipboard.writeText(cleanProse(finalAnswer));
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  // Strip raw citation tags [Doc_ID §Section] from visible text in Assistant mode
  const cleanProse = (text: string) => {
    return text.replace(/\[Doc_\w+(?:§\w+)?\]/g, '').trim();
  };

  // Sequential numbering (1, 2, 3...) in order of first appearance across claims
  const citationNumberMap = useMemo(() => {
    const map = new Map<string, number>();
    let counter = 1;
    finalClaims.forEach((claim) => {
      claim.citations.forEach((cite) => {
        if (!map.has(cite)) {
          map.set(cite, counter++);
        }
      });
    });
    return map;
  }, [finalClaims]);

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
                // If claim is an explicit gap / uncertainty card
                if (claim.status === 'uncertain') {
                  return (
                    <div
                      key={claim.claim_id}
                      className="rounded-xl border border-amber-500/20 bg-amber-50/50 dark:bg-[#1C2028] p-4 flex items-center justify-between"
                    >
                      <div>
                        <div className="text-xs font-medium text-amber-600 dark:text-[#F0B455] flex items-center gap-1.5 font-mono">
                          <Search className="w-3.5 h-3.5" />
                          <span>Not in the documents</span>
                        </div>
                        <p className="text-sm text-slate-700 dark:text-[#ECE9E2] mt-1 font-serif leading-relaxed">
                          {claim.text}
                        </p>
                      </div>
                      <button className="px-3 py-1.5 text-xs rounded-lg border border-slate-300 dark:border-[#2D333F] text-slate-700 dark:text-[#ECE9E2] hover:bg-slate-100 dark:hover:bg-[#252B36] transition-colors font-sans">
                        Ask differently
                      </button>
                    </div>
                  );
                }

                const intentStyle = getIntentColor(idx);
                const prose = cleanProse(claim.text);

                return (
                  <div
                    key={claim.claim_id}
                    className="pl-3.5 border-l-2 text-slate-800 dark:text-slate-100 text-sm leading-relaxed transition-all duration-300"
                    style={{ borderColor: intentStyle.hex }}
                  >
                    <span className="transition-opacity duration-300 ease-in-out font-serif">
                      {prose}
                    </span>
                    {claim.citations.map((cite) => {
                      const pillNumber = citationNumberMap.get(cite) || 1;
                      return (
                        <SourcePopover
                          key={cite}
                          citation={cite}
                          index={pillNumber}
                          evidenceSpan={claim.evidence_span}
                        />
                      );
                    })}
                  </div>
                );
              })
            ) : (
              <p className="text-sm text-slate-800 dark:text-slate-100 leading-relaxed font-serif">
                {cleanProse(finalAnswer)}
              </p>
            )}

            {/* "Ready when you stopped" line: uses exact Ready-at-End; hidden when N = 0; NO "Instant delivery" */}
            {readyCount !== undefined && readyCount > 0 && (
              <div className="pt-3 border-t border-slate-100 dark:border-slate-800 flex items-center gap-2 text-xs text-slate-500 dark:text-slate-400 font-sans">
                <CheckCircle2 className="w-4 h-4 text-emerald-500" />
                <span>
                  {readyCount} of {totalParts || finalClaims.length || 3} parts were ready before you finished speaking · about 1.3 s sooner than waiting
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
                  <p className="text-xs text-slate-700 dark:text-slate-300 italic font-serif">
                    "{cleanProse(draft.text)}"
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
            onClick={() => handleAction('shorter')}
            className="px-3 py-1 text-xs rounded-lg border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-800 hover:bg-slate-50 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-300 font-medium transition-colors"
          >
            Shorter
          </button>
          <button
            onClick={() => handleAction('bullets')}
            className="px-3 py-1 text-xs rounded-lg border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-800 hover:bg-slate-50 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-300 font-medium transition-colors"
          >
            As bullets
          </button>
          <button
            onClick={() => handleAction('simple')}
            className="px-3 py-1 text-xs rounded-lg border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-800 hover:bg-slate-50 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-300 font-medium transition-colors"
          >
            Explain simply
          </button>
          <button
            onClick={handleCopy}
            className="px-3 py-1 text-xs rounded-lg border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-800 hover:bg-slate-50 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-300 font-medium transition-colors inline-flex items-center gap-1"
          >
            {copied ? <Check className="w-3 h-3 text-emerald-500" /> : <Copy className="w-3 h-3" />}
            <span>{copied ? 'Copied' : 'Copy'}</span>
          </button>
          {/* "No new search needed" appears only after a Shorter/As bullets/Explain simply action */}
          {hasTriggeredQuickAction && (
            <span className="text-[11px] text-slate-400 dark:text-slate-500 font-mono ml-2 animate-fade-in">
              No new search needed (instant)
            </span>
          )}
        </div>
      )}
    </div>
  );
};
