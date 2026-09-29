import React from 'react';
import { Play, Sparkles, Terminal, Moon, Sun } from 'lucide-react';

interface HeaderProps {
  mode: 'assistant' | 'inspector';
  onModeChange: (mode: 'assistant' | 'inspector') => void;
  onPlayDemo: () => void;
  status: 'connected' | 'connecting' | 'closed' | 'error';
  isStoryActive: boolean;
  theme: 'light' | 'dark';
  onToggleTheme: () => void;
}

export const Header: React.FC<HeaderProps> = ({
  mode,
  onModeChange,
  onPlayDemo,
  status,
  isStoryActive,
  theme,
  onToggleTheme,
}) => {
  return (
    <header className="border-b border-slate-200 dark:border-slate-800 bg-white/80 dark:bg-slate-900/80 backdrop-blur sticky top-0 z-50 px-4 py-3">
      <div className="max-w-6xl mx-auto flex items-center justify-between">
        {/* Brand */}
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-blue-600 flex items-center justify-center text-white shadow-sm font-bold text-lg">
            K
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-semibold tracking-tight text-slate-900 dark:text-white">Kairos</span>
              <span className="text-[10px] uppercase font-mono px-1.5 py-0.5 rounded bg-blue-50 dark:bg-blue-900/40 text-blue-600 dark:text-blue-300 font-medium">
                Live RAG
              </span>
            </div>
            <p className="text-xs text-slate-500 dark:text-slate-400 hidden sm:block">
              Answers formed while you speak
            </p>
          </div>
        </div>

        {/* Center: Mode Toggle */}
        <div className="flex items-center bg-slate-100 dark:bg-slate-800 p-1 rounded-xl">
          <button
            onClick={() => onModeChange('assistant')}
            className={`flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded-lg transition-all ${
              mode === 'assistant'
                ? 'bg-white dark:bg-slate-700 text-slate-900 dark:text-white shadow-sm'
                : 'text-slate-600 dark:text-slate-400 hover:text-slate-900'
            }`}
          >
            <Sparkles className="w-3.5 h-3.5 text-blue-500" />
            <span>Assistant</span>
          </button>
          <button
            onClick={() => onModeChange('inspector')}
            className={`flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded-lg transition-all ${
              mode === 'inspector'
                ? 'bg-white dark:bg-slate-700 text-slate-900 dark:text-white shadow-sm'
                : 'text-slate-600 dark:text-slate-400 hover:text-slate-900'
            }`}
          >
            <Terminal className="w-3.5 h-3.5 text-purple-500" />
            <span>Inspector</span>
          </button>
        </div>

        {/* Right: Actions */}
        <div className="flex items-center gap-2">
          {/* Story mode demo button */}
          <button
            onClick={onPlayDemo}
            disabled={isStoryActive}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
              isStoryActive
                ? 'bg-blue-100 dark:bg-blue-900/40 text-blue-600 dark:text-blue-300 animate-pulse'
                : 'bg-blue-600 hover:bg-blue-700 text-white shadow-sm hover:shadow'
            }`}
          >
            <Play className="w-3.5 h-3.5 fill-current" />
            <span className="hidden sm:inline">Play the demo</span>
          </button>

          {/* Connection status indicator */}
          <div
            className="flex items-center gap-1.5 px-2 py-1 rounded-md text-xs font-mono text-slate-500 dark:text-slate-400 border border-slate-200 dark:border-slate-800"
            title={`Status: ${status}`}
          >
            <span
              className={`w-2 h-2 rounded-full ${
                status === 'connected'
                  ? 'bg-emerald-500'
                  : status === 'connecting'
                  ? 'bg-amber-500 animate-ping'
                  : 'bg-rose-500'
              }`}
            />
            <span className="hidden md:inline capitalize text-[11px]">{status}</span>
          </div>

          {/* Theme switch */}
          <button
            onClick={onToggleTheme}
            className="p-1.5 text-slate-500 hover:text-slate-800 dark:hover:text-slate-200 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-800"
            aria-label="Toggle color theme"
          >
            {theme === 'dark' ? <Sun className="w-4 h-4" /> : <Moon className="w-4 h-4" />}
          </button>
        </div>
      </div>
    </header>
  );
};
