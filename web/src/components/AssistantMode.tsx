import React, { useState } from 'react';
import { Mic, Send, Search, Sparkles } from 'lucide-react';
import { AnswerCanvas } from './AnswerCanvas';
import { ClaimObject, LegInfo, VersionDiff } from '../types';
import strings from '../strings.en.json';

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
  isDrafting: boolean;
  onSendText: (text: string) => void;
  onQuickAction: (action: 'shorter' | 'bullets' | 'simple') => void;
  onSeeDiff: () => void;
}

const SUGGESTIONS = [
  "What venues are available in Pune for workshops?",
  "What is the standard cancellation timeline?",
  "How do travel expenses get reimbursed for staff?",
];

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
  isDrafting,
  onSendText,
  onQuickAction,
  onSeeDiff,
}) => {
  const [inputText, setInputText] = useState('');

  const handleSend = (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputText.trim()) return;
    onSendText(inputText.trim());
    setInputText('');
  };

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      {/* Live Transcript / Speech Area */}
      <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-5 shadow-sm space-y-3">
        <div className="flex items-center justify-between text-xs font-mono text-slate-400">
          <span className="uppercase">Live Transcript</span>
          {isSearching && (
            <span className="inline-flex items-center gap-1 text-blue-600 dark:text-blue-400 font-semibold animate-pulse">
              <Search className="w-3 h-3" />
              <span>{strings.assistant.searching}</span>
            </span>
          )}
        </div>

        <div className="min-h-[50px] text-base leading-relaxed text-slate-800 dark:text-slate-100 font-medium">
          {transcript ? (
            <span>{transcript}</span>
          ) : (
            <span className="text-slate-400 dark:text-slate-500 font-normal italic">
              "Ask a question or describe your requirements..."
            </span>
          )}
        </div>
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
        isDrafting={isDrafting}
        onQuickAction={onQuickAction}
        onSeeDiff={onSeeDiff}
      />

      {/* Suggested Questions when no conversation has started */}
      {!transcript && !finalAnswer && (
        <div className="space-y-2 pt-2">
          <div className="text-xs font-mono uppercase text-slate-400 px-1">
            {strings.assistant.suggestedTitle}
          </div>
          <div className="grid gap-2">
            {SUGGESTIONS.map((q, i) => (
              <button
                key={i}
                onClick={() => onSendText(q)}
                className="text-left text-xs p-3 rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 hover:border-blue-400 text-slate-700 dark:text-slate-200 transition-colors flex items-center justify-between"
              >
                <span>{q}</span>
                <Sparkles className="w-3.5 h-3.5 text-blue-500 shrink-0" />
              </button>
            ))}
          </div>
        </div>
      )}

      {/* User Input Bar */}
      <form onSubmit={handleSend} className="relative flex items-center gap-2 pt-2">
        <input
          type="text"
          value={inputText}
          onChange={(e) => setInputText(e.target.value)}
          placeholder="Ask a question or add a detail..."
          className="w-full pl-4 pr-24 py-3 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 text-slate-900 dark:text-white shadow-sm"
        />
        <div className="absolute right-2 flex items-center gap-1">
          <button
            type="button"
            className="p-2 text-slate-400 hover:text-blue-600 rounded-xl hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
            title="Voice input"
          >
            <Mic className="w-4 h-4" />
          </button>
          <button
            type="submit"
            disabled={!inputText.trim()}
            className="p-2 bg-blue-600 hover:bg-blue-700 disabled:opacity-40 text-white rounded-xl shadow-sm transition-all"
            title="Send query"
          >
            <Send className="w-4 h-4" />
          </button>
        </div>
      </form>
    </div>
  );
};
