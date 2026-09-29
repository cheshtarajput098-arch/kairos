import { SessionInfo, StreamEvent } from './types';

const API_BASE = window.location.origin;

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
    const host = window.location.host;
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
