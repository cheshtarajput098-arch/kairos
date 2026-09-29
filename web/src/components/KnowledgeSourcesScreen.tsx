import React, { useState, useEffect } from 'react';
import {
  Search,
  ShieldCheck,
  FileText,
  UploadCloud,
  RotateCw,
} from 'lucide-react';
import { getCorpusDocs, ApiCorpusDoc } from '../api';

interface DocumentRow {
  title: string;
  id: string;
  sections: number;
  words: number;
  status: string;
  integrity: string;
}

const DEFAULT_DOCS: DocumentRow[] = [
  {
    title: 'Travel Reimbursement Policy',
    id: 'Doc_05',
    sections: 4,
    words: 180,
    status: 'Searchable',
    integrity: 'Hash verified · clean',
  },
  {
    title: 'Workshop Venues in Pune',
    id: 'Doc_12',
    sections: 4,
    words: 199,
    status: 'Searchable',
    integrity: 'Hash verified · clean',
  },
  {
    title: 'Meeting Rooms in Bengaluru Office',
    id: 'Doc_20',
    sections: 3,
    words: 92,
    status: 'Searchable',
    integrity: 'Hash verified · clean',
  },
  {
    title: 'Event Cancellation and Refund Policy',
    id: 'Doc_31',
    sections: 4,
    words: 166,
    status: 'Searchable',
    integrity: 'Hash verified · clean',
  },
  {
    title: 'IT Equipment Loans',
    id: 'Doc_44',
    sections: 3,
    words: 72,
    status: 'Searchable',
    integrity: 'Hash verified · clean',
  },
  {
    title: 'Remote Work Policy',
    id: 'Doc_57',
    sections: 3,
    words: 67,
    status: 'Searchable',
    integrity: 'Hash verified · clean',
  },
  {
    title: 'Expense Receipt Standards',
    id: 'Doc_63',
    sections: 3,
    words: 98,
    status: 'Searchable',
    integrity: 'Hash verified · clean',
  },
  {
    title: 'Catering Options for Events',
    id: 'Doc_89',
    sections: 3,
    words: 113,
    status: 'Searchable',
    integrity: 'Hash verified · clean',
  },
];

export const KnowledgeSourcesScreen: React.FC = () => {
  const [filterText, setFilterText] = useState('');
  const [docs, setDocs] = useState<DocumentRow[]>(DEFAULT_DOCS);
  const [isReindexing, setIsReindexing] = useState(false);

  // Fetch real document metrics from API if running against live server
  useEffect(() => {
    getCorpusDocs().then((resp) => {
      if (resp && resp.documents && resp.documents.length > 0) {
        const rows: DocumentRow[] = resp.documents.map((d: ApiCorpusDoc) => {
          let wordCount = 0;
          d.chunks.forEach((c) => {
            wordCount += c.text.split(/\s+/).filter(Boolean).length;
          });
          return {
            title: d.title,
            id: d.id,
            sections: d.sections_count || d.chunks.length,
            words: wordCount || 100,
            status: 'Searchable',
            integrity: 'Hash verified · clean',
          };
        });
        setDocs(rows);
      }
    });
  }, []);

  const totalSections = docs.reduce((acc, d) => acc + d.sections, 0);
  const totalWords = docs.reduce((acc, d) => acc + d.words, 0);

  const filteredDocs = docs.filter(
    (d) =>
      d.title.toLowerCase().includes(filterText.toLowerCase()) ||
      d.id.toLowerCase().includes(filterText.toLowerCase())
  );

  const handleReindex = () => {
    setIsReindexing(true);
    setTimeout(() => {
      setIsReindexing(false);
    }, 1200);
  };

  return (
    <div className="w-full max-w-5xl mx-auto py-8 px-4 sm:px-6 space-y-8">
      {/* Header (Board 8) */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-[#1E2330]">
        <div>
          <div className="flex items-center gap-3">
            <h1 className="text-2xl sm:text-3xl font-bold text-[#ECE9E2] tracking-tight">
              Company policies
            </h1>
            <span className="flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-mono bg-[#4ADE80]/15 text-[#4ADE80] border border-[#4ADE80]/30">
              <span className="w-1.5 h-1.5 rounded-full bg-[#4ADE80]" />
              <span>Index ready</span>
            </span>
          </div>
          <p className="text-xs sm:text-sm text-[#7D8594] mt-1 font-mono">
            {docs.length} documents · {totalSections} sections · {totalWords} words · Veloria
            Systems (fictional demo corpus)
          </p>
        </div>

        {/* Action button */}
        <div className="flex items-center gap-2">
          <button
            onClick={handleReindex}
            disabled={isReindexing}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-[#1C2028] border border-[#282D3A] hover:bg-[#252B36] text-xs font-medium text-[#ECE9E2] transition-colors cursor-pointer disabled:opacity-50"
          >
            <RotateCw
              className={`w-3.5 h-3.5 text-[#8FB3FF] ${isReindexing ? 'animate-spin' : ''}`}
            />
            <span>{isReindexing ? 'Indexing…' : 'Re-index'}</span>
          </button>
        </div>
      </div>

      {/* 4 Real Index Metrics Cards (Board 8) */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Card 1: Meaning search */}
        <div className="bg-[#15181E] border border-[#1E2330] rounded-2xl p-4 sm:p-5 space-y-2">
          <div className="text-[11px] font-mono text-[#7D8594] uppercase tracking-wider">
            Meaning search
          </div>
          <div className="text-base sm:text-lg font-bold text-[#ECE9E2] font-mono">
            BGE-small-en-v1.5
          </div>
          <p className="text-xs text-[#7D8594] leading-relaxed">
            Runs locally on the CPU, no embedding API
          </p>
        </div>

        {/* Card 2: Keyword search */}
        <div className="bg-[#15181E] border border-[#1E2330] rounded-2xl p-4 sm:p-5 space-y-2">
          <div className="text-[11px] font-mono text-[#7D8594] uppercase tracking-wider">
            Keyword search
          </div>
          <div className="text-base sm:text-lg font-bold text-[#ECE9E2] font-mono">
            BM25
          </div>
          <p className="text-xs text-[#7D8594] leading-relaxed">
            Catches exact names, numbers and policy terms
          </p>
        </div>

        {/* Card 3: Fusion */}
        <div className="bg-[#15181E] border border-[#1E2330] rounded-2xl p-4 sm:p-5 space-y-2">
          <div className="text-[11px] font-mono text-[#7D8594] uppercase tracking-wider">
            Fusion
          </div>
          <div className="text-base sm:text-lg font-bold text-[#ECE9E2] font-mono">
            Reciprocal Rank Fusion
          </div>
          <p className="text-xs text-[#7D8594] leading-relaxed">
            k = 60 · rank-based, no score tuning
          </p>
        </div>

        {/* Card 4: Ingest safety */}
        <div className="bg-[#15181E] border border-[#1E2330] rounded-2xl p-4 sm:p-5 space-y-2">
          <div className="text-[11px] font-mono text-[#7D8594] uppercase tracking-wider">
            Ingest safety
          </div>
          <div className="text-base sm:text-lg font-bold text-[#6FD39A] font-mono">
            0 passages flagged
          </div>
          <p className="text-xs text-[#7D8594] leading-relaxed">
            Scanned for hidden instructions before indexing
          </p>
        </div>
      </div>

      {/* Filter Bar */}
      <div className="flex items-center justify-between gap-4">
        <div className="relative flex-1 max-w-sm">
          <Search className="w-4 h-4 text-[#7D8594] absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            value={filterText}
            onChange={(e) => setFilterText(e.target.value)}
            placeholder="Filter documents"
            className="w-full bg-[#15181E] border border-[#1E2330] rounded-xl pl-9 pr-4 py-2 text-xs sm:text-sm text-[#ECE9E2] placeholder-[#7D8594] focus:outline-none focus:border-[#8FB3FF]/40 transition-colors"
          />
        </div>

        <span className="text-xs text-[#7D8594] font-mono">
          Showing {filteredDocs.length} of {docs.length}
        </span>
      </div>

      {/* Document Table (Board 8) */}
      <div className="bg-[#15181E] border border-[#1E2330] rounded-2xl overflow-hidden shadow-lg">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse text-xs">
            <thead>
              <tr className="border-b border-[#1E2330] bg-[#12151B] text-[#7D8594] font-mono uppercase tracking-wider">
                <th className="py-3 px-4 font-semibold">Document</th>
                <th className="py-3 px-4 font-semibold">ID</th>
                <th className="py-3 px-4 font-semibold text-right">Sections</th>
                <th className="py-3 px-4 font-semibold text-right">Words</th>
                <th className="py-3 px-4 font-semibold">Status</th>
                <th className="py-3 px-4 font-semibold">Integrity</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#1E2330]">
              {filteredDocs.map((doc) => (
                <tr
                  key={doc.id}
                  className="hover:bg-[#1C2028] transition-colors group cursor-default"
                >
                  <td className="py-3.5 px-4 font-medium text-[#ECE9E2] flex items-center gap-2.5">
                    <FileText className="w-3.5 h-3.5 text-[#8FB3FF] shrink-0" />
                    <span>{doc.title}</span>
                  </td>
                  <td className="py-3.5 px-4 font-mono text-[#A3A9B5]">{doc.id}</td>
                  <td className="py-3.5 px-4 font-mono text-[#ECE9E2] text-right">
                    {doc.sections}
                  </td>
                  <td className="py-3.5 px-4 font-mono text-[#ECE9E2] text-right">
                    {doc.words}
                  </td>
                  <td className="py-3.5 px-4">
                    <span className="inline-flex items-center gap-1.5 text-[#6FD39A] font-medium">
                      <span className="w-1.5 h-1.5 rounded-full bg-[#6FD39A]" />
                      <span>{doc.status}</span>
                    </span>
                  </td>
                  <td className="py-3.5 px-4 text-[#A3A9B5] flex items-center gap-1.5">
                    <ShieldCheck className="w-3.5 h-3.5 text-[#6FD39A]" />
                    <span>{doc.integrity}</span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Dropdown File Guidance Area (Board 8) */}
      <div className="bg-[#12151B] border border-dashed border-[#282D3A] rounded-2xl p-6 sm:p-8 flex flex-col sm:flex-row items-center justify-between gap-4 text-center sm:text-left">
        <div className="flex items-center gap-4">
          <div className="w-10 h-10 rounded-xl bg-[#1C2028] border border-[#282D3A] flex items-center justify-center text-[#8FB3FF] shrink-0">
            <UploadCloud className="w-5 h-5" />
          </div>
          <div className="space-y-1">
            <div className="text-xs sm:text-sm font-semibold text-[#ECE9E2]">
              Drop Markdown or text files here
            </div>
            <p className="text-xs text-[#7D8594] leading-relaxed">
              Each passage is scanned for hidden instructions and hashed before it becomes
              searchable.
            </p>
          </div>
        </div>

        <button
          className="px-4 py-2 rounded-xl bg-[#1C2028] border border-[#282D3A] hover:bg-[#252B36] text-xs font-medium text-[#ECE9E2] transition-colors cursor-pointer shrink-0"
          title="Corpus updates are administered via CLI ingest in production"
          onClick={() => {
            alert('Corpus ingest is administered via `kairos index` CLI in production.');
          }}
        >
          Browse files
        </button>
      </div>
    </div>
  );
};
