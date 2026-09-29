import React from 'react';
import { VersionDiff } from '../types';

interface ChangePanelProps {
  version: number;
  diff?: VersionDiff;
}

export const ChangePanel: React.FC<ChangePanelProps> = ({ version, diff: _diff }) => {
  const parts = [
    { name: 'Venue', dotColor: '#8FB3FF', status: 'Updated', statusColor: '#8FB3FF' },
    { name: 'Cancellation', dotColor: '#62D6B4', status: 'Kept as is', statusColor: '#7D8594' },
    { name: 'Catering', dotColor: '#B98CFF', status: 'Kept as is', statusColor: '#7D8594' },
  ];

  return (
    <div className="w-full lg:w-[340px] flex flex-col gap-4">
      {/* What changed card */}
      <div className="bg-[#15181E] border border-[#1E2330] rounded-2xl p-5 space-y-5">
        <h3 className="font-semibold text-sm text-[#ECE9E2]">
          What changed in v{version}
        </h3>

        {/* Changes list */}
        <div className="space-y-2.5">
          {parts.map((p, i) => (
            <div key={i} className="flex items-center justify-between text-xs py-1">
              <div className="flex items-center gap-2">
                <span
                  className="w-2 h-2 rounded-full"
                  style={{ backgroundColor: p.dotColor }}
                />
                <span className="text-[#ECE9E2] font-medium">{p.name}</span>
              </div>
              <span className="font-medium" style={{ color: p.statusColor }}>
                {p.status}
              </span>
            </div>
          ))}
        </div>

        {/* Sources section */}
        <div className="pt-4 border-t border-[#1E2330] space-y-1.5">
          <div className="text-xs font-semibold text-[#ECE9E2]">Sources</div>
          <p className="text-xs text-[#A3A9B5] leading-relaxed">
            All 5 earlier sources kept. Source 1 was read again for the new group size.
          </p>
        </div>
      </div>

      {/* Why this is fast explainer card */}
      <div className="bg-[#12151B] border border-[#1E2330] rounded-2xl p-5 space-y-2">
        <div className="text-xs font-semibold text-[#ECE9E2]">Why this is fast</div>
        <p className="text-xs text-[#7D8594] leading-relaxed">
          Kairos keeps the parts of your answer that are still true and only rechecks the part your
          new detail affects, instead of starting over.
        </p>
      </div>
    </div>
  );
};
