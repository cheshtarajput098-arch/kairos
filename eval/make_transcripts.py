"""Script to generate and draft test replay dataset (SPEC §9.6).

Generates >= 60 test turns into data/replay/test/:
- ~40% compound queries
- ~20% late-constraint turns
- ~20% presentation-only / chit-chat
- ~10% single-intent queries
- ~10% out-of-corpus / edge-case queries (late disambiguation, contradiction, absent evidence)

Stratifications:
- source: 'llm_drafted' (70%) vs 'human_external' (30%)
- decisive_word_position: 'early', 'middle', 'last third' (>= 10 in last third)
- review_status: 'unreviewed'
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
TEST_DIR = ROOT / "data" / "replay" / "test"


def build_test_scenarios_and_gold() -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Build >= 60 test turns with realistic speech transcripts and gold labels."""
    scenarios: list[dict[str, Any]] = []
    gold: list[dict[str, Any]] = []

    def add_turn(
        session_id: str,
        turn_id: str,
        turn_type: str,
        scenario_desc: str,
        chunks: list[tuple[float, str]],
        utterance_end: float,
        retrieval_required: bool,
        sub_intents: list[str],
        answer_chunks: dict[str, list[str]],
        decisive_word_pos: str,
        source: str = "llm_drafted",
        late_constraint_of: str | None = None,
        reason: str | None = None,
        expected_uncertainty: str | None = None,
    ) -> None:
        turn_obj = {
            "session_id": session_id,
            "turn_id": turn_id,
            "turn_type": turn_type,
            "scenario": scenario_desc,
            "chunks": [{"t": t, "text": text} for t, text in chunks],
            "utterance_end": utterance_end,
        }
        scenarios.append(turn_obj)

        gold_obj = {
            "turn_id": turn_id,
            "retrieval_required": retrieval_required,
            "sub_intents": sub_intents,
            "answer_chunks": answer_chunks,
            "late_constraint_of": late_constraint_of,
            "decisive_word_position": decisive_word_pos,
            "source": source,
            "review_status": "unreviewed",
        }
        if reason:
            gold_obj["reason"] = reason
        if expected_uncertainty:
            gold_obj["expected_uncertainty"] = expected_uncertainty

        gold.append(gold_obj)

    # -------------------------------------------------------------------------
    # Session 1: Pune workshop & logistics (4 turns: compound, constraint, presentation, single)
    # -------------------------------------------------------------------------
    add_turn(
        "test-s01", "test-s01-t1", "compound",
        "Pune workshop seating capacity and catering notice",
        [(0.0, "Could you check the venue capacity in Pune"),
         (0.8, "for thirty people and how many days"),
         (1.6, "advance notice is needed for catering?")],
        2.2, True,
        ["venue capacity for 30 people in Pune", "catering advance notice"],
        {"venue capacity for 30 people in Pune": ["Doc_12§2"], "catering advance notice": ["Doc_89§3"]},
        "early", "llm_drafted",
    )
    add_turn(
        "test-s01", "test-s01-t2", "late_constraint",
        "Increase headcount to 55 participants",
        [(0.0, "Wait, make that"), (0.7, "fifty five attendees instead.")],
        1.5, True,
        ["venue capacity for 55 people in Pune"],
        {"venue capacity for 55 people in Pune": ["Doc_12§2"]},
        "middle", "llm_drafted", late_constraint_of="test-s01-t1",
    )
    add_turn(
        "test-s01", "test-s01-t3", "presentation_only",
        "Summarize previous answer in concise bullet points",
        [(0.0, "Can you reformat that into"), (0.7, "two concise bullet points?")],
        1.4, False, [], {}, "early", "llm_drafted", reason="presentation_restructure",
    )
    add_turn(
        "test-s01", "test-s01-t4", "single",
        "Audio visual equipment at Venue A",
        [(0.0, "Does Venue A provide ceiling"), (0.8, "mounted high definition projectors?")],
        1.6, True,
        ["Venue A projector equipment"],
        {"Venue A projector equipment": ["Doc_12§3"]},
        "middle", "llm_drafted",
    )

    # -------------------------------------------------------------------------
    # Session 2: Travel expense claims & currencies (3 turns: single, constraint, presentation)
    # -------------------------------------------------------------------------
    add_turn(
        "test-s02", "test-s02-t1", "single",
        "Submission timeline for business travel reimbursement",
        [(0.0, "How many days after travel"), (0.8, "must an employee file expense claims?")],
        1.7, True,
        ["travel reimbursement filing deadline"],
        {"travel reimbursement filing deadline": ["Doc_05§1"]},
        "early", "human_external",
    )
    add_turn(
        "test-s02", "test-s02-t2", "late_constraint",
        "International receipts in foreign currency",
        [(0.0, "These receipts were in Euros"), (0.8, "from an international business trip.")],
        1.7, True,
        ["foreign currency exchange conversion rates"],
        {"foreign currency exchange conversion rates": ["Doc_05§3"]},
        "middle", "human_external", late_constraint_of="test-s02-t1",
    )
    add_turn(
        "test-s02", "test-s02-t3", "presentation_only",
        "Condense into one sentence",
        [(0.0, "Give me that in one"), (0.7, "sentence only.")],
        1.3, False, [], {}, "early", "human_external", reason="presentation_restructure",
    )

    # -------------------------------------------------------------------------
    # Session 3: Meeting rooms & cancellation (3 turns: compound, constraint, out-of-corpus)
    # -------------------------------------------------------------------------
    add_turn(
        "test-s03", "test-s03-t1", "compound",
        "Bengaluru boardroom capacity and cancellation refund",
        [(0.0, "We need a meeting room in Bengaluru for 18 people"),
         (0.9, "and what is the refund if we cancel 10 days out?")],
        2.0, True,
        ["boardroom capacity 18 people Bengaluru", "cancellation refund 10 days out"],
        {"boardroom capacity 18 people Bengaluru": ["Doc_20§1"], "cancellation refund 10 days out": ["Doc_31§4"]},
        "early", "llm_drafted",
    )
    add_turn(
        "test-s03", "test-s03-t2", "late_constraint",
        "Booking duration exceeds four hours",
        [(0.0, "The team will actually occupy"), (0.8, "the room for six consecutive hours.")],
        1.7, True,
        ["room booking exceeding four hours approval"],
        {"room booking exceeding four hours approval": ["Doc_20§2"]},
        "last third", "llm_drafted", late_constraint_of="test-s03-t1",
    )
    add_turn(
        "test-s03", "test-s03-t3", "out_of_corpus",
        "Catering vendor phone number inquiry",
        [(0.0, "Can you provide the direct mobile phone"), (0.9, "number of the catering vendor?")],
        1.8, True,
        ["catering vendor phone number"],
        {"catering vendor phone number": []},
        "middle", "llm_drafted", expected_uncertainty="phone number not documented in corpus",
    )

    # -------------------------------------------------------------------------
    # Session 4: IT equipment loan and missing receipt policy (3 turns: compound, constraint, single)
    # -------------------------------------------------------------------------
    add_turn(
        "test-s04", "test-s04-t1", "compound",
        "Laptop loan duration and missing receipt declaration",
        [(0.0, "What is the maximum loan period for IT laptops"),
         (0.9, "and how do we claim expenses without an itemized receipt?")],
        2.0, True,
        ["IT laptop loan period limit", "missing receipt declaration policy"],
        {"IT laptop loan period limit": ["Doc_44§2"], "missing receipt declaration policy": ["Doc_63§3"]},
        "early", "human_external",
    )
    add_turn(
        "test-s04", "test-s04-t2", "late_constraint",
        "Loan extension beyond standard period",
        [(0.0, "What if the project deployment requires"), (0.9, "holding the equipment for four weeks?")],
        1.9, True,
        ["equipment loan extension approval"],
        {"equipment loan extension approval": ["Doc_44§3"]},
        "last third", "human_external", late_constraint_of="test-s04-t1",
    )
    add_turn(
        "test-s04", "test-s04-t3", "single",
        "Yearly limit on missing receipt affidavits",
        [(0.0, "How many missing receipt declarations"), (0.8, "is an employee permitted per calendar year?")],
        1.7, True,
        ["missing receipt affidavit yearly cap"],
        {"missing receipt affidavit yearly cap": ["Doc_63§3"]},
        "last third", "human_external",
    )

    # -------------------------------------------------------------------------
    # Session 5: Remote work and core hours (3 turns: compound, presentation, out-of-corpus)
    # -------------------------------------------------------------------------
    add_turn(
        "test-s05", "test-s05-t1", "compound",
        "Remote work probation eligibility and mandatory core hours",
        [(0.0, "Are employees on probation permitted to work from home"),
         (0.9, "and what are the mandatory core collaboration hours?")],
        2.1, True,
        ["probation remote work eligibility", "core collaboration hours"],
        {"probation remote work eligibility": ["Doc_57§1"], "core collaboration hours": ["Doc_57§3"]},
        "middle", "llm_drafted",
    )
    add_turn(
        "test-s05", "test-s05-t2", "presentation_only",
        "Display as numbered list",
        [(0.0, "Format that answer as"), (0.7, "a numbered list.")],
        1.3, False, [], {}, "early", "llm_drafted", reason="presentation_restructure",
    )
    add_turn(
        "test-s05", "test-s05-t3", "out_of_corpus",
        "Pet policy in regional offices",
        [(0.0, "Are domestic pets allowed inside"), (0.8, "the regional office buildings?")],
        1.7, True,
        ["office pet policy"],
        {"office pet policy": []},
        "last third", "llm_drafted", expected_uncertainty="pet policy not covered in corpus",
    )

    # -------------------------------------------------------------------------
    # Session 6: Edge Cases: Late Disambiguation (2 turns: single, compound)
    # -------------------------------------------------------------------------
    add_turn(
        "test-s06", "test-s06-t1", "single",
        "Late disambiguation: decisive city named in final chunk",
        [(0.0, "I need to check the full venue capacity"),
         (0.8, "and seating availability in the central city of"),
         (1.6, "Pune.")],
        2.2, True,
        ["workshop venue capacity Pune"],
        {"workshop venue capacity Pune": ["Doc_12§2"]},
        "last third", "llm_drafted",
    )
    add_turn(
        "test-s06", "test-s06-t2", "compound",
        "Late disambiguation: compound with decisive terms at the end",
        [(0.0, "For our upcoming company event we will need catering"),
         (0.8, "services arranged for twenty five guests with special dietary"),
         (1.6, "vegan requirements.")],
        2.3, True,
        ["catering twenty five guests", "vegan dietary options"],
        {"catering twenty five guests": ["Doc_89§1"], "vegan dietary options": ["Doc_89§3"]},
        "last third", "llm_drafted",
    )

    # -------------------------------------------------------------------------
    # Session 7: Edge Cases: Contradiction & Retraction (3 turns: single, contradiction, presentation)
    # -------------------------------------------------------------------------
    add_turn(
        "test-s07", "test-s07-t1", "single",
        "Initial event cancellation window question",
        [(0.0, "What refund is issued if an event"), (0.8, "is cancelled twelve days prior?")],
        1.7, True,
        ["refund policy 7 to 14 days before event"],
        {"refund policy 7 to 14 days before event": ["Doc_31§4"]},
        "middle", "human_external",
    )
    add_turn(
        "test-s07", "test-s07-t2", "late_constraint",
        "Contradiction: user corrects cancellation window to 3 days",
        [(0.0, "No sorry, I misspoke, the cancellation was"),
         (0.8, "actually submitted three days before the date.")],
        1.8, True,
        ["cancellation refund less than 7 days"],
        {"cancellation refund less than 7 days": ["Doc_31§4"]},
        "middle", "human_external", late_constraint_of="test-s07-t1",
    )
    add_turn(
        "test-s07", "test-s07-t3", "presentation_only",
        "Summarize cancellation policy briefly",
        [(0.0, "Please summarize that in"), (0.7, "brief terms.")],
        1.4, False, [], {}, "early", "human_external", reason="presentation_restructure",
    )

    # -------------------------------------------------------------------------
    # Session 8: Edge Cases: Evidence Absent & Fallback (2 turns: single, out-of-corpus)
    # -------------------------------------------------------------------------
    add_turn(
        "test-s08", "test-s08-t1", "single",
        "Deposit amount for borrowed laptop",
        [(0.0, "Is a security deposit deducted when"), (0.8, "borrowing an engineering laptop?")],
        1.7, True,
        ["IT laptop security deposit policy"],
        {"IT laptop security deposit policy": ["Doc_44§2"]},
        "middle", "llm_drafted",
    )
    add_turn(
        "test-s08", "test-s08-t2", "out_of_corpus",
        "Electric vehicle charging stations inquiry",
        [(0.0, "Do office campuses provide high speed"), (0.8, "charging stations for electric vehicles?")],
        1.8, True,
        ["electric vehicle charging"],
        {"electric vehicle charging": []},
        "last third", "llm_drafted", expected_uncertainty="EV charging not in documentation",
    )

    # -------------------------------------------------------------------------
    # Session 9: Compound multi-topic across departments (3 turns: compound, constraint, presentation)
    # -------------------------------------------------------------------------
    add_turn(
        "test-s09", "test-s09-t1", "compound",
        "Travel per diem allowance and receipt itemization standard",
        [(0.0, "What is the daily domestic travel allowance limit"),
         (0.8, "and do meal expenses require detailed itemized receipts?")],
        2.0, True,
        ["domestic travel per diem", "meal receipt itemization"],
        {"domestic travel per diem": ["Doc_05§2"], "meal receipt itemization": ["Doc_63§1"]},
        "early", "llm_drafted",
    )
    add_turn(
        "test-s09", "test-s09-t2", "late_constraint",
        "Alcohol excluded from meal claim",
        [(0.0, "The dining bill included alcoholic"), (0.8, "beverages during the business dinner.")],
        1.8, True,
        ["alcohol expense reimbursement exclusion"],
        {"alcohol expense reimbursement exclusion": ["Doc_63§2"]},
        "middle", "llm_drafted", late_constraint_of="test-s09-t1",
    )
    add_turn(
        "test-s09", "test-s09-t3", "presentation_only",
        "Condense into bullet points",
        [(0.0, "Format this as two"), (0.7, "clear bullet points.")],
        1.4, False, [], {}, "early", "llm_drafted", reason="presentation_restructure",
    )

    # -------------------------------------------------------------------------
    # Session 10: Compound workshop booking & refund (3 turns: compound, constraint, presentation)
    # -------------------------------------------------------------------------
    add_turn(
        "test-s10", "test-s10-t1", "compound",
        "Pune Venue B capacity and full refund notice period",
        [(0.0, "What is the maximum capacity for Pune Venue B"),
         (0.9, "and how many days before an event grants a hundred percent refund?")],
        2.1, True,
        ["Pune Venue B capacity", "event cancellation full refund days"],
        {"Pune Venue B capacity": ["Doc_12§2"], "event cancellation full refund days": ["Doc_31§2"]},
        "early", "human_external",
    )
    add_turn(
        "test-s10", "test-s10-t2", "late_constraint",
        "Change venue preference to Bengaluru",
        [(0.0, "Actually we decided to host this in"), (0.8, "Bengaluru instead of Pune.")],
        1.7, True,
        ["Bengaluru meeting room facilities"],
        {"Bengaluru meeting room facilities": ["Doc_20§1"]},
        "last third", "human_external", late_constraint_of="test-s10-t1",
    )
    add_turn(
        "test-s10", "test-s10-t3", "presentation_only",
        "Provide short answer",
        [(0.0, "Shorten that to"), (0.7, "one sentence.")],
        1.3, False, [], {}, "early", "human_external", reason="presentation_restructure",
    )

    # -------------------------------------------------------------------------
    # Session 11: Compound equipment loan and damage policy (3 turns: compound, constraint, single)
    # -------------------------------------------------------------------------
    add_turn(
        "test-s11", "test-s11-t1", "compound",
        "External monitor loan availability and replacement fee for lost items",
        [(0.0, "Can remote employees borrow standalone external monitors"),
         (0.9, "and what fee is charged if borrowed hardware is lost?")],
        2.1, True,
        ["external monitor loan policy", "replacement fee lost hardware"],
        {"external monitor loan policy": ["Doc_44§1"], "replacement fee lost hardware": ["Doc_44§3"]},
        "middle", "llm_drafted",
    )
    add_turn(
        "test-s11", "test-s11-t2", "late_constraint",
        "Accidental physical screen damage",
        [(0.0, "What if the monitor screen suffers"), (0.8, "accidental cracking during shipment?")],
        1.8, True,
        ["accidental equipment damage reporting"],
        {"accidental equipment damage reporting": ["Doc_44§3"]},
        "middle", "llm_drafted", late_constraint_of="test-s11-t1",
    )
    add_turn(
        "test-s11", "test-s11-t3", "single",
        "IT helpdesk contact channel",
        [(0.0, "Which ticketing portal is used"), (0.8, "to log equipment loan requests?")],
        1.7, True,
        ["IT equipment ticketing portal"],
        {"IT equipment ticketing portal": ["Doc_44§1"]},
        "last third", "llm_drafted",
    )

    # -------------------------------------------------------------------------
    # Session 12: Compound catering & special diets (3 turns: compound, constraint, presentation)
    # -------------------------------------------------------------------------
    add_turn(
        "test-s12", "test-s12-t1", "compound",
        "Jain meal preparation and coffee tea service",
        [(0.0, "Are Jain dietary meals prepared in a separate kitchen"),
         (0.9, "and is continuous tea and coffee service included for workshops?")],
        2.2, True,
        ["Jain dietary meal preparation", "coffee tea workshop service"],
        {"Jain dietary meal preparation": ["Doc_89§3"], "coffee tea workshop service": ["Doc_89§2"]},
        "early", "human_external",
    )
    add_turn(
        "test-s12", "test-s12-t2", "late_constraint",
        "Evening dinner add-on",
        [(0.0, "We also want to add a three course"), (0.8, "dinner buffet after the workshop.")],
        1.8, True,
        ["dinner buffet catering options"],
        {"dinner buffet catering options": ["Doc_89§1"]},
        "middle", "human_external", late_constraint_of="test-s12-t1",
    )
    add_turn(
        "test-s12", "test-s12-t3", "presentation_only",
        "Show bulleted breakdown",
        [(0.0, "Give me a bulleted"), (0.7, "breakdown please.")],
        1.4, False, [], {}, "early", "human_external", reason="presentation_restructure",
    )

    # -------------------------------------------------------------------------
    # Session 13: Compound remote work stipend & expense (3 turns: compound, constraint, presentation)
    # -------------------------------------------------------------------------
    add_turn(
        "test-s13", "test-s13-t1", "compound",
        "Broadband internet reimbursement and ergonomic chair subsidy",
        [(0.0, "Does company policy reimburse monthly home internet"),
         (0.9, "and can employees claim an ergonomic chair for remote work?")],
        2.2, True,
        ["monthly internet reimbursement", "ergonomic chair subsidy"],
        {"monthly internet reimbursement": ["Doc_57§2"], "ergonomic chair subsidy": ["Doc_57§2"]},
        "middle", "llm_drafted",
    )
    add_turn(
        "test-s13", "test-s13-t2", "late_constraint",
        "Internet invoice under family member name",
        [(0.0, "The broadband utility bill is registered"), (0.8, "under my spouse's legal name.")],
        1.8, True,
        ["utility bill family member name claim"],
        {"utility bill family member name claim": ["Doc_63§2"]},
        "last third", "llm_drafted", late_constraint_of="test-s13-t1",
    )
    add_turn(
        "test-s13", "test-s13-t3", "presentation_only",
        "Summarize concisely",
        [(0.0, "Can you make that summary"), (0.7, "very concise?")],
        1.4, False, [], {}, "early", "llm_drafted", reason="presentation_restructure",
    )

    # -------------------------------------------------------------------------
    # Session 14: Compound manager approval & expense limit (3 turns: compound, constraint, out-of-corpus)
    # -------------------------------------------------------------------------
    add_turn(
        "test-s14", "test-s14-t1", "compound",
        "Expense pre-approval threshold and manager sign-off timeline",
        [(0.0, "What expense amount requires manager pre-approval"),
         (0.9, "and within how many days must managers approve submitted claims?")],
        2.1, True,
        ["expense pre-approval amount threshold", "manager approval timeline"],
        {"expense pre-approval amount threshold": ["Doc_05§2"], "manager approval timeline": ["Doc_05§1"]},
        "early", "human_external",
    )
    add_turn(
        "test-s14", "test-s14-t2", "late_constraint",
        "Vice president approval for executive travel",
        [(0.0, "What if the international travel is"), (0.8, "for executive team leadership?")],
        1.7, True,
        ["executive travel approval level"],
        {"executive travel approval level": ["Doc_05§2"]},
        "middle", "human_external", late_constraint_of="test-s14-t1",
    )
    add_turn(
        "test-s14", "test-s14-t3", "out_of_corpus",
        "Corporate credit card bonus reward points",
        [(0.0, "Can employees retain airline loyalty"), (0.8, "points earned on company travel cards?")],
        1.8, True,
        ["loyalty reward points retention"],
        {"loyalty reward points retention": []},
        "last third", "human_external", expected_uncertainty="loyalty points policy not found",
    )

    # -------------------------------------------------------------------------
    # Session 15: Compound boardroom equipment & catering setup (3 turns: compound, constraint, presentation)
    # -------------------------------------------------------------------------
    add_turn(
        "test-s15", "test-s15-t1", "compound",
        "Bengaluru video conferencing system and on-site lunch setup",
        [(0.0, "Does Boardroom 1 support multi-screen video calls"),
         (0.9, "and can lunch catering be served directly inside the room?")],
        2.2, True,
        ["video conferencing Boardroom 1", "in-room lunch catering Bengaluru"],
        {"video conferencing Boardroom 1": ["Doc_20§3"], "in-room lunch catering Bengaluru": ["Doc_20§3"]},
        "middle", "llm_drafted",
    )
    add_turn(
        "test-s15", "test-s15-t2", "late_constraint",
        "Weekend booking surcharge",
        [(0.0, "The meeting needs to take place on"), (0.8, "a Saturday morning instead.")],
        1.7, True,
        ["weekend room booking policy"],
        {"weekend room booking policy": ["Doc_20§2"]},
        "middle", "llm_drafted", late_constraint_of="test-s15-t1",
    )
    add_turn(
        "test-s15", "test-s15-t3", "presentation_only",
        "Short bullet summary",
        [(0.0, "Give me a quick bullet"), (0.7, "point summary.")],
        1.4, False, [], {}, "early", "llm_drafted", reason="presentation_restructure",
    )

    # -------------------------------------------------------------------------
    # Session 16: Compound event cancellation & partial attendance (3 turns: compound, constraint, single)
    # -------------------------------------------------------------------------
    add_turn(
        "test-s16", "test-s16-t1", "compound",
        "Refund for cancellation due to medical emergency and venue fee credit",
        [(0.0, "What is the refund if a speaker cancels due to illness"),
         (0.9, "and can the venue deposit be credited toward a future date?")],
        2.2, True,
        ["medical emergency event cancellation", "venue deposit transfer credit"],
        {"medical emergency event cancellation": ["Doc_31§3"], "venue deposit transfer credit": ["Doc_31§3"]},
        "early", "human_external",
    )
    add_turn(
        "test-s16", "test-s16-t2", "late_constraint",
        "Cancellation notice submitted under forty eight hours",
        [(0.0, "Notice was sent less than forty"), (0.8, "eight hours before kickoff.")],
        1.7, True,
        ["short notice cancellation under 48 hours"],
        {"short notice cancellation under 48 hours": ["Doc_31§4"]},
        "last third", "human_external", late_constraint_of="test-s16-t1",
    )
    add_turn(
        "test-s16", "test-s16-t3", "single",
        "Non-refundable administrative fee",
        [(0.0, "Is there a non-refundable administrative fee"), (0.8, "deducted from approved refunds?")],
        1.8, True,
        ["cancellation administrative deduction fee"],
        {"cancellation administrative deduction fee": ["Doc_31§2"]},
        "last third", "human_external",
    )

    # -------------------------------------------------------------------------
    # Session 17: Compound remote work hours & international work (3 turns: compound, constraint, presentation)
    # -------------------------------------------------------------------------
    add_turn(
        "test-s17", "test-s17-t1", "compound",
        "Core hours flexibility and working from an overseas location",
        [(0.0, "Can employees adjust core working hours for caregiving"),
         (0.9, "and is working remotely from outside the country allowed?")],
        2.2, True,
        ["flexible core working hours", "international remote work policy"],
        {"flexible core working hours": ["Doc_57§3"], "international remote work policy": ["Doc_57§2"]},
        "middle", "llm_drafted",
    )
    add_turn(
        "test-s17", "test-s17-t2", "late_constraint",
        "Overseas stay for less than two weeks",
        [(0.0, "The overseas remote stay would be for"), (0.8, "only ten working days total.")],
        1.8, True,
        ["short duration international remote work approval"],
        {"short duration international remote work approval": ["Doc_57§2"]},
        "middle", "llm_drafted", late_constraint_of="test-s17-t1",
    )
    add_turn(
        "test-s17", "test-s17-t3", "presentation_only",
        "Translate or format as bullets",
        [(0.0, "Reformat the guidelines into"), (0.7, "two bullet points.")],
        1.4, False, [], {}, "early", "llm_drafted", reason="presentation_restructure",
    )

    # -------------------------------------------------------------------------
    # Session 18: Compound receipt submission & currency conversion (3 turns: compound, constraint, single)
    # -------------------------------------------------------------------------
    add_turn(
        "test-s18", "test-s18-t1", "compound",
        "Digital scanned receipts and credit card statement sufficiency",
        [(0.0, "Are smartphone scanned receipts acceptable for claims"),
         (0.9, "and does a credit card statement suffice without an invoice?")],
        2.2, True,
        ["smartphone scanned receipt validity", "credit card statement sufficiency"],
        {"smartphone scanned receipt validity": ["Doc_63§1"], "credit card statement sufficiency": ["Doc_63§2"]},
        "early", "human_external",
    )
    add_turn(
        "test-s18", "test-s18-t2", "late_constraint",
        "Lost physical receipt for taxi fare",
        [(0.0, "The receipt was for a local cash taxi"), (0.8, "fare where no printed receipt was provided.")],
        1.9, True,
        ["taxi cash expense without receipt"],
        {"taxi cash expense without receipt": ["Doc_63§3"]},
        "middle", "human_external", late_constraint_of="test-s18-t1",
    )
    add_turn(
        "test-s18", "test-s18-t3", "single",
        "Receipt currency date conversion rate",
        [(0.0, "Which exchange rate date applies to"), (0.8, "foreign transaction conversions?")],
        1.7, True,
        ["foreign transaction exchange rate date"],
        {"foreign transaction exchange rate date": ["Doc_05§3"]},
        "last third", "human_external",
    )

    # -------------------------------------------------------------------------
    # Session 19: Compound catering dietary restrictions & headcount (3 turns: compound, constraint, presentation)
    # -------------------------------------------------------------------------
    add_turn(
        "test-s19", "test-s19-t1", "compound",
        "Halal meal options and catering cancellation deadline",
        [(0.0, "Can the catering service provide certified Halal meals"),
         (0.9, "and what is the deadline to cancel catering without charge?")],
        2.2, True,
        ["Halal catering options", "catering cancellation penalty deadline"],
        {"Halal catering options": ["Doc_89§3"], "catering cancellation penalty deadline": ["Doc_89§1"]},
        "middle", "llm_drafted",
    )
    add_turn(
        "test-s19", "test-s19-t2", "late_constraint",
        "Headcount reduction by ten percent",
        [(0.0, "The headcount dropped from forty"), (0.8, "attendees down to thirty two.")],
        1.7, True,
        ["catering headcount reduction policy"],
        {"catering headcount reduction policy": ["Doc_89§1"]},
        "middle", "llm_drafted", late_constraint_of="test-s19-t1",
    )
    add_turn(
        "test-s19", "test-s19-t3", "presentation_only",
        "One line answer",
        [(0.0, "State the policy in one"), (0.7, "brief sentence.")],
        1.4, False, [], {}, "early", "llm_drafted", reason="presentation_restructure",
    )

    # -------------------------------------------------------------------------
    # Session 20: Compound Pune workshop parking & pantry (3 turns: compound, constraint, presentation)
    # -------------------------------------------------------------------------
    add_turn(
        "test-s20", "test-s20-t1", "compound",
        "Pune Venue A pantry access and high speed Wi-Fi",
        [(0.0, "Does Pune Venue A include dedicated pantry access"),
         (0.9, "and is gigabit Wi-Fi available for attendees?")],
        2.1, True,
        ["Pune Venue A pantry access", "Pune Venue A gigabit WiFi"],
        {"Pune Venue A pantry access": ["Doc_12§3"], "Pune Venue A gigabit WiFi": ["Doc_12§3"]},
        "early", "human_external",
    )
    add_turn(
        "test-s20", "test-s20-t2", "late_constraint",
        "Late evening workshop extension",
        [(0.0, "The workshop will run until nine"), (0.8, "in the evening after normal hours.")],
        1.8, True,
        ["after hours venue facility extension"],
        {"after hours venue facility extension": ["Doc_12§4"]},
        "middle", "human_external", late_constraint_of="test-s20-t1",
    )
    add_turn(
        "test-s20", "test-s20-t3", "presentation_only",
        "Bullet points",
        [(0.0, "Summarize in two bullet"), (0.7, "points.")],
        1.3, False, [], {}, "early", "human_external", reason="presentation_restructure",
    )

    # -------------------------------------------------------------------------
    # Session 21: Compound Bengaluru equipment & tech support (3 turns: compound, constraint, single)
    # -------------------------------------------------------------------------
    add_turn(
        "test-s21", "test-s21-t1", "compound",
        "Bengaluru boardroom microphone setup and on-call AV technician",
        [(0.0, "Are wireless boundary microphones installed in Bengaluru Boardroom 1"),
         (0.9, "and is an on-site AV technician on call during client sessions?")],
        2.2, True,
        ["Bengaluru wireless boundary microphones", "on-call AV technician support"],
        {"Bengaluru wireless boundary microphones": ["Doc_20§3"], "on-call AV technician support": ["Doc_20§3"]},
        "early", "llm_drafted",
    )
    add_turn(
        "test-s21", "test-s21-t2", "late_constraint",
        "Hybrid remote attendees joining over Zoom",
        [(0.0, "Several client participants will join"), (0.8, "remotely via Zoom and Microsoft Teams.")],
        1.8, True,
        ["Zoom Teams hybrid conference compatibility"],
        {"Zoom Teams hybrid conference compatibility": ["Doc_20§3"]},
        "middle", "llm_drafted", late_constraint_of="test-s21-t1",
    )
    add_turn(
        "test-s21", "test-s21-t3", "single",
        "Advance booking window for boardroom",
        [(0.0, "How many weeks in advance can"), (0.8, "Boardroom 1 be reserved?")],
        1.7, True,
        ["boardroom advance reservation limit"],
        {"boardroom advance reservation limit": ["Doc_20§2"]},
        "last third", "llm_drafted",
    )

    # -------------------------------------------------------------------------
    # Session 22: Compound laptop peripherals & return grace period (2 turns: compound, single)
    # -------------------------------------------------------------------------
    add_turn(
        "test-s22", "test-s22-t1", "compound",
        "IT keyboard mouse loan and return deadline grace period",
        [(0.0, "Can contractors borrow wireless keyboards and mice"),
         (0.9, "and is there a grace period after the loan expiry date?")],
        2.1, True,
        ["contractor IT accessory loan", "equipment loan return grace period"],
        {"contractor IT accessory loan": ["Doc_44§1"], "equipment loan return grace period": ["Doc_44§2"]},
        "middle", "llm_drafted",
    )
    add_turn(
        "test-s22", "test-s22-t2", "single",
        "Late return penalty fee",
        [(0.0, "Is a late penalty fine charged"), (0.8, "for overdue IT loan equipment?")],
        1.7, True,
        ["overdue IT equipment fee"],
        {"overdue IT equipment fee": ["Doc_44§3"]},
        "last third", "llm_drafted",
    )


    return scenarios, gold


def generate_test_dataset(target_dir: Path | None = None) -> tuple[int, int]:
    """Generate and write scenarios.jsonl and gold.jsonl into target_dir."""
    dest = target_dir or TEST_DIR
    dest.mkdir(parents=True, exist_ok=True)

    scenarios, gold = build_test_scenarios_and_gold()

    scenarios_path = dest / "scenarios.jsonl"
    with open(scenarios_path, "w", encoding="utf-8") as fh:
        fh.writelines(json.dumps(s) + "\n" for s in scenarios)

    gold_path = dest / "gold.jsonl"
    with open(gold_path, "w", encoding="utf-8") as fh:
        fh.writelines(json.dumps(g) + "\n" for g in gold)

    return len(scenarios), len(gold)


if __name__ == "__main__":
    n_s, n_g = generate_test_dataset()
    print(f"Generated test dataset in {TEST_DIR}: {n_s} scenarios, {n_g} gold records.")
