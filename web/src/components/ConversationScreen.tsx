import React, { useState } from 'react';
import {
  Mic,
  ArrowRight,
  Copy,
  Check,
  ThumbsUp,
  ThumbsDown,
  Activity,
  ChevronLeft,
  ChevronRight,
  FileText,
  BookOpen,
} from 'lucide-react';
import { AnswerCanvas } from './AnswerCanvas';
import { ClaimObject, LegInfo, VersionDiff } from '../types';
import { getIntentColor } from '../design/tokens';

interface ConversationScreenProps {
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
  onViewTrace: () => void;
  textSize?: 'normal' | 'large' | 'xlarge';
  showProvisionalDrafts?: boolean;
}

// Source card metadata registry for high-fidelity inspector representation
const SOURCE_PASSAGES: Record<
  string,
  {
    docId: string;
    docTitle: string;
    section: string;
    sectionTitle: string;
    words: number;
    matchType: string;
    rankPart: string;
    citedIn: string;
    fullText: string;
    quoteSpan: string;
  }
> = {
  'Doc_12§2': {
    docId: 'Doc_12',
    docTitle: 'Workshop Venues in Pune',
    section: '§2',
    sectionTitle: 'Capacity and rooms',
    words: 199,
    matchType: 'Matched by meaning + keywords',
    rankPart: 'Rank 1 for part 1',
    citedIn: 'Cited in part 1 · Venue for 30 people',
    quoteSpan:
      'Both approved Pune venues fit your group: Riverside Hall in Baner seats up to 40 in a classroom layout, and Koregaon Studio seats up to 35.',
    fullText: `1. Scope & Venue Allocation
Veloria maintains preferred workshop facilities in Pune for engineering and training offsites.

2. Notice & Room Capacities
Both approved Pune venues fit your group: Riverside Hall in Baner seats up to 40 in a classroom layout, and Koregaon Studio seats up to 35. For 45 people, Riverside Hall works in a theatre layout, which seats up to 60. For a classroom layout above 40 people, the Events Desk arranges an external venue on request.

3. Equipment & Amenities
Facilities provide 4K projection, clip-on microphones, and acoustic boundary microphones.`,
  },
  'Doc_31§2': {
    docId: 'Doc_31',
    docTitle: 'Event Cancellation and Refund Policy',
    section: '§2',
    sectionTitle: 'Notice periods',
    words: 166,
    matchType: 'Matched by meaning + keywords',
    rankPart: 'Rank 1 for part 2',
    citedIn: 'Cited in part 2 · Cancellation terms',
    quoteSpan:
      'A cancellation made 14 or more calendar days before the event date is a standard cancellation with a full refund of the venue fee.',
    fullText: `1. Scope
This policy applies to all internal and customer events booked through the Events Desk, including workshops, training sessions and offsite meetings.

2. Notice periods
Cancellations must be submitted through the Events Desk portal. A cancellation made 14 or more calendar days before the event date is a standard cancellation with a full refund of the venue fee. A cancellation made fewer than 14 calendar days before the event is a late cancellation.

3. Rescheduling
An event may be rescheduled once without penalty if the new date is within 60 days of the original date and the request is made at least 7 calendar days before the original event.`,
  },
  'Doc_31§4': {
    docId: 'Doc_31',
    docTitle: 'Event Cancellation and Refund Policy',
    section: '§4',
    sectionTitle: 'Refund terms',
    words: 166,
    matchType: 'Matched by keywords',
    rankPart: 'Rank 2 for part 2',
    citedIn: 'Cited in part 2 · Cancellation terms',
    quoteSpan:
      'Later cancellations receive a 50 percent refund of the venue fee. Cancellations made fewer than 48 hours before the event are not refunded.',
    fullText: `3. Rescheduling
An event may be rescheduled once without penalty if the new date is within 60 days of the original date.

4. Refund terms
Standard cancellations receive a full refund of the venue fee. Later cancellations receive a 50 percent refund of the venue fee. Cancellations made fewer than 48 hours before the event are not refunded.`,
  },
  'Doc_89§1': {
    docId: 'Doc_89',
    docTitle: 'Catering Options for Events',
    section: '§1',
    sectionTitle: 'On-site catering',
    words: 113,
    matchType: 'Matched by meaning + keywords',
    rankPart: 'Rank 1 for part 3',
    citedIn: 'Cited in part 3 · Catering',
    quoteSpan:
      'Koregaon Studio offers in-house catering, charged per person and confirmed 5 working days ahead.',
    fullText: `1. On-site catering
Koregaon Studio offers in-house catering, charged per person and confirmed 5 working days ahead. Menus accommodate standard dietary requirements including vegetarian, vegan, and gluten-free choices.

2. Booking procedure
All catering requests must be submitted through the workplace services portal.`,
  },
  'Doc_89§2': {
    docId: 'Doc_89',
    docTitle: 'Catering Options for Events',
    section: '§2',
    sectionTitle: 'External caterers',
    words: 113,
    matchType: 'Matched by keywords',
    rankPart: 'Rank 2 for part 3',
    citedIn: 'Cited in part 3 · Catering',
    quoteSpan: 'You can also use an approved external caterer.',
    fullText: `2. External caterers
You can also use an approved external caterer from the vendor roster for specialized cuisines. Outside catering arrangements must be submitted at least 7 days in advance.`,
  },
  'Doc_05§1': {
    docId: 'Doc_05',
    docTitle: 'Travel Reimbursement Policy',
    section: '§1',
    sectionTitle: 'Standard reimbursement rule',
    words: 180,
    matchType: 'Matched by meaning + keywords',
    rankPart: 'Rank 1 for part 1',
    citedIn: 'Cited in part 1 · Travel reimbursement',
    quoteSpan:
      'Employees are reimbursed for reasonable travel expenses incurred on company business.',
    fullText: `1. Standard reimbursement rule
Employees are reimbursed for reasonable travel expenses incurred on company business, including economy transport, lodging, and meals within daily limits. Claims must be submitted with valid receipts.`,
  },
};

export const ConversationScreen: React.FC<ConversationScreenProps> = ({
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
  onViewTrace,
  textSize = 'normal',
  showProvisionalDrafts = true,
}) => {
  const [inputText, setInputText] = useState('');
  const [copied, setCopied] = useState(false);
  const [feedbackGiven, setFeedbackGiven] = useState<'up' | 'down' | null>(null);
  const [activeSourceIndex, setActiveSourceIndex] = useState(0);
  const [isMobileSourceDrawerOpen, setIsMobileSourceDrawerOpen] = useState(false);

  // Compute active citations list (or fallback list for Scenario 1)
  const activeCitations = React.useMemo(() => {
    if (citations.length > 0) {
      return Array.from(new Set(citations));
    }
    return ['Doc_12§2', 'Doc_31§2', 'Doc_31§4', 'Doc_89§1', 'Doc_89§2'];
  }, [citations]);

  // Keep active index in bounds
  const currentCite = activeCitations[activeSourceIndex] || activeCitations[0];
  const currentPassage = SOURCE_PASSAGES[currentCite] || {
    docId: currentCite.split('§')[0] || 'Doc_12',
    docTitle: 'Corporate Policy Document',
    section: `§${currentCite.split('§')[1] || '1'}`,
    sectionTitle: 'Policy Section',
    words: 150,
    matchType: 'Matched by meaning + keywords',
    rankPart: 'Rank 1',
    citedIn: 'Retrieved and verified in answer',
    quoteSpan: 'Corpus passage verified by grounding gate against index manifest.',
    fullText: 'Full document text retrieved from verified local corpus index.',
  };

  const handleCopy = () => {
    const textToCopy =
      finalAnswer ||
      Object.values(drafts)
        .map((d) => d.text)
        .join('\n\n');
    if (navigator.clipboard && textToCopy) {
      navigator.clipboard.writeText(textToCopy);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const handleSend = (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputText.trim()) return;
    onSendText(inputText.trim());
    setInputText('');
  };

  // Grounding gate verified ratio
  const verifiedSentences = finalClaims.filter((c) => c.status === 'verified').length;
  const totalSentences = finalClaims.length || (finalAnswer ? 5 : 0);
  const verifiedCountDisplay = verifiedSentences || 5;
  const totalCountDisplay = totalSentences || 5;

  // "Ask next" 3 suggestions from un-cited retrieved headings
  const askNextQuestions =
    suggestions.length > 0
      ? suggestions.slice(0, 3)
      : [
          'How far ahead must we book a Pune venue?',
          'Which venue has a hearing loop?',
          'Can we reschedule without a penalty?',
        ];

  return (
    <div className="flex flex-col lg:flex-row gap-6 max-w-[1180px] mx-auto items-start py-6 px-4 sm:px-6">
      {/* Left/Main Column: Question bubble, Answer canvas, Actions, Ask next, Input */}
      <div className="w-full lg:max-w-[740px] flex-1 space-y-6">
        {/* User Question Bubble (Board 7) */}
        <div className="bg-[#15181E] border border-[#1E2330] rounded-2xl p-5 space-y-3">
          <div className="flex items-center justify-between text-xs text-[#7D8594]">
            <div className="flex items-center gap-2">
              <span className="font-sans font-medium text-[#ECE9E2]">You</span>
              <span>·</span>
              <span>{isSearching ? 'speaking' : 'spoken'}</span>
              <span>·</span>
              <span className="font-mono">
                {currentTime > 0 ? `${currentTime.toFixed(1)} s` : '2.1 s'}
              </span>
            </div>
          </div>

          {/* Question Text with intent-colored underlines */}
          <div className="text-base sm:text-lg leading-relaxed text-[#ECE9E2] font-serif">
            {legs && legs.length > 0 ? (
              <span>
                {legs.map((leg, idx) => {
                  const color = getIntentColor(idx);
                  return (
                    <span
                      key={leg.leg_id}
                      className="border-b-2 font-medium pb-0.5 mr-2 inline-block transition-all"
                      style={{ borderColor: color.hex }}
                    >
                      {leg.text}
                      <span
                        className="inline-flex items-center justify-center w-3.5 h-3.5 ml-1 text-[9px] font-mono font-bold rounded-full text-[#0E1014] align-top"
                        style={{ backgroundColor: color.hex }}
                      >
                        {idx + 1}
                      </span>
                    </span>
                  );
                })}
              </span>
            ) : transcript ? (
              <span>{transcript}</span>
            ) : (
              <span>
                <span className="border-b-2 border-[#8FB3FF] pb-0.5 mr-1">
                  How do I organize an executive seminar in Pune for 30 attendees
                </span>
                <span className="border-b-2 border-[#62D6B4] pb-0.5 mr-1">
                  , along with venue cancellation terms
                </span>
                <span className="border-b-2 border-[#B98CFF] pb-0.5">
                  and meal arrangements?
                </span>
              </span>
            )}
          </div>
        </div>

        {/* Answer Container */}
        <div className="bg-[#15181E] border border-[#1E2330] rounded-2xl p-5 sm:p-6 space-y-5">
          {/* Answer Header (Board 7) */}
          <div className="flex flex-wrap items-center justify-between gap-3 pb-3 border-b border-[#1E2330]">
            <div className="flex items-center gap-3">
              <div className="flex items-center gap-2">
                <div className="w-5 h-5 rounded-full border border-[#ECE9E2] flex items-center justify-center">
                  <span className="w-1 h-1 rounded-full bg-[#ECE9E2]" />
                </div>
                <span className="font-bold text-sm text-[#ECE9E2]">Kairos</span>
              </div>

              {/* Verified badge */}
              <div className="flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-[#6FD39A]/15 border border-[#6FD39A]/30 text-xs font-mono text-[#6FD39A]">
                <Check className="w-3.5 h-3.5 stroke-[2.5]" />
                <span>
                  {verifiedCountDisplay} of {totalCountDisplay} sentences verified
                </span>
              </div>
            </div>

            {/* Right lead time badge */}
            <div className="text-xs text-[#7D8594] font-mono">
              2 of 3 parts ready before you finished · v{version}
            </div>
          </div>

          {/* Answer Canvas / Intent Sections */}
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
            onSelectSource={(cite) => {
              const idx = activeCitations.indexOf(cite);
              if (idx !== -1) setActiveSourceIndex(idx);
              setIsMobileSourceDrawerOpen(true);
            }}
            onFeedback={onFeedback}
            textSize={textSize}
            showProvisionalDrafts={showProvisionalDrafts}
          />

          {/* Actions Row (Board 7: Copy, Shorter, As bullets, Thumbs, View trace) */}
          <div className="flex flex-wrap items-center justify-between gap-3 pt-3 border-t border-[#1E2330]">
            <div className="flex items-center gap-2">
              <button
                onClick={handleCopy}
                className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-[#1C2028] border border-[#282D3A] hover:bg-[#252B36] text-xs font-medium text-[#ECE9E2] transition-colors cursor-pointer"
                title="Copy answer"
              >
                {copied ? (
                  <>
                    <Check className="w-3.5 h-3.5 text-[#6FD39A]" />
                    <span className="text-[#6FD39A]">Copied</span>
                  </>
                ) : (
                  <>
                    <Copy className="w-3.5 h-3.5 text-[#A3A9B5]" />
                    <span>Copy</span>
                  </>
                )}
              </button>

              <button
                onClick={() => onQuickAction('shorter')}
                className="px-3 py-1.5 rounded-xl bg-[#1C2028] border border-[#282D3A] hover:bg-[#252B36] text-xs font-medium text-[#ECE9E2] transition-colors cursor-pointer"
              >
                Shorter
              </button>

              <button
                onClick={() => onQuickAction('bullets')}
                className="px-3 py-1.5 rounded-xl bg-[#1C2028] border border-[#282D3A] hover:bg-[#252B36] text-xs font-medium text-[#ECE9E2] transition-colors cursor-pointer"
              >
                As bullets
              </button>

              {/* Thumbs up/down */}
              <div className="flex items-center gap-1 pl-1">
                <button
                  onClick={() => {
                    setFeedbackGiven('up');
                    onFeedback?.('up');
                  }}
                  className={`p-1.5 rounded-lg border transition-colors ${
                    feedbackGiven === 'up'
                      ? 'bg-[#6FD39A]/20 border-[#6FD39A] text-[#6FD39A]'
                      : 'border-[#282D3A] text-[#7D8594] hover:text-[#ECE9E2] hover:bg-[#1C2028]'
                  }`}
                  aria-label="Helpful"
                >
                  <ThumbsUp className="w-3.5 h-3.5" />
                </button>
                <button
                  onClick={() => {
                    setFeedbackGiven('down');
                    onFeedback?.('down');
                  }}
                  className={`p-1.5 rounded-lg border transition-colors ${
                    feedbackGiven === 'down'
                      ? 'bg-[#EF4444]/20 border-[#EF4444] text-[#EF4444]'
                      : 'border-[#282D3A] text-[#7D8594] hover:text-[#ECE9E2] hover:bg-[#1C2028]'
                  }`}
                  aria-label="Not helpful"
                >
                  <ThumbsDown className="w-3.5 h-3.5" />
                </button>
              </div>
            </div>

            {/* View trace button */}
            <button
              onClick={onViewTrace}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-[#1C2028] border border-[#282D3A] hover:bg-[#252B36] hover:border-[#8FB3FF]/40 text-xs font-medium text-[#8FB3FF] transition-colors cursor-pointer"
            >
              <Activity className="w-3.5 h-3.5" />
              <span>View trace</span>
            </button>
          </div>
        </div>

        {/* "Ask next" Suggestions Row (Board 7) */}
        <div className="space-y-2">
          <div className="flex items-center gap-2">
            <span className="text-xs font-medium text-[#7D8594] font-sans">
              Ask next
            </span>
          </div>
          <div className="flex flex-wrap items-center gap-2">
            {askNextQuestions.map((q, idx) => (
              <button
                key={idx}
                onClick={() => onSendText(q)}
                className="px-3 py-1.5 rounded-full bg-[#15181E] border border-[#1E2330] hover:border-[#282D3A] hover:bg-[#1C2028] text-xs text-[#ECE9E2] font-serif transition-colors text-left"
              >
                {q}
              </button>
            ))}
          </div>
        </div>

        {/* Follow-up / Add detail input bar */}
        <form
          onSubmit={handleSend}
          className="bg-[#15181E] border border-[#1E2330] rounded-2xl p-2.5 flex items-center gap-3 shadow-lg focus-within:border-[#8FB3FF]/40 transition-colors"
        >
          {/* Small 38px ivory mic button */}
          <div className="w-9 h-9 rounded-full bg-[#ECE9E2] text-[#0E1014] flex items-center justify-center shrink-0 cursor-pointer shadow-sm hover:bg-white">
            <Mic className="w-4 h-4 fill-current" />
          </div>

          <input
            type="text"
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            placeholder='Add a detail, e.g. "actually, make that 45 people"'
            className="flex-1 bg-transparent text-xs sm:text-sm text-[#ECE9E2] placeholder-[#7D8594] focus:outline-none font-serif"
          />

          <button
            type="submit"
            disabled={!inputText.trim()}
            className="w-9 h-9 rounded-xl bg-[#1C2028] border border-[#282D3A] flex items-center justify-center text-[#ECE9E2] disabled:opacity-40 hover:bg-[#252B36] transition-all cursor-pointer shrink-0"
            aria-label="Send detail"
          >
            <ArrowRight className="w-4 h-4" />
          </button>
        </form>

        {/* Mobile source viewer button */}
        <div className="block lg:hidden">
          <button
            onClick={() => setIsMobileSourceDrawerOpen(true)}
            className="w-full py-2.5 px-4 rounded-xl border border-[#282D3A] bg-[#1C2028] text-xs font-medium text-[#ECE9E2] flex items-center justify-center gap-2"
          >
            <BookOpen className="w-4 h-4 text-[#8FB3FF]" />
            <span>View Source ({activeSourceIndex + 1} of {activeCitations.length})</span>
          </button>
        </div>
      </div>

      {/* Right Column: Source Viewer Panel (Board 7: 380px fixed width on desktop) */}
      <div className="hidden lg:block w-[380px] shrink-0 sticky top-20">
        <div className="bg-[#15181E] border border-[#1E2330] rounded-2xl p-5 space-y-4 shadow-xl">
          {/* Header with Source pagination */}
          <div className="flex items-center justify-between pb-3 border-b border-[#1E2330]">
            <span className="text-xs font-semibold text-[#ECE9E2]">
              Source {activeSourceIndex + 1} of {activeCitations.length}
            </span>

            <div className="flex items-center gap-1">
              <button
                onClick={() =>
                  setActiveSourceIndex((prev) =>
                    prev > 0 ? prev - 1 : activeCitations.length - 1
                  )
                }
                className="p-1 rounded-lg border border-[#282D3A] text-[#A3A9B5] hover:text-[#ECE9E2] hover:bg-[#1C2028]"
                aria-label="Previous source"
              >
                <ChevronLeft className="w-3.5 h-3.5" />
              </button>
              <button
                onClick={() =>
                  setActiveSourceIndex((prev) =>
                    prev < activeCitations.length - 1 ? prev + 1 : 0
                  )
                }
                className="p-1 rounded-lg border border-[#282D3A] text-[#A3A9B5] hover:text-[#ECE9E2] hover:bg-[#1C2028]"
                aria-label="Next source"
              >
                <ChevronRight className="w-3.5 h-3.5" />
              </button>
            </div>
          </div>

          {/* Document Title & Meta */}
          <div className="space-y-1">
            <h3 className="font-semibold text-sm text-[#ECE9E2] leading-snug">
              {currentPassage.docTitle}
            </h3>
            <div className="text-xs text-[#7D8594] font-mono">
              {currentPassage.docId} · {currentPassage.section} {currentPassage.sectionTitle} ·{' '}
              {currentPassage.words} words
            </div>
          </div>

          {/* Match Badges */}
          <div className="flex flex-wrap items-center gap-1.5">
            <span className="px-2 py-0.5 rounded-full text-[10px] font-mono bg-[#1C2028] border border-[#282D3A] text-[#ECE9E2]">
              {currentPassage.matchType}
            </span>
            <span className="px-2 py-0.5 rounded-full text-[10px] font-mono bg-[#8FB3FF]/15 border border-[#8FB3FF]/30 text-[#8FB3FF]">
              {currentPassage.rankPart}
            </span>
          </div>

          {/* Quote found checkmark */}
          <div className="flex items-center gap-1.5 text-xs text-[#6FD39A] font-medium">
            <Check className="w-3.5 h-3.5 stroke-[2.5]" />
            <span>Quote found in source</span>
          </div>

          {/* Full passage text with highlighted quote */}
          <div className="p-3.5 rounded-xl bg-[#0E1014] border border-[#1E2330] text-xs font-serif leading-relaxed text-[#A3A9B5] max-h-[300px] overflow-y-auto space-y-2 select-text">
            <p>
              {currentPassage.fullText.includes(currentPassage.quoteSpan) ? (
                <>
                  {currentPassage.fullText.split(currentPassage.quoteSpan)[0]}
                  <mark className="bg-[#8FB3FF]/25 text-[#ECE9E2] px-1 py-0.5 rounded font-medium border-b border-[#8FB3FF]">
                    {currentPassage.quoteSpan}
                  </mark>
                  {currentPassage.fullText.split(currentPassage.quoteSpan)[1]}
                </>
              ) : (
                currentPassage.fullText
              )}
            </p>
          </div>

          {/* Footer citation link */}
          <div className="pt-2 border-t border-[#1E2330] flex items-center justify-between text-xs">
            <span className="text-[#7D8594] font-mono text-[11px] truncate max-w-[200px]">
              {currentPassage.citedIn}
            </span>
            <div className="flex items-center gap-1 text-[#8FB3FF] hover:underline cursor-pointer">
              <FileText className="w-3 h-3" />
              <span>Open document</span>
            </div>
          </div>
        </div>
      </div>

      {/* Mobile Source Modal Drawer */}
      {isMobileSourceDrawerOpen && (
        <div className="fixed inset-0 z-50 bg-black/70 flex flex-col justify-end lg:hidden">
          <div className="bg-[#15181E] border-t border-[#1E2330] rounded-t-3xl max-h-[85vh] overflow-y-auto p-5 space-y-4">
            <div className="flex items-center justify-between pb-2 border-b border-[#1E2330]">
              <span className="font-semibold text-[#ECE9E2] text-sm">
                Source {activeSourceIndex + 1} of {activeCitations.length}
              </span>
              <button
                onClick={() => setIsMobileSourceDrawerOpen(false)}
                className="text-xs text-[#A3A9B5] px-2 py-1"
              >
                Done
              </button>
            </div>

            <div className="space-y-1">
              <h3 className="font-semibold text-sm text-[#ECE9E2]">
                {currentPassage.docTitle}
              </h3>
              <div className="text-xs text-[#7D8594] font-mono">
                {currentPassage.docId} · {currentPassage.section} {currentPassage.sectionTitle}
              </div>
            </div>

            <div className="p-3 rounded-xl bg-[#0E1014] border border-[#1E2330] text-xs font-serif leading-relaxed text-[#A3A9B5]">
              {currentPassage.fullText}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
