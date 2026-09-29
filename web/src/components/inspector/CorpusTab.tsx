import React, { useState } from 'react';
import { Search, CheckCircle2, Shield } from 'lucide-react';
import { CORPUS_DOCS, CorpusDoc } from '../../fixtures/corpusChunks';

export const CorpusTab: React.FC = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedDocId, setSelectedDocId] = useState('Doc_12');

  const selectedDoc: CorpusDoc = CORPUS_DOCS.find((d) => d.id === selectedDocId) || CORPUS_DOCS[0];

  const filteredChunks = selectedDoc.chunks.filter((c) => {
    if (!searchTerm) return true;
    const term = searchTerm.toLowerCase();
    return c.text.toLowerCase().includes(term) || c.title.toLowerCase().includes(term);
  });

  return (
    <div className="space-y-6">
      {/* Tab Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="text-xs text-[#7D8594] font-mono">SPEC Ingest & Security · SHA-256 Manifest Verified</div>
          <h2 className="text-xl sm:text-2xl font-bold text-[#ECE9E2] mt-1 tracking-tight">
            Corpus Document Explorer
          </h2>
        </div>

        <div className="flex items-center gap-2">
          <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-[#1C2028] border border-[#282D3A] text-xs">
            <Shield className="w-3.5 h-3.5 text-[#6FD39A]" />
            <span className="text-[#ECE9E2] font-mono font-medium">Manifest: valid</span>
          </div>
          <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-[#1C2028] border border-[#282D3A] text-xs">
            <CheckCircle2 className="w-3.5 h-3.5 text-[#8FB3FF]" />
            <span className="text-[#ECE9E2] font-mono font-medium">4 docs · 27 chunks</span>
          </div>
        </div>
      </div>

      {/* Main Split Layout: Documents List (left) + Chunks View (right) */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        {/* Left Column: Document Cards (4 cols) */}
        <div className="lg:col-span-4 space-y-3">
          <div className="text-xs font-semibold text-[#A3A9B5] uppercase tracking-wider px-1">
            Corpus Documents
          </div>

          <div className="space-y-2">
            {CORPUS_DOCS.map((doc) => {
              const isSelected = doc.id === selectedDocId;
              return (
                <button
                  key={doc.id}
                  onClick={() => setSelectedDocId(doc.id)}
                  className={`w-full text-left p-4 rounded-xl border transition-all ${
                    isSelected
                      ? 'bg-[#1C2028] border-[#8FB3FF] shadow-sm'
                      : 'bg-[#15181E] border-[#1E2330] hover:border-[#282D3A]'
                  }`}
                >
                  <div className="flex items-center justify-between pb-1">
                    <span className="font-mono font-bold text-xs text-[#8FB3FF]">
                      {doc.id}
                    </span>
                    <span className="text-[11px] font-mono text-[#7D8594]">
                      {doc.sectionsCount} sections
                    </span>
                  </div>
                  <div className="font-semibold text-sm text-[#ECE9E2] leading-snug">
                    {doc.title}
                  </div>
                  <p className="text-xs text-[#7D8594] mt-1.5 line-clamp-2 leading-relaxed">
                    {doc.summary}
                  </p>
                </button>
              );
            })}
          </div>
        </div>

        {/* Right Column: Section Chunks & Filter (8 cols) */}
        <div className="lg:col-span-8 space-y-4">
          {/* Search bar inside selected doc */}
          <div className="flex items-center gap-3 bg-[#15181E] border border-[#1E2330] rounded-xl px-3.5 py-2">
            <Search className="w-4 h-4 text-[#7D8594]" />
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder={`Filter passages in ${selectedDoc.id} (${selectedDoc.title})…`}
              className="w-full bg-transparent text-xs text-[#ECE9E2] placeholder-[#7D8594] focus:outline-none"
            />
            {searchTerm && (
              <button
                onClick={() => setSearchTerm('')}
                className="text-xs text-[#7D8594] hover:text-[#ECE9E2]"
              >
                Clear
              </button>
            )}
          </div>

          {/* Chunks List */}
          <div className="space-y-3">
            {filteredChunks.length === 0 ? (
              <div className="bg-[#15181E] border border-[#1E2330] rounded-xl p-8 text-center text-xs text-[#7D8594]">
                No passages match "{searchTerm}". Try a different keyword.
              </div>
            ) : (
              filteredChunks.map((chunk) => (
                <div
                  key={chunk.id}
                  className="bg-[#15181E] border border-[#1E2330] rounded-xl p-4 space-y-2.5 hover:border-[#282D3A] transition-colors"
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <span className="px-2 py-0.5 rounded font-mono text-[11px] font-bold bg-[#1C2028] border border-[#282D3A] text-[#8FB3FF]">
                        [{chunk.id}]
                      </span>
                      <span className="text-xs font-semibold text-[#ECE9E2]">
                        {chunk.title}
                      </span>
                    </div>

                    <span className="text-[10px] font-mono text-[#6FD39A] bg-[#6FD39A]/10 px-2 py-0.5 rounded-full border border-[#6FD39A]/20">
                      clean · no injection
                    </span>
                  </div>

                  <p className="text-xs font-serif leading-relaxed text-[#ECE9E2]/90 bg-[#0E1014]/60 p-3 rounded-lg border border-[#1E2330]">
                    {chunk.text}
                  </p>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
