import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { KnowledgeSourcesScreen } from '../components/KnowledgeSourcesScreen';

describe('KnowledgeSourcesScreen Component (Board 8)', () => {
  it('renders real index metrics, document table, and drop guidance card', () => {
    render(<KnowledgeSourcesScreen />);

    // Header
    expect(screen.getByText(/Company policies/i)).toBeDefined();
    expect(screen.getByText(/Index ready/i)).toBeDefined();

    // 4 Metrics cards
    expect(screen.getByText(/BGE-small-en-v1\.5/i)).toBeDefined();
    expect(screen.getByText(/BM25/i)).toBeDefined();
    expect(screen.getByText(/Reciprocal Rank Fusion/i)).toBeDefined();
    expect(screen.getByText(/0 passages flagged/i)).toBeDefined();

    // Document Table rows
    expect(screen.getByText(/Workshop Venues in Pune/i)).toBeDefined();
    expect(screen.getByText(/Event Cancellation and Refund Policy/i)).toBeDefined();
    expect(screen.getByText(/Catering Options for Events/i)).toBeDefined();

    // Drop guidance card
    expect(screen.getByText(/Drop Markdown or text files here/i)).toBeDefined();
  });
});
