import React from 'react';
import {
  Menu,
  ChevronDown,
  Play,
  Share2,
  RotateCw,
  Plus,
  Download,
  Settings,
} from 'lucide-react';
import { NavTab } from './Sidebar';

interface TopBarProps {
  activeTab: NavTab;
  isConversation: boolean;
  questionTitle?: string;
  onOpenMobileMenu: () => void;
  onPlayDemo: () => void;
  onOpenSettings: () => void;
  onReindex?: () => void;
  onExportJson?: () => void;
  status?: 'connected' | 'connecting' | 'closed' | 'error';
}

export const TopBar: React.FC<TopBarProps> = ({
  activeTab,
  isConversation,
  questionTitle,
  onOpenMobileMenu,
  onPlayDemo,
  onOpenSettings,
  onReindex,
  onExportJson,
  status = 'connected',
}) => {
  return (
    <header className="h-16 shrink-0 bg-[#0E1014] border-b border-[#1E2330] px-4 sm:px-6 flex items-center justify-between z-30">
      {/* Left side */}
      <div className="flex items-center gap-3 sm:gap-4 min-w-0">
        {/* Mobile menu hamburger button */}
        <button
          onClick={onOpenMobileMenu}
          className="lg:hidden p-1.5 rounded-lg text-[#A3A9B5] hover:text-[#ECE9E2] hover:bg-[#15181E] border border-[#1E2330] transition-colors"
          aria-label="Open menu"
        >
          <Menu className="w-4 h-4" />
        </button>

        {/* Breadcrumb / Title */}
        <div className="flex items-center gap-2 min-w-0">
          {activeTab === 'ask' ? (
            isConversation && questionTitle ? (
              <div className="flex items-center gap-2 truncate">
                <span className="text-sm font-semibold text-[#ECE9E2] truncate">
                  {questionTitle}
                </span>
                <span className="hidden sm:inline text-xs text-[#7D8594] font-serif">
                  Today, 10:42
                </span>
              </div>
            ) : (
              <span className="text-sm font-semibold text-[#ECE9E2]">Ask</span>
            )
          ) : activeTab === 'sources' ? (
            <span className="text-sm font-semibold text-[#ECE9E2]">
              Knowledge sources
            </span>
          ) : activeTab === 'traces' ? (
            <span className="text-sm font-semibold text-[#ECE9E2]">Traces</span>
          ) : (
            <span className="text-sm font-semibold text-[#ECE9E2]">
              Evaluation
            </span>
          )}

          {/* Collection Chip */}
          <div className="hidden md:flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-[#15181E] border border-[#1E2330] text-xs text-[#A3A9B5] hover:text-[#ECE9E2] hover:border-[#282D3A] transition-colors cursor-pointer select-none">
            <span className="w-1.5 h-1.5 rounded-full bg-[#8FB3FF]" />
            <span>Searching Company policies · 8 documents</span>
            <ChevronDown className="w-3 h-3 text-[#7D8594]" />
          </div>
        </div>
      </div>

      {/* Right side */}
      <div className="flex items-center gap-3 shrink-0">
        {/* Local model status indicator */}
        <div className="hidden sm:flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-[#12151B] border border-[#1E2330] text-xs font-mono text-[#A3A9B5]">
          <span
            className={`w-1.5 h-1.5 rounded-full ${
              status === 'connected'
                ? 'bg-[#4ADE80] animate-pulse'
                : 'bg-[#F0B455]'
            }`}
          />
          <span>Local model · offline</span>
        </div>

        {/* Context-specific action button */}
        {activeTab === 'ask' && !isConversation && (
          <button
            onClick={onPlayDemo}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-[#1C2028] border border-[#282D3A] hover:bg-[#252B36] text-xs font-medium text-[#ECE9E2] hover:border-[#8FB3FF]/30 transition-all shadow-sm cursor-pointer"
          >
            <Play className="w-3.5 h-3.5 text-[#8FB3FF] fill-current" />
            <span>Play the demo</span>
          </button>
        )}

        {activeTab === 'ask' && isConversation && (
          <button
            onClick={() => {
              if (navigator.clipboard) {
                navigator.clipboard.writeText(window.location.href);
              }
            }}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-[#1C2028] border border-[#282D3A] hover:bg-[#252B36] text-xs font-medium text-[#ECE9E2] transition-all cursor-pointer"
            title="Share conversation"
          >
            <Share2 className="w-3.5 h-3.5 text-[#A3A9B5]" />
            <span className="hidden sm:inline">Share</span>
          </button>
        )}

        {activeTab === 'sources' && (
          <div className="flex items-center gap-2">
            <button
              onClick={onReindex}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-[#1C2028] border border-[#282D3A] hover:bg-[#252B36] text-xs font-medium text-[#ECE9E2] transition-all cursor-pointer"
            >
              <RotateCw className="w-3.5 h-3.5 text-[#8FB3FF]" />
              <span className="hidden sm:inline">Re-index</span>
            </button>
            <button
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-[#ECE9E2] text-[#0E1014] hover:bg-white text-xs font-medium transition-all cursor-pointer"
              title="Add documents (Administered via CLI)"
            >
              <Plus className="w-3.5 h-3.5" />
              <span>Add documents</span>
            </button>
          </div>
        )}

        {activeTab === 'traces' && (
          <button
            onClick={onExportJson}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-[#1C2028] border border-[#282D3A] hover:bg-[#252B36] text-xs font-medium text-[#ECE9E2] transition-all cursor-pointer"
          >
            <Download className="w-3.5 h-3.5 text-[#8FB3FF]" />
            <span>Export JSON</span>
          </button>
        )}

        {/* Settings button */}
        <button
          onClick={onOpenSettings}
          className="p-1.5 rounded-xl text-[#7D8594] hover:text-[#ECE9E2] hover:bg-[#15181E] border border-transparent hover:border-[#1E2330] transition-colors"
          aria-label="Settings"
        >
          <Settings className="w-4 h-4" />
        </button>
      </div>
    </header>
  );
};
