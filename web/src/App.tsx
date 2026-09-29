import React, { useEffect, useState, useRef } from 'react';
import { Header } from './components/Header';
import { StoryBar } from './components/StoryBar';
import { AssistantMode } from './components/AssistantMode';
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
  const [mode, setMode] = useState<'assistant' | 'inspector'>('assistant');
  const [status, setStatus] = useState<'connected' | 'connecting' | 'closed' | 'error'>('connecting');

  // Session authentication & API
  const [session, setSession] = useState<SessionInfo | null>(null);

  // Settings state (Item 8)
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);
  const [showDraftsWhileSpeaking, setShowDraftsWhileSpeaking] = useState(true);
  const [textSize, setTextSize] = useState<'normal' | 'large' | 'xlarge'>('normal');

  // Suggested questions from index headings (Item 6)
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

  // Status & error banners (Item 7)
  const [micPermissionDenied, setMicPermissionDenied] = useState(false);
  const [rateLimitError, setRateLimitError] = useState<{ message: string; requestId: string } | null>(null);
  const [outOfScopeError, setOutOfScopeError] = useState<{ message: string; requestId: string } | null>(null);
  const [generalError, setGeneralError] = useState<{ code: string; message: string; requestId: string } | null>(null);

  // Story mode
  const [isStoryActive, setIsStoryActive] = useState(false);
  const [currentScenarioIndex, setCurrentScenarioIndex] = useState(0);
  const [isPlayingStory, setIsPlayingStory] = useState(false);

  const clientRef = useRef<KairosStreamClient | null>(null);
  const storyTimerRef = useRef<number[]>([]);
  const inputRef = useRef<HTMLInputElement>(null);

  // Fetch suggested questions from index headings on mount
  useEffect(() => {
    getSuggestions().then((items) => {
      if (items.length > 0) {
        setSuggestions(items);
      }
    });
  }, []);

  // Global Keyboard Shortcuts (Item 11: Space talk/stop, / focus, I toggle Inspector, Esc close)
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      const activeTag = (document.activeElement?.tagName || '').toLowerCase();
      const isInput = activeTag === 'input' || activeTag === 'textarea';

      if (e.key === ' ' && !isInput) {
        e.preventDefault();
        setIsSearching((prev) => !prev);
      } else if (e.key === '/' && !isInput) {
        e.preventDefault();
        inputRef.current?.focus();
      } else if (e.key.toLowerCase() === 'i' && !isInput) {
        e.preventDefault();
        setMode((prev) => (prev === 'assistant' ? 'inspector' : 'assistant'));
      } else if (e.key === 'Escape') {
        setIsSettingsOpen(false);
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  // Initialize session & WebSocket
  const initSession = () => {
    setStatus('connecting');
    setGeneralError(null);
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
        setGeneralError({
          code: 'SESSION_INIT_FAILED',
          message: 'Failed to establish session with engine.',
          requestId: `err_${Date.now().toString(36)}`,
        });
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
        if (event.turn_type === 'out_of_corpus') {
          setOutOfScopeError({
            message: event.answer,
            requestId: `turn_${event.version}_${Date.now().toString(36)}`,
          });
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

  // Play a demo scenario through the real WebSocket stream
  const playScenario = (index: number) => {
    clearStoryTimers();
    const scenario = SCENARIOS[index];
    if (!scenario || !clientRef.current) return;

    setCurrentScenarioIndex(index);
    setIsPlayingStory(true);
    setIsStoryActive(true);

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

  const handleSendText = (text: string) => {
    if (!clientRef.current) return;
    setTranscript(text);
    setFinalAnswer('');
    setFinalClaims([]);
    setOutOfScopeError(null);
    setRateLimitError(null);
    setUtteranceEndT(2.0);
    clientRef.current.sendChunk(0.0, text, true);
  };

  // Item 2: Quick actions run as presentation-only turns with zero searches
  const handleQuickAction = async (action: 'shorter' | 'bullets' | 'simple') => {
    if (!session) return;
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

  // Item 9: Thumbs up/down per answer, kept in session telemetry only
  const handleFeedback = (rating: 'up' | 'down') => {
    if (session) {
      sendFeedback(session.session_id, version, rating);
    }
  };

  const currentScenario = SCENARIOS[currentScenarioIndex] || SCENARIOS[0];

  return (
    <div className="min-h-screen flex flex-col font-sans bg-[#0E1014] text-[#ECE9E2]">
      {/* Top Header */}
      <Header
        mode={mode}
        onModeChange={setMode}
        onPlayDemo={() => playScenario(0)}
        status={status}
        isStoryActive={isStoryActive}
        onOpenSettings={() => setIsSettingsOpen(true)}
      />

      {/* Settings Sheet (Item 8) */}
      <SettingsSheet
        isOpen={isSettingsOpen}
        onClose={() => setIsSettingsOpen(false)}
        showDraftsWhileSpeaking={showDraftsWhileSpeaking}
        onToggleDraftsWhileSpeaking={setShowDraftsWhileSpeaking}
        textSize={textSize}
        onChangeTextSize={setTextSize}
      />

      {/* Slim 56px Story Mode Top Bar if active */}
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

      {/* Main Content Area */}
      <main className="flex-1 max-w-[1280px] w-full mx-auto px-6 py-8">
        {mode === 'assistant' ? (
          <AssistantMode
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
            onSendText={handleSendText}
            onQuickAction={handleQuickAction}
            onSeeDiff={() => setMode('inspector')}
            onFeedback={handleFeedback}
            connectionStatus={status}
            onRetryConnection={initSession}
            micPermissionDenied={micPermissionDenied}
            onTypeInstead={() => setMicPermissionDenied(false)}
            rateLimitError={rateLimitError}
            outOfScopeError={outOfScopeError}
            generalError={generalError}
            textSize={textSize}
            showProvisionalDrafts={showDraftsWhileSpeaking}
            inputRef={inputRef}
          />
        ) : (
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
        )}
      </main>
    </div>
  );
};
