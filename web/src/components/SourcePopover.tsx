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
        className="inline-flex items-center justify-center w-4 h-4 text-[10px] font-mono font-bold rounded-full bg-blue-100 dark:bg-blue-900/50 text-blue-700 dark:text-blue-300 hover:bg-blue-200 transition-colors"
        aria-label={`Source citation ${citation}`}
      >
        {index}
      </button>

      {isOpen && (
        <div
          onMouseEnter={() => setIsOpen(true)}
          onMouseLeave={() => setIsOpen(false)}
          className="absolute z-50 bottom-full left-1/2 -translate-x-1/2 mb-2 w-72 p-3 bg-white dark:bg-slate-800 rounded-xl shadow-lg border border-slate-200 dark:border-slate-700 text-left text-xs"
        >
          <div className="flex items-center justify-between pb-1.5 border-b border-slate-100 dark:border-slate-700 text-slate-500 font-mono text-[11px]">
            <span className="flex items-center gap-1 font-semibold text-blue-600 dark:text-blue-400">
              <BookOpen className="w-3 h-3" />
              {docId} {section ? `§ Section ${section}` : ''}
            </span>
            <span className="flex items-center gap-0.5 text-emerald-600 dark:text-emerald-400">
              <ShieldCheck className="w-3 h-3" /> Verified
            </span>
          </div>

          <div className="mt-2 text-slate-700 dark:text-slate-200 italic line-clamp-3">
            "{evidenceSpan || 'Verified corpus evidence chunk in approved index.'}"
          </div>

          <div className="mt-2 pt-1.5 border-t border-slate-100 dark:border-slate-700 flex justify-end">
            <span className="text-[10px] text-slate-400 font-mono">Corpus Verified [Doc_ID §Section]</span>
          </div>
        </div>
      )}
    </span>
  );
};
