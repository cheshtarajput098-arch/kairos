# data/replay/demo — the three theme-guide scenarios

`scenarios.jsonl` holds the three example scenarios from the theme guide (§4) as replay transcripts, matched to the **placeholder** corpus. Story mode and the CI "mvp-replay" job play these. `gold.jsonl` holds what the system is expected to do.

1. **demo-s1**: incremental multi-intent utterance ("workshop in Pune for 30 people… cancellation policy and catering"). Expect WAIT → provisional RETRIEVE → three legs → one answer with citations and an uncertainty note about catering for Venue A.
2. **demo-s2**: late-arriving detail ("the trip was international and booked after travel"). Expect no session reset, delta queries only, prior citations kept, answer version 2.
3. **demo-s3**: query suppression ("repeat your last answer in two bullets"). Expect `retrieval_required: false`, `reason: presentation_restructure`, zero vector searches, same citations.

Status: **DRAFT, needs human review.** When the real corpus arrives, rewrite these scenarios against it (Prompt 3) and re-check every gold label by hand.

Format (SPEC.md §2.2): one turn per line; chunks are `{"t": seconds, "text": "..."}`; `utterance_end` is when the speaker stopped. Timestamps for demo-s2 and demo-s3 were generated at 2.5 words per second.
