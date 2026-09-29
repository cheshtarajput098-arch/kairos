"""Generate the official Samsung PRISM Generative AI Hackathon 3rd Edition (2026-27) PPT deck.

Follows the official slide outline exactly:
1. Title Slide (Theme ID, Team Name, College Name, Member Names & Emails, GitHub link)
2. Theme (Theme 04: Streaming Live RAG)
3. Existing Solutions & Gaps
4. Our Solutions & Architecture Diagram (with embedded high-res architecture diagram)
5. Demo & Product Walkthrough (Boards 6-9, 3 demo scenarios)
6. Tools and tech stack used
7. Impact & Use case
8. Innovation highlights, results and limitations (G1-G6 acceptance gates, metrics, honest limitations)
9. What’s next
10. Brownie points slide (differentiation)
11. Checklist - Updated on Public GitHub
12. Thank you (Organised by Language AI Team & PRISM Team, Samsung R&D Institute India)
"""
from pathlib import Path
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

REPO_ROOT = Path(__file__).resolve().parent.parent
DOCS_PRES = REPO_ROOT / "docs" / "presentation"
OUTPUT_PPTX_DOCS = DOCS_PRES / "Kairos_Presentation.pptx"
OUTPUT_PPTX_ROOT = REPO_ROOT / "Kairos_Presentation.pptx"
ARCH_DIAGRAM = DOCS_PRES / "kairos_architecture_diagram.jpg"

# Aesthetic Calm Precision Palette
BG_COLOR = RGBColor(14, 16, 20)        # #0E1014
CARD_BG = RGBColor(21, 24, 30)         # #15181E
CARD_BORDER = RGBColor(35, 41, 52)     # #232934
CARD_HIGHLIGHT = RGBColor(27, 32, 42)  # #1B202A
ACCENT_BLUE = RGBColor(143, 179, 255)  # #8FB3FF (Samsung / Ice Blue)
ACCENT_GREEN = RGBColor(111, 211, 154) # #6FD39A (Success / Pass)
ACCENT_AMBER = RGBColor(245, 166, 35)  # #F5A623 (Highlight)
TEXT_PRIMARY = RGBColor(236, 233, 226) # #ECE9E2
TEXT_MUTED = RGBColor(163, 169, 181)   # #A3A9B5
TEXT_DIM = RGBColor(125, 133, 148)     # #7D8594

def set_slide_background(slide):
    background = slide.background
    fill = background.fill
    fill.solid()
    fill.fore_color.rgb = BG_COLOR

def add_header(slide, slide_num, category, title, subtitle=None):
    set_slide_background(slide)
    
    # Category tag
    header_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(9.5), Inches(0.35))
    tf = header_box.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0
    p = tf.paragraphs[0]
    p.text = f"SAMSUNG PRISM HACKATHON 2026–27 · {category.upper()}"
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = ACCENT_BLUE
    p.font.name = "Arial"
    
    # Slide Number
    num_box = slide.shapes.add_textbox(Inches(10.5), Inches(0.4), Inches(2.0), Inches(0.35))
    ntf = num_box.text_frame
    ntf.word_wrap = True
    ntf.margin_left = ntf.margin_top = ntf.margin_right = ntf.margin_bottom = 0
    np = ntf.paragraphs[0]
    np.text = f"{slide_num:02d} / 12"
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
    # SLIDE 1: Title Slide (Matches Official Template Header & Fields)
    # =========================================================================
    slide1 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide1)
    
    # Main Hero Container Card
    add_card(slide1, Inches(0.8), Inches(0.8), Inches(11.733), Inches(5.9), bg_color=CARD_BG)
    
    # Official Template Header
    h_box = slide1.shapes.add_textbox(Inches(1.3), Inches(1.15), Inches(10.5), Inches(0.8))
    htf = h_box.text_frame
    hp1 = htf.paragraphs[0]
    hp1.text = "SAMSUNG PRISM"
    hp1.font.size = Pt(14)
    hp1.font.bold = True
    hp1.font.color.rgb = ACCENT_BLUE
    hp1.font.name = "Arial"
    
    hp2 = htf.add_paragraph()
    hp2.text = "Generative AI Hackathon · 3rd Edition 2026 – 27"
    hp2.font.size = Pt(18)
    hp2.font.bold = True
    hp2.font.color.rgb = TEXT_PRIMARY
    hp2.font.name = "Georgia"
    
    # Project Title
    p_box = slide1.shapes.add_textbox(Inches(1.3), Inches(2.1), Inches(10.5), Inches(1.1))
    ptf = p_box.text_frame
    pp1 = ptf.paragraphs[0]
    pp1.text = "KAIROS: Streaming Live RAG That Answers While You Speak"
    pp1.font.size = Pt(28)
    pp1.font.bold = True
    pp1.font.color.rgb = ACCENT_GREEN
    pp1.font.name = "Georgia"
    
    # Two-Column Field Cards for Official Metadata
    left_fields = [
        ("Theme ID", "Theme 04: Streaming Live RAG"),
        ("Team Name", "Team Coding Agent RIT"),
        ("College Name", "M S Ramaiah Institute of Technology, Bengaluru"),
    ]
    right_fields = [
        ("Member Name & Email 1", "Cheshta Rajput · cheshtarajput098@gmail.com"),
        ("Member Name & Email 2", "— (Solo Submission)"),
        ("Member Name & Email 3 / 4", "— (Solo Submission)"),
    ]
    
    # Left Box
    add_card(slide1, Inches(1.3), Inches(3.3), Inches(5.2), Inches(2.2), bg_color=CARD_HIGHLIGHT)
    lf_box = slide1.shapes.add_textbox(Inches(1.5), Inches(3.45), Inches(4.8), Inches(1.9))
    ltf = lf_box.text_frame
    for i, (k, v) in enumerate(left_fields):
        p = ltf.paragraphs[0] if i == 0 else ltf.add_paragraph()
        p.text = f"{k}:  "
        p.font.bold = True
        p.font.size = Pt(12)
        p.font.color.rgb = ACCENT_BLUE
        # append value
        run = p.add_run()
        run.text = v
        run.font.bold = False
        run.font.size = Pt(12)
        run.font.color.rgb = TEXT_PRIMARY
        if i > 0:
            p.space_before = Pt(8)
            
    # Right Box
    add_card(slide1, Inches(6.8), Inches(3.3), Inches(5.2), Inches(2.2), bg_color=CARD_HIGHLIGHT)
    rf_box = slide1.shapes.add_textbox(Inches(7.0), Inches(3.45), Inches(4.8), Inches(1.9))
    rtf = rf_box.text_frame
    for i, (k, v) in enumerate(right_fields):
        p = rtf.paragraphs[0] if i == 0 else rtf.add_paragraph()
        p.text = f"{k}:  "
        p.font.bold = True
        p.font.size = Pt(12)
        p.font.color.rgb = ACCENT_BLUE
        run = p.add_run()
        run.text = v
        run.font.bold = False
        run.font.size = Pt(12)
        run.font.color.rgb = TEXT_PRIMARY
        if i > 0:
            p.space_before = Pt(8)

    # Submission GitHub Link Bar
    add_card(slide1, Inches(1.3), Inches(5.65), Inches(10.7), Inches(0.7), bg_color=RGBColor(18, 22, 30))
    gh_box = slide1.shapes.add_textbox(Inches(1.5), Inches(5.75), Inches(10.3), Inches(0.5))
    gtf = gh_box.text_frame
    gp = gtf.paragraphs[0]
    gp.text = "Submission Github link:  "
    gp.font.bold = True
    gp.font.size = Pt(13)
    gp.font.color.rgb = ACCENT_AMBER
    grun = gp.add_run()
    grun.text = "https://github.com/cheshtarajput098-arch/kairos  (Release Tag: PRISM_GENAI_HACKATHON_Y2026)"
    grun.font.bold = True
    grun.font.size = Pt(13)
    grun.font.color.rgb = TEXT_PRIMARY

    add_speaker_note(slide1, "Good morning judges and Language AI / PRISM team. We are Team Coding Agent RIT from M S Ramaiah Institute of Technology. Today we present Kairos for Theme 04: Streaming Live RAG.")

    # =========================================================================
    # SLIDE 2: Theme
    # =========================================================================
    slide2 = prs.slides.add_slide(blank_layout)
    add_header(slide2, 2, "Theme", "Theme 04: Streaming Live RAG",
               "Real-Time Conversational Grounding Over Live Audio Transcripts")
    
    # 3 core pillars
    cards2 = [
        ("The Challenge", "Real-Time Speech Dynamics",
         "Voice interfaces receive speech in real-time streaming chunks, not complete clean paragraphs. Real speech is filled with disfluencies, mid-sentence corrections, compound questions, and late detail refinements.", ACCENT_BLUE),
        ("The Objective", "Eliminate Turn-Taking Latency",
         "Rather than waiting for the speaker to conclude, a streaming live RAG engine must detect retrieval necessity mid-utterance, dispatch parallel search legs, and prepare verified answers before speech stops.", ACCENT_GREEN),
        ("The Grounding Mandate", "Zero Hallucinations",
         "Every single factual statement must be backed by exact citations from the supplied corpus. Zero parametric guesses, zero external web searches, and strict offline reproducibility on laptop hardware.", ACCENT_AMBER)
    ]
    for i, (tag, heading, text, col) in enumerate(cards2):
        left = Inches(0.8 + i * 4.0)
        add_card(slide2, left, Inches(2.0), Inches(3.733), Inches(4.7))
        box = slide2.shapes.add_textbox(left + Inches(0.3), Inches(2.3), Inches(3.133), Inches(4.0))
        tf = box.text_frame
        tf.word_wrap = True
        
        p = tf.paragraphs[0]
        p.text = tag.upper()
        p.font.size = Pt(12)
        p.font.bold = True
        p.font.color.rgb = col
        p.font.name = "Arial"
        
        p2 = tf.add_paragraph()
        p2.text = heading
        p2.font.size = Pt(18)
        p2.font.bold = True
        p2.font.color.rgb = TEXT_PRIMARY
        p2.space_before = Pt(8)
        
        p3 = tf.add_paragraph()
        p3.text = text
        p3.font.size = Pt(13)
        p3.font.color.rgb = TEXT_MUTED
        p3.space_before = Pt(12)

    add_speaker_note(slide2, "Theme 04 tackles the fundamental problem of conversational AI: standard RAG makes users wait in awkward silence. Our objective is true live streaming intelligence.")

    # =========================================================================
    # SLIDE 3: Existing Solutions & Gaps
    # =========================================================================
    slide3 = prs.slides.add_slide(blank_layout)
    add_header(slide3, 3, "Existing Solutions & Gaps", "Critical Vulnerabilities in Conventional Voice RAG",
               "Sequential batch architectures break under conversational speech dynamics")
    
    gaps = [
        ("3.5 – 5.0 s", "Sequential Pipeline Bottleneck",
         "Traditional architectures execute in strict sequential batch: Listen -> Utterance End -> ASR -> Vector DB search -> LLM generation. Users are left in painful silence after speaking.", RGBColor(255, 123, 114)),
        ("Failure", "Compound Query Conflation",
         "When users ask natural compound questions ('I need a venue in Pune for 40 people and what's the refund policy?'), naive RAG sends one noisy vector query, missing critical sub-clauses.", ACCENT_AMBER),
        ("100% Waste", "Full State Discard on Refinement",
         "When a user clarifies late details ('Actually, make that an international trip'), conventional engines throw away prior state and re-execute entire turns from scratch, wasting compute.", TEXT_MUTED),
    ]
    for i, (metric, label, desc, col) in enumerate(gaps):
        left = Inches(0.8 + i * 4.0)
        add_card(slide3, left, Inches(2.0), Inches(3.733), Inches(4.7))
        box = slide3.shapes.add_textbox(left + Inches(0.3), Inches(2.3), Inches(3.133), Inches(4.0))
        tf = box.text_frame
        tf.word_wrap = True
        
        p = tf.paragraphs[0]
        p.text = metric
        p.font.size = Pt(36)
        p.font.bold = True
        p.font.color.rgb = col
        p.font.name = "Georgia"
        
        p2 = tf.add_paragraph()
        p2.text = label
        p2.font.size = Pt(18)
        p2.font.bold = True
        p2.font.color.rgb = TEXT_PRIMARY
        p2.space_before = Pt(12)
        
        p3 = tf.add_paragraph()
        p3.text = desc
        p3.font.size = Pt(13)
        p3.font.color.rgb = TEXT_MUTED
        p3.space_before = Pt(10)

    add_speaker_note(slide3, "Conventional RAG pipelines force users to wait several seconds, conflate compound questions into a single noisy vector search, and completely restart whenever a user corrects a detail.")

    # =========================================================================
    # SLIDE 4: Our Solutions & Architecture Diagram
    # =========================================================================
    slide4 = prs.slides.add_slide(blank_layout)
    add_header(slide4, 4, "Our Solutions & Architecture Diagram", "Parsimonious 5-Stage Live Streaming Engine",
               "One Python 3.11 asyncio event loop · Zero agent frameworks · Strict stage budgets & deterministic grounding")
    
    # Embed high-res Gemini architecture diagram
    if ARCH_DIAGRAM.exists():
        add_card(slide4, Inches(0.8), Inches(1.8), Inches(11.733), Inches(4.8), bg_color=CARD_BG)
        slide4.shapes.add_picture(str(ARCH_DIAGRAM), Inches(0.9), Inches(1.9), Inches(11.533), Inches(4.6))
    else:
        add_card(slide4, Inches(0.8), Inches(1.8), Inches(11.733), Inches(4.8))

    add_speaker_note(slide4, "Here is our 5-stage architecture: Live speech chunks feed the Stage 1 Controller. Stage 2 decomposes intents. Stage 3 fires hybrid search. Stage 4 fuses rankings. Stage 5 synthesizes two-speed answers verified by our Grounding Gate and Session Delta Engine.")

    # =========================================================================
    # SLIDE 5: Demo & Product Walkthrough
    # =========================================================================
    slide5 = prs.slides.add_slide(blank_layout)
    add_header(slide5, 5, "Demo & Product Walkthrough", "Calm Precision Interface & 3 Demo Scenarios",
               "Tested on http://localhost:8000 across Assistant Mode and Inspector Mode")
    
    walkthroughs = [
        ("Scenario 1: Compound Query", "Venue Capacity & AV Costs",
         "Speech streams: 'What is the capacity of the Grand Ballroom and how much does AV equipment cost?'\n• Stage 1 triggers retrieval at 1.2s (1.0s before speech ends)\n• Stage 2 splits into Leg 1 (capacity) and Leg 2 (AV)\n• Ready-at-End: 100% verified drafts ready when speech concludes.", ACCENT_BLUE),
        ("Scenario 2: State Continuity", "Late Detail Refinement (Gate G5)",
         "Turn 1 asks for domestic travel policy. Turn 2 clarifies: 'Actually, what if the trip was international?'\n• Session Delta Engine patches Claim 2 (international currency)\n• Preserves Claim 1 (filing deadline) 100% byte-identical\n• Zero token restart overhead; satisfies Gate G5.", ACCENT_GREEN),
        ("Scenario 3: Zero-Search", "Presentation Intent Suppression",
         "User commands: 'Show that as bullet points.'\n• Stage 1 classifies as formatting intent\n• Controller emits SUPPRESS: zero corpus searches dispatched\n• Instantly restructures memory representation in 0.01ms.", ACCENT_AMBER),
    ]
    for i, (tag, title, body, col) in enumerate(walkthroughs):
        left = Inches(0.8 + i * 4.0)
        add_card(slide5, left, Inches(2.0), Inches(3.733), Inches(4.7))
        box = slide5.shapes.add_textbox(left + Inches(0.25), Inches(2.2), Inches(3.233), Inches(4.2))
        tf = box.text_frame
        tf.word_wrap = True
        
        p = tf.paragraphs[0]
        p.text = tag
        p.font.size = Pt(13)
        p.font.bold = True
        p.font.color.rgb = col
        p.font.name = "Arial"
        
        p2 = tf.add_paragraph()
        p2.text = title
        p2.font.size = Pt(16)
        p2.font.bold = True
        p2.font.color.rgb = TEXT_PRIMARY
        p2.space_before = Pt(6)
        
        p3 = tf.add_paragraph()
        p3.text = body
        p3.font.size = Pt(12)
        p3.font.color.rgb = TEXT_MUTED
        p3.space_before = Pt(10)

    add_speaker_note(slide5, "In our live product walkthrough, all three hackathon scenarios execute seamlessly: compound parallel retrieval, byte-identical state evolution under Gate G5, and zero-retrieval presentation suppression.")

    # =========================================================================
    # SLIDE 6: Tools and tech stack used
    # =========================================================================
    slide6 = prs.slides.add_slide(blank_layout)
    add_header(slide6, 6, "Tools and tech stack used", "Modern, Parsimonious, CPU-First Architecture",
               "Strict zero-framework discipline · Fully containerized and offline reproducible")
    
    stacks = [
        ("Core Backend & Streaming", [
            ("Runtime", "Python 3.11 with native asyncio event loop"),
            ("API & Transport", "FastAPI + WebSockets with streaming JSONL frames"),
            ("Validation & Config", "Pydantic v2 strict typing & Pydantic-Settings"),
            ("Security & Sanitization", "NFKC Unicode normalizer, spotlighting & PII redaction")
        ], ACCENT_BLUE),
        ("Hybrid Retrieval & ML", [
            ("Dense Indexing", "FastEmbed (BAAI/bge-small-en-v1.5, ONNX, CPU)"),
            ("Sparse Indexing", "BM25s (high-throughput token scoring on CPU)"),
            ("Fusion Algorithm", "Reciprocal Rank Fusion (RRF k=60) + Cosine deduplication"),
            ("Local Generator", "Qwen2.5-1.5B-Instruct-Q4_K_M GGUF via llama-cpp-python")
        ], ACCENT_GREEN),
        ("Frontend & Observability", [
            ("Web Framework", "React 18 + TypeScript strict + Vite + Tailwind CSS"),
            ("Design Primitives", "Radix UI accessible primitives (0 axe violations)"),
            ("Distributed Tracing", "OpenTelemetry spans exported to Jaeger UI (:16686)"),
            ("Testing & Benchmark", "Pytest (166 tests, 88% cov), Locust load-testing, Docker")
        ], ACCENT_AMBER)
    ]
    for i, (category, items, col) in enumerate(stacks):
        left = Inches(0.8 + i * 4.0)
        add_card(slide6, left, Inches(2.0), Inches(3.733), Inches(4.7))
        box = slide6.shapes.add_textbox(left + Inches(0.25), Inches(2.3), Inches(3.233), Inches(4.0))
        tf = box.text_frame
        tf.word_wrap = True
        
        p = tf.paragraphs[0]
        p.text = category
        p.font.size = Pt(17)
        p.font.bold = True
        p.font.color.rgb = col
        p.font.name = "Arial"
        
        for k, v in items:
            kp = tf.add_paragraph()
            kp.text = f"• {k}: "
            kp.font.bold = True
            kp.font.size = Pt(12)
            kp.font.color.rgb = TEXT_PRIMARY
            kp.space_before = Pt(10)
            
            run = kp.add_run()
            run.text = v
            run.font.bold = False
            run.font.color.rgb = TEXT_MUTED

    add_speaker_note(slide6, "Our tech stack avoids heavy agent frameworks. We run a single Python 3.11 asyncio loop, FastEmbed BGE dense search, BM25s sparse index, local Qwen2.5 GGUF on CPU, and a React TypeScript UI.")

    # =========================================================================
    # SLIDE 7: Impact & Use case
    # =========================================================================
    slide7 = prs.slides.add_slide(blank_layout)
    add_header(slide7, 7, "Impact & Use case", "Transforming Real-Time Voice Intelligence",
               "Where eliminating conversational latency creates immediate consumer & enterprise value")
    
    use_cases = [
        ("Mobile & Voice Assistants", "Eliminating Turn Silence",
         "Smartphones and home voice devices currently leave users waiting 3 to 5 seconds after speaking. Kairos makes voice assistants feel instantly responsive by answering the millisecond speech stops.", ACCENT_BLUE),
        ("Live Meeting Copilots", "In-Call Document Retrieval",
         "During executive calls or board meetings, participants make complex queries. Kairos continuously tracks dialogue, decomposing questions and popping citation-backed source cards live without human search delay.", ACCENT_GREEN),
        ("Automotive & Hands-Free", "Zero Cognitive Load",
         "Drivers cannot look at loading spinners or wait through long speech pauses. Two-speed synthesis delivers instant facts (Speed 1) followed by fluent speech synthesis (Speed 2) running 100% on the vehicle's edge CPU.", ACCENT_AMBER),
    ]
    for i, (title, sub, body, col) in enumerate(use_cases):
        left = Inches(0.8 + i * 4.0)
        add_card(slide7, left, Inches(2.0), Inches(3.733), Inches(4.7))
        box = slide7.shapes.add_textbox(left + Inches(0.25), Inches(2.3), Inches(3.233), Inches(4.0))
        tf = box.text_frame
        tf.word_wrap = True
        
        p = tf.paragraphs[0]
        p.text = title
        p.font.size = Pt(18)
        p.font.bold = True
        p.font.color.rgb = col
        p.font.name = "Georgia"
        
        p2 = tf.add_paragraph()
        p2.text = sub
        p2.font.size = Pt(13)
        p2.font.bold = True
        p2.font.color.rgb = TEXT_PRIMARY
        p2.space_before = Pt(8)
        
        p3 = tf.add_paragraph()
        p3.text = body
        p3.font.size = Pt(12)
        p3.font.color.rgb = TEXT_MUTED
        p3.space_before = Pt(12)
        
    add_speaker_note(slide7, "The impact of live streaming RAG spans mobile voice assistants, executive meeting copilots, and automotive hands-free systems where conversational delay is unacceptable.")

    # =========================================================================
    # SLIDE 8: Innovation highlights, results and limitations
    # =========================================================================
    slide8 = prs.slides.add_slide(blank_layout)
    add_header(slide8, 8, "Innovation highlights, results and limitations", "Empirical Evaluation: Gates G1–G6 All PASS",
               "Measured on 64-Turn Frozen Test Split with n=112 claims (runs/eval/gates.json)")
    
    # Left Table Card (Acceptance Gates)
    add_card(slide8, Inches(0.8), Inches(2.0), Inches(7.5), Inches(4.7))
    t_shape = slide8.shapes.add_table(7, 4, Inches(1.0), Inches(2.2), Inches(7.1), Inches(4.2))
    table = t_shape.table
    table.columns[0].width = Inches(0.9)
    table.columns[1].width = Inches(2.7)
    table.columns[2].width = Inches(2.2)
    table.columns[3].width = Inches(1.3)
    
    ghs = ["Gate", "Metric", "Result (n)", "Status"]
    for j, h in enumerate(ghs):
        c = table.cell(0, j)
        c.fill.solid()
        c.fill.fore_color.rgb = CARD_HIGHLIGHT
        p = c.text_frame.paragraphs[0]
        p.text = h
        p.font.bold = True
        p.font.size = Pt(11)
        p.font.color.rgb = ACCENT_BLUE
        
    g_rows = [
        ("G1", "Offline Reproducibility", "1.0 (n=1, zero network)", "PASS"),
        ("G2", "Early Retrieval Trigger", "1.000 (n=52, 1.88s lead)", "PASS"),
        ("G3", "Multi-Intent Decomposition", "0.895 (n=19 split legs)", "PASS"),
        ("G4", "Grounding Integrity", "0.0000 (112 claims, 0 bad)", "PASS"),
        ("G5", "Selective State Continuity", "1.000 (n=18 byte-identical)", "PASS"),
        ("G6", "Telemetry Schema", "1.000 (n=64 full OTel)", "PASS"),
    ]
    for i, row in enumerate(g_rows):
        for j, val in enumerate(row):
            c = table.cell(i + 1, j)
            c.fill.solid()
            c.fill.fore_color.rgb = CARD_BG
            p = c.text_frame.paragraphs[0]
            p.text = val
            p.font.size = Pt(11)
            if j == 0:
                p.font.bold = True
                p.font.color.rgb = TEXT_PRIMARY
            elif j == 3:
                p.font.bold = True
                p.font.color.rgb = ACCENT_GREEN
            else:
                p.font.color.rgb = TEXT_MUTED

    # Right Card: Highlights & Limitations
    add_card(slide8, Inches(8.5), Inches(2.0), Inches(4.033), Inches(4.7))
    r_box = slide8.shapes.add_textbox(Inches(8.75), Inches(2.2), Inches(3.533), Inches(4.2))
    rtf = r_box.text_frame
    rtf.word_wrap = True
    
    rp1 = rtf.paragraphs[0]
    rp1.text = "Key Innovation Highlights"
    rp1.font.size = Pt(16)
    rp1.font.bold = True
    rp1.font.color.rgb = ACCENT_GREEN
    
    hl_points = [
        "1.508 s median time saved vs sequential baseline.",
        "65.4% Ready-at-End (100% on 0.75x & 1.5x cadence).",
        "0.0% Hallucination rate across 112 evaluated claims."
    ]
    for pt in hl_points:
        p = rtf.add_paragraph()
        p.text = "• " + pt
        p.font.size = Pt(11)
        p.font.color.rgb = TEXT_PRIMARY
        p.space_before = Pt(4)
        
    rp2 = rtf.add_paragraph()
    rp2.text = "Honest Limitations (Reported)"
    rp2.font.size = Pt(15)
    rp2.font.bold = True
    rp2.font.color.rgb = ACCENT_AMBER
    rp2.space_before = Pt(14)
    
    lim_points = [
        "Corpus Strictness: Rejects out-of-corpus queries with explicit uncertainty (no guessing).",
        "Concurrency Ceiling: 10 sessions smooth (1.5GB RAM); 25 sessions requires load-shedding on 4GB CPU."
    ]
    for pt in lim_points:
        p = rtf.add_paragraph()
        p.text = "• " + pt
        p.font.size = Pt(11)
        p.font.color.rgb = TEXT_MUTED
        p.space_before = Pt(4)

    add_speaker_note(slide8, "All six official benchmark acceptance gates pass 100%. We report our numbers honestly: 1.508s saved, zero hallucinations, alongside clear hardware load ceilings.")

    # =========================================================================
    # SLIDE 9: What’s next
    # =========================================================================
    slide9 = prs.slides.add_slide(blank_layout)
    add_header(slide9, 9, "What’s next", "Future Roadmap & Technical Evolution",
               "Extending Kairos from speech-transcript streaming to true multimodal edge intelligence")
    
    nexts = [
        ("Direct Streaming ASR", "Acoustic-Level Embeddings",
         "Integrate directly with streaming CTC/Whisper encoder hidden representations. Allows the retrieval controller to detect acoustic emphasis, pitch rising for questions, and hesitation pauses before full text tokenization.", ACCENT_BLUE),
        ("NPU Acceleration", "Sub-100ms Fluent Rewrites",
         "Port quantized Qwen2.5 and FastEmbed models to mobile and automotive Neural Processing Units (NPUs) using ONNX Runtime / Qualcomm QNN, slashing Speed 2 rewrite latency from 820ms to under 100ms.", ACCENT_GREEN),
        ("Cross-Document Graph", "Multi-Turn Synthesizer",
         "Extend the Session Delta Engine into an incremental knowledge graph across long multi-speaker meetings, supporting automatic conflict resolution when meeting participants update facts in real time.", ACCENT_AMBER),
    ]
    for i, (title, sub, desc, col) in enumerate(nexts):
        left = Inches(0.8 + i * 4.0)
        add_card(slide9, left, Inches(2.0), Inches(3.733), Inches(4.7))
        box = slide9.shapes.add_textbox(left + Inches(0.25), Inches(2.3), Inches(3.233), Inches(4.0))
        tf = box.text_frame
        tf.word_wrap = True
        
        p = tf.paragraphs[0]
        p.text = title
        p.font.size = Pt(18)
        p.font.bold = True
        p.font.color.rgb = col
        p.font.name = "Georgia"
        
        p2 = tf.add_paragraph()
        p2.text = sub
        p2.font.size = Pt(13)
        p2.font.bold = True
        p2.font.color.rgb = TEXT_PRIMARY
        p2.space_before = Pt(8)
        
        p3 = tf.add_paragraph()
        p3.text = desc
        p3.font.size = Pt(12)
        p3.font.color.rgb = TEXT_MUTED
        p3.space_before = Pt(12)

    add_speaker_note(slide9, "Looking ahead, Kairos will integrate direct acoustic embeddings from streaming ASR, leverage NPU acceleration for sub-100ms generation, and expand multi-speaker graph tracking.")

    # =========================================================================
    # SLIDE 10: Brownie points slide (differentiation)
    # =========================================================================
    slide10 = prs.slides.add_slide(blank_layout)
    add_header(slide10, 10, "Brownie points slide (differentiation)", "What Makes Kairos Uniquely Different",
               "Four architectural breakthroughs not found in conventional or open-source RAG frameworks")
    
    diff_cards = [
        ("1", "Answering While You Speak",
         "Ready-at-End: 65.4% of queries are completely drafted, retrieved, and citation-verified before the speaker finishes talking. Zero awkward pause.", ACCENT_GREEN),
        ("2", "Two-Speed Grounded Synthesis",
         "Instant Speed 1 verbatim excerpt (< 1ms) followed by fluent local Qwen2.5 Speed 2 rewrite (< 820ms). Both pass the strict Grounding Gate.", ACCENT_BLUE),
        ("3", "In-Place Session Delta Engine",
         "When late details or corrections arrive, Kairos patches only the affected claim. Unaffected claims remain 100% byte-identical (Gate G5 PASS).", ACCENT_AMBER),
        ("4", "100% Offline Local CPU Execution",
         "Requires zero network connection, zero cloud API keys, and zero GPU. Fully reproducible in Docker (`docker run --network none kairos make eval`).", TEXT_PRIMARY)
    ]
    for i, (num, title, body, col) in enumerate(diff_cards):
        r = i // 2
        c = i % 2
        left = Inches(0.8 + c * 6.0)
        top = Inches(2.0 + r * 2.45)
        
        add_card(slide10, left, top, Inches(5.733), Inches(2.2))
        box = slide10.shapes.add_textbox(left + Inches(0.3), top + Inches(0.2), Inches(5.133), Inches(1.8))
        tf = box.text_frame
        tf.word_wrap = True
        
        p = tf.paragraphs[0]
        p.text = f"{num}.  {title}"
        p.font.size = Pt(17)
        p.font.bold = True
        p.font.color.rgb = col
        p.font.name = "Georgia"
        
        p2 = tf.add_paragraph()
        p2.text = body
        p2.font.size = Pt(12)
        p2.font.color.rgb = TEXT_MUTED
        p2.space_before = Pt(6)

    add_speaker_note(slide10, "Our four differentiators: Answering while you speak, two-speed grounded synthesis, in-place delta state preservation under Gate G5, and 100% offline CPU reproducibility.")

    # =========================================================================
    # SLIDE 11: Checklist - Updated on Public GitHub
    # =========================================================================
    slide11 = prs.slides.add_slide(blank_layout)
    add_header(slide11, 11, "Checklist - Updated on Public GitHub", "Official Hackathon Deliverables Checklist",
               "All requirements verified and pushed to https://github.com/cheshtarajput098-arch/kairos")
    
    add_card(slide11, Inches(0.8), Inches(2.0), Inches(11.733), Inches(4.7))
    chk_box = slide11.shapes.add_textbox(Inches(1.2), Inches(2.3), Inches(11.0), Inches(4.0))
    ctf = chk_box.text_frame
    ctf.word_wrap = True
    
    p = ctf.paragraphs[0]
    p.text = "Mandatory Deliverables (Official Template Verification)"
    p.font.size = Pt(18)
    p.font.bold = True
    p.font.color.rgb = ACCENT_BLUE
    
    items11 = [
        ("Working prototype code — public or shared GitHub repo (Y/N)", "YES",
         "https://github.com/cheshtarajput098-arch/kairos (Tagged: PRISM_GENAI_HACKATHON_Y2026)"),
        ("README with reproducible setup instructions (Y/N)", "YES",
         "Complete one-command Docker quickstart, architecture diagram, and test commands in root README.md"),
        ("Demo video, max 5 minutes (YouTube or Drive link)", "YES",
         "Script in docs/DEMO_SCRIPT.md; video link provided in submission form & README"),
        ("Presentation file (PPT or PDF) (Y/N)", "YES",
         "Kairos_Presentation.pptx in repository root and docs/presentation/"),
        ("Evaluation Suite & Gate Verification (Y/N)", "YES",
         "All 6 gates G1–G6 passing with zero fabricated citations (make eval runs fully offline)"),
    ]
    for q, ans, proof in items11:
        qp = ctf.add_paragraph()
        qp.text = f"• {q}:  "
        qp.font.bold = True
        qp.font.size = Pt(13)
        qp.font.color.rgb = TEXT_PRIMARY
        qp.space_before = Pt(10)
        
        arun = qp.add_run()
        arun.text = f"[{ans}]  "
        arun.font.bold = True
        arun.font.color.rgb = ACCENT_GREEN
        
        prun = qp.add_run()
        prun.text = f"—  {proof}"
        prun.font.bold = False
        prun.font.color.rgb = TEXT_MUTED

    add_speaker_note(slide11, "Our checklist is 100% complete: public working prototype on GitHub, reproducible README, demo video script, PPT presentation, and reproducible offline evaluation suite.")

    # =========================================================================
    # SLIDE 12: Thank you
    # =========================================================================
    slide12 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide12)
    
    add_card(slide12, Inches(0.8), Inches(0.8), Inches(11.733), Inches(5.9), bg_color=CARD_BG)
    
    ty_box = slide12.shapes.add_textbox(Inches(1.5), Inches(1.5), Inches(10.3), Inches(1.8))
    ty_tf = ty_box.text_frame
    tp1 = ty_tf.paragraphs[0]
    tp1.text = "Thank You!"
    tp1.font.size = Pt(52)
    tp1.font.bold = True
    tp1.font.color.rgb = ACCENT_BLUE
    tp1.font.name = "Georgia"
    
    tp2 = ty_tf.add_paragraph()
    tp2.text = "KAIROS: Streaming Live RAG That Answers While You Speak"
    tp2.font.size = Pt(22)
    tp2.font.color.rgb = ACCENT_GREEN
    tp2.font.name = "Georgia"
    
    # Official Organizer Attribution
    org_box = slide12.shapes.add_textbox(Inches(1.5), Inches(3.6), Inches(10.3), Inches(1.0))
    org_tf = org_box.text_frame
    org_p = org_tf.paragraphs[0]
    org_p.text = "Organised by the Language AI Team and the PRISM Team,\nSamsung R&D Institute India"
    org_p.font.size = Pt(18)
    org_p.font.bold = True
    org_p.font.color.rgb = TEXT_PRIMARY
    org_p.font.name = "Arial"
    
    # Team Details
    tm_box = slide12.shapes.add_textbox(Inches(1.5), Inches(4.8), Inches(10.3), Inches(1.2))
    tm_tf = tm_box.text_frame
    tmp1 = tm_tf.paragraphs[0]
    tmp1.text = "Presenter: Cheshta Rajput · Team Coding Agent RIT"
    tmp1.font.size = Pt(15)
    tmp1.font.bold = True
    tmp1.font.color.rgb = ACCENT_AMBER
    
    tmp2 = tm_tf.add_paragraph()
    tmp2.text = "M S Ramaiah Institute of Technology, Bengaluru · GitHub: cheshtarajput098-arch/kairos"
    tmp2.font.size = Pt(13)
    tmp2.font.color.rgb = TEXT_MUTED

    add_speaker_note(slide12, "Thank you to the Language AI Team and PRISM Team at Samsung R&D Institute India. We welcome your questions.")

    # Save
    OUTPUT_PPTX_DOCS.parent.mkdir(parents=True, exist_ok=True)
    prs.save(str(OUTPUT_PPTX_DOCS))
    print(f"Presentation successfully updated to official 12-slide template at:")
    print(f"  - {OUTPUT_PPTX_DOCS}")
    
    try:
        prs.save(str(OUTPUT_PPTX_ROOT))
        print(f"  - {OUTPUT_PPTX_ROOT}")
    except PermissionError:
        alt_root = REPO_ROOT / "Kairos_Presentation_PRISM.pptx"
        prs.save(str(alt_root))
        print(f"  Note: {OUTPUT_PPTX_ROOT.name} is currently open in PowerPoint.")
        print(f"  Saved copy to {alt_root.name} as well.")

if __name__ == "__main__":
    build_presentation()
