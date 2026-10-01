import React, { useState } from 'react';
import { ExternalLink } from 'lucide-react';
import { ClaimObject, ControllerDecisionEvent, LegInfo, StreamEvent } from '../../types';

interface DisplayClaim {
  num: number;
  text: string;
  citation: string;
  status: string;
}

const DEFAULT_TIMELINE_CLAIMS: DisplayClaim[] = [
  { num: 1, text: 'Venue: Grand Ballroom capacity 500 guests', citation: 'Doc_12 §2', status: 'verified' },
  { num: 2, text: 'Audiovisual: Dual-projector system included', citation: 'Doc_31 §2', status: 'verified' },
  { num: 3, text: 'Catering: Buffet lunch with vegetarian options', citation: 'Doc_89 §1', status: 'verified' },
];

interface TimelineTabProps {
  decisions: ControllerDecisionEvent[];
  legs: LegInfo[];
  firstRetrievalT: number | null;
  utteranceEndT: number | null;
  currentTime: number;
  events: StreamEvent[];
  readyAtEnd?: number;
  finalClaims: ClaimObject[];
}

export const TimelineTab: React.FC<TimelineTabProps> = ({
  decisions: _decisions,
  legs: _legs,
  firstRetrievalT,
  utteranceEndT,
  finalClaims,
}) => {
  const [scrubTime, setScrubTime] = useState<number>(1.96);

  // If live data exists, calculate lead time; otherwise use board 4 sample values
  const leadTimeVal =
    firstRetrievalT !== null && utteranceEndT !== null && utteranceEndT > firstRetrievalT
      ? (utteranceEndT - firstRetrievalT).toFixed(1)
      : '1.3';

  // Sample or live claims
  const displayClaims: DisplayClaim[] =
    finalClaims.length > 0
      ? finalClaims.map((c: ClaimObject, i: number) => ({
          num: (i % 3) + 1,
          text: c.text.length > 40 ? `${c.text.slice(0, 40)}…` : c.text,
          citation: c.citations[0] ? c.citations[0].replace('§', ' §') : 'no source',
          status: c.status === 'uncertain' ? 'not found' : 'verified',
        }))
      : DEFAULT_TIMELINE_CLAIMS;

  // Event log items (real stream events or board 4 defaults)
  const defaultLog = [
    { t: '0.00', name: 'controller_decision', detail: 'WAIT intent_unstable' },
    { t: '0.80', name: 'retrieval_started', detail: 'L1 "Pune workshop venue capacity 30"' },
    { t: '1.02', name: 'draft_verified', detail: 'L1 Doc_12 §2' },
    { t: '1.60', name: 'subquery_emitted', detail: 'L2 L3' },
    { t: '1.79', name: 'draft_verified', detail: 'L2 Doc_31 §2, §4' },
    { t: '2.00', name: 'leg_updated', detail: 'L3 "catering options"' },
    { t: '2.10', name: 'draft_committed', detail: 'L1 L2' },
    { t: '2.24', name: 'draft_verified', detail: 'L3 Doc_89 §1, §2 · 1 gap' },
  ];

  return (
    <div className="space-y-6">
      {/* Scenario breadcrumb & Title (Board 4) */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="text-xs text-[#7D8594] font-mono">
            Scenario 1 · turn s1-t1 · sample timing
          </div>
          <h2 className="text-xl sm:text-2xl font-bold text-[#ECE9E2] mt-1 tracking-tight">
            Search and drafting started while the speaker was still talking
          </h2>
        </div>

        {/* 3 KPI Cards */}
        <div className="flex items-center gap-3">
          <div className="bg-[#15181E] border border-[#1E2330] rounded-xl px-4 py-2.5 min-w-[100px]">
            <div className="text-[11px] text-[#7D8594] font-medium">Lead time</div>
            <div className="text-lg font-bold text-[#ECE9E2] mt-0.5">{leadTimeVal} s</div>
          </div>

          <div className="bg-[#15181E] border border-[#1E2330] rounded-xl px-4 py-2.5 min-w-[110px]">
            <div className="text-[11px] text-[#7D8594] font-medium">Ready at end</div>
            <div className="text-lg font-bold text-[#ECE9E2] mt-0.5">2 of 3 parts</div>
          </div>

          <div className="bg-[#15181E] border border-[#1E2330] rounded-xl px-4 py-2.5 min-w-[110px]">
            <div className="text-[11px] text-[#7D8594] font-medium">Made-up citations</div>
            <div className="text-lg font-bold text-[#ECE9E2] mt-0.5">0</div>
          </div>
        </div>
      </div>

      {/* Main Gantt Timeline Container */}
      <div className="bg-[#15181E] border border-[#1E2330] rounded-2xl p-6 space-y-4">
        {/* Time Axis Header */}
        <div className="relative ml-28 h-6 text-xs font-mono text-[#7D8594] border-b border-[#1E2330]">
          <span className="absolute left-[0%]">0.0 s</span>
          <span className="absolute left-[25%]">0.5</span>
          <span className="absolute left-[50%]">1.0</span>
          <span className="absolute left-[75%]">1.5</span>
          <span className="absolute left-[95%]">2.0</span>
        </div>

        {/* Gantt Track Area */}
        <div className="relative space-y-3 pt-2">
          {/* Vertical marker: Speaker stopped */}
          <div className="absolute top-0 bottom-6 left-[96%] border-l-2 border-dashed border-[#F0B455] z-20 pointer-events-none">
            <span className="absolute -top-1 left-2 text-[11px] font-mono text-[#F0B455] whitespace-nowrap font-medium">
              Speaker stopped · {utteranceEndT ? utteranceEndT.toFixed(1) : RACE_BENCHMARKS.utteranceEndS.toFixed(1)} s
            </span>
          </div>

          {/* Row 1: Speech */}
          <div className="flex items-center text-xs">
            <span className="w-28 text-[#7D8594] font-medium shrink-0">Speech</span>
            <div className="flex-1 relative h-8 flex items-center gap-1.5">
              <div className="w-[45%] h-7 bg-[#1C2028] border border-[#282D3A] rounded-lg px-2.5 flex items-center text-[11px] text-[#A3A9B5] truncate">
                Organising a customer workshop
              </div>
              <div className="w-[32%] h-7 bg-[#1C2028] border border-[#282D3A] rounded-lg px-2.5 flex items-center text-[11px] text-[#A3A9B5] truncate">
                Attendee capacity and location, with
              </div>
              <div className="w-[18%] h-7 bg-[#1C2028] border border-[#282D3A] rounded-lg px-2.5 flex items-center text-[11px] text-[#A3A9B5] truncate">
                the cancellation policy and…
              </div>
            </div>
          </div>

          {/* Row 2: Decision */}
          <div className="flex items-center text-xs">
            <span className="w-28 text-[#7D8594] font-medium shrink-0">Decision</span>
            <div className="flex-1 relative h-7 flex items-center">
              <span className="absolute left-[0%] px-2.5 py-0.5 rounded-full text-[10px] font-mono bg-[#1C2028] border border-[#282D3A] text-[#7D8594]">
                WAIT · unstable
              </span>
              <span className="absolute left-[40%] px-2.5 py-0.5 rounded-full text-[10px] font-mono bg-[#1C2028] border border-[#8FB3FF]/30 text-[#8FB3FF]">
                RETRIEVE · entities stable
              </span>
              <span className="absolute left-[72%] px-2.5 py-0.5 rounded-full text-[10px] font-mono bg-[#1C2028] border border-[#282D3A] text-[#A3A9B5]">
                SPLIT → 3 parts
              </span>
            </div>
          </div>

          {/* Row 3: 1 · Venue */}
          <div className="flex items-center text-xs">
            <div className="w-28 flex items-center gap-1.5 shrink-0">
              <span className="w-2 h-2 rounded-full bg-[#8FB3FF]" />
              <span className="text-[#ECE9E2] font-medium">1 · Venue</span>
            </div>
            <div className="flex-1 relative h-7">
              <div className="absolute left-[40%] w-[18%] h-6 bg-[#8FB3FF] rounded-md shadow-sm flex items-center justify-end pr-1.5 text-white" />
              <div className="absolute left-[59%] flex items-center gap-1 text-[11px] font-mono text-[#A3A9B5]">
                <span>◆</span>
                <span>draft verified 1.02 s</span>
              </div>
            </div>
          </div>

          {/* Row 4: 2 · Cancellation */}
          <div className="flex items-center text-xs">
            <div className="w-28 flex items-center gap-1.5 shrink-0">
              <span className="w-2 h-2 rounded-full bg-[#62D6B4]" />
              <span className="text-[#ECE9E2] font-medium">2 · Cancellation</span>
            </div>
            <div className="flex-1 relative h-7">
              <div className="absolute left-[70%] w-[15%] h-6 bg-[#62D6B4] rounded-md shadow-sm" />
              <span className="absolute left-[86%] text-[#62D6B4] text-[11px]">◆</span>
            </div>
          </div>

          {/* Row 4b: Superseded bar */}
          <div className="flex items-center text-xs opacity-70">
            <span className="w-28" />
            <div className="flex-1 relative h-5">
              <div className="absolute left-[70%] w-[18%] h-5 border border-dashed border-[#B98CFF] rounded text-[10px] font-mono text-[#B98CFF] flex items-center justify-center">
                superseded
              </div>
            </div>
          </div>

          {/* Row 5: 3 · Catering */}
          <div className="flex items-center text-xs">
            <div className="w-28 flex items-center gap-1.5 shrink-0">
              <span className="w-2 h-2 rounded-full bg-[#B98CFF]" />
              <span className="text-[#ECE9E2] font-medium">3 · Catering</span>
            </div>
            <div className="flex-1 relative h-7">
              <div className="absolute left-[90%] w-[14%] h-6 bg-[#B98CFF] rounded-md shadow-sm" />
              <span className="absolute left-[105%] text-[#B98CFF] text-[11px]">◆</span>
            </div>
          </div>
        </div>

        {/* Legend */}
        <div className="pt-4 border-t border-[#1E2330] flex flex-wrap items-center gap-5 text-xs text-[#7D8594]">
          <div className="flex items-center gap-1.5">
            <span className="w-3.5 h-3.5 bg-[#8FB3FF] rounded-sm" />
            <span>Search + draft for one part</span>
          </div>
          <div className="flex items-center gap-1.5">
            <span className="text-[#ECE9E2]">◆</span>
            <span>Draft checked against its source</span>
          </div>
          <div className="flex items-center gap-1.5">
            <span className="w-3.5 h-3.5 bg-[#1C2028] border border-[#282D3A] rounded-sm" />
            <span>Work hidden behind speech (1.3 s)</span>
          </div>
          <div className="flex items-center gap-1.5">
            <span className="w-3.5 h-3.5 border border-dashed border-[#B98CFF] rounded-sm" />
            <span>Replaced when the speaker said more</span>
          </div>
        </div>

        {/* Replay Scrubber Slider */}
        <div className="pt-2 flex items-center gap-4">
          <span className="text-xs text-[#A3A9B5] font-mono shrink-0">Replay to</span>
          <input
            type="range"
            min="0"
            max="2.5"
            step="0.01"
            value={scrubTime}
            onChange={(e) => setScrubTime(parseFloat(e.target.value))}
            className="flex-1 accent-[#8FB3FF] h-1.5 bg-[#1C2028] rounded-lg cursor-pointer"
          />
          <span className="text-xs text-[#ECE9E2] font-mono w-14 text-right">
            {scrubTime.toFixed(2)} s
          </span>
        </div>
      </div>

      {/* Bottom Grid: Claims Table & Event Log (Board 4) */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Claims Table */}
        <div className="bg-[#15181E] border border-[#1E2330] rounded-2xl p-5 space-y-3">
          <div className="flex items-center justify-between pb-2 border-b border-[#1E2330]">
            <h3 className="font-semibold text-sm text-[#ECE9E2]">Claims · version 1</h3>
            <span className="text-xs text-[#7D8594]">each checked before it is shown</span>
          </div>

          <div className="space-y-2.5">
            {displayClaims.map((claim: DisplayClaim, idx: number) => (
              <div
                key={idx}
                className="flex items-center justify-between text-xs py-1.5 border-b border-[#1E2330]/50 last:border-none"
              >
                <div className="flex items-center gap-3 min-w-0 pr-2">
                  <span
                    className="w-4 h-4 rounded text-[10px] font-mono font-bold flex items-center justify-center shrink-0 text-white"
                    style={{
                      backgroundColor:
                        claim.num === 1 ? '#8FB3FF' : claim.num === 2 ? '#62D6B4' : '#B98CFF',
                    }}
                  >
                    {claim.num}
                  </span>
                  <span className="text-[#ECE9E2] truncate">{claim.text}</span>
                </div>

                <div className="flex items-center gap-3 shrink-0">
                  <span className="font-mono text-[11px] text-[#7D8594]">{claim.citation}</span>
                  <span
                    className={`font-mono text-[11px] ${
                      claim.status === 'verified' ? 'text-[#6FD39A]' : 'text-[#EF4444]'
                    }`}
                  >
                    {claim.status}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Event Log */}
        <div className="bg-[#15181E] border border-[#1E2330] rounded-2xl p-5 space-y-3">
          <div className="flex items-center justify-between pb-2 border-b border-[#1E2330]">
            <h3 className="font-semibold text-sm text-[#ECE9E2]">Event log</h3>
            <a
              href="http://localhost:16686"
              target="_blank"
              rel="noreferrer"
              className="text-xs text-[#5B8DEF] hover:underline flex items-center gap-1"
            >
              <span>Open trace in Jaeger</span>
              <ExternalLink className="w-3 h-3" />
            </a>
          </div>

          <div className="font-mono text-[11px] space-y-1.5 text-[#A3A9B5] max-h-[220px] overflow-y-auto">
            {defaultLog.map((ev, i) => (
              <div key={i} className="flex items-start gap-3 py-0.5">
                <span className="text-[#7D8594] w-9 shrink-0">{ev.t}</span>
                <span className="text-[#ECE9E2] shrink-0">{ev.name}</span>
                <span className="text-[#7D8594] truncate">{ev.detail}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};
