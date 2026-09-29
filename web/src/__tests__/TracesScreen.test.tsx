import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { TracesScreen } from '../components/TracesScreen';

describe('TracesScreen Component (Board 9)', () => {
  it('renders timeline gantt chart, event log, and grounding checks table', () => {
    const handleBack = vi.fn();

    render(
      <TracesScreen
        questionTitle="Pune workshop for 30 people"
        turnId="turn s1-t1"
        onBackToConversation={handleBack}
      />
    );

    // Title and turnId
    expect(screen.getByText(/Pune workshop for 30 people/i)).toBeDefined();
    expect(screen.getByText(/turn s1-t1/i)).toBeDefined();

    // Badges
    expect(screen.getAllByText(/3 parts/i).length).toBeGreaterThan(0);
    expect(screen.getByText(/5 citations, all verified/i)).toBeDefined();
    expect(screen.getByText(/0 fabricated/i)).toBeDefined();

    // Timeline elements
    expect(screen.getByText(/Timeline/i)).toBeDefined();
    expect(screen.getByText(/live transcript/i)).toBeDefined();
    expect(screen.getByText(/Part 1 · Venue/i)).toBeDefined();
    expect(screen.getByText(/Part 2 · Cancellation/i)).toBeDefined();
    expect(screen.getByText(/Part 3 · Catering/i)).toBeDefined();

    // Events Log
    expect(screen.getAllByText(/Events/i).length).toBeGreaterThan(0);
    expect(screen.getAllByText(/Controller/i).length).toBeGreaterThan(0);

    // Grounding Checks Table
    expect(screen.getByText(/Grounding checks/i)).toBeDefined();
    expect(screen.getByText(/Cited passage was retrieved/i)).toBeDefined();
    expect(screen.getByText(/Fabricated citations/i)).toBeDefined();

    // Back button
    const backBtn = screen.getByText(/Back to the conversation/i);
    fireEvent.click(backBtn);
    expect(handleBack).toHaveBeenCalled();
  });
});
