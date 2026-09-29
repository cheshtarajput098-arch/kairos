import React, { useState } from 'react';
import { Search, CheckCircle2, Shield } from 'lucide-react';

interface CorpusDoc {
  id: string;
  title: string;
  sectionsCount: number;
  summary: string;
  chunks: { id: string; section: string; title: string; text: string }[];
}

const CORPUS_DOCS: CorpusDoc[] = [
  {
    id: 'Doc_12',
    title: 'Workshop Venues in Pune',
    sectionsCount: 4,
    summary: 'Approved facilities in Pune for technical workshops, room capacities, layouts, and equipment.',
    chunks: [
      {
        id: 'Doc_12§1',
        section: '§1',
        title: 'Overview and locations',
        text: 'Veloria Systems maintains two approved workshop facilities in Pune: Riverside Hall in Baner and Koregaon Studio in Koregaon Park. Both locations provide high-speed connectivity and presentation screens.',
      },
      {
        id: 'Doc_12§2',
        section: '§2',
        title: 'Capacity and rooms',
        text: 'Both approved Pune venues fit your group: Riverside Hall in Baner seats up to 40 people in a classroom layout, and Koregaon Studio seats up to 35. For 45 people, Riverside Hall works in a theatre layout, which seats up to 60. For a classroom layout above 40 people, the Events Desk arranges an external venue on request.',
      },
      {
        id: 'Doc_12§3',
        section: '§3',
        title: 'Technical equipment',
        text: 'Both Pune facilities feature 4K dual displays, wireless presentation dongles, clip-on microphones, and acoustic boundary ceiling mics. Dedicated AV technician support is provided during business hours.',
      },
    ],
  },
  {
    id: 'Doc_31',
    title: 'Event Cancellation and Refund Policy',
    sectionsCount: 4,
    summary: 'Standard cancellation timelines, refund schedule, and exceptions for corporate events.',
    chunks: [
      {
        id: 'Doc_31§2',
        section: '§2',
        title: 'Notice periods',
        text: 'Cancellations must be submitted through the Events Desk portal. A cancellation made 14 or more calendar days before the event date is a standard cancellation with a full refund of the venue fee.',
      },
      {
        id: 'Doc_31§4',
        section: '§4',
        title: 'Refund terms',
        text: 'Later cancellations received between 13 calendar days and 48 hours prior to the event date receive a 50% refund. Cancellations submitted within 48 hours of the event start time receive zero refund.',
      },
    ],
  },
  {
    id: 'Doc_89',
    title: 'Catering Options for Events',
    sectionsCount: 3,
    summary: 'Internal cafeteria menus, external approved vendors, and dietary request lead times.',
    chunks: [
      {
        id: 'Doc_89§1',
        section: '§1',
        title: 'On-site catering',
        text: 'Koregaon Studio has in-house catering with vegetarian and non-vegetarian menus, charged per person and confirmed 5 working days ahead. Tea and coffee stations with morning snacks are provided continuously.',
      },
      {
        id: 'Doc_89§2',
        section: '§2',
        title: 'External caterers',
        text: 'You can also book an approved external caterer from the Veloria vendor roster for specialized cuisines. Outside catering arrangements must be submitted at least 7 days in advance.',
      },
    ],
  },
  {
    id: 'Doc_05',
    title: 'Travel Reimbursement Policy',
    sectionsCount: 4,
    summary: 'Allowable expenses, domestic and international per diem limits, and travel receipt rules.',
    chunks: [
      {
        id: 'Doc_05§1',
        section: '§1',
        title: 'Domestic travel guidelines',
        text: 'Employees traveling on company business within the country are eligible for standard economy airfare or train transit, reasonable lodging, and daily meal per diems as specified in the rate schedule.',
      },
      {
        id: 'Doc_05§3',
        section: '§3',
        title: 'Receipts and claim submissions',
        text: 'All expense reimbursement claims must be submitted via the finance portal within 30 days of trip completion. Itemized receipts are mandatory for all lodging and single expenses exceeding $25.',
      },
    ],
  },
];

export const CorpusTab: React.FC = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedDocId, setSelectedDocId] = useState('Doc_12');

  const selectedDoc = CORPUS_DOCS.find((d) => d.id === selectedDocId) || CORPUS_DOCS[0];

  const filteredChunks = selectedDoc.chunks.filter((c) => {
    if (!searchTerm) return true;
    const term = searchTerm.toLowerCase();
    return c.text.toLowerCase().includes(term) || c.title.toLowerCase().includes(term);
  });

  return (
    <div className="space-y-6">
      {/* Title */}
      <div>
        <div className="text-xs text-[#7D8594] font-mono">SUPPLIED CORPUS REPOSITORY · READ-ONLY ISOLATION</div>
        <h2 className="text-xl sm:text-2xl font-bold text-[#ECE9E2] mt-1 tracking-tight">
          Corpus Explorer & Provenance Inspector
        </h2>
      </div>

      {/* Search Bar */}
      <div className="relative">
        <Search className="w-4 h-4 text-[#7D8594] absolute left-3.5 top-1/2 -translate-y-1/2" />
        <input
          type="text"
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          placeholder="Filter corpus chunks by keyword (e.g. capacity, refund, catering)..."
          className="w-full bg-[#15181E] border border-[#1E2330] rounded-xl pl-10 pr-4 py-2.5 text-xs text-[#ECE9E2] placeholder-[#7D8594] focus:outline-none focus:border-[#282D3A]"
        />
      </div>

      {/* 2-Column Explorer: Doc List + Chunk Viewer */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Document List */}
        <div className="space-y-2">
          <div className="text-xs font-mono uppercase text-[#7D8594] px-1">Corpus Documents</div>
          {CORPUS_DOCS.map((doc) => {
            const isSelected = doc.id === selectedDocId;

            return (
              <button
                key={doc.id}
                onClick={() => setSelectedDocId(doc.id)}
                className={`w-full text-left p-3.5 rounded-xl border transition-all ${
                  isSelected
                    ? 'bg-[#1C2028] border-[#8FB3FF]/40 shadow-sm'
                    : 'bg-[#15181E] border-[#1E2330] hover:border-[#282D3A]'
                }`}
              >
                <div className="flex items-center justify-between text-xs">
                  <span className="font-mono font-bold text-[#8FB3FF]">{doc.id}</span>
                  <span className="text-[11px] font-mono text-[#7D8594]">{doc.sectionsCount} sections</span>
                </div>
                <div className="text-xs font-medium text-[#ECE9E2] mt-1 truncate">{doc.title}</div>
                <p className="text-[11px] text-[#7D8594] line-clamp-2 mt-1 leading-relaxed">
                  {doc.summary}
                </p>
              </button>
            );
          })}
        </div>

        {/* Chunk Content Viewer */}
        <div className="lg:col-span-2 space-y-3">
          <div className="flex items-center justify-between text-xs px-1">
            <span className="font-mono uppercase text-[#7D8594]">
              {selectedDoc.id} Sections ({filteredChunks.length} matching)
            </span>
            <span className="text-[11px] font-mono text-[#6FD39A] flex items-center gap-1">
              <CheckCircle2 className="w-3.5 h-3.5" /> SHA-256 Manifest Verified
            </span>
          </div>

          <div className="space-y-3">
            {filteredChunks.map((chunk) => (
              <div
                key={chunk.id}
                className="bg-[#15181E] border border-[#1E2330] rounded-2xl p-5 space-y-2"
              >
                <div className="flex items-center justify-between text-xs">
                  <span className="font-mono font-bold text-[#8FB3FF]">
                    {chunk.id} · {chunk.title}
                  </span>
                  <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-[#1C2028] text-[#7D8594] border border-[#282D3A]">
                    {chunk.text.split(' ').length} words
                  </span>
                </div>

                <p className="text-xs font-serif leading-relaxed text-[#ECE9E2] pt-1">
                  {chunk.text}
                </p>

                <div className="pt-2 border-t border-[#1E2330] flex items-center justify-between text-[11px] font-mono text-[#7D8594]">
                  <span className="flex items-center gap-1">
                    <Shield className="w-3 h-3 text-[#6FD39A]" /> Untrusted Corpus Tag Enclosed
                  </span>
                  <span>Isolation: PASS</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};
