import React, { useState } from 'react';
import { Mic, ArrowRight, BookOpen } from 'lucide-react';
import { AnswerCanvas } from './AnswerCanvas';
import { SourcesPanel } from './SourcesPanel';
import { ChangePanel } from './ChangePanel';
import { ClaimObject, LegInfo, VersionDiff } from '../types';

interface AssistantModeProps {
  transcript: string;
  isSearching: boolean;
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
  onSendText: (text: string) => void;
  onQuickAction: (action: 'shorter' | 'bullets' | 'simple') => void;
  onSeeDiff: () => void;
}

export const AssistantMode: React.FC<AssistantModeProps> = ({
  transcript,
  isSearching,
  legs,
  drafts,
  finalAnswer,
  finalClaims,
  citations,
  version,
  diff,
  readyAtEnd,
  readyCount,
  totalParts,
  isDrafting,
  onSendText,
  onQuickAction,
  onSeeDiff,
}) => {
  const [inputText, setInputText] = useState('');
  const [isMobileSourcesOpen, setIsMobileSourcesOpen] = useState(false);

  const handleSend = (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputText.trim()) return;
    onSendText(inputText.trim());
    setInputText('');
  };

  const isSpeaking = isDrafting || (isSearching && !finalAnswer);
  const isV2 = version > 1;

  // Render highlighted / underlined phrases matching intent colours
  const renderHighlightedTranscript = (text: string) => {
    if (!text) {
      return (
        <span className="text-[#7D8594] font-normal italic font-serif">
          "Tap the mic or type to ask about Pune venues, cancellation policy, or catering..."
        </span>
      );
    }

    // Match keywords for semantic intent underline
    const regex = /(workshop in Pune for 30 people|cancellation policy|catering options|catering|45 people)/gi;
    const parts = text.split(regex);

    return parts.map((part, i) => {
      const lower = part.toLowerCase();
      if (lower.includes('pune') || lower.includes('30 people')) {
        return (
          <span
            key={i}
            className="border-b-2 font-medium pb-0.5"
            style={{ borderColor: '#8FB3FF', color: '#ECE9E2' }}
          >
            {part}
            {isSpeaking && (
              <span className="inline-flex items-center justify-center w-3.5 h-3.5 ml-1 text-[9px] font-mono rounded-full bg-[#8FB3FF] text-[#0E1014] align-top">
                1
              </span>
            )}
          </span>
        );
      }
      if (lower.includes('cancellation')) {
        return (
          <span
            key={i}
            className="border-b-2 font-medium pb-0.5"
            style={{ borderColor: '#62D6B4', color: '#ECE9E2' }}
          >
            {part}
            {isSpeaking && (
              <span className="inline-flex items-center justify-center w-3.5 h-3.5 ml-1 text-[9px] font-mono rounded-full bg-[#62D6B4] text-[#0E1014] align-top">
                2
              </span>
            )}
          </span>
        );
      }
      if (lower.includes('cater')) {
        return (
          <span
            key={i}
            className="border-b-2 font-medium pb-0.5"
            style={{ borderColor: '#B98CFF', color: '#ECE9E2' }}
          >
            {part}
          </span>
        );
      }
      if (lower.includes('45 people')) {
        return (
          <span
            key={i}
            className="border-b-2 font-medium pb-0.5"
            style={{ borderColor: '#8FB3FF', color: '#ECE9E2' }}
          >
            {part}
          </span>
        );
      }
      return <span key={i}>{part}</span>;
    });
  };

  return (
    <div className="flex flex-col lg:flex-row gap-6 max-w-[1140px] mx-auto items-start">
      {/* 760px Left/Center Main Column */}
      <div className="w-full lg:max-w-[760px] flex-1 space-y-4">
        {/* Prior question in v2 (Board 3: dimmed) */}
        {isV2 && (
          <div className="flex items-center gap-2 text-xs text-[#7D8594] px-1 font-serif">
            <span className="text-[#A3A9B5] font-sans font-medium">Earlier</span>
            <span className="truncate">
              Organising a customer workshop in Pune for 30 attendees, with cancellation terms and catering options.
            </span>
          </div>
        )}

        {/* Live Transcript / Speech Area (Boards 1, 2, 3) */}
        <div className="bg-[#15181E] border border-[#1E2330] rounded-2xl p-5 space-y-3">
          <div className="flex items-center justify-between text-xs">
            <div className="flex items-center gap-2 text-[#A3A9B5] font-medium">
              {isSpeaking ? (
                <>
                  <div className="flex items-center gap-0.5 text-[#8FB3FF]">
                    <span className="w-0.5 h-3 bg-[#8FB3FF] animate-pulse" />
                    <span className="w-0.5 h-4 bg-[#8FB3FF] animate-pulse delay-75" />
                    <span className="w-0.5 h-2.5 bg-[#8FB3FF] animate-pulse delay-150" />
                  </div>
                  <span>You're speaking</span>
                </>
              ) : isV2 ? (
                <>
                  <span>You added a detail</span>
                  <span className="px-2 py-0.5 rounded-full text-[10px] font-mono bg-[#8FB3FF]/15 text-[#8FB3FF] border border-[#8FB3FF]/30">
                    changes part 1
                  </span>
                </>
              ) : (
                <span>You said</span>
              )}
            </div>

            <span className="text-xs font-mono text-[#7D8594]">
              {isSpeaking ? '1.6 s' : isV2 ? '1.2 s' : '2.1 s'}
            </span>
          </div>

          <div className="min-h-[44px] text-base leading-relaxed text-[#ECE9E2] font-serif">
            {renderHighlightedTranscript(transcript)}
          </div>

          {/* Real-time Intent Status Chips (Board 1) */}
          {isSpeaking && (
            <div className="flex flex-wrap items-center gap-2 pt-2 border-t border-[#1E2330] text-xs">
              <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-[#1C2028] border border-[#282D3A]">
                <span className="w-1.5 h-1.5 rounded-full bg-[#8FB3FF]" />
                <span className="text-[#ECE9E2]">Venue for 30 people</span>
                <span className="text-[#7D8594]">·</span>
                <span className="text-[#6FD39A] font-medium">found</span>
              </div>

              <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-[#1C2028] border border-[#282D3A]">
                <span className="w-1.5 h-1.5 rounded-full bg-[#62D6B4]" />
                <span className="text-[#ECE9E2]">Cancellation terms</span>
                <span className="text-[#7D8594]">·</span>
                <span className="text-[#7D8594]">looking it up</span>
              </div>

              <span className="text-xs text-[#7D8594] ml-1">Listening for more…</span>
            </div>
          )}
        </div>

        {/* Answer Canvas */}
        <AnswerCanvas
          legs={legs}
          drafts={drafts}
          finalAnswer={finalAnswer}
          finalClaims={finalClaims}
          citations={citations}
          version={version}
          diff={diff}
          readyAtEnd={readyAtEnd}
          readyCount={readyCount}
          totalParts={totalParts}
          isDrafting={isDrafting}
          onQuickAction={onQuickAction}
          onSeeDiff={onSeeDiff}
        />

        {/* Mobile-only "Sources · 5" trigger button (Board 5) */}
        <div className="block lg:hidden pt-2">
          <button
            onClick={() => setIsMobileSourcesOpen(!isMobileSourcesOpen)}
            className="w-full py-2.5 px-4 rounded-xl border border-[#282D3A] bg-[#1C2028] text-xs font-medium text-[#ECE9E2] flex items-center justify-center gap-2"
          >
            <BookOpen className="w-4 h-4 text-[#8FB3FF]" />
            <span>Sources · {citations.length || 5}</span>
          </button>
        </div>

        {/* Mobile Sources Drawer Modal */}
        {isMobileSourcesOpen && (
          <div className="fixed inset-0 z-50 bg-black/70 flex flex-col justify-end lg:hidden">
            <div className="bg-[#15181E] border-t border-[#1E2330] rounded-t-3xl max-h-[80vh] overflow-y-auto p-5 space-y-4">
              <div className="flex items-center justify-between pb-2 border-b border-[#1E2330]">
                <span className="font-semibold text-[#ECE9E2]">Sources</span>
                <button
                  onClick={() => setIsMobileSourcesOpen(false)}
                  className="text-xs text-[#A3A9B5] px-2 py-1"
                >
                  Done
                </button>
              </div>
              <SourcesPanel citations={citations} claims={finalClaims} isStreaming={isDrafting} />
            </div>
          </div>
        )}

        {/* Pill-Shaped Input Bar (Boards 1, 2, 3) */}
        {isSpeaking ? (
          /* Speaking Active Bar (Board 1 bottom) */
          <div className="bg-[#15181E] border border-[#1E2330] rounded-2xl p-4 flex items-center justify-between shadow-sm">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-full bg-[#ECE9E2] text-[#0E1014] flex items-center justify-center">
                <Mic className="w-5 h-5 fill-current" />
              </div>
              <div>
                <div className="text-xs font-semibold text-[#ECE9E2]">Listening…</div>
                <div className="text-[12px] text-[#7D8594]">
                  Keep talking. Kairos is already looking things up.
                </div>
              </div>
            </div>
            <button className="px-4 py-1.5 text-xs font-medium rounded-lg border border-[#282D3A] bg-[#1C2028] text-[#ECE9E2] hover:bg-[#252B36]">
              Stop
            </button>
          </div>
        ) : (
          /* Normal Input Bar (Boards 2, 3, 5) */
          <form
            onSubmit={handleSend}
            className="flex items-center bg-[#15181E] border border-[#1E2330] rounded-full px-2 py-1.5 shadow-sm focus-within:border-[#282D3A]"
          >
            {/* Mic Orb */}
            <button
              type="button"
              className="w-10 h-10 rounded-full bg-[#1C2028] border border-[#282D3A] flex items-center justify-center text-[#ECE9E2] hover:bg-[#252B36] transition-colors shrink-0"
              title="Voice input"
            >
              <Mic className="w-4 h-4" />
            </button>

            {/* Input Field */}
            <input
              type="text"
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              placeholder="Tap the mic, or type a question or a new detail…"
              className="flex-1 bg-transparent px-4 py-2 text-xs text-[#ECE9E2] placeholder-[#7D8594] focus:outline-none"
            />

            {/* Send Button */}
            <button
              type="submit"
              disabled={!inputText.trim()}
              className="w-9 h-9 rounded-full bg-[#1C2028] border border-[#282D3A] flex items-center justify-center text-[#A3A9B5] hover:text-[#ECE9E2] hover:bg-[#252B36] disabled:opacity-40 transition-all shrink-0 mr-1"
              title="Submit query"
            >
              <ArrowRight className="w-4 h-4" />
            </button>
          </form>
        )}
      </div>

      {/* 340px Right Column (Desktop only) */}
      <div className="hidden lg:block shrink-0">
        {isV2 ? (
          <ChangePanel version={version} diff={diff} />
        ) : (
          <SourcesPanel
            citations={citations}
            claims={finalClaims}
            isStreaming={isSpeaking}
          />
        )}
      </div>
    </div>
  );
};
