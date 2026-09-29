import React, { useEffect, useState, useRef } from 'react';
import { Sidebar, NavTab } from './components/Sidebar';
import { TopBar } from './components/TopBar';
import { StoryBar } from './components/StoryBar';
import { HomeScreen } from './components/HomeScreen';
import { ConversationScreen } from './components/ConversationScreen';
import { KnowledgeSourcesScreen } from './components/KnowledgeSourcesScreen';
import { TracesScreen } from './components/TracesScreen';
import { InspectorMode } from './components/InspectorMode';
import { SettingsSheet } from './components/SettingsSheet';
import { SCENARIOS } from './components/StoryMode';
import {
  createSession,
  getSuggestions,
  sendFeedback,
  executePresentationTurn,
  KairosStreamClient,
} from './api';
import {
  ClaimObject,
  ControllerDecisionEvent,
  LegInfo,
  SessionInfo,
  StreamEvent,
  VersionDiff,
} from './types';

export const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState<NavTab>('ask');
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [status, setStatus] = useState<'connected' | 'connecting' | 'closed' | 'error'>('connecting');

  // Session authentication & API
  const [session, setSession] = useState<SessionInfo | null>(null);

  // Settings state
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);
  const [showDraftsWhileSpeaking, setShowDraftsWhileSpeaking] = useState(true);
  const [textSize, setTextSize] = useState<'normal' | 'large' | 'xlarge'>('normal');

  // Suggested questions from index headings
  const [suggestions, setSuggestions] = useState<string[]>([]);

  // Live session state
  const [transcript, setTranscript] = useState('');
  const [isSearching, setIsSearching] = useState(false);
  const [isDrafting, setIsDrafting] = useState(false);
  const [decisions, setDecisions] = useState<ControllerDecisionEvent[]>([]);
  const [legs, setLegs] = useState<LegInfo[]>([]);
  const [drafts, setDrafts] = useState<Record<string, ClaimObject>>({});
  const [finalAnswer, setFinalAnswer] = useState('');
  const [finalClaims, setFinalClaims] = useState<ClaimObject[]>([]);
  const [citations, setCitations] = useState<string[]>([]);
  const [version, setVersion] = useState(1);
  const [diff, setDiff] = useState<VersionDiff | undefined>();
  const [readyAtEnd, setReadyAtEnd] = useState<number | undefined>();
  const [readyCount, setReadyCount] = useState<number | undefined>();
  const [totalParts, setTotalParts] = useState<number | undefined>();
  const [firstRetrievalT, setFirstRetrievalT] = useState<number | null>(null);
  const [utteranceEndT, setUtteranceEndT] = useState<number | null>(null);
  const [currentTime, setCurrentTime] = useState(0);
  const [events, setEvents] = useState<StreamEvent[]>([]);

  // Story mode & Turn Metadata
  const [isStoryActive, setIsStoryActive] = useState(false);
  const [currentScenarioIndex, setCurrentScenarioIndex] = useState(0);
  const [isPlayingStory, setIsPlayingStory] = useState(false);
  const [isSpokenTurn, setIsSpokenTurn] = useState(false);
  const [turnType, setTurnType] = useState<string>('standard');

  const clientRef = useRef<KairosStreamClient | null>(null);
  const storyTimerRef = useRef<number[]>([]);

  // Fetch suggested questions from index headings on mount & parse direct navigation params
  useEffect(() => {
    getSuggestions().then((items) => {
      if (items.length > 0) {
        setSuggestions(items);
      }
    });

    const params = new URLSearchParams(window.location.search);
    const tabParam = params.get('tab');
    if (tabParam && ['ask', 'sources', 'traces', 'evaluation'].includes(tabParam)) {
      setActiveTab(tabParam as NavTab);
    }

    if (params.get('mode') === 'conversation' || tabParam === 'conversation') {
      setActiveTab('ask');
      setTranscript(
        'Plan a customer workshop in Pune for 30 attendees, with cancellation policy and catering options.'
      );
      setLegs([
        { leg_id: 'l1', text: 'Venue for 30 people', first_dispatch_s: 0.8 },
        { leg_id: 'l2', text: 'Cancellation terms', first_dispatch_s: 1.6 },
        { leg_id: 'l3', text: 'Catering', first_dispatch_s: 1.6 },
      ]);
      setFinalAnswer(
        'Both approved Pune venues fit your group: Riverside Hall in Baner seats up to 40 in a classroom layout, and Koregaon Studio seats up to 35. Cancelling 14 or more days before the event is a standard cancellation with a full refund of the venue fee. Later cancellations get 50% back, and nothing is refunded within 48 hours. Koregaon Studio offers in-house catering, charged per person and confirmed 5 working days ahead. You can also use an approved external caterer.'
      );
      setFinalClaims([
        {
          claim_id: 'c1',
          leg_id: 'l1',
          text: 'Both approved Pune venues fit your group: Riverside Hall in Baner seats up to 40 in a classroom layout, and Koregaon Studio seats up to 35.',
          citations: ['Doc_12§2'],
          evidence_span:
            'Riverside Hall in Baner seats up to 40 people in a classroom layout, and Koregaon Studio seats up to 35',
          status: 'verified',
          version: 1,
        },
        {
          claim_id: 'c2',
          leg_id: 'l2',
          text: 'Cancelling 14 or more days before the event is a standard cancellation with a full refund of the venue fee.',
          citations: ['Doc_31§2'],
          evidence_span:
            'A cancellation made 14 or more calendar days before the event date is a standard cancellation with a full refund of the venue fee',
          status: 'verified',
          version: 1,
        },
        {
          claim_id: 'c3',
          leg_id: 'l2',
          text: 'Later cancellations get 50% back, and nothing is refunded within 48 hours.',
          citations: ['Doc_31§4'],
          evidence_span:
            'Later cancellations receive a 50 percent refund of the venue fee. Cancellations made fewer than 48 hours before the event are not refunded',
          status: 'verified',
          version: 1,
        },
        {
          claim_id: 'c4',
          leg_id: 'l3',
          text: 'Koregaon Studio offers in-house catering, charged per person and confirmed 5 working days ahead.',
          citations: ['Doc_89§1'],
          evidence_span:
            'Koregaon Studio offers in-house catering, charged per person and confirmed 5 working days ahead',
          status: 'verified',
          version: 1,
        },
        {
          claim_id: 'c5',
          leg_id: 'l3',
          text: 'You can also use an approved external caterer.',
          citations: ['Doc_89§2'],
          evidence_span: 'You can also use an approved external caterer',
          status: 'verified',
          version: 1,
        },
      ]);
      setCitations(['Doc_12§2', 'Doc_31§2', 'Doc_31§4', 'Doc_89§1', 'Doc_89§2']);
      setReadyAtEnd(1);
      setReadyCount(2);
      setTotalParts(3);
    } else if (params.get('mid_answer') === 'true') {
      setActiveTab('ask');
      setTranscript(
        'Plan a customer workshop in Pune for 30 attendees, with cancellation policy and catering'
      );
      setIsSearching(true);
      setIsDrafting(true);
      setCurrentTime(1.6);
      setLegs([
        { leg_id: 'l1', text: 'Venue for 30 people', first_dispatch_s: 0.8 },
        { leg_id: 'l2', text: 'Cancellation terms', first_dispatch_s: 1.6 },
      ]);
      setDrafts({
        l1: {
          claim_id: 'c1',
          leg_id: 'l1',
          text: 'Both approved Pune venues fit your group: Riverside Hall in Baner seats up to 40 people in a classroom layout, and Koregaon Studio seats up to 35.',
          citations: ['Doc_12§2'],
          evidence_span: 'Riverside Hall in Baner seats up to 40 people',
          status: 'verified',
          version: 1,
        },
      });
      setCitations(['Doc_12§2']);
    }
  }, []);

  // Global Keyboard Shortcuts (Space talk, I toggle Evaluation, Esc close)
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      const activeTag = (document.activeElement?.tagName || '').toLowerCase();
      const isInput = activeTag === 'input' || activeTag === 'textarea';

      if (e.key === ' ' && !isInput) {
        e.preventDefault();
        setIsSearching((prev) => !prev);
      } else if (e.key.toLowerCase() === 'i' && !isInput) {
        e.preventDefault();
        setActiveTab((prev) => (prev === 'evaluation' ? 'ask' : 'evaluation'));
      } else if (e.key === 'Escape') {
        setIsSettingsOpen(false);
        setIsMobileMenuOpen(false);
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  // Initialize session & WebSocket
  const initSession = () => {
    setStatus('connecting');
    createSession()
      .then((sess) => {
        setSession(sess);
        const client = new KairosStreamClient(sess, handleIncomingEvent, setStatus);
        client.connect();
        clientRef.current = client;
      })
      .catch((err) => {
        console.error('Session initialization error:', err);
        setStatus('error');
      });
  };

  useEffect(() => {
    initSession();
    return () => {
      if (clientRef.current) {
        clientRef.current.disconnect();
      }
    };
  }, []);

  // Handle incoming stream events from WebSocket
  const handleIncomingEvent = (event: StreamEvent) => {
    setEvents((prev) => [...prev, event]);

    switch (event.event) {
      case 'controller_decision':
        setDecisions((prev) => [...prev, event]);
        if (event.decision === 'RETRIEVE') {
          setIsSearching(true);
          setIsDrafting(true);
          if (firstRetrievalT === null) {
            setFirstRetrievalT(event.t);
          }
        }
        break;

      case 'subqueries_updated':
        setLegs(event.legs);
        break;

      case 'draft_verified':
        setDrafts((prev) => ({ ...prev, [event.leg_id]: event.claim }));
        break;

      case 'turn_completed':
        setIsSearching(false);
        setIsDrafting(false);
        setFinalAnswer(event.answer);
        setVersion(event.version);
        setCitations(event.citations);
        if (event.claims) {
          setFinalClaims(event.claims);
        }
        if (event.diff) {
          setDiff(event.diff);
        }
        if (event.metrics) {
          if (event.metrics.ready_at_end !== undefined) {
            setReadyAtEnd(event.metrics.ready_at_end);
          }
          if (event.metrics.ready_count !== undefined) {
            setReadyCount(event.metrics.ready_count);
          }
          if (event.metrics.total_parts !== undefined) {
            setTotalParts(event.metrics.total_parts);
          }
        }
        break;

      case 'speed2_completed':
        setFinalAnswer(event.answer);
        setVersion(event.version);
        setCitations(event.citations);
        if (event.claims) {
          setFinalClaims(event.claims);
        }
        break;
    }
  };

  // Reset to empty home screen
  const handleNewQuestion = () => {
    clearStoryTimers();
    setIsStoryActive(false);
    setIsPlayingStory(false);
    setIsSpokenTurn(false);
    setTurnType('standard');
    setTranscript('');
    setDecisions([]);
    setLegs([]);
    setDrafts({});
    setFinalAnswer('');
    setFinalClaims([]);
    setCitations([]);
    setDiff(undefined);
    setVersion(1);
    setCurrentTime(0);
    setActiveTab('ask');
  };

  // Play a demo scenario through the real WebSocket stream
  const playScenario = (index: number) => {
    clearStoryTimers();
    const scenario = SCENARIOS[index];
    if (!scenario || !clientRef.current) return;

    setActiveTab('ask');
    setCurrentScenarioIndex(index);
    setIsPlayingStory(true);
    setIsStoryActive(true);
    setIsSpokenTurn(true);
    setTurnType('standard');

    if (index === 0) {
      setVersion(1);
      setDiff(undefined);
    }

    setTranscript('');
    setDecisions([]);
    setLegs([]);
    setDrafts({});
    setFinalAnswer('');
    setFinalClaims([]);
    setReadyAtEnd(undefined);
    setReadyCount(undefined);
    setTotalParts(undefined);
    setFirstRetrievalT(null);
    setUtteranceEndT(scenario.utteranceEnd);
    setCurrentTime(0);

    let runningText = '';
    scenario.chunks.forEach((chunk, i) => {
      const isLast = i === scenario.chunks.length - 1;
      const delayMs = chunk.t * 1000;

      const timerId = window.setTimeout(() => {
        runningText = runningText ? `${runningText} ${chunk.text}` : chunk.text;
        setTranscript(runningText);
        setCurrentTime(chunk.t);
        clientRef.current?.sendChunk(chunk.t, chunk.text, isLast);

        if (isLast) {
          setIsPlayingStory(false);
        }
      }, delayMs);

      storyTimerRef.current.push(timerId);
    });
  };

  const clearStoryTimers = () => {
    storyTimerRef.current.forEach((id) => clearTimeout(id));
    storyTimerRef.current = [];
  };

  const handleSendText = (text: string, isSpoken: boolean = false) => {
    if (!clientRef.current) return;
    setIsSpokenTurn(isSpoken);
    setTurnType('standard');
    setActiveTab('ask');
    setTranscript(text);
    setFinalAnswer('');
    setFinalClaims([]);
    setUtteranceEndT(2.0);
    clientRef.current.sendChunk(0.0, text, true);
  };

  const handleQuickAction = async (action: 'shorter' | 'bullets' | 'simple') => {
    if (!session) return;
    setTurnType('presentation_only');
    try {
      const result = await executePresentationTurn(session.session_id, session.token, action);
      if (result && 'answer' in result) {
        setFinalAnswer(result.answer as string);
        if ('claims' in result && Array.isArray(result.claims)) {
          setFinalClaims(result.claims as ClaimObject[]);
        }
      }
    } catch (err) {
      console.debug('Presentation turn failed:', err);
    }
  };

  const handleFeedback = (rating: 'up' | 'down') => {
    if (session) {
      sendFeedback(session.session_id, version, rating);
    }
  };

  // Determine if in conversation or home view under 'ask'
  const isConversation = Boolean(transcript || finalAnswer || Object.keys(drafts).length > 0 || isStoryActive);
  const currentScenario = SCENARIOS[currentScenarioIndex] || SCENARIOS[0];

  const questionTitle = transcript
    ? transcript.slice(0, 36) + (transcript.length > 36 ? '…' : '')
    : 'Pune workshop for 30 people';

  return (
    <div className="min-h-screen flex bg-[#0E1014] text-[#ECE9E2] font-sans antialiased overflow-x-hidden">
      {/* 248px Left Navigation Menu (Board 6–9 App Shell) */}
      <Sidebar
        activeTab={activeTab}
        onTabChange={setActiveTab}
        onNewQuestion={handleNewQuestion}
        onSelectRecent={(idx) => playScenario(idx)}
        isOpenMobile={isMobileMenuOpen}
        onCloseMobile={() => setIsMobileMenuOpen(false)}
      />

      {/* Main Right Area: 64px TopBar + Main Views */}
      <div className="flex-1 flex flex-col min-w-0 min-h-screen">
        {/* 64px Top Bar */}
        <TopBar
          activeTab={activeTab}
          isConversation={isConversation}
          questionTitle={questionTitle}
          onOpenMobileMenu={() => setIsMobileMenuOpen(true)}
          onPlayDemo={() => playScenario(0)}
          onOpenSettings={() => setIsSettingsOpen(true)}
          status={status}
        />

        {/* Settings Sheet Modal */}
        <SettingsSheet
          isOpen={isSettingsOpen}
          onClose={() => setIsSettingsOpen(false)}
          showDraftsWhileSpeaking={showDraftsWhileSpeaking}
          onToggleDraftsWhileSpeaking={setShowDraftsWhileSpeaking}
          textSize={textSize}
          onChangeTextSize={setTextSize}
        />

        {/* Slim Story Mode Bar if active */}
        {isStoryActive && (
          <StoryBar
            currentScenarioIndex={currentScenarioIndex}
            totalScenarios={SCENARIOS.length}
            title={currentScenario.title}
            description={currentScenario.caption}
            isPlaying={isPlayingStory}
            onPause={() => {
              clearStoryTimers();
              setIsPlayingStory(false);
            }}
            onResume={() => playScenario(currentScenarioIndex)}
            onNext={() => playScenario((currentScenarioIndex + 1) % SCENARIOS.length)}
            onExit={() => {
              clearStoryTimers();
              setIsStoryActive(false);
              setIsPlayingStory(false);
            }}
          />
        )}

        {/* Main Content View Switcher */}
        <main className="flex-1 overflow-y-auto">
          {activeTab === 'ask' && !isConversation && (
            <HomeScreen
              onSendQuestion={(text, spoken) => handleSendText(text, Boolean(spoken))}
              onPlayScenario={playScenario}
              isListening={isSearching}
              onToggleMic={() => setIsSearching((prev) => !prev)}
            />
          )}

          {activeTab === 'ask' && isConversation && (
            <ConversationScreen
              transcript={transcript}
              isSearching={isSearching}
              legs={legs}
              drafts={drafts}
              finalAnswer={finalAnswer}
              finalClaims={finalClaims}
              citations={citations}
              version={version}
              diff={diff}
              readyAtEnd={readyAtEnd}
              readyCount={readyCount}
              totalParts={totalParts}
              isDrafting={isDrafting}
              currentTime={currentTime}
              suggestions={suggestions}
              isSpoken={isSpokenTurn}
              turnType={turnType}
              onSendText={(text) => handleSendText(text, false)}
              onQuickAction={handleQuickAction}
              onSeeDiff={() => setActiveTab('evaluation')}
              onFeedback={handleFeedback}
              onViewTrace={() => setActiveTab('traces')}
              textSize={textSize}
              showProvisionalDrafts={showDraftsWhileSpeaking}
            />
          )}

          {activeTab === 'sources' && <KnowledgeSourcesScreen />}

          {activeTab === 'traces' && (
            <TracesScreen
              questionTitle={questionTitle}
              turnId={`turn s${currentScenarioIndex + 1}-t${version}`}
              onBackToConversation={() => setActiveTab('ask')}
              events={events}
            />
          )}

          {activeTab === 'evaluation' && (
            <div className="max-w-[1280px] w-full mx-auto px-6 py-8">
              <InspectorMode
                decisions={decisions}
                legs={legs}
                firstRetrievalT={firstRetrievalT}
                utteranceEndT={utteranceEndT}
                currentTime={currentTime}
                events={events}
                readyAtEnd={readyAtEnd}
                finalAnswer={finalAnswer}
                finalClaims={finalClaims}
                citations={citations}
                version={version}
                diff={diff}
              />
            </div>
          )}
        </main>
      </div>
    </div>
  );
};
