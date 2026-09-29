"""Generate an aesthetic, professional 16-slide PowerPoint deck for Kairos.

Adheres strictly to the Calm Precision design language:
- 16:9 Widescreen (13.333" x 7.5")
- Deep Obsidian background (#0E1014)
- Ice Blue (#8FB3FF) and Emerald (#6FD39A) accents
- Card-based layouts with high-contrast text
- Embedded high-res architecture diagram on Slide 4
- Formatted metrics and acceptance gate tables
"""
import os
import sys
from pathlib import Path
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

# Paths
REPO_ROOT = Path(__file__).resolve().parent.parent
DOCS_PRES = REPO_ROOT / "docs" / "presentation"
OUTPUT_PPTX_DOCS = DOCS_PRES / "Kairos_Presentation.pptx"
OUTPUT_PPTX_ROOT = REPO_ROOT / "Kairos_Presentation.pptx"
ARCH_DIAGRAM = DOCS_PRES / "kairos_architecture_diagram.jpg"
LOGO_IMG = REPO_ROOT / "docs" / "kairos-logo.jpg"

# Palette
BG_COLOR = RGBColor(14, 16, 20)       # #0E1014
CARD_BG = RGBColor(21, 24, 30)        # #15181E
CARD_BORDER = RGBColor(35, 41, 52)    # #232934
ACCENT_BLUE = RGBColor(143, 179, 255) # #8FB3FF
ACCENT_GREEN = RGBColor(111, 211, 154)# #6FD39A
ACCENT_AMBER = RGBColor(245, 166, 35) # #F5A623
TEXT_PRIMARY = RGBColor(236, 233, 226)# #ECE9E2
TEXT_MUTED = RGBColor(163, 169, 181)  # #A3A9B5
TEXT_DIM = RGBColor(125, 133, 148)    # #7D8594
CARD_HIGHLIGHT = RGBColor(27, 32, 42)

def set_slide_background(slide):
    background = slide.background
    fill = background.fill
    fill.solid()
    fill.fore_color.rgb = BG_COLOR

def add_header(slide, slide_num, category, title, subtitle=None):
    set_slide_background(slide)
    
    # Category tag & Slide number
    header_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(11.733), Inches(0.4))
    tf = header_box.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0
    p = tf.paragraphs[0]
    p.text = category.upper()
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = ACCENT_BLUE
    p.font.name = "Arial"
    
    # Slide Number on Right
    num_box = slide.shapes.add_textbox(Inches(10.5), Inches(0.4), Inches(2.0), Inches(0.4))
    ntf = num_box.text_frame
    ntf.word_wrap = True
    ntf.margin_left = ntf.margin_top = ntf.margin_right = ntf.margin_bottom = 0
    np = ntf.paragraphs[0]
    np.text = f"{slide_num:02d} / 16"
    np.alignment = PP_ALIGN.RIGHT
    np.font.size = Pt(11)
    np.font.color.rgb = TEXT_DIM
    np.font.name = "Arial"
    
    # Title
    title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.75), Inches(11.733), Inches(0.8))
    ttf = title_box.text_frame
    ttf.word_wrap = True
    ttf.margin_left = ttf.margin_top = ttf.margin_right = ttf.margin_bottom = 0
    tp = ttf.paragraphs[0]
    tp.text = title
    tp.font.size = Pt(26)
    tp.font.bold = True
    tp.font.color.rgb = TEXT_PRIMARY
    tp.font.name = "Georgia"
    
    if subtitle:
        sp = ttf.add_paragraph()
        sp.text = subtitle
        sp.font.size = Pt(13)
        sp.font.color.rgb = TEXT_MUTED
        sp.font.name = "Arial"

def add_card(slide, left, top, width, height, bg_color=CARD_BG, border_color=CARD_BORDER):
    shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    shape.fill.solid()
    shape.fill.fore_color.rgb = bg_color
    shape.line.color.rgb = border_color
    shape.line.width = Pt(1)
    return shape

def add_speaker_note(slide, note_text):
    notes_slide = slide.notes_slide
    text_frame = notes_slide.notes_text_frame
    text_frame.text = note_text

def build_presentation():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]
    
    # =========================================================================
    # SLIDE 1: Title Slide
    # =========================================================================
    slide1 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide1)
    
    # Main hero card
    add_card(slide1, Inches(0.8), Inches(0.8), Inches(11.733), Inches(5.9), bg_color=CARD_BG)
    
    # Subtitle / Hackathon badge
    badge = slide1.shapes.add_textbox(Inches(1.5), Inches(1.3), Inches(10.0), Inches(0.4))
    btf = badge.text_frame
    bp = btf.paragraphs[0]
    bp.text = "SAMSUNG PRISM GENAI HACKATHON 2026 · THEME 04: STREAMING LIVE RAG"
    bp.font.size = Pt(12)
    bp.font.bold = True
    bp.font.color.rgb = ACCENT_BLUE
    bp.font.name = "Arial"
    
    # Title
    tbox = slide1.shapes.add_textbox(Inches(1.5), Inches(1.8), Inches(10.3), Inches(1.8))
    ttf = tbox.text_frame
    ttf.word_wrap = True
    tp = ttf.paragraphs[0]
    tp.text = "KAIROS"
    tp.font.size = Pt(54)
    tp.font.bold = True
    tp.font.color.rgb = TEXT_PRIMARY
    tp.font.name = "Georgia"
    
    tp2 = ttf.add_paragraph()
    tp2.text = "Streaming Live RAG That Answers While You Speak"
    tp2.font.size = Pt(28)
    tp2.font.color.rgb = ACCENT_GREEN
    tp2.font.name = "Georgia"
    
    # Subtitle description
    desc_box = slide1.shapes.add_textbox(Inches(1.5), Inches(3.7), Inches(9.5), Inches(1.0))
    dtf = desc_box.text_frame
    dtf.word_wrap = True
    dp = dtf.paragraphs[0]
    dp.text = "Event-Driven Speculative Retrieval, Multi-Intent Decomposition & In-Place State Evolution\nOptimized for 100% Offline Local CPU Inference"
    dp.font.size = Pt(15)
    dp.font.color.rgb = TEXT_MUTED
    dp.font.name = "Arial"
    
    # Author Footer Card
    auth_box = slide1.shapes.add_textbox(Inches(1.5), Inches(5.2), Inches(10.0), Inches(1.0))
    atf = auth_box.text_frame
    atf.word_wrap = True
    ap1 = atf.paragraphs[0]
    ap1.text = "Presenter: Cheshta Rajput"
    ap1.font.size = Pt(16)
    ap1.font.bold = True
    ap1.font.color.rgb = TEXT_PRIMARY
    ap1.font.name = "Arial"
    
    ap2 = atf.add_paragraph()
    ap2.text = "Team Coding Agent RIT · M S Ramaiah Institute of Technology, Bengaluru"
    ap2.font.size = Pt(13)
    ap2.font.color.rgb = TEXT_DIM
    ap2.font.name = "Arial"
    
    add_speaker_note(slide1, "Good morning judges. We are Team Coding Agent RIT. Today we present Kairos — an event-driven live streaming RAG engine that eliminates the awkward conversational silence of voice assistants by answering while you speak.")
    
    # =========================================================================
    # SLIDE 2: Core Problem
    # =========================================================================
    slide2 = prs.slides.add_slide(blank_layout)
    add_header(slide2, 2, "Problem Statement", "Traditional Voice RAG Imposes Painful Conversational Pauses",
               "Conventional pipelines create severe latency bottlenecks and break under conversational speech dynamics")
    
    cols = [
        ("3.5 – 5.0 s", "Awkward Silence", "Sequential batch processing (Listen -> ASR -> Retrieve -> LLM) leaves users waiting in complete silence after speaking.", RGBColor(255, 123, 114)),
        ("Failure", "On Compound Questions", "Natural queries ('I need a venue in Pune for 40 people and what's the refund policy?') are sent as one noisy vector search.", ACCENT_AMBER),
        ("100% Waste", "On Detail Revisions", "Late self-repairs ('Actually make that 60 people') force naive engines to discard state and re-execute entire turns.", TEXT_MUTED),
    ]
    for i, (val, label, desc, val_col) in enumerate(cols):
        left = Inches(0.8 + i * 4.0)
        add_card(slide2, left, Inches(2.0), Inches(3.733), Inches(4.7))
        
        box = slide2.shapes.add_textbox(left + Inches(0.3), Inches(2.3), Inches(3.133), Inches(4.0))
        tf = box.text_frame
        tf.word_wrap = True
        
        p = tf.paragraphs[0]
        p.text = val
        p.font.size = Pt(36)
        p.font.bold = True
        p.font.color.rgb = val_col
        p.font.name = "Georgia"
        
        p2 = tf.add_paragraph()
        p2.text = label
        p2.font.size = Pt(18)
        p2.font.bold = True
        p2.font.color.rgb = TEXT_PRIMARY
        p2.font.name = "Arial"
        p2.space_before = Pt(14)
        
        p3 = tf.add_paragraph()
        p3.text = desc
        p3.font.size = Pt(13)
        p3.font.color.rgb = TEXT_MUTED
        p3.font.name = "Arial"
        p3.space_before = Pt(10)
        
    add_speaker_note(slide2, "When you speak to standard voice assistants, they wait until you finish talking, take several seconds to search, and then respond. If you ask two questions at once or correct yourself, they stumble. Voice interaction demands real-time intelligence.")

    # =========================================================================
    # SLIDE 3: The Kairos Solution
    # =========================================================================
    slide3 = prs.slides.add_slide(blank_layout)
    add_header(slide3, 3, "Core Innovation", "What Makes Kairos Different: Answering While You Speak",
               "Three architectural differentiators engineered specifically for live streaming voice interactions")
    
    diffs = [
        ("65.4%", "Ready-at-End Drafting", "Kairos evaluates speech prefix chunks mid-utterance, predicts search necessity, and synthesizes verified answer drafts BEFORE you stop talking.", ACCENT_GREEN),
        ("Two-Speed", "Grounded Synthesis", "Speed 1 delivers an instant verbatim candidate in < 1ms; Speed 2 generates a fluent local rewrite (< 820ms) passing the strict Grounding Gate.", ACCENT_BLUE),
        ("Gate G5", "In-Place Delta Evolution", "When late details arrive, the Session Delta Engine patches only the affected claim while preserving unaffected claims 100% byte-identical.", ACCENT_AMBER),
    ]
    for i, (val, label, desc, val_col) in enumerate(diffs):
        left = Inches(0.8 + i * 4.0)
        add_card(slide3, left, Inches(2.0), Inches(3.733), Inches(4.7))
        
        box = slide3.shapes.add_textbox(left + Inches(0.3), Inches(2.3), Inches(3.133), Inches(4.0))
        tf = box.text_frame
        tf.word_wrap = True
        
        p = tf.paragraphs[0]
        p.text = val
        p.font.size = Pt(34)
        p.font.bold = True
        p.font.color.rgb = val_col
        p.font.name = "Georgia"
        
        p2 = tf.add_paragraph()
        p2.text = label
        p2.font.size = Pt(18)
        p2.font.bold = True
        p2.font.color.rgb = TEXT_PRIMARY
        p2.font.name = "Arial"
        p2.space_before = Pt(14)
        
        p3 = tf.add_paragraph()
        p3.text = desc
        p3.font.size = Pt(13)
        p3.font.color.rgb = TEXT_MUTED
        p3.font.name = "Arial"
        p3.space_before = Pt(10)
        
    add_speaker_note(slide3, "Kairos breaks the sequential barrier. By moving retrieval and draft synthesis into the utterance window, the answer is already verified the millisecond speech stops.")

    # =========================================================================
    # SLIDE 4: System Architecture (With Embedded Architecture Diagram)
    # =========================================================================
    slide4 = prs.slides.add_slide(blank_layout)
    add_header(slide4, 4, "System Architecture", "Parsimonious 5-Stage Live Streaming Pipeline",
               "Zero external agent frameworks (no LangChain, no LlamaIndex) · Single asyncio event loop · Strict stage budgets")
    
    # Embed high-resolution Gemini architecture diagram
    if ARCH_DIAGRAM.exists():
        # Add card backdrop
        add_card(slide4, Inches(0.8), Inches(1.8), Inches(11.733), Inches(4.8), bg_color=CARD_BG)
        # Embed diagram spanning nicely
        slide4.shapes.add_picture(str(ARCH_DIAGRAM), Inches(0.9), Inches(1.9), Inches(11.533), Inches(4.6))
    else:
        # Fallback text card
        add_card(slide4, Inches(0.8), Inches(1.8), Inches(11.733), Inches(4.8))
        box = slide4.shapes.add_textbox(Inches(1.2), Inches(2.2), Inches(11.0), Inches(4.0))
        tf = box.text_frame
        p = tf.paragraphs[0]
        p.text = "5-Stage Pipeline Architecture Diagram"
        p.font.size = Pt(20)
        p.font.color.rgb = ACCENT_BLUE

    add_speaker_note(slide4, "Our architecture follows strict architectural parsimony: one asyncio event loop, five stages, zero framework bloat. Every stage has a justified microsecond budget.")

    # =========================================================================
    # SLIDE 5: Stage 1 - Controller
    # =========================================================================
    slide5 = prs.slides.add_slide(blank_layout)
    add_header(slide5, 5, "Stage 1: Streaming Controller", "Retrieval Controller & Speculation Manager",
               "Sub-millisecond decisions per chunk: WAIT, RETRIEVE, or SUPPRESS based on acoustic and linguistic features")
    
    # 3 decision cards
    decisions = [
        ("WAIT", "Syntactic Openness", "Holds dispatch when utterances are incomplete or semantic drift between chunks exceeds threshold.\n\n• Entity saturation check\n• Embedding delta tracker\n• Zero premature searches", ACCENT_AMBER),
        ("RETRIEVE", "Early Dispatch", "Fires speculative retrieval as soon as prefix information stabilizes, well before speech ends.\n\n• Prefix-hash lookup\n• Parallel leg branching\n• Lead time: median 1.80s", ACCENT_GREEN),
        ("SUPPRESS", "Presentation Intents", "Detects structural requests ('show as bullets', 'summarize', 'table') and inhibits corpus search.\n\n• 100% suppression rate\n• Zero vector waste\n• Immediate in-memory transform", ACCENT_BLUE),
    ]
    for i, (dec, subtitle, body, col) in enumerate(decisions):
        left = Inches(0.8 + i * 4.0)
        add_card(slide5, left, Inches(2.0), Inches(3.733), Inches(4.7))
        box = slide5.shapes.add_textbox(left + Inches(0.3), Inches(2.3), Inches(3.133), Inches(4.0))
        tf = box.text_frame
        tf.word_wrap = True
        
        p = tf.paragraphs[0]
        p.text = dec
        p.font.size = Pt(28)
        p.font.bold = True
        p.font.color.rgb = col
        p.font.name = "Arial"
        
        p2 = tf.add_paragraph()
        p2.text = subtitle
        p2.font.size = Pt(16)
        p2.font.bold = True
        p2.font.color.rgb = TEXT_PRIMARY
        p2.space_before = Pt(8)
        
        p3 = tf.add_paragraph()
        p3.text = body
        p3.font.size = Pt(13)
        p3.font.color.rgb = TEXT_MUTED
        p3.space_before = Pt(12)
        
    add_speaker_note(slide5, "Stage 1 monitors linguistic stability. It knows when enough information has arrived to begin searching, while suppressing searches when users merely ask to change format.")

    # =========================================================================
    # SLIDE 6: Stage 2 & 3 - Decomposer & Hybrid Retrieval
    # =========================================================================
    slide6 = prs.slides.add_slide(blank_layout)
    add_header(slide6, 6, "Stages 2 & 3: Decomposition & Retrieval", "Multi-Intent Decomposition & Hybrid Retrieval",
               "Speech disfluency normalization, parallel search legs, and Reciprocal Rank Fusion")
    
    # 2 large cards
    add_card(slide6, Inches(0.8), Inches(2.0), Inches(5.666), Inches(4.7))
    box1 = slide6.shapes.add_textbox(Inches(1.1), Inches(2.3), Inches(5.066), Inches(4.0))
    tf1 = box1.text_frame
    tf1.word_wrap = True
    
    p = tf1.paragraphs[0]
    p.text = "Stage 2: Multi-Intent Decomposer"
    p.font.size = Pt(20)
    p.font.bold = True
    p.font.color.rgb = ACCENT_BLUE
    
    bullets1 = [
        "Speech Disfluency Stripping: Filters acoustic filler ('uh', 'um') and resolves mid-sentence corrections ('Pune — no, Mumbai' -> Mumbai).",
        "Context Inheritance: Propagates entity and geographic constraints across split clauses seamlessly.",
        "Bounded Fan-Out: Hard cap of max 4 parallel legs with near-duplicate suppression (cosine > 0.90).",
        "Deterministic Leg IDs: Stable query leg identifiers ensure reproducible downstream fusion."
    ]
    for b in bullets1:
        bp = tf1.add_paragraph()
        bp.text = "• " + b
        bp.font.size = Pt(13)
        bp.font.color.rgb = TEXT_MUTED
        bp.space_before = Pt(10)
        
    add_card(slide6, Inches(6.866), Inches(2.0), Inches(5.666), Inches(4.7))
    box2 = slide6.shapes.add_textbox(Inches(7.166), Inches(2.3), Inches(5.066), Inches(4.0))
    tf2 = box2.text_frame
    tf2.word_wrap = True
    
    p = tf2.paragraphs[0]
    p.text = "Stage 3 & 4: Hybrid Search & Fusion"
    p.font.size = Pt(20)
    p.font.bold = True
    p.font.color.rgb = ACCENT_GREEN
    
    bullets2 = [
        "Dual Retrieval Engines: FastEmbed BGE-small dense embeddings concurrently executed with BM25s sparse index.",
        "Reciprocal Rank Fusion (RRF k=60): Deterministic score combination immune to score scale divergence.",
        "Prefix-Hash In-Memory Caching: Sub-millisecond instant retrieval for repeated query stems across chunks.",
        "400 ms Deadline Bounding: Speculative retrieval legs are automatically canceled if speech mutates."
    ]
    for b in bullets2:
        bp = tf2.add_paragraph()
        bp.text = "• " + b
        bp.font.size = Pt(13)
        bp.font.color.rgb = TEXT_MUTED
        bp.space_before = Pt(10)

    add_speaker_note(slide6, "When you ask compound questions, Stage 2 decomposes them into parallel search legs while inheriting context. Stage 3 fires hybrid search concurrently with deadline bounds.")

    # =========================================================================
    # SLIDE 7: Stage 5 - Two-Speed Grounded Synthesis
    # =========================================================================
    slide7 = prs.slides.add_slide(blank_layout)
    add_header(slide7, 7, "Stage 5: Synthesis & Grounding", "Two-Speed Grounded Synthesis & Local LLM",
               "Instant extractive answers followed by fluent local CPU rewrites under strict deterministic verification")
    
    cols7 = [
        ("< 1 ms", "Speed 1: Extractive", "Deterministic verbatim excerpt (<= 30 words) with exact [Doc_ID §Section] source attribution. Emitted instantly with zero hallucination risk.", ACCENT_GREEN),
        ("< 820 ms", "Speed 2: Grounded Rewrite", "Quantized Qwen2.5-1.5B-Instruct running locally on CPU. Delivers conversational fluency while restricted strictly to retrieved facts.", ACCENT_BLUE),
        ("0.0000", "Deterministic Gate (G4)", "Every single claim must map byte-for-byte to an indexed chunk ID and verbatim span. 3-strike circuit breaker falls back to Speed 1 if violated.", ACCENT_AMBER),
    ]
    for i, (val, label, desc, val_col) in enumerate(cols7):
        left = Inches(0.8 + i * 4.0)
        add_card(slide7, left, Inches(2.0), Inches(3.733), Inches(4.7))
        box = slide7.shapes.add_textbox(left + Inches(0.3), Inches(2.3), Inches(3.133), Inches(4.0))
        tf = box.text_frame
        tf.word_wrap = True
        
        p = tf.paragraphs[0]
        p.text = val
        p.font.size = Pt(34)
        p.font.bold = True
        p.font.color.rgb = val_col
        p.font.name = "Georgia"
        
        p2 = tf.add_paragraph()
        p2.text = label
        p2.font.size = Pt(18)
        p2.font.bold = True
        p2.font.color.rgb = TEXT_PRIMARY
        p2.space_before = Pt(14)
        
        p3 = tf.add_paragraph()
        p3.text = desc
        p3.font.size = Pt(13)
        p3.font.color.rgb = TEXT_MUTED
        p3.space_before = Pt(10)
        
    add_speaker_note(slide7, "Kairos delivers answers at two speeds: an instant verbatim answer in under 1 millisecond, followed by a fluent rewrite from local Qwen2.5 running right on your laptop CPU.")

    # =========================================================================
    # SLIDE 8: Measured Time Savings vs Sequential Baseline
    # =========================================================================
    slide8 = prs.slides.add_slide(blank_layout)
    add_header(slide8, 8, "Empirical Validation: Race Benchmark", "Measured Time Savings vs Sequential Batch Baseline",
               "Shared Virtual Clock Replay on 64-turn frozen test split (runs/eval/race.json)")
    
    # 2 Stat Cards on Left + Detailed comparison on Right
    add_card(slide8, Inches(0.8), Inches(2.0), Inches(3.6), Inches(2.2))
    b1 = slide8.shapes.add_textbox(Inches(1.0), Inches(2.2), Inches(3.2), Inches(1.8))
    t1 = b1.text_frame
    p = t1.paragraphs[0]
    p.text = "1.508 s"
    p.font.size = Pt(38)
    p.font.bold = True
    p.font.color.rgb = ACCENT_GREEN
    p.font.name = "Georgia"
    p2 = t1.add_paragraph()
    p2.text = "Median Time Saved / Turn\n100.0% of RETRIEVE turns saved time"
    p2.font.size = Pt(13)
    p2.font.color.rgb = TEXT_PRIMARY
    
    add_card(slide8, Inches(0.8), Inches(4.5), Inches(3.6), Inches(2.2))
    b2 = slide8.shapes.add_textbox(Inches(1.0), Inches(4.7), Inches(3.2), Inches(1.8))
    t2 = b2.text_frame
    p = t2.paragraphs[0]
    p.text = "0 Tokens"
    p.font.size = Pt(38)
    p.font.bold = True
    p.font.color.rgb = ACCENT_BLUE
    p.font.name = "Georgia"
    p2 = t2.add_paragraph()
    p2.text = "Restart Overhead\nZero prompt re-ingestion waste"
    p2.font.size = Pt(13)
    p2.font.color.rgb = TEXT_PRIMARY
    
    # Right Detailed Table Card
    add_card(slide8, Inches(4.8), Inches(2.0), Inches(7.733), Inches(4.7))
    br = slide8.shapes.add_textbox(Inches(5.1), Inches(2.3), Inches(7.133), Inches(4.0))
    tr = br.text_frame
    tr.word_wrap = True
    
    p = tr.paragraphs[0]
    p.text = "Virtual Clock Latency Distribution (n = 64 turns)"
    p.font.size = Pt(18)
    p.font.bold = True
    p.font.color.rgb = TEXT_PRIMARY
    
    comp_bullets = [
        "Sequential Batch Baseline p50 Latency: 3.708 s (waits for full speech end before starting)",
        "Kairos Ready-at-End p50 Latency: 2.200 s (answer verified before speech concludes)",
        "Mean Time Saved: 1.579 s per turn across all test scenarios",
        "Peak Time Saved: Up to 2.450 s saved on multi-clause complex utterances",
        "Hidden Retrieval Fraction: H = 1.0 (100% of retrieval latency hidden during speech)",
        "Full Telemetry Tracing: OpenTelemetry spans record microsecond timings for every stage"
    ]
    for b in comp_bullets:
        bp = tr.add_paragraph()
        bp.text = "• " + b
        bp.font.size = Pt(13)
        bp.font.color.rgb = TEXT_MUTED
        bp.space_before = Pt(8)
        
    add_speaker_note(slide8, "Compared to the sequential batch baseline on a shared virtual clock, Kairos saves a median 1.508 seconds per turn. Users experience zero waiting time.")

    # =========================================================================
    # SLIDE 9: Benchmark Acceptance Gates (Official & Strict)
    # =========================================================================
    slide9 = prs.slides.add_slide(blank_layout)
    add_header(slide9, 9, "Acceptance Gates", "All Six Benchmark Acceptance Gates: 100% PASS",
               "Measured on 64-Turn Frozen Test Split with n=112 claims (Source: runs/eval/gates.json)")
    
    # Table Card
    add_card(slide9, Inches(0.8), Inches(2.0), Inches(11.733), Inches(4.7))
    
    # Add Table shape
    rows, cols = 7, 5
    table_shape = slide9.shapes.add_table(rows, cols, Inches(1.1), Inches(2.2), Inches(11.133), Inches(4.2))
    table = table_shape.table
    table.columns[0].width = Inches(1.2)
    table.columns[1].width = Inches(3.6)
    table.columns[2].width = Inches(1.8)
    table.columns[3].width = Inches(2.8)
    table.columns[4].width = Inches(1.7)
    
    headers = ["Gate", "Metric Description", "Threshold", "Measured Result (n)", "Status"]
    for j, h in enumerate(headers):
        cell = table.cell(0, j)
        cell.fill.solid()
        cell.fill.fore_color.rgb = CARD_HIGHLIGHT
        cp = cell.text_frame.paragraphs[0]
        cp.text = h
        cp.font.bold = True
        cp.font.size = Pt(12)
        cp.font.color.rgb = ACCENT_BLUE
        
    gate_data = [
        ("G1", "Offline Container Reproducibility", "1.0", "1.0 (n=1, zero network)", "PASS"),
        ("G2", "Early Retrieval Triggering", ">= 0.80", "1.000 (n=52, 1.88s lead)", "PASS"),
        ("G3", "Multi-Intent Decomposition", ">= 0.70", "0.895 (n=19)", "PASS"),
        ("G4", "Grounding Integrity (Hallucinations)", "<= 0.00", "0.0000 (n=112 claims, 0 bad)", "PASS"),
        ("G5", "Selective State Continuity", "1.0", "1.000 (n=18, byte-identical)", "PASS"),
        ("G6", "Structured Telemetry Schema", "1.0", "1.000 (n=64, full OTel)", "PASS"),
    ]
    for i, row in enumerate(gate_data):
        for j, val in enumerate(row):
            cell = table.cell(i + 1, j)
            cell.fill.solid()
            cell.fill.fore_color.rgb = CARD_BG
            cp = cell.text_frame.paragraphs[0]
            cp.text = val
            cp.font.size = Pt(12)
            if j == 0:
                cp.font.bold = True
                cp.font.color.rgb = TEXT_PRIMARY
            elif j == 4:
                cp.font.bold = True
                cp.font.color.rgb = ACCENT_GREEN
            else:
                cp.font.color.rgb = TEXT_MUTED

    add_speaker_note(slide9, "All six official hackathon acceptance gates pass with flying colors. Most importantly, Gate G4 achieved exactly 0 fabricated citations across all 112 evaluated claims.")

    # =========================================================================
    # SLIDE 10: State Continuity & Delta Engine
    # =========================================================================
    slide10 = prs.slides.add_slide(blank_layout)
    add_header(slide10, 10, "Conversational Evolution", "Session Delta Engine: In-Place State Continuity",
               "Demonstrated via Demo Scenario 2: Business Travel Expense Policy (Doc_05)")
    
    turns = [
        ("Turn 1: Compound Query", "What is the filing deadline for domestic travel expenses, and what currency rate applies?",
         "Decomposes into Leg A (deadline) and Leg B (currency). Both retrieved and answered concurrently.", ACCENT_BLUE),
        ("Turn 2: Late Refinement", "Actually, what if the trip was international?",
         "Patches Claim 2 (international currency) while Claim 1 (filing deadline) remains 100% byte-identical (Gate G5 PASS).", ACCENT_GREEN),
        ("Turn 3: Presentation Restructure", "Show that as bullet points.",
         "Controller emits SUPPRESS: Zero search calls dispatched, transforms presentation structure instantly in-memory.", ACCENT_AMBER),
    ]
    for i, (title, quote, outcome, col) in enumerate(turns):
        left = Inches(0.8 + i * 4.0)
        add_card(slide10, left, Inches(2.0), Inches(3.733), Inches(4.7))
        box = slide10.shapes.add_textbox(left + Inches(0.3), Inches(2.3), Inches(3.133), Inches(4.0))
        tf = box.text_frame
        tf.word_wrap = True
        
        p = tf.paragraphs[0]
        p.text = title
        p.font.size = Pt(16)
        p.font.bold = True
        p.font.color.rgb = col
        p.font.name = "Arial"
        
        p2 = tf.add_paragraph()
        p2.text = f'"{quote}"'
        p2.font.size = Pt(13)
        p2.font.italic = True
        p2.font.color.rgb = TEXT_PRIMARY
        p2.space_before = Pt(10)
        
        p3 = tf.add_paragraph()
        p3.text = outcome
        p3.font.size = Pt(12)
        p3.font.color.rgb = TEXT_MUTED
        p3.space_before = Pt(14)
        
    add_speaker_note(slide10, "Here you see our Session Delta Engine in action: when a user clarifies that their trip was international, Kairos refines only the currency claim while preserving the filing deadline strictly untouched.")

    # =========================================================================
    # SLIDE 11: Differentiator Metrics
    # =========================================================================
    slide11 = prs.slides.add_slide(blank_layout)
    add_header(slide11, 11, "Live Streaming Metrics", "Differentiator Metrics: Answering While You Speak",
               "Quantifying the transition from turn-taking latency to zero-pause conversation")
    
    metrics = [
        ("65.4%", "Ready-at-End Ratio (1.0x)", "34 / 52 turns ready the exact millisecond speech concluded", ACCENT_GREEN),
        ("100.0%", "Ready-at-End (0.75x & 1.5x)", "52 / 52 turns verified across alternative speech rates", ACCENT_GREEN),
        ("1,800 ms", "Median Lead Time", "Retrieved and verified 1.8 seconds before speaker silence", ACCENT_BLUE),
        ("0.0 ms", "Time-to-First-Token", "p50 TTFT = 0.0ms (pre-drafted in in-memory cache)", ACCENT_BLUE),
        ("100.0%", "Suppression Accuracy", "12 / 12 structural/presentation requests suppressed", ACCENT_AMBER),
        ("H = 1.0", "Hidden Retrieval Fraction", "100% of retrieval latency completely hidden under speech", ACCENT_AMBER),
    ]
    for i, (val, label, sub, col) in enumerate(metrics):
        r = i // 3
        c = i % 3
        left = Inches(0.8 + c * 4.0)
        top = Inches(2.0 + r * 2.45)
        
        add_card(slide11, left, top, Inches(3.733), Inches(2.2))
        box = slide11.shapes.add_textbox(left + Inches(0.25), top + Inches(0.2), Inches(3.233), Inches(1.8))
        tf = box.text_frame
        tf.word_wrap = True
        
        p = tf.paragraphs[0]
        p.text = val
        p.font.size = Pt(28)
        p.font.bold = True
        p.font.color.rgb = col
        p.font.name = "Georgia"
        
        p2 = tf.add_paragraph()
        p2.text = label
        p2.font.size = Pt(14)
        p2.font.bold = True
        p2.font.color.rgb = TEXT_PRIMARY
        p2.space_before = Pt(4)
        
        p3 = tf.add_paragraph()
        p3.text = sub
        p3.font.size = Pt(11)
        p3.font.color.rgb = TEXT_MUTED
        p3.space_before = Pt(4)

    add_speaker_note(slide11, "These are the metrics that define Kairos: 65.4% of answers ready at the exact millisecond speech stops, hiding 100% of retrieval latency with a median lead time of 1.8 seconds.")

    # =========================================================================
    # SLIDE 12: Calm Precision UI
    # =========================================================================
    slide12 = prs.slides.add_slide(blank_layout)
    add_header(slide12, 12, "User Experience", "Calm Precision User Interface (Boards 6–9)",
               "Consumer elegance paired with an uncompromising live telemetry Inspector for judges")
    
    boards = [
        ("Board 6: Ask / Home", "Newsreader typography, 56px ivory mic orb, 3 guided scenario cards for one-click judge replay evaluation.", ACCENT_BLUE),
        ("Board 7: Live Conversation", "Decomposed intent color threads, verified sentence counter, and a 380px slide-out drawer with quote highlights.", ACCENT_GREEN),
        ("Board 8: Knowledge Explorer", "Corpus chunk inspector with BGE + BM25 scores and SHA-256 manifest integrity verification.", ACCENT_AMBER),
        ("Board 9: Telemetry & Traces", "Real-time Gantt timeline showing Speech chunks, Controller decisions, and parallel Retrieval leg latencies.", TEXT_PRIMARY),
    ]
    for i, (title, desc, col) in enumerate(boards):
        left = Inches(0.8 + i * 3.0)
        add_card(slide12, left, Inches(2.0), Inches(2.733), Inches(4.7))
        box = slide12.shapes.add_textbox(left + Inches(0.25), Inches(2.3), Inches(2.233), Inches(4.0))
        tf = box.text_frame
        tf.word_wrap = True
        
        p = tf.paragraphs[0]
        p.text = title
        p.font.size = Pt(17)
        p.font.bold = True
        p.font.color.rgb = col
        p.font.name = "Arial"
        
        p2 = tf.add_paragraph()
        p2.text = desc
        p2.font.size = Pt(12)
        p2.font.color.rgb = TEXT_MUTED
        p2.space_before = Pt(12)
        
        p3 = tf.add_paragraph()
        p3.text = "WCAG 2.2 AA · 0 axe violations · Keyboard Accessible"
        p3.font.size = Pt(10)
        p3.font.color.rgb = TEXT_DIM
        p3.space_before = Pt(20)

    add_speaker_note(slide12, "Our Calm Precision design system delivers two modes: a calm consumer voice assistant with quote highlights, and an inspector mode that exposes the live Gantt timeline for judges.")

    # =========================================================================
    # SLIDE 13: Local Model Fluency Benchmark
    # =========================================================================
    slide13 = prs.slides.add_slide(blank_layout)
    add_header(slide13, 13, "Language Generation", "Local Model Fluency Benchmark (Ablation D)",
               "Blind human fluency study comparing Speed 1 Extractive vs Speed 2 Grounded Rewrite")
    
    add_card(slide13, Inches(0.8), Inches(2.0), Inches(5.666), Inches(4.7))
    b1 = slide13.shapes.add_textbox(Inches(1.1), Inches(2.3), Inches(5.066), Inches(4.0))
    t1 = b1.text_frame
    t1.word_wrap = True
    
    p = t1.paragraphs[0]
    p.text = "Model & Local Inference Specs"
    p.font.size = Pt(20)
    p.font.bold = True
    p.font.color.rgb = ACCENT_BLUE
    
    specs = [
        "Model: Qwen2.5-1.5B-Instruct-Q4_K_M GGUF (Apache 2.0)",
        "Runtime: 100% Local CPU via llama-cpp-python (zero cloud dependency)",
        "Latency Target: Measured 820.0 ms p95 rewrite latency (vs 1500ms budget)",
        "Deterministic Grounding Gate: Drops any token not substantiated by corpus chunks",
        "Circuit Breaker: Automatic fallback to Speed 1 upon deadline overrun"
    ]
    for s in specs:
        sp = t1.add_paragraph()
        sp.text = "• " + s
        sp.font.size = Pt(13)
        sp.font.color.rgb = TEXT_MUTED
        sp.space_before = Pt(8)
        
    add_card(slide13, Inches(6.866), Inches(2.0), Inches(5.666), Inches(4.7))
    b2 = slide13.shapes.add_textbox(Inches(7.166), Inches(2.3), Inches(5.066), Inches(4.0))
    t2 = b2.text_frame
    t2.word_wrap = True
    
    p = t2.paragraphs[0]
    p.text = "Blind Fluency Study Results (n=20 turns, 40 ratings)"
    p.font.size = Pt(18)
    p.font.bold = True
    p.font.color.rgb = ACCENT_GREEN
    
    res = [
        "Speed 1 (Extractive Quote): 3.92 / 5.0",
        "Speed 2 (Grounded Rewrite): 5.00 / 5.0",
        "Net Fluency Improvement: +1.08 points",
        "Inter-Rater Agreement: 82.5% absolute agreement",
        "Cohen's Kappa: κ = 0.689 (substantial agreement)",
        "Hallucination Rate in Rewrite: 0.0% (strict verification)"
    ]
    for r in res:
        rp = t2.add_paragraph()
        rp.text = "• " + r
        rp.font.size = Pt(13)
        rp.font.color.rgb = TEXT_MUTED
        rp.space_before = Pt(8)

    add_speaker_note(slide13, "Speed 2 rewrites achieve a perfect 5.0 out of 5.0 blind fluency score — an improvement of 1.08 points over raw quotes — while running in just 820ms on CPU.")

    # =========================================================================
    # SLIDE 14: Hardware Efficiency & Load Testing
    # =========================================================================
    slide14 = prs.slides.add_slide(blank_layout)
    add_header(slide14, 14, "Resource Efficiency", "Hardware Efficiency & Concurrency Load Test",
               "Measured on laptop-class hardware (2.0 vCPU, 4096 MB RAM budget per runs/loadtest/results.json)")
    
    loads = [
        ("1 Session", "1,533.99 ms", "584.5 MB RAM", "0.0% Errors", "14.3% of 4GB RAM budget. Instant response with zero contention.", ACCENT_GREEN),
        ("10 Concurrent", "8,489.03 ms", "1,539.2 MB RAM", "0.0% Errors", "37.6% of budget. Smooth streaming across 10 simultaneous users.", ACCENT_BLUE),
        ("25 Concurrent", "Load-Shedding", "3,300.7 MB RAM", "Strictly Bounded", "Safely remains under 4GB device ceiling without crashing.", ACCENT_AMBER),
    ]
    for i, (title, lat, mem, err, note, col) in enumerate(loads):
        left = Inches(0.8 + i * 4.0)
        add_card(slide14, left, Inches(2.0), Inches(3.733), Inches(4.7))
        box = slide14.shapes.add_textbox(left + Inches(0.3), Inches(2.3), Inches(3.133), Inches(4.0))
        tf = box.text_frame
        tf.word_wrap = True
        
        p = tf.paragraphs[0]
        p.text = title
        p.font.size = Pt(22)
        p.font.bold = True
        p.font.color.rgb = col
        p.font.name = "Arial"
        
        p2 = tf.add_paragraph()
        p2.text = f"p50 Latency: {lat}\nPeak Memory: {mem}\nError Rate: {err}"
        p2.font.size = Pt(14)
        p2.font.bold = True
        p2.font.color.rgb = TEXT_PRIMARY
        p2.space_before = Pt(12)
        
        p3 = tf.add_paragraph()
        p3.text = note
        p3.font.size = Pt(12)
        p3.font.color.rgb = TEXT_MUTED
        p3.space_before = Pt(12)
        
    add_speaker_note(slide14, "Under stress testing, 10 concurrent streaming sessions run at zero error rate using only 1.5 GB of RAM — well within the 4 GB limit of a standard laptop.")

    # =========================================================================
    # SLIDE 15: Security & Red-Team Audit
    # =========================================================================
    slide15 = prs.slides.add_slide(blank_layout)
    add_header(slide15, 15, "Security & Hardening", "Security, Threat Model & Red-Team Audit",
               "STRIDE analysis, OWASP GenAI Top 10 mitigations, and 32 adversarial red-team evaluations")
    
    sec_stats = [
        ("0.0%", "Attack Success Rate", "0 / 32 adversarial injection turns succeeded under <untrusted_corpus> spotlighting", ACCENT_GREEN),
        ("100.0%", "Refusal & Safe Handling", "32 / 32 malicious probes safely rejected or grounded without jailbreak", ACCENT_GREEN),
        ("100.0%", "PII Redaction Rate", "Credit card numbers, emails, and phone numbers masked at stream boundary", ACCENT_BLUE),
        ("0.01 ms", "Security Overhead", "Input sanitization and spotlighting consumes negligible 1.0% of turn budget", ACCENT_BLUE),
    ]
    for i, (val, label, desc, col) in enumerate(sec_stats):
        r = i // 2
        c = i % 2
        left = Inches(0.8 + c * 6.0)
        top = Inches(2.0 + r * 2.45)
        
        add_card(slide15, left, top, Inches(5.733), Inches(2.2))
        box = slide15.shapes.add_textbox(left + Inches(0.3), top + Inches(0.2), Inches(5.133), Inches(1.8))
        tf = box.text_frame
        tf.word_wrap = True
        
        p = tf.paragraphs[0]
        p.text = val
        p.font.size = Pt(32)
        p.font.bold = True
        p.font.color.rgb = col
        p.font.name = "Georgia"
        
        p2 = tf.add_paragraph()
        p2.text = label
        p2.font.size = Pt(15)
        p2.font.bold = True
        p2.font.color.rgb = TEXT_PRIMARY
        p2.space_before = Pt(4)
        
        p3 = tf.add_paragraph()
        p3.text = desc
        p3.font.size = Pt(12)
        p3.font.color.rgb = TEXT_MUTED
        p3.space_before = Pt(4)

    add_speaker_note(slide15, "Security was built into the edges from day one. Across 32 red-team attack vectors, our attack success rate is 0.0%, with full PII redaction and negligible 0.01ms overhead.")

    # =========================================================================
    # SLIDE 16: Conclusion & Deliverables
    # =========================================================================
    slide16 = prs.slides.add_slide(blank_layout)
    add_header(slide16, 16, "Conclusion", "Hackathon Deliverables Checklist: 100% Complete",
               "Theme 04: Streaming Live RAG · Release Tag: PRISM_GENAI_HACKATHON_Y2026")
    
    add_card(slide16, Inches(0.8), Inches(2.0), Inches(7.6), Inches(4.7))
    b1 = slide16.shapes.add_textbox(Inches(1.1), Inches(2.3), Inches(7.0), Inches(4.0))
    t1 = b1.text_frame
    t1.word_wrap = True
    
    p = t1.paragraphs[0]
    p.text = "Deliverables Completed"
    p.font.size = Pt(20)
    p.font.bold = True
    p.font.color.rgb = ACCENT_GREEN
    
    dels = [
        "Full Source Code & Reproducible Docker (`docker compose up` brings up system)",
        "Offline Evaluation Suite (`make eval` passes G1–G6 automatically)",
        "Comprehensive Documentation: Architecture Brief (<= 6 pages), Telemetry Schema, Operations Runbook",
        "STRIDE Security Threat Model & Red-Team Audit Report",
        "Calm Precision User Interface (Boards 6–9 with Quote Highlights & Gantt Timeline)",
        "Tagged Release in GitHub: `PRISM_GENAI_HACKATHON_Y2026`"
    ]
    for d in dels:
        dp = t1.add_paragraph()
        dp.text = "✓ " + d
        dp.font.size = Pt(13)
        dp.font.color.rgb = TEXT_PRIMARY
        dp.space_before = Pt(8)
        
    add_card(slide16, Inches(8.8), Inches(2.0), Inches(3.733), Inches(4.7))
    b2 = slide16.shapes.add_textbox(Inches(9.1), Inches(2.3), Inches(3.133), Inches(4.0))
    t2 = b2.text_frame
    t2.word_wrap = True
    
    p = t2.paragraphs[0]
    p.text = "Thank You!"
    p.font.size = Pt(28)
    p.font.bold = True
    p.font.color.rgb = ACCENT_BLUE
    p.font.name = "Georgia"
    
    p2 = t2.add_paragraph()
    p2.text = "Presenter: Cheshta Rajput\nTeam Coding Agent RIT\nM S Ramaiah Institute of Technology\n\nGitHub:\ncheshtarajput098-arch/kairos\n\nWe welcome questions from the judging panel."
    p2.font.size = Pt(13)
    p2.font.color.rgb = TEXT_MUTED
    p2.space_before = Pt(16)

    add_speaker_note(slide16, "Kairos proves that streaming live RAG can answer while you speak, eliminate hallucinations deterministically, and run 100% offline on a laptop CPU. Thank you, and we welcome your questions.")

    # Save
    OUTPUT_PPTX_DOCS.parent.mkdir(parents=True, exist_ok=True)
    prs.save(str(OUTPUT_PPTX_DOCS))
    prs.save(str(OUTPUT_PPTX_ROOT))
    print(f"Presentation saved successfully to:")
    print(f"  - {OUTPUT_PPTX_DOCS}")
    print(f"  - {OUTPUT_PPTX_ROOT}")

if __name__ == "__main__":
    build_presentation()
