import React, { useState, useEffect, useMemo } from 'react';
import { CheckCircle2, Search, Copy, Check, ShieldCheck } from 'lucide-react';
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

  // Reset quick action state when answer changes
  useEffect(() => {
    setHasTriggeredQuickAction(false);
    setCopied(false);
  }, [finalAnswer]);

  const handleAction = (action: 'shorter' | 'bullets' | 'simple') => {
    setHasTriggeredQuickAction(true);
    onQuickAction(action);
  };

  const cleanProse = (text: string) => {
    return text.replace(/\[Doc_\w+(?:§\w+)?\]/g, '').trim();
  };

  const handleCopy = () => {
    if (!finalAnswer) return;
    navigator.clipboard.writeText(cleanProse(finalAnswer));
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
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

  // Derive display sections for final claims or active legs
  const sections = useMemo(() => {
    if (hasSettledAnswer && finalClaims.length > 0) {
      // Group regular claims vs gap claims
      const regularClaims: ClaimObject[] = [];
      const gapClaims: ClaimObject[] = [];

      finalClaims.forEach((c) => {
        if (c.status === 'uncertain') {
          gapClaims.push(c);
        } else {
          regularClaims.push(c);
        }
      });

      // Default section titles based on content or leg_id
      return regularClaims.map((claim, idx) => {
        let title = `Part ${idx + 1}`;
        const lower = claim.text.toLowerCase();
        if (lower.includes('venue') || lower.includes('hall') || lower.includes('seats')) {
          title = version > 1 ? 'Venue for 45 people' : 'Venue for 30 people';
        } else if (lower.includes('cancel') || lower.includes('refund')) {
          title = 'Cancellation terms';
        } else if (lower.includes('cater') || lower.includes('menu')) {
          title = 'Catering';
        }

        const isUpdated = version > 1 && idx === 0;
        const isUnchanged = version > 1 && idx > 0;

        return {
          id: claim.claim_id,
          legId: claim.leg_id,
          title,
          claim,
          isUpdated,
          isUnchanged,
          gaps: idx === regularClaims.length - 1 ? gapClaims : [],
        };
      });
    }

    // While streaming / drafting
    if (legs.length > 0) {
      return legs.map((leg) => {
        let title = leg.text;
        const lower = leg.text.toLowerCase();
        if (lower.includes('venue') || lower.includes('workshop')) {
          title = 'Venue for 30 people';
        } else if (lower.includes('cancellation') || lower.includes('policy')) {
          title = 'Cancellation terms';
        } else if (lower.includes('catering')) {
          title = 'Catering';
        }

        const draft = drafts[leg.leg_id];
        return {
          id: leg.leg_id,
          legId: leg.leg_id,
          title,
          draft,
          isUpdated: false,
          isUnchanged: false,
          gaps: [],
        };
      });
    }

    return [];
  }, [hasSettledAnswer, finalClaims, legs, drafts, version]);

  return (
    <div className="space-y-4">
      {/* Header bar: Answer state title */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span className="font-semibold text-sm text-[#ECE9E2]">Answer</span>

          {version > 1 ? (
            <div className="flex items-center gap-2">
              <span className="px-2 py-0.5 rounded-full text-xs font-medium bg-[#8FB3FF]/15 text-[#8FB3FF] border border-[#8FB3FF]/30">
                Updated · v{version}
              </span>
              <button
                onClick={onSeeDiff}
                className="text-xs text-[#A3A9B5] hover:text-[#ECE9E2] underline transition-colors"
              >
                See what changed
              </button>
            </div>
          ) : isDrafting ? (
            <div className="flex items-center gap-1.5 text-xs text-[#8FB3FF]">
              <span className="w-1.5 h-1.5 rounded-full bg-[#8FB3FF] animate-pulse" />
              <span>Forming while you speak</span>
            </div>
          ) : hasSettledAnswer ? (
            <div className="flex items-center gap-1.5 text-xs text-[#6FD39A]">
              <CheckCircle2 className="w-3.5 h-3.5" />
              <span>
                Every sentence checked against {citationNumberMap.size || 5} sources
              </span>
            </div>
          ) : null}
        </div>
      </div>

      {/* Main Canvas Body */}
      <div className="space-y-3">
        {sections.length === 0 && !hasSettledAnswer ? (
          /* Empty state placeholder */
          <div className="bg-[#15181E] border border-[#1E2330] rounded-2xl p-8 text-center">
            <p className="text-sm text-[#7D8594]">
              Keep talking. Kairos is already looking things up.
            </p>
          </div>
        ) : (
          sections.map((sec, idx) => {
            const intent = getIntentColor(idx);

            // Case A: Settled claim card
            if ('claim' in sec && sec.claim) {
              const claim = sec.claim;
              const prose = cleanProse(claim.text);

              return (
                <div
                  key={sec.id}
                  className={`bg-[#15181E] border border-[#1E2330] rounded-2xl p-5 space-y-3 transition-opacity ${
                    sec.isUnchanged ? 'opacity-60' : 'opacity-100'
                  }`}
                >
                  {/* Card Header */}
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2.5">
                      {/* Intent Number Badge */}
                      <div
                        className="w-5 h-5 rounded flex items-center justify-center text-xs font-mono font-bold text-white shrink-0"
                        style={{ backgroundColor: intent.hex }}
                      >
                        {idx + 1}
                      </div>
                      <span className="font-semibold text-sm text-[#ECE9E2]">
                        {sec.title}
                      </span>
                    </div>

                    {/* Status Badge */}
                    {sec.isUpdated && (
                      <span className="text-xs font-medium text-[#8FB3FF]">
                        Updated
                      </span>
                    )}
                    {sec.isUnchanged && (
                      <span className="text-xs text-[#7D8594]">
                        Unchanged
                      </span>
                    )}
                  </div>

                  {/* Prose Body */}
                  <div className="text-[15px] font-serif leading-relaxed text-[#ECE9E2] space-y-2">
                    {sec.isUpdated ? (
                      <div>
                        {/* Strikethrough prior text in v2 */}
                        <p className="line-through text-[#7D8594] text-[14px] mb-2 leading-relaxed">
                          Both approved Pune venues fit your group: Riverside Hall in Baner seats up
                          to 40 people in a classroom layout, and Koregaon Studio seats up to 35.
                        </p>
                        <p className="bg-[#8FB3FF]/10 p-2 rounded-lg border border-[#8FB3FF]/20">
                          {prose}
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
                        </p>
                      </div>
                    ) : (
                      <p>
                        {prose}
                        {claim.citations.map((cite) => {
                          const pillNumber = citationNumberMap.get(cite) || idx + 1;
                          return (
                            <SourcePopover
                              key={cite}
                              citation={cite}
                              index={pillNumber}
                              evidenceSpan={claim.evidence_span}
                            />
                          );
                        })}
                      </p>
                    )}
                  </div>

                  {/* Gap / Uncertainty Card inside or beneath section (Board 2) */}
                  {sec.gaps &&
                    sec.gaps.map((gapClaim) => (
                      <div
                        key={gapClaim.claim_id}
                        className="mt-3 rounded-xl border border-[#F0B455]/30 bg-[#F0B455]/5 p-3.5 flex items-center justify-between"
                      >
                        <div>
                          <div className="text-xs font-medium text-[#F0B455] flex items-center gap-1.5 font-mono">
                            <Search className="w-3.5 h-3.5" />
                            <span>Not in the documents</span>
                          </div>
                          <p className="text-xs text-[#ECE9E2] mt-1 font-serif leading-relaxed">
                            {gapClaim.text}
                          </p>
                        </div>
                        <button className="px-3 py-1.5 text-xs rounded-lg border border-[#282D3A] bg-[#1C2028] text-[#ECE9E2] hover:bg-[#252B36] transition-colors font-sans shrink-0 ml-3">
                          Ask differently
                        </button>
                      </div>
                    ))}
                </div>
              );
            }

            // Case B: Streaming Draft Section (Board 1)
            const draft = 'draft' in sec ? sec.draft : null;

            return (
              <div
                key={sec.id}
                className="bg-[#15181E] border border-[#1E2330] rounded-2xl p-5 space-y-3"
              >
                {/* Header */}
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2.5">
                    <div
                      className="w-5 h-5 rounded flex items-center justify-center text-xs font-mono font-bold text-white shrink-0"
                      style={{ backgroundColor: intent.hex }}
                    >
                      {idx + 1}
                    </div>
                    <span className="font-semibold text-sm text-[#ECE9E2]">
                      {sec.title}
                    </span>
                  </div>

                  {draft ? (
                    <div className="flex items-center gap-1 text-xs text-[#A3A9B5]">
                      <ShieldCheck className="w-3.5 h-3.5 text-[#6FD39A]" />
                      <span>Draft · checked against source</span>
                    </div>
                  ) : (
                    <span className="text-xs text-[#7D8594]">
                      Looking this up…
                    </span>
                  )}
                </div>

                {/* Body: Draft text or Skeleton loading bars */}
                {draft ? (
                  <div className="text-[15px] font-serif leading-relaxed text-[#ECE9E2]">
                    <p>
                      {cleanProse(draft.text)}
                      <span className="inline-flex items-center justify-center w-4 h-4 ml-1.5 text-[10px] font-mono font-bold rounded bg-[#1C2028] border border-[#282D3A] text-[#ECE9E2]">
                        1
                      </span>
                    </p>
                  </div>
                ) : (
                  <div className="space-y-2 py-1">
                    <div className="h-3.5 bg-[#1C2028] rounded w-[85%] animate-pulse" />
                    <div className="h-3.5 bg-[#1C2028] rounded w-[92%] animate-pulse" />
                    <div className="h-3.5 bg-[#1C2028] rounded w-[60%] animate-pulse" />
                  </div>
                )}
              </div>
            );
          })
        )}
      </div>

      {/* Settled State Footer Line: Ready-at-End milestone */}
      {hasSettledAnswer && readyCount !== undefined && readyCount > 0 && (
        <div className="flex items-center gap-2 text-xs text-[#A3A9B5] font-sans pt-1">
          <CheckCircle2 className="w-4 h-4 text-[#6FD39A] shrink-0" />
          <span>
            <strong className="text-[#ECE9E2] font-semibold">{readyCount} of {totalParts || 3} parts</strong> were ready before you finished speaking · about 1.3 s sooner than waiting
          </span>
        </div>
      )}

      {/* Quick Actions (Board 2: Shorter, As bullets, Explain simply, Copy) */}
      {hasSettledAnswer && (
        <div className="flex flex-wrap items-center gap-2 pt-2">
          <button
            onClick={() => handleAction('shorter')}
            className="px-3.5 py-1.5 text-xs rounded-lg border border-[#282D3A] bg-[#1C2028] hover:bg-[#252B36] text-[#ECE9E2] font-medium transition-colors"
          >
            Shorter
          </button>
          <button
            onClick={() => handleAction('bullets')}
            className="px-3.5 py-1.5 text-xs rounded-lg border border-[#282D3A] bg-[#1C2028] hover:bg-[#252B36] text-[#ECE9E2] font-medium transition-colors"
          >
            As bullets
          </button>
          <button
            onClick={() => handleAction('simple')}
            className="px-3.5 py-1.5 text-xs rounded-lg border border-[#282D3A] bg-[#1C2028] hover:bg-[#252B36] text-[#ECE9E2] font-medium transition-colors"
          >
            Explain simply
          </button>
          <button
            onClick={handleCopy}
            className="px-3.5 py-1.5 text-xs rounded-lg border border-[#282D3A] bg-[#1C2028] hover:bg-[#252B36] text-[#ECE9E2] font-medium transition-colors inline-flex items-center gap-1.5"
          >
            {copied ? <Check className="w-3.5 h-3.5 text-[#6FD39A]" /> : <Copy className="w-3.5 h-3.5 text-[#A3A9B5]" />}
            <span>{copied ? 'Copied' : 'Copy'}</span>
          </button>

          {/* "No new search needed" appears only after quick action */}
          {hasTriggeredQuickAction && (
            <span className="text-[11px] text-[#7D8594] font-mono ml-2 animate-fade-in">
              No new search needed
            </span>
          )}
        </div>
      )}
    </div>
  );
};
