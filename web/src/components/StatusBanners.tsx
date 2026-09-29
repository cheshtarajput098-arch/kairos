import React from 'react';
import { AlertCircle, WifiOff, MicOff, RefreshCw, HelpCircle, ShieldAlert } from 'lucide-react';

interface StatusBannersProps {
  connectionStatus: 'connected' | 'connecting' | 'closed' | 'error';
  onRetryConnection: () => void;
  micPermissionDenied: boolean;
  onTypeInstead: () => void;
  rateLimitError?: { message: string; requestId: string } | null;
  outOfScopeError?: { message: string; requestId: string } | null;
  generalError?: { code: string; message: string; requestId: string } | null;
  onDismissError?: () => void;
}

export const StatusBanners: React.FC<StatusBannersProps> = ({
  connectionStatus,
  onRetryConnection,
  micPermissionDenied,
  onTypeInstead,
  rateLimitError,
  outOfScopeError,
  generalError,
  onDismissError,
}) => {
  return (
    <div className="space-y-3">
      {/* 1. Offline / Reconnecting Banner */}
      {(connectionStatus === 'closed' || connectionStatus === 'error') && (
        <div className="bg-[#E5484D]/10 border border-[#E5484D]/30 rounded-xl p-3.5 flex items-center justify-between gap-3 text-xs">
          <div className="flex items-center gap-2.5 text-[#E5484D]">
            <WifiOff className="w-4 h-4 shrink-0" />
            <span>
              <strong>Disconnected from engine.</strong> Reconnecting automatically…
            </span>
          </div>
          <button
            onClick={onRetryConnection}
            className="px-3 py-1 rounded-lg bg-[#E5484D]/20 hover:bg-[#E5484D]/30 text-[#ECE9E2] border border-[#E5484D]/40 font-medium transition-colors flex items-center gap-1.5 shrink-0"
          >
            <RefreshCw className="w-3.5 h-3.5" />
            <span>Retry now</span>
          </button>
        </div>
      )}

      {/* 2. Mic Permission Denied Banner */}
      {micPermissionDenied && (
        <div className="bg-[#F0B455]/10 border border-[#F0B455]/30 rounded-xl p-3.5 flex items-center justify-between gap-3 text-xs">
          <div className="flex items-center gap-2.5 text-[#F0B455]">
            <MicOff className="w-4 h-4 shrink-0" />
            <span>
              Microphone permission is blocked by your browser.
            </span>
          </div>
          <button
            onClick={onTypeInstead}
            className="px-3 py-1 rounded-lg bg-[#1C2028] hover:bg-[#252B36] text-[#ECE9E2] border border-[#282D3A] font-medium transition-colors shrink-0"
          >
            Type instead
          </button>
        </div>
      )}

      {/* 3. Rate-Limited Message Card (429) */}
      {rateLimitError && (
        <div className="bg-[#F0B455]/10 border border-[#F0B455]/30 rounded-xl p-4 space-y-2 text-xs">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2 text-[#F0B455] font-semibold">
              <ShieldAlert className="w-4 h-4" />
              <span>Rate Limit Exceeded (HTTP 429)</span>
            </div>
            <span className="font-mono text-[11px] text-[#7D8594]">
              request_id: {rateLimitError.requestId}
            </span>
          </div>
          <p className="text-[#ECE9E2] font-serif leading-relaxed">
            {rateLimitError.message ||
              'You have exceeded the turn request limit. Please wait a few seconds before asking another question.'}
          </p>
        </div>
      )}

      {/* 4. Out-of-Scope Question Card */}
      {outOfScopeError && (
        <div className="bg-[#1C2028] border border-[#282D3A] rounded-xl p-4 space-y-2 text-xs">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2 text-[#A3A9B5] font-semibold">
              <HelpCircle className="w-4 h-4 text-[#8FB3FF]" />
              <span>Out of Scope</span>
            </div>
            <span className="font-mono text-[11px] text-[#7D8594]">
              request_id: {outOfScopeError.requestId}
            </span>
          </div>
          <p className="text-[#ECE9E2] font-serif leading-relaxed">
            {outOfScopeError.message ||
              'This topic is not covered in the approved corpus documents. Under strict corpus isolation rules, Kairos does not synthesize speculative answers.'}
          </p>
        </div>
      )}

      {/* 5. General Error Card with request_id */}
      {generalError && (
        <div className="bg-[#E5484D]/10 border border-[#E5484D]/30 rounded-xl p-4 space-y-2 text-xs">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2 text-[#E5484D] font-semibold">
              <AlertCircle className="w-4 h-4" />
              <span>Error: {generalError.code}</span>
            </div>
            <div className="flex items-center gap-3">
              <span className="font-mono text-[11px] text-[#7D8594]">
                request_id: {generalError.requestId}
              </span>
              {onDismissError && (
                <button
                  onClick={onDismissError}
                  className="text-xs text-[#A3A9B5] hover:text-[#ECE9E2]"
                >
                  Dismiss
                </button>
              )}
            </div>
          </div>
          <p className="text-[#ECE9E2] font-serif leading-relaxed">
            {generalError.message}
          </p>
        </div>
      )}
    </div>
  );
};
