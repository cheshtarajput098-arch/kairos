import React, { useState, useRef } from 'react';
import { Mic, ArrowRight, BookOpen, Square } from 'lucide-react';
import { AnswerCanvas } from './AnswerCanvas';
import { SourcesPanel } from './SourcesPanel';
import { ChangePanel } from './ChangePanel';
import { FirstRunScreen } from './FirstRunScreen';
import { StatusBanners } from './StatusBanners';
import { useSpeechRecognition } from '../hooks/useSpeechRecognition';
import { ClaimObject, LegInfo, VersionDiff } from '../types';
import { getIntentColor } from '../design/tokens';

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
  currentTime?: number;
  suggestions?: string[];
  onSendText: (text: string) => void;
  onQuickAction: (action: 'shorter' | 'bullets' | 'simple') => void;
  onSeeDiff: () => void;
  onFeedback?: (rating: 'up' | 'down') => void;
  connectionStatus?: 'connected' | 'connecting' | 'closed' | 'error';
  onRetryConnection?: () => void;
  micPermissionDenied?: boolean;
  onTypeInstead?: () => void;
  rateLimitError?: { message: string; requestId: string } | null;
  outOfScopeError?: { message: string; requestId: string } | null;
  generalError?: { code: string; message: string; requestId: string } | null;
  textSize?: 'normal' | 'large' | 'xlarge';
  showProvisionalDrafts?: boolean;
  inputRef?: React.RefObject<HTMLInputElement>;
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
  currentTime = 0,
  suggestions = [],
  onSendText,
  onQuickAction,
  onSeeDiff,
  onFeedback,
  connectionStatus = 'connected',
  onRetryConnection = () => {},
  micPermissionDenied = false,
  onTypeInstead,
  rateLimitError = null,
  outOfScopeError = null,
  generalError = null,
  textSize = 'normal',
  showProvisionalDrafts = true,
  inputRef,
}) => {
  const [inputText, setInputText] = useState('');
  const internalInputRef = useRef<HTMLInputElement>(null);
  const effectiveInputRef = inputRef || internalInputRef;
  const [isMobileSourcesOpen, setIsMobileSourcesOpen] = useState(false);
  const [selectedCitation, setSelectedCitation] = useState<string | null>(null);
  const [isListeningManual, setIsListeningManual] = useState(false);

  const {
    isListening: isSpeechListening,
    permissionDenied: isSpeechPermissionDenied,
    toggleListening: toggleSpeech,
    stopListening: stopSpeech,
  } = useSpeechRecognition((transcriptText, isFinal) => {
    setInputText(transcriptText);
    if (isFinal && transcriptText.trim()) {
      onSendText(transcriptText.trim());
      setInputText('');
    }
  });

  const isSpeaking =
    isDrafting ||
    (isSearching && !finalAnswer) ||
    isListeningManual ||
    isSpeechListening;
  const isV2 = version > 1;
  const isFirstRun = !transcript && !finalAnswer && legs.length === 0;

  const handleSend = (e: React.FormEvent) => {
    e.preventDefault();
    if (isSpeechListening) {
      stopSpeech();
    }
    if (!inputText.trim()) return;
    onSendText(inputText.trim());
    setInputText('');
    setIsListeningManual(false);
  };

  const handleMicToggle = () => {
    toggleSpeech();
    setIsListeningManual((prev) => !prev);
  };

  const handleSourceSelect = (cite: string) => {
    setSelectedCitation(cite);
    setIsMobileSourcesOpen(true);
  };

  // Render highlighted / underlined phrases matching dynamic intent subqueries
  const renderHighlightedTranscript = (text: string) => {
    if (!text) {
      return (
        <span className="text-[#7D8594] font-normal italic font-serif">
          "Tap the mic or type to ask about policies, venue rules, or equipment..."
        </span>
      );
    }

    if (!legs || legs.length === 0) {
      return <span>{text}</span>;
    }

    // Dynamic matching of leg subquery keywords
    return (
      <span>
        {legs.map((leg, idx) => {
          const color = getIntentColor(idx);
          return (
            <span
              key={leg.leg_id}
              className="border-b-2 font-medium pb-0.5 mr-2 inline-block"
              style={{ borderColor: color.hex, color: '#ECE9E2' }}
            >
              {leg.text}
              {isSpeaking && (
                <span
                  className="inline-flex items-center justify-center w-3.5 h-3.5 ml-1 text-[9px] font-mono font-bold rounded-full text-[#0E1014] align-top"
                  style={{ backgroundColor: color.hex }}
                >
                  {idx + 1}
                </span>
              )}
            </span>
          );
        })}
      </span>
    );
  };

  return (
    <div className="flex flex-col lg:flex-row gap-6 max-w-[1140px] mx-auto items-start">
      {/* 760px Left/Center Main Column */}
      <div className="w-full lg:max-w-[760px] flex-1 space-y-4">
        {/* Status Banners (Item 7: offline, mic permission, rate limit, out of scope, request_id) */}
        <StatusBanners
          connectionStatus={connectionStatus}
          onRetryConnection={onRetryConnection}
          micPermissionDenied={micPermissionDenied}
          onTypeInstead={() => {
            if (onTypeInstead) onTypeInstead();
            inputRef?.current?.focus();
          }}
          rateLimitError={rateLimitError}
          outOfScopeError={outOfScopeError}
          generalError={generalError}
        />

        {/* First-Run Screen (Item 6: Suggestions generated from corpus headings at index time) */}
        {isFirstRun ? (
          <FirstRunScreen
            suggestions={suggestions}
            onSelectSuggestion={(q) => onSendText(q)}
          />
        ) : (
          <>
            {/* Prior question in v2 (Board 3: dimmed) */}
            {isV2 && (
              <div className="flex items-center gap-2 text-xs text-[#7D8594] px-1 font-serif">
                <span className="text-[#A3A9B5] font-sans font-medium">Earlier</span>
                <span className="truncate">
                  {diff?.v1_text ? `Prior turn: ${diff.v1_text}` : 'Earlier question'}
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
                  {currentTime > 0 ? `${currentTime.toFixed(1)} s` : ''}
                </span>
              </div>

              <div className="min-h-[44px] text-base leading-relaxed text-[#ECE9E2] font-serif">
                {renderHighlightedTranscript(transcript)}
              </div>

              {/* Dynamic Real-time Intent Status Chips (Item 12: real events, no hardcoded text) */}
              {isSpeaking && legs.length > 0 && (
                <div className="flex flex-wrap items-center gap-2 pt-2 border-t border-[#1E2330] text-xs">
                  {legs.map((leg, idx) => {
                    const isFound = Boolean(drafts[leg.leg_id]);
                    const color = getIntentColor(idx);
                    return (
                      <div
                        key={leg.leg_id}
                        className="flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-[#1C2028] border border-[#282D3A]"
                      >
                        <span
                          className="w-1.5 h-1.5 rounded-full"
                          style={{ backgroundColor: color.hex }}
                        />
                        <span className="text-[#ECE9E2]">{leg.text}</span>
                        <span className="text-[#7D8594]">·</span>
                        <span
                          className={isFound ? 'text-[#6FD39A] font-medium' : 'text-[#7D8594]'}
                        >
                          {isFound ? 'found' : 'looking it up'}
                        </span>
                      </div>
                    );
                  })}
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
              onSelectSource={handleSourceSelect}
              onFeedback={onFeedback}
              textSize={textSize}
              showProvisionalDrafts={showProvisionalDrafts}
            />
          </>
        )}

        {/* Mobile-only "Sources" trigger button (Board 5) */}
        <div className="block lg:hidden pt-2">
          <button
            onClick={() => setIsMobileSourcesOpen(!isMobileSourcesOpen)}
            className="w-full py-2.5 px-4 rounded-xl border border-[#282D3A] bg-[#1C2028] text-xs font-medium text-[#ECE9E2] flex items-center justify-center gap-2"
          >
            <BookOpen className="w-4 h-4 text-[#8FB3FF]" />
            <span>Sources · {citations.length || 0}</span>
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
              <SourcesPanel
                citations={citations}
                claims={finalClaims}
                isStreaming={isDrafting}
                selectedCitation={selectedCitation}
                onSelectCitation={setSelectedCitation}
              />
            </div>
          </div>
        )}

        {/* Item 1: Mic bar: 52–56px ivory mic with listening ring, "Listening… Keep talking. Kairos is already looking things up.", Stop button, text input and send button */}
        <div className="bg-[#15181E] border border-[#1E2330] rounded-2xl p-3.5 space-y-3 shadow-lg">
          {/* Active Listening Indicator Banner when speaking */}
          {isSpeaking && (
            <div className="flex items-center justify-between px-2 py-1 bg-[#1C2028]/80 border border-[#282D3A] rounded-xl">
              <div className="flex items-center gap-2 text-xs">
                <span className="relative flex h-2.5 w-2.5">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-[#8FB3FF] opacity-75"></span>
                  <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-[#8FB3FF]"></span>
                </span>
                <div>
                  <span className="font-semibold text-[#ECE9E2]">Listening…</span>{' '}
                  <span className="text-[#7D8594]">Keep talking. Kairos is already looking things up.</span>
                </div>
              </div>
              <button
                type="button"
                onClick={handleMicToggle}
                className="px-3 py-1 text-xs font-medium rounded-lg border border-[#282D3A] bg-[#15181E] text-[#ECE9E2] hover:bg-[#252B36] flex items-center gap-1.5 shrink-0"
              >
                <Square className="w-3 h-3 fill-current text-[#E5484D]" />
                <span>Stop</span>
              </button>
            </div>
          )}

          {/* Mic Permission Denied Banner (Item 7) */}
          {isSpeechPermissionDenied && (
            <div className="flex items-center justify-between px-4 py-2.5 rounded-xl bg-[#E5484D]/10 border border-[#E5484D]/30 text-xs text-[#E5484D] animate-fade-in">
              <div className="flex items-center gap-2">
                <span>Microphone access was denied. You can type your question instead.</span>
              </div>
              <button
                type="button"
                onClick={() => effectiveInputRef.current?.focus()}
                className="font-medium underline hover:text-[#FF8B8B] transition-colors"
              >
                Type instead
              </button>
            </div>
          )}

          {/* Unified Input Row: 52-56px Ivory Mic Orb + Text Input + Send Button */}
          <form onSubmit={handleSend} className="flex items-center gap-3">
            {/* 52-56px Ivory Mic with listening ring */}
            <div className="relative shrink-0">
              <button
                type="button"
                onClick={handleMicToggle}
                className={`w-[54px] h-[54px] rounded-full flex items-center justify-center transition-all ${
                  isSpeaking
                    ? 'bg-[#ECE9E2] text-[#0E1014] ring-4 ring-[#ECE9E2]/30 ring-offset-2 ring-offset-[#0E1014] animate-pulse shadow-lg'
                    : 'bg-[#ECE9E2] text-[#0E1014] hover:bg-white hover:scale-105 shadow-md'
                }`}
                title={isSpeaking ? 'Stop listening' : 'Start speaking'}
                aria-label={isSpeaking ? 'Stop listening' : 'Start speaking'}
              >
                <Mic className="w-6 h-6 fill-current" />
              </button>
            </div>

            {/* Text Input Field */}
            <div className="flex-1 relative flex items-center bg-[#12151B] border border-[#1E2330] rounded-xl px-4 py-2.5 focus-within:border-[#8FB3FF]/50 transition-colors">
              <input
                ref={effectiveInputRef}
                type="text"
                value={inputText}
                onChange={(e) => setInputText(e.target.value)}
                placeholder="Tap the mic or type a question or detail…"
                className="w-full bg-transparent text-xs sm:text-sm text-[#ECE9E2] placeholder-[#7D8594] focus:outline-none"
              />
            </div>

            {/* Send Button */}
            <button
              type="submit"
              disabled={!inputText.trim()}
              className="w-11 h-11 rounded-xl bg-[#1C2028] border border-[#282D3A] flex items-center justify-center text-[#A3A9B5] hover:text-[#ECE9E2] hover:bg-[#252B36] hover:border-[#8FB3FF]/40 disabled:opacity-40 transition-all shrink-0 cursor-pointer"
              title="Send question"
              aria-label="Send question"
            >
              <ArrowRight className="w-5 h-5" />
            </button>
          </form>
        </div>
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
            selectedCitation={selectedCitation}
            onSelectCitation={setSelectedCitation}
          />
        )}
      </div>
    </div>
  );
};
