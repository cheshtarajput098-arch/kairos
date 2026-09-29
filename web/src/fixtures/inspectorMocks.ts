export interface MockTimelineClaim {
  num: number;
  text: string;
  citation: string;
  status: 'verified' | 'not found';
}

export const DEFAULT_TIMELINE_CLAIMS: MockTimelineClaim[] = [
  { num: 1, text: 'Approved Pune workshop venues fit 30 people (Riverside Hall seats 40, Koregaon Studio seats 35)', citation: 'Doc_12 §2', status: 'verified' },
  { num: 2, text: '14+ days notice: 100% refund; 13d–48h: 50% refund; <48h: 0% refund', citation: 'Doc_31 §2, §4', status: 'verified' },
  { num: 3, text: 'Koregaon Studio has in-house catering confirmed 5 days ahead; outside catering requires 7 days notice', citation: 'Doc_89 §1, §2', status: 'verified' },
  { num: 3, text: 'Catering provision details for secondary hall', citation: 'no source', status: 'not found' },
];

export const RACE_BENCHMARKS = {
  utteranceEndS: 2.1,
  firstRetrievalS: 0.8,
  kairosFirstDraftS: 1.02,
  kairosSettledS: 2.1,
  batchRetrievalStartS: 2.1,
  batchRetrievalEndS: 2.95,
  batchSynthStartS: 2.95,
  batchSettledS: 3.61,
  medianTimeSavingsS: 1.51,
};
