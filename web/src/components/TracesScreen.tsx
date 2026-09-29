import React from 'react';
import {
  ArrowLeft,
  Download,
  CheckCircle2,
} from 'lucide-react';
import { StreamEvent } from '../types';

interface TracesScreenProps {
  questionTitle?: string;
  turnId?: string;
  onBackToConversation: () => void;
  events?: StreamEvent[];
  onExportJson?: () => void;
}

export const TracesScreen: React.FC<TracesScreenProps> = ({
  questionTitle = 'Pune workshop for 30 people',
  turnId = 'turn s1-t1',
  onBackToConversation,
  events = [],
  onExportJson,
}) => {
  const handleExport = () => {
    if (onExportJson) {
      onExportJson();
      return;
    }
    const dataStr =
      'data:text/json;charset=utf-8,' +
      encodeURIComponent(
        JSON.stringify(
          {
            session_id: 'sess_live_trace',
            turn: turnId,
            question: questionTitle,
            events: events.length > 0 ? events : defaultEvents,
          },
          null,
          2
        )
      );
    const downloadAnchor = document.createElement('a');
    downloadAnchor.setAttribute('href', dataStr);
    downloadAnchor.setAttribute('download', `kairos_trace_${Date.now()}.json`);
    document.body.appendChild(downloadAnchor);
    downloadAnchor.click();
    downloadAnchor.remove();
  };

  const defaultEvents = [
    { t: '0.00', source: 'Controller', msg: 'WAIT: no searchable place or group size yet' },
    { t: '0.80', source: 'Controller', msg: 'RETRIEVE: “workshop in Pune for 30 people” is stable' },
    { t: '0.80', source: 'Search', msg: 'Part 1: meaning + keyword search, fused (RRF k=60)' },
    { t: '1.60', source: 'Decomposer', msg: 'Split into 3 parts; shared context “Pune” kept in each' },
    { t: '1.60', source: 'Search', msg: 'Parts 2 and 3 searched in parallel' },
    { t: '2.10', source: 'Speech', msg: 'Speaker stopped; 2 of 3 parts already verified' },
    { t: '2.24', source: 'Grounding gate', msg: '5 of 5 sentences: cited passage retrieved, quote found' },
    { t: '2.24', source: 'Grounding gate', msg: 'Gap: catering for Riverside Hall not in documents' },
  ];

  const groundingChecks = [
    { label: 'Sentences shown', value: '5' },
    { label: 'Cited passage was retrieved', value: '5 / 5' },
    { label: 'Quoted words found in passage', value: '5 / 5' },
    { label: 'Fabricated citations', value: '0', success: true },
    { label: 'Hidden-instruction flags', value: '0', success: true },
    { label: 'Parts ready before speaker stopped', value: '2 / 3' },
  ];

  return (
    <div className="w-full max-w-5xl mx-auto py-8 px-4 sm:px-6 space-y-6">
      {/* Top Header Row (Board 9) */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-[#1E2330]">
        <div className="space-y-2">
          <button
            onClick={onBackToConversation}
            className="flex items-center gap-1.5 text-xs text-[#8FB3FF] hover:underline cursor-pointer"
          >
            <ArrowLeft className="w-3.5 h-3.5" />
            <span>Back to the conversation</span>
          </button>

          <div className="flex flex-wrap items-center gap-3">
            <h1 className="text-xl sm:text-2xl font-bold text-[#ECE9E2] tracking-tight">
              {questionTitle}
            </h1>
            <span className="text-xs font-mono text-[#7D8594]">{turnId}</span>
          </div>

          {/* Badges row */}
          <div className="flex flex-wrap items-center gap-2 pt-1">
            <span className="px-2.5 py-0.5 rounded-full text-xs font-mono bg-[#1C2028] border border-[#282D3A] text-[#ECE9E2]">
              3 parts
            </span>
            <span className="flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-mono bg-[#6FD39A]/15 border border-[#6FD39A]/30 text-[#6FD39A]">
              <span className="w-1.5 h-1.5 rounded-full bg-[#6FD39A]" />
              <span>5 citations, all verified</span>
            </span>
            <span className="flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-mono bg-[#1C2028] border border-[#282D3A] text-[#ECE9E2]">
              <span className="w-1.5 h-1.5 rounded-full bg-[#4ADE80]" />
              <span>0 fabricated</span>
            </span>
            <span className="px-2.5 py-0.5 rounded-full text-xs font-mono bg-[#8FB3FF]/15 border border-[#8FB3FF]/30 text-[#8FB3FF]">
              Ready at end: 2 of 3
            </span>
          </div>
        </div>

        {/* Action: Export JSON */}
        <div className="shrink-0">
          <button
            onClick={handleExport}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-[#1C2028] border border-[#282D3A] hover:bg-[#252B36] text-xs font-medium text-[#ECE9E2] transition-colors cursor-pointer"
          >
            <Download className="w-3.5 h-3.5 text-[#8FB3FF]" />
            <span>Export JSON</span>
          </button>
        </div>
      </div>

      {/* Timeline Gantt Chart Box (Board 9) */}
      <div className="bg-[#15181E] border border-[#1E2330] rounded-2xl p-5 space-y-4 shadow-xl">
        <div className="flex flex-wrap items-center justify-between gap-2 pb-2 border-b border-[#1E2330]">
          <div className="flex items-center gap-3">
            <h2 className="text-sm font-semibold text-[#ECE9E2]">Timeline</h2>
            <div className="flex items-center gap-1.5 text-xs text-[#62D6B4] font-mono">
              <span className="rotate-45 w-2 h-2 bg-[#62D6B4] inline-block" />
              <span>verified draft</span>
            </div>
          </div>
          <span className="text-xs text-[#A3A9B5] font-mono">
            seconds from first word
          </span>
        </div>

        {/* Gantt Chart Container */}
        <div className="space-y-3 pt-2">
          {/* Time axis header */}
          <div className="flex items-center text-[11px] font-mono text-[#A3A9B5] pl-36 pr-4 justify-between border-b border-[#1E2330]/50 pb-1">
            <span>0.0</span>
            <span>0.5</span>
            <span>1.0</span>
            <span>1.5</span>
            <span>2.0</span>
            <span>2.5</span>
            <span>3.0</span>
          </div>

          {/* Row 1: Speech */}
          <div className="flex items-center gap-3 text-xs">
            <div className="w-32 shrink-0">
              <div className="font-medium text-[#ECE9E2]">Speech</div>
              <div className="text-[10px] text-[#A3A9B5]">live transcript</div>
            </div>
            <div className="flex-1 relative h-7 bg-[#12151B] border border-[#1E2330] rounded-lg overflow-hidden flex items-center px-3">
              <div
                className="absolute left-0 top-0 bottom-0 bg-[#282D3A] rounded"
                style={{ width: '70%' }}
              />
              <span className="relative z-10 text-[11px] text-[#ECE9E2] truncate max-w-[80%] font-serif">
                Plan a customer workshop in Pune for 30 attendees, with cancellation policy…
              </span>
              <span className="absolute right-2 text-[10px] font-mono text-[#F0B455]">
                speaker stopped · 2.1 s
              </span>
            </div>
          </div>

          {/* Row 2: Controller */}
          <div className="flex items-center gap-3 text-xs">
            <div className="w-32 shrink-0">
              <div className="font-medium text-[#ECE9E2]">Controller</div>
              <div className="text-[10px] text-[#A3A9B5]">wait · retrieve</div>
            </div>
            <div className="flex-1 relative h-7 bg-[#12151B] border border-[#1E2330] rounded-lg flex items-center px-1 text-[11px] font-mono">
              <div
                className="h-5 px-2 rounded bg-[#1C2028] border border-[#282D3A] text-[#A3A9B5] flex items-center justify-center mr-1"
                style={{ width: '27%' }}
              >
                WAIT
              </div>
              <div
                className="h-5 px-2 rounded bg-[#8FB3FF]/15 border border-[#8FB3FF]/40 text-[#8FB3FF] flex items-center justify-center mr-1"
                style={{ width: '27%' }}
              >
                RETRIEVE
              </div>
              <div
                className="h-5 px-2 rounded bg-[#62D6B4]/15 border border-[#62D6B4]/40 text-[#62D6B4] flex items-center justify-center"
                style={{ width: '17%' }}
              >
                SPLIT
              </div>
            </div>
          </div>

          {/* Row 3: Part 1 · Venue */}
          <div className="flex items-center gap-3 text-xs">
            <div className="w-32 shrink-0">
              <div className="font-medium text-[#8FB3FF]">Part 1 · Venue</div>
              <div className="text-[10px] font-mono text-[#7D8594]">Doc_12 §2</div>
            </div>
            <div className="flex-1 relative h-7 bg-[#12151B] border border-[#1E2330] rounded-lg flex items-center px-1 text-[10px] font-mono">
              <div
                className="h-5 rounded bg-[#8FB3FF]/20 border border-[#8FB3FF]/40 text-[#8FB3FF] flex items-center justify-center absolute"
                style={{ left: '27%', width: '10%' }}
              >
                search
              </div>
              <div
                className="h-5 rounded bg-[#8FB3FF]/30 border border-[#8FB3FF]/50 text-[#ECE9E2] flex items-center justify-center absolute"
                style={{ left: '38%', width: '12%' }}
              >
                draft
              </div>
              {/* Verified diamond marker */}
              <div
                className="absolute rotate-45 w-2.5 h-2.5 bg-[#62D6B4] shadow-sm -top-1"
                style={{ left: '50%' }}
                title="draft verified 1.02s"
              />
              <div
                className="h-5 rounded bg-[#8FB3FF]/15 border border-[#8FB3FF]/30 text-[#8FB3FF] flex items-center justify-center absolute"
                style={{ left: '72%', width: '14%' }}
              >
                rewrite
              </div>
            </div>
          </div>

          {/* Row 4: Part 2 · Cancellation */}
          <div className="flex items-center gap-3 text-xs">
            <div className="w-32 shrink-0">
              <div className="font-medium text-[#62D6B4]">Part 2 · Cancellation</div>
              <div className="text-[10px] font-mono text-[#7D8594]">Doc_31 §2, §4</div>
            </div>
            <div className="flex-1 relative h-7 bg-[#12151B] border border-[#1E2330] rounded-lg flex items-center px-1 text-[10px] font-mono">
              <div
                className="h-5 rounded bg-[#62D6B4]/20 border border-[#62D6B4]/40 text-[#62D6B4] flex items-center justify-center absolute"
                style={{ left: '54%', width: '9%' }}
              >
                search
              </div>
              <div
                className="h-5 rounded bg-[#62D6B4]/30 border border-[#62D6B4]/50 text-[#ECE9E2] flex items-center justify-center absolute"
                style={{ left: '64%', width: '10%' }}
              >
                draft
              </div>
              {/* Verified diamond marker */}
              <div
                className="absolute rotate-45 w-2.5 h-2.5 bg-[#62D6B4] shadow-sm -top-1"
                style={{ left: '74%' }}
                title="draft verified 1.79s"
              />
              <div
                className="h-5 rounded bg-[#62D6B4]/15 border border-[#62D6B4]/30 text-[#62D6B4] flex items-center justify-center absolute"
                style={{ left: '75%', width: '14%' }}
              >
                rewrite
              </div>
            </div>
          </div>

          {/* Row 5: Part 3 · Catering */}
          <div className="flex items-center gap-3 text-xs">
            <div className="w-32 shrink-0">
              <div className="font-medium text-[#B98CFF]">Part 3 · Catering</div>
              <div className="text-[10px] font-mono text-[#7D8594]">Doc_89 §1, §2 · 1 gap</div>
            </div>
            <div className="flex-1 relative h-7 bg-[#12151B] border border-[#1E2330] rounded-lg flex items-center px-1 text-[10px] font-mono">
              <div
                className="h-5 rounded bg-[#B98CFF]/20 border border-[#B98CFF]/40 text-[#B98CFF] flex items-center justify-center absolute"
                style={{ left: '54%', width: '10%' }}
              >
                search
              </div>
              <div
                className="h-5 rounded bg-[#B98CFF]/30 border border-[#B98CFF]/50 text-[#ECE9E2] flex items-center justify-center absolute"
                style={{ left: '65%', width: '12%' }}
              >
                draft
              </div>
              {/* Verified diamond marker */}
              <div
                className="absolute rotate-45 w-2.5 h-2.5 bg-[#62D6B4] shadow-sm -top-1"
                style={{ left: '78%' }}
                title="draft verified 2.24s"
              />
              <div
                className="h-5 rounded bg-[#B98CFF]/15 border border-[#B98CFF]/30 text-[#B98CFF] flex items-center justify-center absolute"
                style={{ left: '80%', width: '14%' }}
              >
                rewrite
              </div>
            </div>
          </div>
        </div>

        {/* Footnote */}
        <div className="pt-2 text-[11px] text-[#7D8594] font-serif">
          Bar lengths come from the run's trace file; only the speech and controller times here
          are fixed by the scenario.
        </div>
      </div>

      {/* Lower Two Columns: Events Log + Grounding Checks (Board 9) */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 items-start">
        {/* Left Column: Events Log */}
        <div className="bg-[#15181E] border border-[#1E2330] rounded-2xl p-5 space-y-4">
          <div className="flex items-center justify-between pb-2 border-b border-[#1E2330]">
            <h2 className="text-sm font-semibold text-[#ECE9E2]">Events</h2>
            <span className="text-xs font-mono text-[#7D8594]">
              {defaultEvents.length} events logged
            </span>
          </div>

          <div className="space-y-2.5 font-mono text-xs max-h-[360px] overflow-y-auto pr-1">
            {defaultEvents.map((ev, i) => (
              <div
                key={i}
                className="flex items-start gap-2.5 p-2 rounded-lg bg-[#12151B] border border-[#1E2330]"
              >
                <span className="text-[#8FB3FF] shrink-0 font-bold">{ev.t}</span>
                <span className="text-[#A3A9B5] shrink-0 font-medium">{ev.source}</span>
                <span className="text-[#ECE9E2] break-words flex-1 font-serif text-[11px] leading-relaxed">
                  {ev.msg}
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* Right Column: Grounding Checks Table */}
        <div className="bg-[#15181E] border border-[#1E2330] rounded-2xl p-5 space-y-4">
          <div className="flex items-center gap-2 pb-2 border-b border-[#1E2330]">
            <CheckCircle2 className="w-4 h-4 text-[#6FD39A]" />
            <h2 className="text-sm font-semibold text-[#ECE9E2]">
              Grounding checks
            </h2>
          </div>

          <div className="divide-y divide-[#1E2330] text-xs">
            {groundingChecks.map((row, i) => (
              <div
                key={i}
                className="py-3 flex items-center justify-between text-[#ECE9E2]"
              >
                <span className="text-[#A3A9B5]">{row.label}</span>
                <span
                  className={`font-mono font-medium ${
                    row.success ? 'text-[#6FD39A]' : 'text-[#ECE9E2]'
                  }`}
                >
                  {row.value}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};
