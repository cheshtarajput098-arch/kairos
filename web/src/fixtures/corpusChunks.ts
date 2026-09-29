export interface DocChunk {
  id: string;
  section: string;
  title: string;
  text: string;
}

export interface CorpusDoc {
  id: string;
  title: string;
  sectionsCount: number;
  summary: string;
  chunks: DocChunk[];
}

export const CORPUS_DOCS: CorpusDoc[] = [
  {
    id: 'Doc_12',
    title: 'Workshop Venues in Pune',
    sectionsCount: 4,
    summary: 'Approved facilities in Pune, room capacities, layouts, and AV technology packages.',
    chunks: [
      {
        id: 'Doc_12§1',
        section: '§1',
        title: 'Overview and locations',
        text: 'Veloria Systems maintains two approved workshop facilities in Pune: Riverside Hall in Baner and Koregaon Studio in Koregaon Park. Both locations provide high-speed connectivity and presentation screens.',
      },
      {
        id: 'Doc_12§2',
        section: '§2',
        title: 'Capacity and rooms',
        text: 'Both approved Pune venues fit your group: Riverside Hall in Baner seats up to 40 people in a classroom layout, and Koregaon Studio seats up to 35. For 45 people, Riverside Hall works in a theatre layout, which seats up to 60. For a classroom layout above 40 people, the Events Desk arranges an external venue on request.',
      },
      {
        id: 'Doc_12§3',
        section: '§3',
        title: 'Technical equipment',
        text: 'Both Pune facilities feature 4K dual displays, wireless presentation dongles, clip-on microphones, and acoustic boundary ceiling mics. Dedicated AV technician support is provided during business hours.',
      },
    ],
  },
  {
    id: 'Doc_31',
    title: 'Event Cancellation and Refund Policy',
    sectionsCount: 4,
    summary: 'Standard cancellation timelines, refund schedule, and exceptions for corporate events.',
    chunks: [
      {
        id: 'Doc_31§2',
        section: '§2',
        title: 'Notice periods',
        text: 'Cancellations must be submitted through the Events Desk portal. A cancellation made 14 or more calendar days before the event date is a standard cancellation with a full refund of the venue fee.',
      },
      {
        id: 'Doc_31§4',
        section: '§4',
        title: 'Refund terms',
        text: 'Later cancellations received between 13 calendar days and 48 hours prior to the event date receive a 50% refund. Cancellations submitted within 48 hours of the event start time receive zero refund.',
      },
    ],
  },
  {
    id: 'Doc_89',
    title: 'Catering Options for Events',
    sectionsCount: 3,
    summary: 'Internal cafeteria menus, external approved vendors, and dietary request lead times.',
    chunks: [
      {
        id: 'Doc_89§1',
        section: '§1',
        title: 'On-site catering',
        text: 'Koregaon Studio has in-house catering with vegetarian and non-vegetarian menus, charged per person and confirmed 5 working days ahead. Tea and coffee stations with morning snacks are provided continuously.',
      },
      {
        id: 'Doc_89§2',
        section: '§2',
        title: 'External caterers',
        text: 'You can also book an approved external caterer from the Veloria vendor roster for specialized cuisines. Outside catering arrangements must be submitted at least 7 days in advance.',
      },
    ],
  },
  {
    id: 'Doc_05',
    title: 'Travel Reimbursement Policy',
    sectionsCount: 4,
    summary: 'Business travel expense rules, approval workflows, per diem rates, and late claim submission.',
    chunks: [
      {
        id: 'Doc_05§1',
        section: '§1',
        title: 'Standard reimbursement rule',
        text: 'Employees are reimbursed for reasonable travel expenses incurred on company business, including economy transport, lodging, and meals within daily limits.',
      },
      {
        id: 'Doc_05§3',
        section: '§3',
        title: 'International travel',
        text: 'Foreign currency receipts must undergo verification before payment is released. The exchange rate on the expense date applies.',
      },
    ],
  },
];
