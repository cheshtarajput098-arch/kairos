/**
 * Design tokens for Kairos (SPEC §14.2, §14.3a "Calm Precision").
 */

export const colors = {
  neutral: {
    bgLight: '#F8FAFC',
    bgDark: '#0B0F19',
    cardLight: '#FFFFFF',
    cardDark: '#131B2E',
    borderLight: '#E2E8F0',
    borderDark: '#1E293B',
    textLight: '#0F172A',
    textDark: '#F1F5F9',
    mutedLight: '#64748B',
    mutedDark: '#94A3B8',
  },
  brand: {
    primary: '#2563EB', // Confident deep blue
    hover: '#1D4ED8',
    subtle: '#EFF6FF',
    subtleDark: '#1E3A8A20',
  },
  decision: {
    RETRIEVE: '#2563EB',
    WAIT: '#64748B',
    NO_RETRIEVAL: '#8B5CF6',
  },
  intent: [
    { id: 1, name: 'Intent A', hex: '#3B82F6', bg: 'rgba(59, 130, 246, 0.1)', border: '#3B82F6' },
    { id: 2, name: 'Intent B', hex: '#10B981', bg: 'rgba(16, 185, 129, 0.1)', border: '#10B981' },
    { id: 3, name: 'Intent C', hex: '#8B5CF6', bg: 'rgba(139, 92, 246, 0.1)', border: '#8B5CF6' },
    { id: 4, name: 'Intent D', hex: '#F97316', bg: 'rgba(249, 115, 22, 0.1)', border: '#F97316' },
  ],
  status: {
    verified: '#10B981',
    uncertain: '#F59E0B',
    dropped: '#EF4444',
  },
};

export const getIntentColor = (index: number) => {
  return colors.intent[index % colors.intent.length];
};
