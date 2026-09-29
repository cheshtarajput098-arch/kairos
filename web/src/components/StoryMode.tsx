export interface StoryScenario {
  id: string;
  title: string;
  tag: string;
  caption: string;
  chunks: { t: number; text: string }[];
  utteranceEnd: number;
}

export const SCENARIOS: StoryScenario[] = [
  {
    id: 's1',
    title: 'A question with three parts',
    tag: 'Multi-Intent Decomposition',
    caption: 'Watch the answer form while the sentence is still being spoken.',
    chunks: [
      { t: 0.0, text: 'We want to organise a workshop in' },
      { t: 0.8, text: 'Pune for 30 attendees, and need' },
      { t: 1.6, text: 'the cancellation policy plus catering options.' },
    ],
    utteranceEnd: 2.1,
  },
  {
    id: 's2',
    title: 'Adding a detail later',
    tag: 'In-Place Refinement (v1 → v2)',
    caption: 'Only the part you changed was looked up again.',
    chunks: [
      { t: 0.0, text: 'Actually, make that 45 people.' },
    ],
    utteranceEnd: 1.2,
  },
  {
    id: 's3',
    title: 'Presentation reformat',
    tag: 'Zero-Retrieval Presentation',
    caption: 'No new search needed: re-synthesizes presentation instantly.',
    chunks: [
      { t: 0.0, text: 'Format that as bullet points.' },
    ],
    utteranceEnd: 1.5,
  },
];
