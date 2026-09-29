import React from 'react';
import {
  MessageSquare,
  BookOpen,
  Activity,
  Sliders,
  Plus,
  ChevronDown,
  Lock,
  X,
} from 'lucide-react';

export type NavTab = 'ask' | 'sources' | 'traces' | 'evaluation';

interface SidebarProps {
  activeTab: NavTab;
  onTabChange: (tab: NavTab) => void;
  onNewQuestion: () => void;
  onSelectRecent: (scenarioIndex: number) => void;
  isOpenMobile: boolean;
  onCloseMobile: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({
  activeTab,
  onTabChange,
  onNewQuestion,
  onSelectRecent,
  isOpenMobile,
  onCloseMobile,
}) => {
  const navItems = [
    { id: 'ask' as const, label: 'Ask', icon: MessageSquare },
    { id: 'sources' as const, label: 'Knowledge sources', icon: BookOpen },
    { id: 'traces' as const, label: 'Traces', icon: Activity },
    { id: 'evaluation' as const, label: 'Evaluation', icon: Sliders },
  ];

  const recentItems = [
    { title: 'Pune workshop for 30 people', scenarioIndex: 0 },
    { title: 'International travel claim', scenarioIndex: 1 },
    { title: 'Venue cancellation notice', scenarioIndex: 2 },
  ];

  const content = (
    <div className="w-[248px] h-full flex flex-col justify-between bg-[#12151B] border-r border-[#1E2330] p-4 text-[#ECE9E2] select-none">
      {/* Top Section */}
      <div className="space-y-4">
        {/* Brand header */}
        <div className="flex items-center justify-between pt-1 px-1">
          <div className="flex items-center gap-2.5">
            <div className="w-6 h-6 rounded-full border border-[#ECE9E2] flex items-center justify-center">
              <span className="w-1.5 h-1.5 rounded-full bg-[#ECE9E2]" />
            </div>
            <span className="font-sans font-bold text-base tracking-tight text-[#ECE9E2]">
              Kairos
            </span>
          </div>

          {/* Mobile close button */}
          <button
            onClick={onCloseMobile}
            className="lg:hidden text-[#7D8594] hover:text-[#ECE9E2] p-1"
            aria-label="Close menu"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Workspace selector */}
        <div className="bg-[#15181E] border border-[#1E2330] rounded-xl px-2.5 py-2 flex items-center justify-between hover:border-[#282D3A] transition-colors cursor-pointer">
          <div className="flex items-center gap-2 min-w-0">
            <div className="w-5 h-5 rounded-md bg-[#252B36] border border-[#343B4B] flex items-center justify-center text-[10px] font-bold text-[#8FB3FF] shrink-0">
              V
            </div>
            <span className="text-xs font-medium text-[#ECE9E2] truncate">
              Veloria Systems
            </span>
          </div>
          <ChevronDown className="w-3.5 h-3.5 text-[#7D8594] shrink-0" />
        </div>

        {/* + New question button */}
        <button
          onClick={() => {
            onNewQuestion();
            onCloseMobile();
          }}
          className="w-full bg-[#ECE9E2] text-[#0E1014] hover:bg-white font-medium text-xs py-2 px-3 rounded-xl flex items-center justify-center gap-1.5 transition-all shadow-sm active:scale-[0.98]"
        >
          <Plus className="w-3.5 h-3.5 stroke-[2.5]" />
          <span>New question</span>
        </button>

        {/* Navigation items */}
        <nav className="space-y-1 pt-1">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => {
                  onTabChange(item.id);
                  onCloseMobile();
                }}
                className={`w-full flex items-center gap-2.5 px-3 py-2 rounded-xl text-xs font-medium transition-all ${
                  isActive
                    ? 'bg-[#1C2028] text-[#ECE9E2] border border-[#282D3A]'
                    : 'text-[#A3A9B5] hover:text-[#ECE9E2] hover:bg-[#15181E] border border-transparent'
                }`}
              >
                <Icon
                  className={`w-4 h-4 ${
                    isActive ? 'text-[#8FB3FF]' : 'text-[#7D8594]'
                  }`}
                />
                <span>{item.label}</span>
              </button>
            );
          })}
        </nav>

        {/* Recent Section */}
        <div className="pt-2">
          <div className="text-[10px] font-mono uppercase tracking-wider text-[#7D8594] px-3 pb-1.5">
            Recent
          </div>
          <div className="space-y-0.5">
            {recentItems.map((r, i) => (
              <button
                key={i}
                onClick={() => {
                  onSelectRecent(r.scenarioIndex);
                  onCloseMobile();
                }}
                className="w-full text-left px-3 py-1.5 rounded-lg text-xs text-[#A3A9B5] hover:text-[#ECE9E2] hover:bg-[#15181E] truncate transition-colors"
                title={r.title}
              >
                {r.title}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Bottom Section */}
      <div className="space-y-3 pt-4 border-t border-[#1E2330]">
        {/* Private by design card */}
        <div className="bg-[#15181E] border border-[#1E2330] rounded-xl p-3 space-y-1">
          <div className="flex items-center gap-1.5 text-xs font-semibold text-[#ECE9E2]">
            <Lock className="w-3.5 h-3.5 text-[#8FB3FF]" />
            <span>Private by design</span>
          </div>
          <p className="text-[11px] text-[#7D8594] leading-relaxed">
            Runs on this computer. Your questions and documents never leave it.
          </p>
        </div>

        {/* User profile row */}
        <div className="flex items-center gap-2.5 px-1 pt-1">
          <div className="w-7 h-7 rounded-full bg-[#1C2028] border border-[#282D3A] flex items-center justify-center text-[11px] font-bold text-[#ECE9E2]">
            CR
          </div>
          <div className="min-w-0 flex-1">
            <div className="text-xs font-medium text-[#ECE9E2] truncate">
              Cheshta Rajput
            </div>
            <div className="text-[10px] text-[#7D8594] truncate">
              Workspace admin
            </div>
          </div>
        </div>
      </div>
    </div>
  );

  return (
    <>
      {/* Desktop fixed sidebar */}
      <aside className="hidden lg:block w-[248px] shrink-0 h-screen sticky top-0 overflow-hidden">
        {content}
      </aside>

      {/* Mobile slide-over drawer */}
      {isOpenMobile && (
        <div className="fixed inset-0 z-50 lg:hidden flex">
          <div
            className="fixed inset-0 bg-black/70 backdrop-blur-sm"
            onClick={onCloseMobile}
          />
          <div className="relative z-10 h-full w-[248px] shadow-2xl">
            {content}
          </div>
        </div>
      )}
    </>
  );
};
