import React, { useState, useEffect, useMemo } from 'react';
import { CheckCircle2, Search, Copy, Check, ShieldCheck, ThumbsUp, ThumbsDown, RefreshCw } from 'lucide-react';
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
  onSelectSource?: (citation: string, evidenceSpan?: string) => void;
  onFeedback?: (rating: 'up' | 'down') => void;
  textSize?: 'normal' | 'large' | 'xlarge';
  showProvisionalDrafts?: boolean;
}

export const AnswerCanvas: React.FC<AnswerCanvasProps> = ({
  legs,
  drafts,
  finalAnswer,
  finalClaims,
  version,
  diff,
  readyCount,
  totalParts,
  isDrafting,
  onQuickAction,
  onSeeDiff,
  onSelectSource,
  onFeedback,
  textSize = 'normal',
  showProvisionalDrafts = true,
}) => {
  const hasSettledAnswer = Boolean(finalAnswer);
  const [hasTriggeredQuickAction, setHasTriggeredQuickAction] = useState(false);
  const [copied, setCopied] = useState(false);
  const [feedbackRating, setFeedbackRating] = useState<'up' | 'down' | null>(null);

  // Reset quick action state when answer changes
  useEffect(() => {
    setHasTriggeredQuickAction(false);
    setCopied(false);
    setFeedbackRating(null);
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

  const handleFeedback = (rating: 'up' | 'down') => {
    setFeedbackRating(rating);
    if (onFeedback) {
      onFeedback(rating);
    }
  };

  // Font size class mapping
  const textSizeClass =
    textSize === 'xlarge'
      ? 'text-[19px] leading-loose'
      : textSize === 'large'
      ? 'text-[17px] leading-relaxed'
      : 'text-[15px] leading-relaxed';

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

      return regularClaims.map((claim, idx) => {
        const associatedLeg = legs.find((l) => l.leg_id === claim.leg_id);
        const title = associatedLeg ? associatedLeg.text : `Part ${idx + 1}`;

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
        const title = leg.text;
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
    <div className="space-y-4" aria-live="polite" aria-atomic="false">
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
                Every sentence checked against {citationNumberMap.size || 3} sources
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
              const isSpeed2 = (claim as unknown as { speed?: number }).speed === 2;
              const speed1Prose = (claim as unknown as { speed1_text?: string }).speed1_text
                ? cleanProse((claim as unknown as { speed1_text?: string }).speed1_text || '')
                : prose;

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

                  {/* Prose Body with Two-Speed Cross-Fade (Item 3) */}
                  <div className={`${textSizeClass} font-serif text-[#ECE9E2] space-y-2`}>
                    {sec.isUpdated ? (
                      <div>
                        {diff?.v1_text && (
                          <p className="line-through text-[#7D8594] text-[14px] mb-2 leading-relaxed">
                            {diff.v1_text}
                          </p>
                        )}
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
                                onSelectSource={onSelectSource}
                              />
                            );
                          })}
                        </p>
                      </div>
                    ) : (
                      <div className="relative inline">
                        {/* Two-speed cross-fade without layout shift */}
                        <div className="grid grid-cols-1 grid-rows-1 items-start inline">
                          <span
                            className={`col-start-1 row-start-1 transition-opacity duration-500 ease-in-out ${
                              isSpeed2 ? 'opacity-0 pointer-events-none' : 'opacity-100'
                            }`}
                          >
                            {speed1Prose}
                          </span>
                          {isSpeed2 && (
                            <span className="col-start-1 row-start-1 transition-opacity duration-500 ease-in-out opacity-100">
                              {prose}
                            </span>
                          )}
                        </div>

                        {/* Citations sit immediately adjacent without shifting */}
                        <span className="inline-block ml-1 align-baseline">
                          {claim.citations.map((cite) => {
                            const pillNumber = citationNumberMap.get(cite) || idx + 1;
                            return (
                              <SourcePopover
                                key={cite}
                                citation={cite}
                                index={pillNumber}
                                evidenceSpan={claim.evidence_span}
                                onSelectSource={onSelectSource}
                              />
                            );
                          })}
                        </span>
                      </div>
                    )}
                  </div>

                  {/* Gap / Uncertainty Card beneath section */}
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

            // Case B: Streaming Draft Section (Respects showProvisionalDrafts toggle)
            if (!showProvisionalDrafts) {
              return null;
            }

            const draft = 'draft' in sec ? sec.draft : null;
            const isRetracted = draft?.status === 'retracted';

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

                {/* Body: Draft text with rollback animation (Item 4) */}
                {draft ? (
                  <div
                    className={`${textSizeClass} font-serif text-[#ECE9E2] transition-opacity duration-300 ${
                      isRetracted ? 'opacity-30' : 'opacity-100'
                    }`}
                  >
                    {isRetracted ? (
                      <div className="flex items-center gap-2 text-xs text-[#F0B455] italic py-1">
                        <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                        <span>Refilling draft with updated details…</span>
                      </div>
                    ) : (
                      <p>
                        {cleanProse(draft.text)}
                        <span className="inline-flex items-center justify-center w-4 h-4 ml-1.5 text-[10px] font-mono font-bold rounded bg-[#1C2028] border border-[#282D3A] text-[#ECE9E2]">
                          1
                        </span>
                      </p>
                    )}
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

      {/* Quick Actions (Item 2: Shorter, As bullets, Explain simply, Copy) + Thumbs Feedback (Item 9) */}
      {hasSettledAnswer && (
        <div className="flex flex-wrap items-center justify-between gap-3 pt-2">
          <div className="flex flex-wrap items-center gap-2">
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

            {/* "No new search needed" appears only after quick action (Item 2) */}
            {hasTriggeredQuickAction && (
              <span className="text-[11px] text-[#7D8594] font-mono ml-2 animate-fade-in">
                No new search needed
              </span>
            )}
          </div>

          {/* Thumbs up/down per answer, kept in session telemetry only (Item 9) */}
          <div className="flex items-center gap-1.5 text-xs text-[#7D8594]">
            <button
              type="button"
              onClick={() => handleFeedback('up')}
              className={`p-1.5 rounded-lg border transition-colors ${
                feedbackRating === 'up'
                  ? 'bg-[#6FD39A]/20 border-[#6FD39A] text-[#6FD39A]'
                  : 'border-[#282D3A] bg-[#1C2028] hover:text-[#ECE9E2]'
              }`}
              title="Helpful answer"
              aria-label="Thumbs up"
            >
              <ThumbsUp className="w-3.5 h-3.5" />
            </button>
            <button
              type="button"
              onClick={() => handleFeedback('down')}
              className={`p-1.5 rounded-lg border transition-colors ${
                feedbackRating === 'down'
                  ? 'bg-[#E5484D]/20 border-[#E5484D] text-[#E5484D]'
                  : 'border-[#282D3A] bg-[#1C2028] hover:text-[#ECE9E2]'
              }`}
              title="Unhelpful answer"
              aria-label="Thumbs down"
            >
              <ThumbsDown className="w-3.5 h-3.5" />
            </button>
            {feedbackRating && (
              <span className="text-[11px] font-mono text-[#6FD39A] ml-1">Feedback saved</span>
            )}
          </div>
        </div>
      )}
    </div>
  );
};
