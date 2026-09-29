/**
 * Design tokens for Kairos — Adopted from Approved Design Boards (docs/UI_DESIGN.md).
 * Calm Precision theme (Dark).
 */

export const colors = {
  canvas: '#0E1014',
  surface: {
    1: '#15181E', // Primary cards & panels
    2: '#1C2028', // Elevated cards, input bar
    3: '#12151B', // Recessed areas, sidebars, story bar
  },
  text: {
    primary: '#ECE9E2', // Warm ivory
    secondary: '#A3A9B5', // Subheadings, labels
    tertiary: '#7D8594', // Timestamps, placeholders
  },
  border: {
    default: '#1E2330',
    subtle: '#282D3A',
  },
  intent: [
    { id: 1, name: 'Intent 1', hex: '#8FB3FF', bg: 'rgba(143, 179, 255, 0.15)', border: '#8FB3FF' },
    { id: 2, name: 'Intent 2', hex: '#62D6B4', bg: 'rgba(98, 214, 180, 0.15)', border: '#62D6B4' },
    { id: 3, name: 'Intent 3', hex: '#B98CFF', bg: 'rgba(185, 140, 255, 0.15)', border: '#B98CFF' },
    { id: 4, name: 'Intent 4', hex: '#F0B455', bg: 'rgba(240, 180, 85, 0.15)', border: '#F0B455' },
  ],
  status: {
    verified: '#6FD39A',
    gap: '#F0B455',
    error: '#EF4444',
    updated: '#8FB3FF',
  },
  accent: {
    blue: '#5B8DEF',
    greenDot: '#4ADE80',
  },
  button: {
    ivory: '#ECE9E2',
    ivoryBg: '#1C2028',
  }
};

export const getIntentColor = (index: number) => {
  return colors.intent[index % colors.intent.length];
};
