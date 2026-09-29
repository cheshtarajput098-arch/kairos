import { SessionInfo, StreamEvent } from './types';

const isDevPort =
  typeof window !== 'undefined' &&
  (window.location.port === '5173' || window.location.port === '3000');

export const API_BASE = isDevPort
  ? 'http://localhost:8000'
  : typeof window !== 'undefined'
  ? window.location.origin
  : 'http://localhost:8000';

export async function createSession(): Promise<SessionInfo> {
  const res = await fetch(`${API_BASE}/v1/sessions`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
  });
  if (!res.ok) {
    throw new Error(`Failed to create session: ${res.statusText}`);
  }
  return res.json();
}

export async function getSuggestions(): Promise<string[]> {
  try {
    const res = await fetch(`${API_BASE}/v1/suggestions`);
    if (!res.ok) return [];
    const data = await res.json();
    return data.suggestions || [];
  } catch {
    return [];
  }
}

export interface ApiCorpusDoc {
  id: string;
  title: string;
  sections_count: number;
  summary: string;
  chunks: {
    id: string;
    section: string;
    title: string;
    text: string;
    flagged?: boolean;
  }[];
}

export interface ApiCorpusResponse {
  documents: ApiCorpusDoc[];
  total_chunks: number;
}

export async function getCorpusDocs(): Promise<ApiCorpusResponse | null> {
  try {
    const res = await fetch(`${API_BASE}/v1/corpus/docs`);
    if (!res.ok) return null;
    return await res.json();
  } catch {
    return null;
  }
}

export async function sendFeedback(
  sessionId: string,
  version: number,
  rating: 'up' | 'down'
): Promise<void> {
  try {
    await fetch(`${API_BASE}/v1/telemetry/feedback`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ session_id: sessionId, version, rating }),
    });
  } catch (err) {
    console.debug('Failed to send telemetry feedback:', err);
  }
}

export async function executePresentationTurn(
  sessionId: string,
  token: string,
  action: 'shorter' | 'bullets' | 'simple'
): Promise<StreamEvent> {
  const res = await fetch(`${API_BASE}/v1/turns/presentation`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ session_id: sessionId, token, action }),
  });
  if (!res.ok) {
    throw new Error(`Presentation turn failed: ${res.statusText}`);
  }
  return res.json();
}

export class KairosStreamClient {
  private ws: WebSocket | null = null;
  private session: SessionInfo;
  private onEventCallback: (event: StreamEvent) => void;
  private onStatusChangeCallback: (status: 'connected' | 'connecting' | 'closed' | 'error') => void;

  constructor(
    session: SessionInfo,
    onEvent: (event: StreamEvent) => void,
    onStatusChange: (status: 'connected' | 'connecting' | 'closed' | 'error') => void
  ) {
    this.session = session;
    this.onEventCallback = onEvent;
    this.onStatusChangeCallback = onStatusChange;
  }

  public connect(): void {
    const proto = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const host = isDevPort ? 'localhost:8000' : window.location.host;
    const url = `${proto}//${host}/v1/stream?session_id=${encodeURIComponent(
      this.session.session_id
    )}&token=${encodeURIComponent(this.session.token)}`;

    this.onStatusChangeCallback('connecting');
    this.ws = new WebSocket(url);

    this.ws.onopen = () => {
      this.onStatusChangeCallback('connected');
    };

    this.ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        this.onEventCallback(data);
      } catch (err) {
        console.error('Failed to parse WebSocket message:', err);
      }
    };

    this.ws.onerror = () => {
      this.onStatusChangeCallback('error');
    };

    this.ws.onclose = () => {
      this.onStatusChangeCallback('closed');
    };
  }

  public sendChunk(t: number, text: string, isFinal: boolean = false): void {
    if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
      console.warn('Cannot send chunk: WebSocket is not open');
      return;
    }
    const payload = JSON.stringify({ t, text, is_final: isFinal });
    this.ws.send(payload);
  }

  public disconnect(): void {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }
}
