import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { AnswerCanvas } from '../components/AnswerCanvas';

describe('AnswerCanvas Component', () => {
  const mockClaims = [
    {
      claim_id: 'c1',
      leg_id: 'l1',
      text: 'Approved venue facilities fit technical workshop needs [Doc_12§2].',
      citations: ['Doc_12§2'],
      evidence_span: 'Facilities fit technical workshop needs.',
      status: 'verified' as const,
      version: 1,
    },
  ];

  it('renders quick action buttons: Shorter, As bullets, Explain simply, Copy', () => {
    const handleAction = vi.fn();
    render(
      <AnswerCanvas
        legs={[{ leg_id: 'l1', text: 'Venue facilities', first_dispatch_s: 0.5 }]}
        drafts={{}}
        finalAnswer="Approved venue facilities fit technical workshop needs [Doc_12§2]."
        finalClaims={mockClaims}
        citations={['Doc_12§2']}
        version={1}
        isDrafting={false}
        onQuickAction={handleAction}
        onSeeDiff={vi.fn()}
      />
    );

    expect(screen.getByText('Shorter')).toBeDefined();
    expect(screen.getByText('As bullets')).toBeDefined();
    expect(screen.getByText('Explain simply')).toBeDefined();
    expect(screen.getByText('Copy')).toBeDefined();

    // Triggering quick action displays "No new search needed"
    fireEvent.click(screen.getByText('Shorter'));
    expect(handleAction).toHaveBeenCalledWith('shorter');
    expect(screen.getByText('No new search needed')).toBeDefined();
  });

  it('renders thumbs up/down buttons and records feedback', () => {
    const handleFeedback = vi.fn();
    render(
      <AnswerCanvas
        legs={[{ leg_id: 'l1', text: 'Venue facilities', first_dispatch_s: 0.5 }]}
        drafts={{}}
        finalAnswer="Approved venue facilities fit technical workshop needs [Doc_12§2]."
        finalClaims={mockClaims}
        citations={['Doc_12§2']}
        version={1}
        isDrafting={false}
        onQuickAction={vi.fn()}
        onSeeDiff={vi.fn()}
        onFeedback={handleFeedback}
      />
    );

    const upButton = screen.getByLabelText('Thumbs up');
    fireEvent.click(upButton);
    expect(handleFeedback).toHaveBeenCalledWith('up');
    expect(screen.getByText('Feedback saved')).toBeDefined();
  });
});
