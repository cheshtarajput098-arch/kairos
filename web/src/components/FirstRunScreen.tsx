import React from 'react';
import { Sparkles, ArrowRight, BookOpen, ShieldCheck } from 'lucide-react';

interface FirstRunScreenProps {
  suggestions: string[];
  onSelectSuggestion: (question: string) => void;
}

export const FirstRunScreen: React.FC<FirstRunScreenProps> = ({
  suggestions,
  onSelectSuggestion,
}) => {
  return (
    <div className="bg-[#15181E] border border-[#1E2330] rounded-2xl p-8 space-y-6">
      <div className="max-w-xl space-y-2">
        <div className="flex items-center gap-2 text-xs font-mono text-[#8FB3FF]">
          <Sparkles className="w-4 h-4 text-[#8FB3FF]" />
          <span>Grounded Live Assistant</span>
        </div>
        <h2 className="text-xl sm:text-2xl font-bold text-[#ECE9E2] tracking-tight">
          Answers form while you speak.
        </h2>
        <p className="text-xs sm:text-sm text-[#7D8594] leading-relaxed font-serif">
          Speak naturally or type your inquiry. Kairos decomposes compound questions, retrieves verified passages in parallel, and checks every claim before you stop talking.
        </p>
      </div>

      {/* Suggested Questions (Generated from corpus headings at index time) */}
      <div className="space-y-3 pt-2">
        <div className="flex items-center gap-2 text-xs font-semibold text-[#A3A9B5] uppercase tracking-wider">
          <BookOpen className="w-3.5 h-3.5 text-[#7D8594]" />
          <span>Suggested Questions from Corpus Headings</span>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
          {suggestions.map((q, idx) => (
            <button
              key={idx}
              onClick={() => onSelectSuggestion(q)}
              className="text-left p-3.5 rounded-xl border border-[#1E2330] bg-[#12151B] hover:border-[#8FB3FF]/40 hover:bg-[#1C2028] transition-all flex items-start justify-between gap-3 group"
            >
              <span className="text-xs text-[#ECE9E2] font-serif leading-snug group-hover:text-[#8FB3FF] transition-colors">
                "{q}"
              </span>
              <ArrowRight className="w-3.5 h-3.5 text-[#7D8594] group-hover:text-[#8FB3FF] group-hover:translate-x-0.5 transition-all shrink-0 mt-0.5" />
            </button>
          ))}
        </div>
      </div>

      {/* Trust Badges */}
      <div className="flex flex-wrap items-center gap-4 pt-4 border-t border-[#1E2330] text-xs text-[#7D8594] font-mono">
        <span className="flex items-center gap-1.5">
          <ShieldCheck className="w-4 h-4 text-[#6FD39A]" />
          100% Corpus Grounded
        </span>
        <span>·</span>
        <span>Zero Outside Knowledge</span>
        <span>·</span>
        <span>Per-Claim Citations</span>
      </div>
    </div>
  );
};
