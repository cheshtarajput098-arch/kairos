import React, { useState } from 'react';
import { TimelineTab } from './inspector/TimelineTab';
import { RaceTab } from './inspector/RaceTab';
import { ResultsTab } from './inspector/ResultsTab';
import { CorpusTab } from './inspector/CorpusTab';
import { PlaygroundTab } from './inspector/PlaygroundTab';
import { AboutTab } from './inspector/AboutTab';
import { ClaimObject, ControllerDecisionEvent, LegInfo, StreamEvent, VersionDiff } from '../types';

interface InspectorModeProps {
  decisions: ControllerDecisionEvent[];
  legs: LegInfo[];
  firstRetrievalT: number | null;
  utteranceEndT: number | null;
  currentTime: number;
  events: StreamEvent[];
  readyAtEnd?: number;
  finalAnswer: string;
  finalClaims: ClaimObject[];
  citations: string[];
  version: number;
  diff?: VersionDiff;
}

type TabType = 'timeline' | 'race' | 'results' | 'corpus' | 'playground' | 'about';

export const InspectorMode: React.FC<InspectorModeProps> = ({
  decisions,
  legs,
  firstRetrievalT,
  utteranceEndT,
  currentTime,
  events,
  readyAtEnd,
  finalClaims,
}) => {
  const [activeTab, setActiveTab] = useState<TabType>('timeline');

  const tabs: { id: TabType; label: string }[] = [
    { id: 'timeline', label: 'Timeline' },
    { id: 'race', label: 'Race vs. batch' },
    { id: 'results', label: 'Results' },
    { id: 'corpus', label: 'Corpus' },
    { id: 'playground', label: 'Try it yourself' },
    { id: 'about', label: 'About & Core vs. harness' },
  ];

  return (
    <div className="space-y-6">
      {/* Sub-tab navigation bar (Board 4) */}
      <div className="flex items-center gap-6 border-b border-[#1E2330] pb-2 text-sm overflow-x-auto">
        {tabs.map((t) => {
          const isActive = activeTab === t.id;

          return (
            <button
              key={t.id}
              onClick={() => setActiveTab(t.id)}
              className={`pb-2.5 font-medium transition-all relative whitespace-nowrap ${
                isActive
                  ? 'text-[#ECE9E2] font-semibold'
                  : 'text-[#7D8594] hover:text-[#A3A9B5]'
              }`}
            >
              <span>{t.label}</span>
              {isActive && (
                <span className="absolute bottom-0 left-0 right-0 h-0.5 bg-[#8FB3FF] rounded-full" />
              )}
            </button>
          );
        })}
      </div>

      {/* Active Tab View */}
      {activeTab === 'timeline' && (
        <TimelineTab
          decisions={decisions}
          legs={legs}
          firstRetrievalT={firstRetrievalT}
          utteranceEndT={utteranceEndT}
          currentTime={currentTime}
          events={events}
          readyAtEnd={readyAtEnd}
          finalClaims={finalClaims}
        />
      )}

      {activeTab === 'race' && <RaceTab />}

      {activeTab === 'results' && <ResultsTab />}

      {activeTab === 'corpus' && <CorpusTab />}

      {activeTab === 'playground' && <PlaygroundTab />}

      {activeTab === 'about' && <AboutTab />}
    </div>
  );
};
