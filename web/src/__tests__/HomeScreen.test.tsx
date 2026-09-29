import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { HomeScreen } from '../components/HomeScreen';

describe('HomeScreen Component (Board 6)', () => {
  it('renders headline, 56px mic, 3 guided example cards, and trust row', () => {
    const handleSend = vi.fn();
    const handlePlayScenario = vi.fn();

    render(
      <HomeScreen
        onSendQuestion={handleSend}
        onPlayScenario={handlePlayScenario}
      />
    );

    // Headline
    expect(
      screen.getByText(/Ask several things at once\. Kairos starts answering before you finish\./i)
    ).toBeDefined();

    // 56px Mic Orb
    const micButton = screen.getByLabelText(/start speaking/i);
    expect(micButton).toBeDefined();

    // Guided example cards
    expect(screen.getByText(/3 questions in one/i)).toBeDefined();
    expect(screen.getByText(/Detail added later/i)).toBeDefined();
    expect(screen.getByText(/No search needed/i)).toBeDefined();

    // Clicking guided example triggers onPlayScenario(0)
    fireEvent.click(screen.getByText(/3 questions in one/i));
    expect(handlePlayScenario).toHaveBeenCalledWith(0);

    // Trust row
    expect(screen.getByText(/Every sentence cites its exact source line/i)).toBeDefined();
    expect(screen.getByText(/Says when the documents don't cover it/i)).toBeDefined();
    expect(screen.getByText(/Runs offline, no API keys/i)).toBeDefined();
  });
});
