import React from 'react';
import { Play, Settings } from 'lucide-react';

interface HeaderProps {
  mode: 'assistant' | 'inspector';
  onModeChange: (mode: 'assistant' | 'inspector') => void;
  onPlayDemo: () => void;
  status: 'connected' | 'connecting' | 'closed' | 'error';
  isStoryActive: boolean;
  onOpenSettings?: () => void;
}

export const Header: React.FC<HeaderProps> = ({
  mode,
  onModeChange,
  onPlayDemo,
  status,
  isStoryActive,
  onOpenSettings,
}) => {
  return (
    <header className="border-b border-[#1E2330] bg-[#0E1014] sticky top-0 z-50 px-6 py-3.5">
      <div className="max-w-[1280px] mx-auto flex items-center justify-between">
        {/* Brand */}
        <div className="flex items-center gap-3">
          <div className="w-7 h-7 rounded-full border-2 border-[#ECE9E2] flex items-center justify-center">
            <div className="w-2.5 h-2.5 rounded-full bg-[#ECE9E2]" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-semibold text-base text-[#ECE9E2] tracking-tight">Kairos</span>
            </div>
            <p className="text-[12px] text-[#7D8594] leading-tight">
              Answers while you speak
            </p>
          </div>
        </div>

        {/* Center: Mode Toggle */}
        <div className="flex items-center bg-[#15181E] border border-[#1E2330] p-1 rounded-xl">
          <button
            onClick={() => onModeChange('assistant')}
            className={`px-3.5 py-1.5 text-xs font-medium rounded-lg transition-all ${
              mode === 'assistant'
                ? 'bg-[#1C2028] text-[#ECE9E2] shadow-sm'
                : 'text-[#A3A9B5] hover:text-[#ECE9E2]'
            }`}
          >
            Assistant
          </button>
          <button
            onClick={() => onModeChange('inspector')}
            className={`px-3.5 py-1.5 text-xs font-medium rounded-lg transition-all ${
              mode === 'inspector'
                ? 'bg-[#1C2028] text-[#ECE9E2] shadow-sm'
                : 'text-[#A3A9B5] hover:text-[#ECE9E2]'
            }`}
          >
            Show how it works
          </button>
        </div>

        {/* Right: Actions */}
        <div className="flex items-center gap-3">
          {/* Connection status indicator */}
          <div className="flex items-center gap-2 text-xs font-mono text-[#A3A9B5]">
            <span
              className={`w-2 h-2 rounded-full ${
                status === 'connected'
                  ? 'bg-[#4ADE80]'
                  : status === 'connecting'
                  ? 'bg-[#F0B455] animate-ping'
                  : 'bg-[#EF4444]'
              }`}
            />
            <span className="capitalize text-[12px]">{status}</span>
          </div>

          {/* Play the demo button */}
          <button
            onClick={onPlayDemo}
            disabled={isStoryActive}
            className={`flex items-center gap-2 px-3.5 py-1.5 rounded-lg text-xs font-medium transition-all ${
              isStoryActive
                ? 'bg-[#1C2028] text-[#7D8594] border border-[#1E2330] cursor-not-allowed'
                : 'bg-[#1C2028] hover:bg-[#252b36] text-[#ECE9E2] border border-[#282D3A] shadow-sm'
            }`}
          >
            <Play className="w-3.5 h-3.5 fill-current text-[#ECE9E2]" />
            <span>Play the demo</span>
          </button>

          {/* Settings button (Item 8) */}
          <button
            type="button"
            onClick={onOpenSettings}
            className="p-1.5 text-[#7D8594] hover:text-[#ECE9E2] hover:bg-[#1C2028] rounded-lg transition-colors cursor-pointer"
            title="Settings"
            aria-label="Settings"
          >
            <Settings className="w-4 h-4" />
          </button>
        </div>
      </div>
    </header>
  );
};
