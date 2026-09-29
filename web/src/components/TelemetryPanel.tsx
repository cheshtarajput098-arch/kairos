import React, { useState } from 'react';
import { Copy, Check, ExternalLink, Activity } from 'lucide-react';
import { StreamEvent } from '../types';

interface TelemetryPanelProps {
  events: StreamEvent[];
  readyAtEnd?: number;
  retrievalsCount: number;
}

export const TelemetryPanel: React.FC<TelemetryPanelProps> = ({
  events,
  readyAtEnd,
  retrievalsCount,
}) => {
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(JSON.stringify(events, null, 2));
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-5 shadow-sm space-y-4">
      <div className="flex items-center justify-between border-b border-slate-100 dark:border-slate-800 pb-2">
        <div className="flex items-center gap-2">
          <Activity className="w-4 h-4 text-blue-500" />
          <span className="text-xs font-mono font-bold uppercase text-slate-800 dark:text-slate-200">
            Live Telemetry & Event Log
          </span>
        </div>

        <div className="flex items-center gap-3">
          <a
            href="http://localhost:16686"
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-1 text-[11px] font-mono text-blue-600 dark:text-blue-400 hover:underline"
          >
            <span>Jaeger UI</span>
            <ExternalLink className="w-3 h-3" />
          </a>

          <button
            onClick={handleCopy}
            className="inline-flex items-center gap-1 px-2.5 py-1 text-[11px] font-mono rounded bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 text-slate-600 dark:text-slate-300 transition-colors"
          >
            {copied ? <Check className="w-3 h-3 text-emerald-500" /> : <Copy className="w-3 h-3" />}
            <span>{copied ? 'Copied' : 'Copy JSON'}</span>
          </button>
        </div>
      </div>

      {/* Metrics Row */}
      <div className="grid grid-cols-3 gap-3">
        <div className="p-3 bg-slate-50 dark:bg-slate-850 rounded-xl border border-slate-100 dark:border-slate-800">
          <div className="text-[10px] uppercase font-mono text-slate-400">Ready-at-End</div>
          <div className="text-lg font-mono font-bold text-slate-900 dark:text-white mt-0.5">
            {readyAtEnd !== undefined ? `${Math.round(readyAtEnd * 100)}%` : 'TBD'}
          </div>
        </div>
        <div className="p-3 bg-slate-50 dark:bg-slate-850 rounded-xl border border-slate-100 dark:border-slate-800">
          <div className="text-[10px] uppercase font-mono text-slate-400">Retrieval Legs</div>
          <div className="text-lg font-mono font-bold text-slate-900 dark:text-white mt-0.5">
            {retrievalsCount}
          </div>
        </div>
        <div className="p-3 bg-slate-50 dark:bg-slate-850 rounded-xl border border-slate-100 dark:border-slate-800">
          <div className="text-[10px] uppercase font-mono text-slate-400">Est. Cost</div>
          <div className="text-lg font-mono font-bold text-emerald-600 dark:text-emerald-400 mt-0.5">
            $0.00 <span className="text-[10px] font-normal text-slate-400">(Offline)</span>
          </div>
        </div>
      </div>

      {/* Raw JSON event list */}
      <div className="bg-slate-950 rounded-xl p-3 text-slate-200 font-mono text-xs max-h-48 overflow-y-auto space-y-1">
        {events.length === 0 ? (
          <div className="text-slate-500 italic">No events received yet.</div>
        ) : (
          events.map((ev, i) => (
            <div key={i} className="text-[11px] leading-relaxed border-b border-slate-900 pb-1">
              <span className="text-blue-400">[{ev.event}]</span>{' '}
              <span className="text-slate-400">{JSON.stringify(ev)}</span>
            </div>
          ))
        )}
      </div>
    </div>
  );
};
