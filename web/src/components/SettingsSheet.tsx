import React, { useEffect } from 'react';
import { X, Sliders, Type, Eye } from 'lucide-react';

interface SettingsSheetProps {
  isOpen: boolean;
  onClose: () => void;
  showDraftsWhileSpeaking: boolean;
  onToggleDraftsWhileSpeaking: (val: boolean) => void;
  textSize: 'normal' | 'large' | 'xlarge';
  onChangeTextSize: (size: 'normal' | 'large' | 'xlarge') => void;
}

export const SettingsSheet: React.FC<SettingsSheetProps> = ({
  isOpen,
  onClose,
  showDraftsWhileSpeaking,
  onToggleDraftsWhileSpeaking,
  textSize,
  onChangeTextSize,
}) => {
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && isOpen) {
        onClose();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  return (
    <div
      className="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm flex justify-end transition-opacity"
      role="dialog"
      aria-modal="true"
      aria-label="Application Settings"
      onClick={onClose}
    >
      <div
        className="w-full max-w-md bg-[#15181E] border-l border-[#1E2330] h-full p-6 shadow-2xl flex flex-col justify-between"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="space-y-6">
          {/* Header */}
          <div className="flex items-center justify-between pb-4 border-b border-[#1E2330]">
            <div className="flex items-center gap-2 text-[#ECE9E2]">
              <Sliders className="w-5 h-5 text-[#8FB3FF]" />
              <h2 className="text-base font-semibold">Settings</h2>
            </div>
            <button
              onClick={onClose}
              className="p-1.5 rounded-lg text-[#7D8594] hover:text-[#ECE9E2] hover:bg-[#1C2028] transition-colors"
              aria-label="Close settings"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Setting 1: Show answer while I speak */}
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <div className="flex items-start gap-2.5">
                <Eye className="w-4 h-4 text-[#8FB3FF] mt-0.5" />
                <div>
                  <div className="text-xs font-medium text-[#ECE9E2]">Show answer while I speak</div>
                  <p className="text-[11px] text-[#7D8594] mt-0.5 leading-relaxed">
                    Render provisional verified drafts as each intent completes, before you stop talking.
                  </p>
                </div>
              </div>

              <button
                type="button"
                role="switch"
                aria-checked={showDraftsWhileSpeaking}
                onClick={() => onToggleDraftsWhileSpeaking(!showDraftsWhileSpeaking)}
                className={`relative inline-flex h-6 w-11 shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none ${
                  showDraftsWhileSpeaking ? 'bg-[#8FB3FF]' : 'bg-[#282D3A]'
                }`}
              >
                <span
                  className={`pointer-events-none inline-block h-5 w-5 transform rounded-full bg-[#0E1014] shadow ring-0 transition duration-200 ease-in-out ${
                    showDraftsWhileSpeaking ? 'translate-x-5' : 'translate-x-0'
                  }`}
                />
              </button>
            </div>
          </div>

          {/* Setting 2: Text Size */}
          <div className="space-y-3 pt-4 border-t border-[#1E2330]">
            <div className="flex items-center gap-2 text-xs font-medium text-[#ECE9E2]">
              <Type className="w-4 h-4 text-[#8FB3FF]" />
              <span>Text size</span>
            </div>

            <div className="grid grid-cols-3 gap-2">
              {(
                [
                  { id: 'normal', label: 'Normal', sample: '15px' },
                  { id: 'large', label: 'Large', sample: '17px' },
                  { id: 'xlarge', label: 'Extra Large', sample: '19px' },
                ] as const
              ).map((opt) => (
                <button
                  key={opt.id}
                  onClick={() => onChangeTextSize(opt.id)}
                  className={`py-2 px-3 rounded-xl border text-xs flex flex-col items-center gap-1 transition-all ${
                    textSize === opt.id
                      ? 'bg-[#1C2028] border-[#8FB3FF] text-[#ECE9E2] font-semibold'
                      : 'bg-[#12151B] border-[#1E2330] text-[#7D8594] hover:text-[#ECE9E2]'
                  }`}
                >
                  <span>{opt.label}</span>
                  <span className="text-[10px] font-mono text-[#7D8594]">{opt.sample}</span>
                </button>
              ))}
            </div>
          </div>

          {/* Accessibility Info Note */}
          <div className="p-3.5 rounded-xl bg-[#1C2028]/60 border border-[#282D3A] text-[11px] text-[#A3A9B5] leading-relaxed">
            <span className="font-semibold text-[#ECE9E2]">Shortcuts:</span> Press{' '}
            <kbd className="px-1.5 py-0.5 rounded bg-[#0E1014] border border-[#282D3A] font-mono text-[10px]">
              Space
            </kbd>{' '}
            to talk/stop,{' '}
            <kbd className="px-1.5 py-0.5 rounded bg-[#0E1014] border border-[#282D3A] font-mono text-[10px]">
              /
            </kbd>{' '}
            to focus input,{' '}
            <kbd className="px-1.5 py-0.5 rounded bg-[#0E1014] border border-[#282D3A] font-mono text-[10px]">
              I
            </kbd>{' '}
            to toggle Inspector.
          </div>
        </div>

        <div className="pt-4 border-t border-[#1E2330] flex justify-end">
          <button
            onClick={onClose}
            className="px-4 py-2 rounded-xl text-xs font-semibold bg-[#1C2028] border border-[#282D3A] text-[#ECE9E2] hover:bg-[#252B36] transition-colors"
          >
            Done
          </button>
        </div>
      </div>
    </div>
  );
};
