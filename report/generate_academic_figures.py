import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# Ensure figures output directory exists
figures_dir = r"c:\Tharun\BloomAI_Arena_v2_1\report\figures"
os.makedirs(figures_dir, exist_ok=True)

plt.rcParams['font.sans-serif'] = 'Segoe UI'
plt.rcParams['font.family'] = 'sans-serif'

# Palette definition (Academic IEEE / Visio style)
BG_WHITE = '#FFFFFF'
BORDER_GRAY = '#333333'
NAVY_HEADER = '#1F4E78'
BLUE_BOX = '#D9E1F2'
BLUE_BORDER = '#2F5597'
TEAL_BOX = '#E2EFDA'
TEAL_BORDER = '#375623'
ORANGE_BOX = '#FCE4D6'
ORANGE_BORDER = '#C65911'
GRAY_BOX = '#F2F2F2'

def draw_rounded_box(ax, x, y, width, height, title, subtitle="", bg_color=BLUE_BOX, border_color=BLUE_BORDER, text_color='#000000', fontsize=10):
    box = patches.FancyBboxPatch(
        (x, y), width, height,
        boxstyle="round,pad=0.03,rounding_size=0.1",
        ec=border_color, fc=bg_color, lw=1.5, zorder=3
    )
    ax.add_patch(box)
    
    if subtitle:
        ax.text(x + width/2, y + height*0.62, title, ha='center', va='center', fontsize=fontsize, fontweight='bold', color=text_color, zorder=4)
        ax.text(x + width/2, y + height*0.32, subtitle, ha='center', va='center', fontsize=fontsize*0.82, color='#404040', zorder=4)
    else:
        ax.text(x + width/2, y + height/2, title, ha='center', va='center', fontsize=fontsize, fontweight='bold', color=text_color, zorder=4)

def draw_arrow(ax, x1, y1, x2, y2, label=""):
    ax.annotate(
        "", xy=(x2, y2), xytext=(x1, y1),
        arrowprops=dict(arrowstyle="->", color="#333333", lw=1.5, mutation_scale=15),
        zorder=5
    )
    if label:
        mid_x = (x1 + x2) / 2
        mid_y = (y1 + y2) / 2
        ax.text(mid_x, mid_y + 0.15, label, ha='center', va='center', fontsize=8, color='#555555', backgroundcolor='#FFFFFF', zorder=6)

# ==============================================================================
# FIGURE 1.1: Bloom's Revised Taxonomy Hierarchy
# ==============================================================================
def create_fig_1_1():
    fig, ax = plt.subplots(figsize=(9, 5), dpi=300)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6.5)
    ax.axis('off')
    fig.patch.set_facecolor(BG_WHITE)

    ax.text(5, 6.1, "Figure 1.1: Anderson & Krathwohl's Revised Bloom Taxonomy Hierarchy", ha='center', va='center', fontsize=12, fontweight='bold', color=NAVY_HEADER)

    levels = [
        ("6. CREATE", "Build, Design, Synthesize, Architect", ORANGE_BOX, ORANGE_BORDER),
        ("5. EVALUATE", "Assess, Critique, Judge, Justify", ORANGE_BOX, ORANGE_BORDER),
        ("4. ANALYZE", "Differentiate, Deconstruct, Investigate", ORANGE_BOX, ORANGE_BORDER),
        ("3. APPLY", "Calculate, Execute, Implement, Solve", TEAL_BOX, TEAL_BORDER),
        ("2. UNDERSTAND", "Explain, Describe, Summarize, Classify", TEAL_BOX, TEAL_BORDER),
        ("1. REMEMBER", "Define, List, State, Recall", TEAL_BOX, TEAL_BORDER),
    ]

    # Draw pyramid levels
    for i, (title, sub, bg, border) in enumerate(levels):
        y = 5.2 - i * 0.8
        w = 4.0 + i * 0.8
        x = 5 - w/2
        draw_rounded_box(ax, x, y, w, 0.65, title, sub, bg_color=bg, border_color=border, fontsize=9.5)

    # Annotations for HOTS and LOTS
    ax.annotate("Higher-Order Thinking Skills\n(HOTS)", xy=(0.8, 4.2), fontsize=9, fontweight='bold', color=ORANGE_BORDER, ha='center')
    ax.annotate("Lower-Order Thinking Skills\n(LOTS)", xy=(0.8, 1.6), fontsize=9, fontweight='bold', color=TEAL_BORDER, ha='center')

    plt.tight_layout()
    out_path = os.path.join(figures_dir, "fig_1_1_bloom_taxonomy_hierarchy.png")
    plt.savefig(out_path, bbox_inches='tight', facecolor=BG_WHITE)
    plt.close()
    print(f"Saved: {out_path}")

# ==============================================================================
# FIGURE 1.2: System Boundary Architecture
# ==============================================================================
def create_fig_1_2():
    fig, ax = plt.subplots(figsize=(10, 5), dpi=300)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6)
    ax.axis('off')
    fig.patch.set_facecolor(BG_WHITE)

    ax.text(5, 5.6, "Figure 1.2: BloomEngine System Boundary Architecture", ha='center', va='center', fontsize=12, fontweight='bold', color=NAVY_HEADER)

    # Subgraph Boundaries
    b1 = patches.Rectangle((0.5, 0.8), 2.5, 4.2, ls='--', ec='#2F5597', fc='#F2F4F8', lw=1.5)
    b2 = patches.Rectangle((3.5, 0.8), 3.0, 4.2, ls='--', ec='#375623', fc='#F2F8F2', lw=1.5)
    b3 = patches.Rectangle((7.0, 0.8), 2.5, 4.2, ls='--', ec='#C65911', fc='#FDF6F2', lw=1.5)
    ax.add_patch(b1); ax.add_patch(b2); ax.add_patch(b3)

    ax.text(1.75, 4.7, "Client Boundary", ha='center', fontsize=10, fontweight='bold', color='#2F5597')
    ax.text(5.0, 4.7, "Application Boundary", ha='center', fontsize=10, fontweight='bold', color='#375623')
    ax.text(8.25, 4.7, "Data & Model Boundary", ha='center', fontsize=10, fontweight='bold', color='#C65911')

    # Components
    draw_rounded_box(ax, 0.8, 2.3, 1.9, 1.2, "Web Interface\n(SPA Client)", "HTML5 / JS / Chart.js", BLUE_BOX, BLUE_BORDER)
    draw_rounded_box(ax, 3.8, 3.0, 2.4, 1.0, "Flask Server\n(app.py)", "REST API & Routes", TEAL_BOX, TEAL_BORDER)
    draw_rounded_box(ax, 3.8, 1.3, 2.4, 1.0, "Validation Engine\n(7-Stage Core)", "validation_engine.py", TEAL_BOX, TEAL_BORDER)

    draw_rounded_box(ax, 7.3, 3.0, 1.9, 1.0, "AI Transformers", "DeBERTa / FLAN-T5", ORANGE_BOX, ORANGE_BORDER)
    draw_rounded_box(ax, 7.3, 1.3, 1.9, 1.0, "Session Store", "In-Memory / Uploads", ORANGE_BOX, ORANGE_BORDER)

    # Connections
    draw_arrow(ax, 2.7, 2.9, 3.8, 3.5, "HTTP POST")
    draw_arrow(ax, 5.0, 3.0, 5.0, 2.3)
    draw_arrow(ax, 6.2, 3.5, 7.3, 3.5, "Inference")
    draw_arrow(ax, 6.2, 1.8, 7.3, 1.8, "Cache")

    plt.tight_layout()
    out_path = os.path.join(figures_dir, "fig_1_2_system_boundary.png")
    plt.savefig(out_path, bbox_inches='tight', facecolor=BG_WHITE)
    plt.close()
    print(f"Saved: {out_path}")

# ==============================================================================
# FIGURE 4.1: High-Level Layered Architecture
# ==============================================================================
def create_fig_4_1():
    fig, ax = plt.subplots(figsize=(10, 6), dpi=300)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 7)
    ax.axis('off')
    fig.patch.set_facecolor(BG_WHITE)

    ax.text(5, 6.6, "Figure 4.1: High-Level Layered Architecture of BloomEngine", ha='center', va='center', fontsize=12, fontweight='bold', color=NAVY_HEADER)

    layers = [
        ("Presentation Layer", "Question Studio Playground | Analytics Dashboard | Bulk Document Processor | Export Engine", BLUE_BOX, BLUE_BORDER, 5.3),
        ("Controller & API Layer", "Flask REST Application (app.py) | Route Orchestration | Thread Locks | Memory Store", TEAL_BOX, TEAL_BORDER, 4.0),
        ("Natural Language Processing Layer", "spaCy Parser (Noun Chunks / NER) | Question Profiler | Domain Hierarchy Builder", ORANGE_BOX, ORANGE_BORDER, 2.7),
        ("AI Model & Inference Layer", "DeBERTa-v3 6-Class Classifier | FLAN-T5 Seq2Seq Generator | SBERT Vector Embeddings", GRAY_BOX, BORDER_GRAY, 1.4),
        ("Validation & Quality Control Engine", "7-Stage Sequential Pipeline (Bloom, Concept, Entity, Number, Knowledge, Semantic, Grammar)", BLUE_BOX, BLUE_BORDER, 0.1),
    ]

    for title, desc, bg, border, y in layers:
        draw_rounded_box(ax, 0.5, y, 9.0, 0.95, title, desc, bg_color=bg, border_color=border, fontsize=10)

    # Vertical connectors
    for y in [5.3, 4.0, 2.7, 1.4]:
        draw_arrow(ax, 5.0, y, 5.0, y - 0.35)

    plt.tight_layout()
    out_path = os.path.join(figures_dir, "fig_4_1_high_level_architecture.png")
    plt.savefig(out_path, bbox_inches='tight', facecolor=BG_WHITE)
    plt.close()
    print(f"Saved: {out_path}")

# ==============================================================================
# FIGURE 4.2: 7-Stage Validation Pipeline Flowchart
# ==============================================================================
def create_fig_4_2():
    fig, ax = plt.subplots(figsize=(11, 5.5), dpi=300)
    ax.set_xlim(0, 11)
    ax.set_ylim(0, 6)
    ax.axis('off')
    fig.patch.set_facecolor(BG_WHITE)

    ax.text(5.5, 5.6, "Figure 4.2: 7-Stage Sequential Validation Pipeline Flowchart", ha='center', va='center', fontsize=12, fontweight='bold', color=NAVY_HEADER)

    draw_rounded_box(ax, 0.3, 2.5, 1.2, 1.0, "Input\nCandidate", "FLAN-T5", ORANGE_BOX, ORANGE_BORDER, fontsize=8.5)

    stages = [
        ("S1: Bloom", "Verb & Class"),
        ("S2: Concept", "Noun Chunks"),
        ("S3: Entity", "Jargon/NER"),
        ("S4: Number", "Constants"),
        ("S5: Domain", "Topic Drift"),
        ("S6: Semantic", "SBERT Sim"),
        ("S7: Syntax", "Grammar"),
    ]

    for i, (title, sub) in enumerate(stages):
        x = 1.8 + i * 1.15
        draw_rounded_box(ax, x, 2.5, 1.0, 1.0, title, sub, BLUE_BOX, BLUE_BORDER, fontsize=8.5)
        if i == 0:
            draw_arrow(ax, 1.5, 3.0, 1.8, 3.0)
        else:
            draw_arrow(ax, x - 0.15, 3.0, x, 3.0)

    draw_rounded_box(ax, 9.85, 3.5, 1.0, 1.0, "Candidate\nRanker", "Score Weights", TEAL_BOX, TEAL_BORDER, fontsize=8.5)
    draw_rounded_box(ax, 9.85, 1.5, 1.0, 1.0, "Reject /\nRetry", "Log Reason", ORANGE_BOX, ORANGE_BORDER, fontsize=8.5)

    draw_arrow(ax, 9.7, 3.0, 9.85, 4.0, "Pass")
    draw_arrow(ax, 9.7, 3.0, 9.85, 2.0, "Fail")

    plt.tight_layout()
    out_path = os.path.join(figures_dir, "fig_4_2_validation_pipeline_flowchart.png")
    plt.savefig(out_path, bbox_inches='tight', facecolor=BG_WHITE)
    plt.close()
    print(f"Saved: {out_path}")

# Generate all figures
if __name__ == "__main__":
    create_fig_1_1()
    create_fig_1_2()
    create_fig_4_1()
    create_fig_4_2()
    print("All vector figures successfully generated!")
