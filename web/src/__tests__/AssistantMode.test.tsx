import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { AssistantMode } from '../components/AssistantMode';

describe('AssistantMode Component', () => {
  it('renders ivory mic button and first-run screen when empty', () => {
    const handleSend = vi.fn();
    render(
      <AssistantMode
        transcript=""
        isSearching={false}
        legs={[]}
        drafts={{}}
        finalAnswer=""
        finalClaims={[]}
        citations={[]}
        version={1}
        isDrafting={false}
        suggestions={['What are the workshop venue options?', 'What is the refund policy?']}
        onSendText={handleSend}
        onQuickAction={vi.fn()}
        onSeeDiff={vi.fn()}
      />
    );

    // Mic button
    const micButton = screen.getByLabelText(/start speaking/i);
    expect(micButton).toBeDefined();

    // Suggested questions
    const q1 = screen.getByText(/What are the workshop venue options\?/i);
    const q2 = screen.getByText(/What is the refund policy\?/i);
    expect(q1).toBeDefined();
    expect(q2).toBeDefined();

    // Clicking a suggestion triggers onSendText
    fireEvent.click(q1);
    expect(handleSend).toHaveBeenCalledWith('What are the workshop venue options?');
  });

  it('displays listening status copy and stop button when speaking', () => {
    render(
      <AssistantMode
        transcript="Test question in progress"
        isSearching={true}
        legs={[{ leg_id: 'l1', text: 'Venue layout options', first_dispatch_s: 0.5 }]}
        drafts={{}}
        finalAnswer=""
        finalClaims={[]}
        citations={[]}
        version={1}
        isDrafting={true}
        onSendText={vi.fn()}
        onQuickAction={vi.fn()}
        onSeeDiff={vi.fn()}
      />
    );

    expect(screen.getByText(/Listening…/i)).toBeDefined();
    expect(
      screen.getByText(/Keep talking\. Kairos is already looking things up\./i)
    ).toBeDefined();
    expect(screen.getByText(/Stop/i)).toBeDefined();
  });
});
