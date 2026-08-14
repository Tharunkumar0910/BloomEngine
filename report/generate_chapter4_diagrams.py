import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches

figures_dir = r"c:\Tharun\BloomAI_Arena_v2_1\report\figures"
os.makedirs(figures_dir, exist_ok=True)

plt.rcParams['font.sans-serif'] = 'Segoe UI'
plt.rcParams['font.family'] = 'sans-serif'

# Academic Palette
BG_WHITE = '#FFFFFF'
NAVY_HEADER = '#1F4E78'
BLUE_BOX = '#D9E1F2'
BLUE_BORDER = '#2F5597'
TEAL_BOX = '#E2EFDA'
TEAL_BORDER = '#375623'
ORANGE_BOX = '#FCE4D6'
ORANGE_BORDER = '#C65911'
GRAY_BOX = '#F2F2F2'
BORDER_GRAY = '#555555'

def draw_rounded_box(ax, x, y, width, height, title, subtitle="", bg_color=BLUE_BOX, border_color=BLUE_BORDER, text_color='#000000', fontsize=9.5):
    box = patches.FancyBboxPatch(
        (x, y), width, height,
        boxstyle="round,pad=0.03,rounding_size=0.08",
        ec=border_color, fc=bg_color, lw=1.5, zorder=3
    )
    ax.add_patch(box)
    if subtitle:
        ax.text(x + width/2, y + height*0.62, title, ha='center', va='center', fontsize=fontsize, fontweight='bold', color=text_color, zorder=4)
        ax.text(x + width/2, y + height*0.30, subtitle, ha='center', va='center', fontsize=fontsize*0.8, color='#333333', zorder=4)
    else:
        ax.text(x + width/2, y + height/2, title, ha='center', va='center', fontsize=fontsize, fontweight='bold', color=text_color, zorder=4)

def draw_oval(ax, x, y, width, height, title, bg_color=TEAL_BOX, border_color=TEAL_BORDER):
    ellipse = patches.Ellipse((x, y), width, height, ec=border_color, fc=bg_color, lw=1.5, zorder=3)
    ax.add_patch(ellipse)
    ax.text(x, y, title, ha='center', va='center', fontsize=9, fontweight='bold', color='#000000', zorder=4)

def draw_arrow(ax, x1, y1, x2, y2, label=""):
    ax.annotate(
        "", xy=(x2, y2), xytext=(x1, y1),
        arrowprops=dict(arrowstyle="->", color="#333333", lw=1.4, mutation_scale=14),
        zorder=5
    )
    if label:
        mid_x = (x1 + x2) / 2
        mid_y = (y1 + y2) / 2
        ax.text(mid_x, mid_y + 0.12, label, ha='center', va='center', fontsize=8, color='#444444', backgroundcolor='#FFFFFF', zorder=6)

# ==============================================================================
# 4.1 System Architecture
# ==============================================================================
def create_fig_4_1():
    fig, ax = plt.subplots(figsize=(10, 6), dpi=300)
    ax.set_xlim(0, 10); ax.set_ylim(0, 7); ax.axis('off')
    fig.patch.set_facecolor(BG_WHITE)

    ax.text(5, 6.6, "Figure 4.1: BloomEngine System Architecture Diagram", ha='center', fontsize=12, fontweight='bold', color=NAVY_HEADER)

    layers = [
        ("Presentation Layer", "Single Page Web UI (HTML5 / Tailwind CSS) | Interactive Question Studio | Analytics Dashboard", BLUE_BOX, BLUE_BORDER, 5.3),
        ("Application & REST API Controller", "Flask 3.0 Web Server (app.py) | Endpoints (/rephrase, /export) | Session Management", TEAL_BOX, TEAL_BORDER, 4.0),
        ("Question Parsing & Linguistic Engine", "spaCy Pipeline (en_core_web_sm) | Question Profiler | Domain Hierarchy Indexer", ORANGE_BOX, ORANGE_BORDER, 2.7),
        ("Deep Learning & Inference Engine", "DeBERTa-v3 Classifier (6 Bloom Classes) | FLAN-T5 Seq2Seq Rewriter | SentenceTransformers", GRAY_BOX, BORDER_GRAY, 1.4),
        ("Validation & Persistence Engine", "7-Stage Sequential Validation Engine | Dynamic Candidate Ranker | In-Memory SQLite Cache", BLUE_BOX, BLUE_BORDER, 0.1),
    ]

    for title, desc, bg, border, y in layers:
        draw_rounded_box(ax, 0.5, y, 9.0, 0.95, title, desc, bg_color=bg, border_color=border)

    for y in [5.3, 4.0, 2.7, 1.4]:
        draw_arrow(ax, 5.0, y, 5.0, y - 0.35)

    plt.tight_layout()
    out_path = os.path.join(figures_dir, "fig_4_1_system_architecture.png")
    plt.savefig(out_path, bbox_inches='tight', facecolor=BG_WHITE)
    plt.close()
    print(f"Saved: {out_path}")

# ==============================================================================
# 4.2 System Modules Breakdown
# ==============================================================================
def create_fig_4_2():
    fig, ax = plt.subplots(figsize=(10, 6.5), dpi=300)
    ax.set_xlim(0, 10); ax.set_ylim(0, 7); ax.axis('off')
    fig.patch.set_facecolor(BG_WHITE)

    ax.text(5, 6.6, "Figure 4.2: System Modules Decomposition Diagram", ha='center', fontsize=12, fontweight='bold', color=NAVY_HEADER)

    draw_rounded_box(ax, 3.0, 5.3, 4.0, 0.9, "BloomEngine Core System", "Main Orchestrator (app.py)", NAVY_HEADER, NAVY_HEADER, text_color='#FFFFFF')

    modules = [
        ("M1: Question\nParser Module", "question_understanding.py", BLUE_BOX, BLUE_BORDER, 0.5, 3.2),
        ("M2: Taxonomic\nClassifier", "deberta_bloom_model", TEAL_BOX, TEAL_BORDER, 2.0, 3.2),
        ("M3: Seq2Seq\nTransformer", "flan_t5_model", ORANGE_BOX, ORANGE_BORDER, 3.5, 3.2),
        ("M4: Validation\nEngine", "validation_engine.py", BLUE_BOX, BLUE_BORDER, 5.0, 3.2),
        ("M5: Candidate\nRanker Module", "candidate_ranker.py", TEAL_BOX, TEAL_BORDER, 6.5, 3.2),
        ("M6: Ingestion &\nExport Module", "Document Exporters", ORANGE_BOX, ORANGE_BORDER, 8.0, 3.2),
    ]

    for title, desc, bg, border, x, y in modules:
        draw_rounded_box(ax, x, y, 1.4, 1.2, title, desc, bg, border, fontsize=8.5)
        draw_arrow(ax, 5.0, 5.3, x + 0.7, y + 1.2)

    # Secondary details layer
    draw_rounded_box(ax, 0.5, 1.0, 4.2, 1.2, "Sub-Modules: NLP & Parsing", "spaCy POS | Noun Chunking | NER | Abbrev Normalizer", GRAY_BOX, BORDER_GRAY, fontsize=8.5)
    draw_rounded_box(ax, 5.3, 1.0, 4.2, 1.2, "Sub-Modules: 7-Stage Validators", "Bloom | Concept | Entity | Number | Knowledge | Semantic | Syntax", GRAY_BOX, BORDER_GRAY, fontsize=8.5)

    draw_arrow(ax, 2.6, 3.2, 2.6, 2.2)
    draw_arrow(ax, 7.4, 3.2, 7.4, 2.2)

    plt.tight_layout()
    out_path = os.path.join(figures_dir, "fig_4_2_system_modules.png")
    plt.savefig(out_path, bbox_inches='tight', facecolor=BG_WHITE)
    plt.close()
    print(f"Saved: {out_path}")

# ==============================================================================
# 4.3 Use Case Diagram
# ==============================================================================
def create_fig_4_3():
    fig, ax = plt.subplots(figsize=(9, 6), dpi=300)
    ax.set_xlim(0, 10); ax.set_ylim(0, 7); ax.axis('off')
    fig.patch.set_facecolor(BG_WHITE)

    ax.text(5, 6.6, "Figure 4.3: UML Use Case Diagram for BloomEngine", ha='center', fontsize=12, fontweight='bold', color=NAVY_HEADER)

    # Draw Actor (Stickman)
    # Head
    head = patches.Circle((1.2, 4.0), 0.35, ec=BLUE_BORDER, fc=BLUE_BOX, lw=1.5, zorder=4)
    ax.add_patch(head)
    # Body
    ax.plot([1.2, 1.2], [2.6, 3.65], color=BLUE_BORDER, lw=2, zorder=4)
    # Arms
    ax.plot([0.7, 1.7], [3.2, 3.2], color=BLUE_BORDER, lw=2, zorder=4)
    # Legs
    ax.plot([1.2, 0.7], [2.6, 1.8], color=BLUE_BORDER, lw=2, zorder=4)
    ax.plot([1.2, 1.7], [2.6, 1.8], color=BLUE_BORDER, lw=2, zorder=4)
    ax.text(1.2, 1.3, "Educator / User", ha='center', fontweight='bold', fontsize=10, color=NAVY_HEADER)

    # System boundary box
    sys_box = patches.Rectangle((3.0, 0.8), 6.5, 5.4, ls='--', ec=NAVY_HEADER, fc='#F9FAFC', lw=1.5, zorder=1)
    ax.add_patch(sys_box)
    ax.text(6.25, 5.9, "BloomEngine System Boundary", ha='center', fontweight='bold', fontsize=10, color=NAVY_HEADER)

    # Use Cases (Ovals)
    use_cases = [
        ("Transform Single Question", 5.0),
        ("Configure Target Bloom & Difficulty", 4.2),
        ("Batch File Upload (.xlsx, .pdf, .docx)", 3.4),
        ("Inspect 7-Stage Validation Matrix", 2.6),
        ("View Analytics & Failure Charts", 1.8),
        ("Export Transformed Questions", 1.0),
    ]

    for uc_title, y_pos in use_cases:
        draw_oval(ax, 6.25, y_pos, 4.5, 0.65, uc_title, bg_color=TEAL_BOX, border_color=TEAL_BORDER)
        ax.plot([1.7, 4.0], [3.2, y_pos], color='#555555', lw=1.2, ls='-', zorder=2)

    plt.tight_layout()
    out_path = os.path.join(figures_dir, "fig_4_3_use_case_diagram.png")
    plt.savefig(out_path, bbox_inches='tight', facecolor=BG_WHITE)
    plt.close()
    print(f"Saved: {out_path}")

# ==============================================================================
# 4.4 Activity Diagram
# ==============================================================================
def create_fig_4_4():
    fig, ax = plt.subplots(figsize=(8, 7.5), dpi=300)
    ax.set_xlim(0, 8); ax.set_ylim(0, 8.5); ax.axis('off')
    fig.patch.set_facecolor(BG_WHITE)

    ax.text(4, 8.1, "Figure 4.4: UML Activity Diagram (Question Transformation Flow)", ha='center', fontsize=12, fontweight='bold', color=NAVY_HEADER)

    # Start Node
    start_node = patches.Circle((4.0, 7.5), 0.2, fc='#000000', ec='#000000', zorder=4)
    ax.add_patch(start_node)
    draw_arrow(ax, 4.0, 7.3, 4.0, 6.8)

    activities = [
        ("Input Source Question & Target Parameters", 6.2),
        ("Parse Question & Extract Noun Chunks (spaCy)", 5.2),
        ("Classify Source Bloom Level (DeBERTa-v3)", 4.2),
        ("Generate Candidate Variants (FLAN-T5 Model)", 3.2),
    ]

    for title, y in activities:
        draw_rounded_box(ax, 1.5, y, 5.0, 0.6, title, bg_color=BLUE_BOX, border_color=BLUE_BORDER, fontsize=8.5)
        if y < 6.2:
            draw_arrow(ax, 4.0, y + 1.0, 4.0, y + 0.6)

    # Decision Diamond
    draw_arrow(ax, 4.0, 3.2, 4.0, 2.6)
    diamond = patches.Polygon([[4.0, 2.6], [5.0, 2.1], [4.0, 1.6], [3.0, 2.1]], ec=ORANGE_BORDER, fc=ORANGE_BOX, lw=1.5, zorder=3)
    ax.add_patch(diamond)
    ax.text(4.0, 2.1, "Pass 7-Stage\nValidation?", ha='center', va='center', fontsize=8, fontweight='bold')

    # Pass flow
    draw_arrow(ax, 5.0, 2.1, 6.2, 2.1, "Yes")
    draw_rounded_box(ax, 6.0, 0.8, 1.8, 0.6, "Select Top Rank\nCandidate", bg_color=TEAL_BOX, border_color=TEAL_BORDER, fontsize=8)

    # Fail flow
    draw_arrow(ax, 3.0, 2.1, 1.8, 2.1, "No (Retry)")
    draw_rounded_box(ax, 0.6, 0.8, 1.8, 0.6, "Fallback Best\nCandidate & Log", bg_color=ORANGE_BOX, border_color=ORANGE_BORDER, fontsize=8)
    draw_arrow(ax, 1.5, 1.4, 3.0, 3.5, "Retry Loop")

    # End Node
    end_outer = patches.Circle((4.0, 0.4), 0.22, ec='#000000', fc='#FFFFFF', lw=1.5, zorder=4)
    end_inner = patches.Circle((4.0, 0.4), 0.14, fc='#000000', ec='#000000', zorder=5)
    ax.add_patch(end_outer); ax.add_patch(end_inner)

    draw_arrow(ax, 6.9, 0.8, 4.25, 0.4)
    draw_arrow(ax, 1.5, 0.8, 3.75, 0.4)

    plt.tight_layout()
    out_path = os.path.join(figures_dir, "fig_4_4_activity_diagram.png")
    plt.savefig(out_path, bbox_inches='tight', facecolor=BG_WHITE)
    plt.close()
    print(f"Saved: {out_path}")

# ==============================================================================
# 4.5 Sequence Diagram
# ==============================================================================
def create_fig_4_5():
    fig, ax = plt.subplots(figsize=(10, 6), dpi=300)
    ax.set_xlim(0, 10); ax.set_ylim(0, 7); ax.axis('off')
    fig.patch.set_facecolor(BG_WHITE)

    ax.text(5, 6.6, "Figure 4.5: UML Sequence Diagram (Question Transformation Lifecycle)", ha='center', fontsize=12, fontweight='bold', color=NAVY_HEADER)

    lifelines = [
        ("User/Client", 1.0),
        ("Flask API", 3.0),
        ("DeBERTa", 5.0),
        ("FLAN-T5", 7.0),
        ("Validator", 9.0),
    ]

    # Lifeline Headers & Vertical Dashed Lines
    for name, x in lifelines:
        draw_rounded_box(ax, x - 0.7, 5.8, 1.4, 0.5, name, bg_color=BLUE_BOX, border_color=BLUE_BORDER, fontsize=8.5)
        ax.plot([x, x], [0.8, 5.8], color='#888888', ls='--', lw=1.2, zorder=1)

    # Messages
    msgs = [
        (1.0, 3.0, 5.2, "1: POST /rephrase (q, target_bloom)"),
        (3.0, 5.0, 4.5, "2: classify_text(cleaned_q)"),
        (5.0, 3.0, 3.9, "3: return (src_bloom, confidence)"),
        (3.0, 7.0, 3.3, "4: generate(**prompt_inputs)"),
        (7.0, 3.0, 2.7, "5: return candidate_variants"),
        (3.0, 9.0, 2.1, "6: evaluate_candidate()"),
        (9.0, 3.0, 1.5, "7: return ValidationEngineOutput"),
        (3.0, 1.0, 0.9, "8: HTTP 200 JSON Response"),
    ]

    for x1, x2, y, label in msgs:
        draw_arrow(ax, x1, y, x2, y, label)

    plt.tight_layout()
    out_path = os.path.join(figures_dir, "fig_4_5_sequence_diagram.png")
    plt.savefig(out_path, bbox_inches='tight', facecolor=BG_WHITE)
    plt.close()
    print(f"Saved: {out_path}")

# ==============================================================================
# 4.6 Data Flow Diagram (DFD Level 1)
# ==============================================================================
def create_fig_4_6():
    fig, ax = plt.subplots(figsize=(10, 6), dpi=300)
    ax.set_xlim(0, 10); ax.set_ylim(0, 7); ax.axis('off')
    fig.patch.set_facecolor(BG_WHITE)

    ax.text(5, 6.6, "Figure 4.6: Data Flow Diagram (DFD Level 1)", ha='center', fontsize=12, fontweight='bold', color=NAVY_HEADER)

    # External Entities (Rectangles)
    draw_rounded_box(ax, 0.5, 4.8, 1.5, 0.9, "External Entity\nUser / Educator", bg_color=ORANGE_BOX, border_color=ORANGE_BORDER, fontsize=8.5)
    draw_rounded_box(ax, 0.5, 1.5, 1.5, 0.9, "External Entity\nBatch Documents", bg_color=ORANGE_BOX, border_color=ORANGE_BORDER, fontsize=8.5)

    # Processes (Circles / Rounded Rectangles)
    processes = [
        ("P1: Parse & Normalization", 3.0, 4.8),
        ("P2: DeBERTa Classifier", 5.5, 4.8),
        ("P3: FLAN-T5 Generator", 8.0, 4.8),
        ("P4: 7-Stage Validation", 5.5, 2.5),
        ("P5: Candidate Ranker", 8.0, 2.5),
    ]

    for p_name, x, y in processes:
        draw_rounded_box(ax, x - 0.8, y - 0.4, 1.6, 0.8, p_name, bg_color=TEAL_BOX, border_color=TEAL_BORDER, fontsize=8)

    # Data Stores (Open Rectangles)
    draw_rounded_box(ax, 3.0, 0.8, 2.0, 0.7, "D1: Session Store\n(MEMORY_STORE)", bg_color=GRAY_BOX, border_color=BORDER_GRAY, fontsize=8)
    draw_rounded_box(ax, 6.5, 0.8, 2.0, 0.7, "D2: Embedding Cache\n(EMBEDDING_CACHE)", bg_color=GRAY_BOX, border_color=BORDER_GRAY, fontsize=8)

    # Data Flow Arrows
    draw_arrow(ax, 2.0, 5.25, 2.2, 5.25, "Source Q")
    draw_arrow(ax, 3.8, 5.25, 4.7, 5.25, "Normalized Profile")
    draw_arrow(ax, 6.3, 5.25, 7.2, 5.25, "Target Bloom")
    draw_arrow(ax, 8.0, 4.4, 8.0, 3.3, "Candidates")
    draw_arrow(ax, 7.2, 2.9, 6.3, 2.9, "Scores")
    draw_arrow(ax, 5.5, 2.1, 4.0, 1.5, "Save Results")
    draw_arrow(ax, 6.3, 2.5, 6.5, 1.5, "Vector Cache")

    plt.tight_layout()
    out_path = os.path.join(figures_dir, "fig_4_6_dfd_level1.png")
    plt.savefig(out_path, bbox_inches='tight', facecolor=BG_WHITE)
    plt.close()
    print(f"Saved: {out_path}")

# ==============================================================================
# 4.7 Database Design & ER Diagram
# ==============================================================================
def create_fig_4_7():
    fig, ax = plt.subplots(figsize=(10, 6), dpi=300)
    ax.set_xlim(0, 10); ax.set_ylim(0, 7); ax.axis('off')
    fig.patch.set_facecolor(BG_WHITE)

    ax.text(5, 6.6, "Figure 4.7: Database & In-Memory Cache Entity-Relationship (ER) Schema", ha='center', fontsize=12, fontweight='bold', color=NAVY_HEADER)

    entities = [
        ("QuestionSession", ["session_id (PK)", "batch_id", "created_at", "total_questions"], 0.8, 4.2),
        ("ValidationResult", ["result_id (PK)", "session_id (FK)", "source_question", "target_bloom", "predicted_bloom", "validation_status", "total_score"], 4.0, 4.0),
        ("CandidateLog", ["candidate_id (PK)", "result_id (FK)", "candidate_text", "bloom_score", "concept_score", "entity_score", "rejection_reason"], 7.2, 4.0),
        ("EmbeddingCache", ["cache_key (PK)", "normalized_text", "vector_blob", "hit_count"], 4.0, 1.0),
    ]

    for title, fields, x, y in entities:
        height = 0.4 + len(fields) * 0.45
        draw_rounded_box(ax, x, y, 2.2, height, title, "", bg_color=BLUE_BOX, border_color=BLUE_BORDER, fontsize=9)
        for idx, f in enumerate(fields):
            f_y = y + height - 0.6 - idx * 0.42
            font_w = 'bold' if '(PK)' in f or '(FK)' in f else 'normal'
            color = NAVY_HEADER if '(PK)' in f else ('#C65911' if '(FK)' in f else '#222222')
            ax.text(x + 0.15, f_y, f, fontsize=8, fontweight=font_w, color=color, zorder=4)

    # Relationships
    draw_arrow(ax, 3.0, 5.0, 4.0, 5.0, "1 : N")
    draw_arrow(ax, 6.2, 5.0, 7.2, 5.0, "1 : N")
    draw_arrow(ax, 5.1, 4.0, 5.1, 2.7, "Uses")

    plt.tight_layout()
    out_path = os.path.join(figures_dir, "fig_4_7_database_schema.png")
    plt.savefig(out_path, bbox_inches='tight', facecolor=BG_WHITE)
    plt.close()
    print(f"Saved: {out_path}")

if __name__ == "__main__":
    create_fig_4_1()
    create_fig_4_2()
    create_fig_4_3()
    create_fig_4_4()
    create_fig_4_5()
    create_fig_4_6()
    create_fig_4_7()
    print("All Chapter 4 figures generated successfully!")
