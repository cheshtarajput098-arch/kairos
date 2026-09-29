import React, { useState } from 'react';
import {
  Mic,
  ArrowRight,
  ChevronDown,
  CheckCircle2,
  Search,
  Lock,
  Play,
  Square,
  AlertCircle,
} from 'lucide-react';
import { useSpeechRecognition } from '../hooks/useSpeechRecognition';

interface HomeScreenProps {
  onSendQuestion: (text: string, isSpoken?: boolean) => void;
  onPlayScenario: (index: number) => void;
  isListening?: boolean;
  onToggleMic?: () => void;
}

export const HomeScreen: React.FC<HomeScreenProps> = ({
  onSendQuestion,
  onPlayScenario,
  isListening: externalIsListening = false,
  onToggleMic,
}) => {
  const [inputText, setInputText] = useState('');
  const [wasSpoken, setWasSpoken] = useState(false);

  const {
    isListening: isSpeechListening,
    permissionDenied: micDenied,
    toggleListening: toggleSpeech,
    stopListening: stopSpeech,
  } = useSpeechRecognition((transcriptText, isFinal) => {
    setInputText(transcriptText);
    setWasSpoken(true);
    if (isFinal && transcriptText.trim()) {
      onSendQuestion(transcriptText.trim(), true);
      setInputText('');
      setWasSpoken(false);
    }
  });

  const isListening = externalIsListening || isSpeechListening;

  const handleMicClick = () => {
    toggleSpeech();
    onToggleMic?.();
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const spoken = wasSpoken || isSpeechListening;
    if (isSpeechListening) {
      stopSpeech();
    }
    if (!inputText.trim()) return;
    onSendQuestion(inputText.trim(), spoken);
    setInputText('');
    setWasSpoken(false);
  };

  const guidedExamples = [
    {
      badge: '3 questions in one',
      badgeColor: 'text-[#8FB3FF] bg-[#8FB3FF]/15 border-[#8FB3FF]/30',
      quote:
        '“Plan a customer workshop in Pune for 30 attendees, with venue cancellation terms and catering options.”',
      meta: '1 turn · early search · split into 3 parts',
      scenarioIndex: 0,
    },
    {
      badge: 'Detail added later',
      badgeColor: 'text-[#62D6B4] bg-[#62D6B4]/15 border-[#62D6B4]/30',
      quote:
        '“Travel reimbursement guidelines for an employee journey. Then: the flight was international and booked post-travel.”',
      meta: '2 turns · refines v1 into v2',
      scenarioIndex: 1,
    },
    {
      badge: 'No search needed',
      badgeColor: 'text-[#B98CFF] bg-[#B98CFF]/15 border-[#B98CFF]/30',
      quote:
        '“Cancellation refund timeline for workshop venues. Then: summarize previous response in two bullet points.”',
      meta: '2 turns · reuses citations, 0 searches',
      scenarioIndex: 2,
    },
  ];

  return (
    <div className="w-full max-w-4xl mx-auto py-8 sm:py-12 px-4 sm:px-6 space-y-10 sm:space-y-12">
      {/* Hero Headline & Subtitle (Board 6) */}
      <div className="text-center space-y-4 max-w-3xl mx-auto">
        <h1 className="font-serif text-3xl sm:text-4xl lg:text-[42px] font-normal leading-tight text-[#ECE9E2] tracking-tight">
          Ask several things at once. Kairos starts answering before you finish.
        </h1>
        <p className="text-sm sm:text-base text-[#A3A9B5] leading-relaxed max-w-2xl mx-auto font-sans">
          Every sentence is checked against your documents and linked to the exact line it came
          from. When the documents don't say, Kairos tells you instead of guessing.
        </p>
      </div>

      {/* Large Question Input Card */}
      <form
        onSubmit={handleSubmit}
        className="bg-[#15181E] border border-[#1E2330] rounded-2xl p-4 sm:p-5 shadow-2xl focus-within:border-[#8FB3FF]/40 transition-all space-y-4"
      >
        <textarea
          rows={3}
          value={inputText}
          onChange={(e) => setInputText(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
              e.preventDefault();
              handleSubmit(e);
            }
          }}
          placeholder="Speak or type. Ask about venues, policies, travel, expenses…"
          className="w-full bg-transparent text-base sm:text-lg text-[#ECE9E2] placeholder-[#7D8594] focus:outline-none resize-none font-serif leading-relaxed"
        />

        {/* Bottom card toolbar */}
        <div className="flex flex-wrap items-center justify-between gap-3 pt-2 border-t border-[#1E2330]">
          {/* Left collection chip */}
          <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-[#1C2028] border border-[#282D3A] text-xs text-[#A3A9B5] select-none">
            <span className="w-1.5 h-1.5 rounded-full bg-[#8FB3FF]" />
            <span>Searching Company policies · 8 documents</span>
            <ChevronDown className="w-3 h-3 text-[#7D8594]" />
          </div>

          {/* Right action group with 56px Ivory Mic button */}
          <div className="flex items-center gap-3">
            <span className="hidden sm:inline text-xs text-[#7D8594] font-mono">
              Press Space to talk
            </span>

            {/* Send button (if text typed) */}
            {inputText.trim() && (
              <button
                type="submit"
                className="w-10 h-10 rounded-xl bg-[#1C2028] border border-[#282D3A] flex items-center justify-center text-[#ECE9E2] hover:bg-[#252B36] transition-all cursor-pointer"
                aria-label="Submit question"
              >
                <ArrowRight className="w-4 h-4" />
              </button>
            )}

            {/* 56px Ivory Circular Mic Orb */}
            <button
              type="button"
              onClick={handleMicClick}
              className={`w-14 h-14 rounded-full flex items-center justify-center transition-all ${
                isListening
                  ? 'bg-[#ECE9E2] text-[#0E1014] ring-4 ring-[#8FB3FF]/40 ring-offset-2 ring-offset-[#0E1014] animate-pulse shadow-lg'
                  : 'bg-[#ECE9E2] text-[#0E1014] hover:bg-white hover:scale-105 shadow-md active:scale-95'
              }`}
              title={isListening ? 'Stop listening' : 'Start speaking'}
              aria-label={isListening ? 'Stop listening' : 'Start speaking'}
            >
              <Mic className="w-6 h-6 fill-current" />
            </button>
          </div>
        </div>

        {/* Listening / Permission Denied Banners */}
        {isListening && (
          <div className="flex items-center justify-between px-3 py-2 bg-[#1C2028] border border-[#8FB3FF]/30 rounded-xl text-xs">
            <div className="flex items-center gap-2 text-[#ECE9E2]">
              <span className="relative flex h-2 w-2">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-[#8FB3FF] opacity-75"></span>
                <span className="relative inline-flex rounded-full h-2 w-2 bg-[#8FB3FF]"></span>
              </span>
              <span>Listening… speak your question or detail.</span>
            </div>
            <button
              type="button"
              onClick={stopSpeech}
              className="px-2.5 py-1 rounded-lg border border-[#282D3A] bg-[#15181E] text-[#ECE9E2] hover:bg-[#252B36] flex items-center gap-1 font-medium"
            >
              <Square className="w-3 h-3 fill-current text-[#E5484D]" />
              <span>Stop</span>
            </button>
          </div>
        )}

        {micDenied && (
          <div className="flex items-center gap-2 px-3 py-2 bg-[#F0B455]/10 border border-[#F0B455]/30 rounded-xl text-xs text-[#F0B455]">
            <AlertCircle className="w-4 h-4 shrink-0" />
            <span>Microphone permission denied. You can type your question in the text box.</span>
          </div>
        )}
      </form>

      {/* Guided Examples Section */}
      <div className="space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-1 px-1">
          <h2 className="text-sm font-semibold text-[#ECE9E2]">Try a guided example</h2>
          <span className="text-xs text-[#7D8594] font-serif">
            Replays a real recorded question, word by word
          </span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {guidedExamples.map((item, idx) => (
            <div
              key={idx}
              onClick={() => onPlayScenario(item.scenarioIndex)}
              className="bg-[#15181E] border border-[#1E2330] hover:border-[#282D3A] hover:bg-[#1C2028] p-4 sm:p-5 rounded-2xl flex flex-col justify-between space-y-4 cursor-pointer transition-all group"
            >
              <div className="space-y-3">
                <span
                  className={`inline-block px-2.5 py-0.5 rounded-full text-[11px] font-mono font-medium border ${item.badgeColor}`}
                >
                  {item.badge}
                </span>
                <p className="text-xs sm:text-sm text-[#ECE9E2] font-serif leading-relaxed line-clamp-4">
                  {item.quote}
                </p>
              </div>

              <div className="flex items-center justify-between text-xs text-[#7D8594] pt-2 border-t border-[#1E2330] group-hover:text-[#A3A9B5] transition-colors">
                <div className="flex items-center gap-1.5">
                  <Play className="w-3 h-3 text-[#8FB3FF] fill-current" />
                  <span>{item.meta}</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Trust Row */}
      <div className="pt-4 border-t border-[#1E2330]/60 flex flex-wrap items-center justify-center gap-6 sm:gap-10 text-xs text-[#7D8594]">
        <div className="flex items-center gap-2">
          <CheckCircle2 className="w-4 h-4 text-[#6FD39A]" />
          <span>Every sentence cites its exact source line</span>
        </div>
        <div className="flex items-center gap-2">
          <Search className="w-4 h-4 text-[#8FB3FF]" />
          <span>Says when the documents don't cover it</span>
        </div>
        <div className="flex items-center gap-2">
          <Lock className="w-4 h-4 text-[#A3A9B5]" />
          <span>Runs offline, no API keys</span>
        </div>
      </div>
    </div>
  );
};
