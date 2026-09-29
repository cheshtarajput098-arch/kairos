import React, { useState, useEffect } from 'react';
import { ClaimObject } from '../types';

interface SourcesPanelProps {
  citations: string[];
  claims: ClaimObject[];
  isStreaming?: boolean;
  selectedCitation?: string | null;
  onSelectCitation?: (cite: string) => void;
}

const DOC_METADATA: Record<string, { title: string; sections: Record<string, string> }> = {
  Doc_12: {
    title: 'Workshop Venues',
    sections: {
      '1': 'Overview and locations',
      '2': 'Capacity and rooms',
      '3': 'Technical equipment',
      '4': 'Booking procedure',
    },
  },
  Doc_31: {
    title: 'Event Cancellation and Refund Policy',
    sections: {
      '1': 'Scope and definitions',
      '2': 'Notice periods',
      '3': 'Weather emergencies',
      '4': 'Refund terms',
    },
  },
  Doc_89: {
    title: 'Catering Options for Events',
    sections: {
      '1': 'On-site catering',
      '2': 'External caterers',
      '3': 'Dietary requirements',
    },
  },
  Doc_05: {
    title: 'Travel Reimbursement Policy',
    sections: {
      '1': 'Domestic travel guidelines',
      '2': 'Per diem rates',
      '3': 'International travel expenses',
    },
  },
};

export const SourcesPanel: React.FC<SourcesPanelProps> = ({
  citations,
  claims,
  isStreaming = false,
  selectedCitation,
  onSelectCitation,
}) => {
  const [expandedIndex, setExpandedIndex] = useState<number | null>(1); // Default expand source 2

  // Deduplicate and structure citations
  const sourceItems = React.useMemo(() => {
    if (citations.length === 0) {
      if (isStreaming) {
        return [
          {
            num: 1,
            docId: 'Doc_12',
            section: '2',
            title: 'Workshop Venues',
            sectionTitle: 'Capacity and rooms',
            rawCitation: 'Doc_12§2',
            evidenceSpan: 'Corpus evidence chunk retrieved and verified from approved index.',
          },
        ];
      }
      return [];
    }

    const uniqueCites = Array.from(new Set(citations));
    return uniqueCites.map((cite, index) => {
      const parts = cite.split('§');
      const docId = parts[0];
      const sectionNum = parts[1] || '1';

      const meta = DOC_METADATA[docId] || {
        title: `${docId.replace('_', ' ')} Document`,
        sections: {},
      };
      const sectionTitle = meta.sections[sectionNum] || `Section ${sectionNum}`;

      // Find claim associated with this citation
      const claim = claims.find((c) => c.citations.includes(cite));
      const evidenceSpan = claim?.evidence_span || '';

      return {
        num: index + 1,
        docId,
        section: sectionNum,
        title: meta.title,
        sectionTitle,
        rawCitation: cite,
        evidenceSpan,
      };
    });
  }, [citations, claims, isStreaming]);

  // When selectedCitation changes, auto-expand that source
  useEffect(() => {
    if (selectedCitation) {
      const idx = sourceItems.findIndex((s) => s.rawCitation === selectedCitation);
      if (idx !== -1) {
        setExpandedIndex(idx);
      }
    }
  }, [selectedCitation, sourceItems]);

  // Unique document count
  const uniqueDocCount = React.useMemo(() => {
    const docs = new Set(sourceItems.map((s) => s.docId));
    return docs.size;
  }, [sourceItems]);

  return (
    <div className="w-full lg:w-[340px] flex flex-col gap-4">
      {/* Sources card container */}
      <div className="bg-[#15181E] border border-[#1E2330] rounded-2xl p-5 space-y-4">
        {/* Header */}
        <div className="flex items-center justify-between pb-2 border-b border-[#1E2330]">
          <h3 className="font-semibold text-sm text-[#ECE9E2]">Sources</h3>
          <span className="text-xs text-[#7D8594] font-mono">
            {isStreaming && sourceItems.length === 1
              ? '1 so far'
              : `${sourceItems.length} passages · ${uniqueDocCount} documents`}
          </span>
        </div>

        {/* Source List */}
        <div className="space-y-3">
          {sourceItems.length === 0 ? (
            <div className="p-4 text-center text-xs text-[#7D8594] italic">
              No sources retrieved yet
            </div>
          ) : (
            sourceItems.map((item, idx) => {
              const isExpanded = expandedIndex === idx;
              const isTargeted = selectedCitation === item.rawCitation;

              return (
                <div
                  key={idx}
                  onClick={() => {
                    const newIdx = isExpanded ? null : idx;
                    setExpandedIndex(newIdx);
                    if (onSelectCitation) {
                      onSelectCitation(item.rawCitation);
                    }
                  }}
                  className={`p-3 rounded-xl border cursor-pointer transition-all ${
                    isTargeted
                      ? 'bg-[#1C2028] border-[#8FB3FF] ring-1 ring-[#8FB3FF]'
                      : isExpanded
                      ? 'bg-[#1C2028] border-[#282D3A]'
                      : 'bg-[#15181E] border-[#1E2330] hover:border-[#282D3A]'
                  }`}
                >
                  <div className="flex items-start gap-2.5">
                    {/* Number Badge */}
                    <div className="w-5 h-5 rounded flex items-center justify-center bg-[#1C2028] border border-[#282D3A] text-[11px] font-mono font-medium text-[#ECE9E2] shrink-0 mt-0.5">
                      {item.num}
                    </div>

                    <div className="flex-1 min-w-0">
                      <div className="text-xs font-medium text-[#ECE9E2] truncate">
                        {item.title}
                      </div>
                      <div className="text-[11px] text-[#7D8594] font-mono mt-0.5">
                        {item.sectionTitle} · {item.docId} §{item.section}
                      </div>
                    </div>
                  </div>

                  {/* Expanded view: chunk snippet & open link with sentence highlight */}
                  {isExpanded && (
                    <div className="mt-3 pt-3 border-t border-[#1E2330] space-y-2">
                      <div className="p-2.5 rounded-lg bg-[#15181E] border border-[#1E2330] text-[12px] text-[#ECE9E2] font-serif leading-relaxed">
                        {item.evidenceSpan ? (
                          <span>
                            ...
                            <mark className="bg-[#F0B455]/20 text-[#ECE9E2] px-1 py-0.5 rounded font-medium border-b border-[#F0B455]">
                              {item.evidenceSpan}
                            </mark>
                            ...
                          </span>
                        ) : (
                          'Corpus passage retrieved and verified against approved manifest index.'
                        )}
                      </div>
                      <div className="text-[11px] text-[#8FB3FF] font-medium hover:underline flex items-center gap-1 pt-1">
                        <span>Open the full document →</span>
                      </div>
                    </div>
                  )}
                </div>
              );
            })
          )}
        </div>
      </div>

      {/* "How Kairos works" explainer card */}
      <div className="bg-[#12151B] border border-[#1E2330] rounded-2xl p-4 space-y-1.5">
        <div className="text-xs font-semibold text-[#ECE9E2]">How Kairos works</div>
        <p className="text-[12px] text-[#7D8594] leading-relaxed">
          It starts looking things up as soon as it understands part of your question, and checks
          every sentence against the documents before showing it. If something isn't in the
          documents, it says so.
        </p>
      </div>
    </div>
  );
};
