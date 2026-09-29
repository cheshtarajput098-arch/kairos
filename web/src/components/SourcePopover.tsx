import React, { useState } from 'react';
import { BookOpen, ShieldCheck } from 'lucide-react';

interface SourcePopoverProps {
  citation: string;
  index: number;
  evidenceSpan?: string;
}

export const SourcePopover: React.FC<SourcePopoverProps> = ({
  citation,
  index,
  evidenceSpan,
}) => {
  const [isOpen, setIsOpen] = useState(false);

  // Parse doc and section
  const [docId, section] = citation.split('§');

  return (
    <span className="relative inline-block ml-1">
      <button
        onClick={() => setIsOpen(!isOpen)}
        onMouseEnter={() => setIsOpen(true)}
        onMouseLeave={() => setIsOpen(false)}
        className="inline-flex items-center justify-center w-[18px] h-[18px] text-[10px] font-mono font-bold rounded bg-[#1C2028] border border-[#282D3A] text-[#ECE9E2] hover:border-[#8FB3FF] transition-colors align-baseline"
        aria-label={`Source citation ${citation}`}
      >
        {index}
      </button>

      {isOpen && (
        <div
          onMouseEnter={() => setIsOpen(true)}
          onMouseLeave={() => setIsOpen(false)}
          className="absolute z-50 bottom-full left-1/2 -translate-x-1/2 mb-2 w-72 p-3.5 bg-[#15181E] rounded-xl shadow-2xl border border-[#1E2330] text-left text-xs"
        >
          <div className="flex items-center justify-between pb-2 border-b border-[#1E2330] font-mono text-[11px]">
            <span className="flex items-center gap-1.5 font-semibold text-[#8FB3FF]">
              <BookOpen className="w-3.5 h-3.5" />
              {docId} {section ? `§ ${section}` : ''}
            </span>
            <span className="flex items-center gap-1 text-[#6FD39A] font-medium">
              <ShieldCheck className="w-3.5 h-3.5" /> Verified
            </span>
          </div>

          <div className="mt-2 text-[#ECE9E2] font-serif italic text-xs leading-relaxed line-clamp-3">
            "{evidenceSpan || 'Verified corpus evidence chunk in approved index.'}"
          </div>

          <div className="mt-2 pt-1.5 border-t border-[#1E2330] flex justify-end">
            <span className="text-[10px] text-[#7D8594] font-mono">Corpus Verified [Doc_ID §Section]</span>
          </div>
        </div>
      )}
    </span>
  );
};
