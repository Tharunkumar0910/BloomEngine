import os

def render_diagram():
    try:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        import matplotlib.patches as patches
    except ImportError:
        print("Matplotlib not ready yet.")
        return

    # Create figure with high DPI for A4 printing landscape
    fig, ax = plt.subplots(figsize=(20, 15), dpi=300)
    fig.patch.set_facecolor('#FFFFFF')
    ax.set_facecolor('#FFFFFF')
    ax.axis('off')

    # Color Palette (Academic Blue and Gray theme)
    PRIMARY_HEADER = '#1E3A8A'  # Deep Navy Blue
    HEADER_BLUE    = '#1D4ED8'  # Royal Blue
    ACCENT_BLUE    = '#2563EB'  # Bright Academic Blue
    NLP_BLUE      = '#3B82F6'  # Deep Sky Blue
    VALIDATION_GRAY= '#64748B'  # Slate Gray
    STORAGE_GRAY   = '#475569'  # Dark Slate
    OUTPUT_DARK    = '#0F172A'  # Slate Dark
    
    LAYER_BG       = '#F8FAFC'  # Off-white / light slate
    CARD_BG        = '#FFFFFF'  # Pure white card
    CARD_BORDER    = '#CBD5E1'  # Light gray border
    TEXT_MAIN      = '#0F172A'  # Dark slate text
    TEXT_MUTED     = '#475569'  # Muted slate text

    # Layer Definitions (Title, Height, Header Fill, Subtitle)
    layers = [
        ("1. USER LAYER (Actors & Clients)", 1.0, PRIMARY_HEADER, "(Academic Educators, Web Browsers & Question Bank Administrators)"),
        ("2. PRESENTATION LAYER (Frontend Web UI)", 1.4, HEADER_BLUE, "(templates/landing.html, auth.html, index.html | static/js/main.js)"),
        ("3. APPLICATION LAYER (Flask Server & APIs)", 2.0, ACCENT_BLUE, "(app.py | REST API Services, Document Parsing & Async Exporters)"),
        ("4. AI / NLP PROCESSING LAYER (Deep Learning Models)", 2.2, NLP_BLUE, "(DeBERTa Classifier, FLAN-T5 Generator, Question Understanding & Knowledge Base)"),
        ("5. VALIDATION ENGINE LAYER (7-Stage NLP Pipeline)", 2.1, VALIDATION_GRAY, "(validation_engine.py | 7-Stage Weighted Multi-Criteria NLP Engine)"),
        ("6. STORAGE & CACHING LAYER (Memory & Local Disk)", 1.2, STORAGE_GRAY, "(In-Memory Session Store, Thread-Safe Embedding Cache & Uploads)"),
        ("7. OUTPUT LAYER (Artifacts & File Deliverables)", 0.9, OUTPUT_DARK, "(Rephrased Questions, Multi-Format Bank Files, Rejection Logs & QA Reports)")
    ]

    # Y-coordinates computation
    total_height = sum(l[1] for l in layers) + len(layers) * 0.4 + 1.5
    ax.set_xlim(0, 22)
    ax.set_ylim(0, total_height)

    # Title
    ax.text(11, total_height - 0.5, "Figure 3.1 Overall System Architecture of BloomEngine", 
            fontsize=20, fontweight='bold', color='#0F172A', ha='center', va='center')
    ax.text(11, total_height - 0.85, "Comprehensive Layered Architecture Inferred from Source Code Implementation", 
            fontsize=12, fontweight='medium', color='#475569', ha='center', va='center')

    current_y = total_height - 1.4

    layer_boxes = []

    for idx, (title, h, header_color, subtitle) in enumerate(layers):
        current_y -= h
        layer_y = current_y
        
        # Layer outer frame (rounded rectangle)
        rect = patches.FancyBboxPatch((0.8, layer_y), 20.4, h,
                                      boxstyle="round,pad=0.03,rounding_size=0.15",
                                      linewidth=1.2, edgecolor='#CBD5E1', facecolor=LAYER_BG)
        ax.add_patch(rect)

        # Layer Side Header Bar
        header_rect = patches.FancyBboxPatch((0.8, layer_y), 2.8, h,
                                             boxstyle="round,pad=0.03,rounding_size=0.15",
                                             linewidth=0, edgecolor='none', facecolor=header_color)
        ax.add_patch(header_rect)
        # Patch overlap rectangle to ensure clean straight divider on right side of header
        ax.add_patch(patches.Rectangle((3.4, layer_y), 0.2, h, facecolor=header_color, edgecolor='none'))

        # Header Text
        words = title.split(' ')
        num_part = words[0] + ' ' + words[1]
        name_part = ' '.join(words[2:])
        
        ax.text(2.2, layer_y + h/2 + 0.15, num_part, fontsize=11, fontweight='bold', color='#FFFFFF', ha='center', va='center')
        ax.text(2.2, layer_y + h/2 - 0.15, name_part, fontsize=10, fontweight='bold', color='#FFFFFF', ha='center', va='center')

        layer_boxes.append((layer_y, h))

        # Render Specific Cards per Layer
        if idx == 0: # User Layer
            cards = [
                ("Academic Educators & Test Creators", "Input Single Questions or Bulk Files\n(TXT, CSV, PDF, DOCX)", 3.4, 5.2),
                ("Client Web Browsers", "Desktop & Mobile HTML5 Browsers\n(REST API / HTTP Communication)", 9.0, 5.2),
                ("Question Bank Administrators", "Manual Reclassification Reviewers\n& Multi-Format Export Consumers", 14.6, 5.2)
            ]
            for ctitle, cdesc, cx, cw in cards:
                c_box = patches.FancyBboxPatch((cx, layer_y + 0.15), cw, h - 0.3,
                                               boxstyle="round,pad=0.02,rounding_size=0.1",
                                               linewidth=1, edgecolor='#94A3B8', facecolor=CARD_BG)
                ax.add_patch(c_box)
                ax.text(cx + cw/2, layer_y + h/2 + 0.12, ctitle, fontsize=10, fontweight='bold', color=TEXT_MAIN, ha='center', va='center')
                ax.text(cx + cw/2, layer_y + h/2 - 0.15, cdesc, fontsize=8.5, color=TEXT_MUTED, ha='center', va='center')

        elif idx == 1: # Presentation Layer
            cards = [
                ("Landing Page Module", "templates/landing.html\nstatic/js/landing.js | landing.css", 3.4, 3.8),
                ("Authentication Page", "templates/auth.html\nstatic/js/auth.js | auth.css", 7.5, 3.8),
                ("Interactive Main Dashboard UI", "templates/index.html | main.js | style.css\nSingle & Batch Classifier, Progress Bar & Upload Drag-Drop", 11.6, 5.2),
                ("Modals & Widgets", "Manual Reclassification Editor\nAnalytics & Multi-Format Exporter Modal", 17.1, 3.9)
            ]
            for ctitle, cdesc, cx, cw in cards:
                border_c = ACCENT_BLUE if "Main Dashboard" in ctitle else '#94A3B8'
                lw = 1.4 if "Main Dashboard" in ctitle else 1.0
                c_box = patches.FancyBboxPatch((cx, layer_y + 0.15), cw, h - 0.3,
                                               boxstyle="round,pad=0.02,rounding_size=0.1",
                                               linewidth=lw, edgecolor=border_c, facecolor=CARD_BG)
                ax.add_patch(c_box)
                ax.text(cx + cw/2, layer_y + h/2 + 0.15, ctitle, fontsize=9.5, fontweight='bold', color=PRIMARY_HEADER, ha='center', va='center')
                ax.text(cx + cw/2, layer_y + h/2 - 0.18, cdesc, fontsize=8, color=TEXT_MUTED, ha='center', va='center')

        elif idx == 2: # Application Layer
            cards = [
                ("Flask Web Server (app.py)", "Flask App Router & Secret Keys\nLifecycle & Warmup Handler\nSession Store & Thread Locks\nGET /, /landing, /dashboard, /health", 3.4, 4.0),
                ("REST API Endpoints Services", "POST /classify & /rephrase\nPOST /parse-upload & /upload-batch\nPOST /start-batch & GET /batch-status\nPUT /update-question & DELETE /delete-question", 7.7, 4.2),
                ("Document Extraction Engine", "Multi-Format Parsers:\n• Plain Text (.txt)\n• CSV / TSV Reader\n• PDF Reader (PyPDF2)\n• MS Word (python-docx)", 12.2, 3.8),
                ("Async Exporters & Workers", "Background Thread Worker\nMulti-Format Bank Exporters:\n• CSV, Excel (pandas/openpyxl)\n• MS Word (docx), PDF (FPDF), PPTX\n• Rejection Log (/export-rejections)", 16.3, 4.7)
            ]
            for ctitle, cdesc, cx, cw in cards:
                border_c = ACCENT_BLUE if "Flask" in ctitle else '#94A3B8'
                lw = 1.4 if "Flask" in ctitle else 1.0
                c_box = patches.FancyBboxPatch((cx, layer_y + 0.15), cw, h - 0.3,
                                               boxstyle="round,pad=0.02,rounding_size=0.1",
                                               linewidth=lw, edgecolor=border_c, facecolor=CARD_BG)
                ax.add_patch(c_box)
                ax.text(cx + cw/2, layer_y + h - 0.4, ctitle, fontsize=9.5, fontweight='bold', color=PRIMARY_HEADER, ha='center', va='center')
                ax.text(cx + cw/2, layer_y + (h - 0.4)/2, cdesc, fontsize=8, color=TEXT_MUTED, ha='center', va='center')

        elif idx == 3: # AI / NLP Processing Layer
            cards = [
                ("DeBERTa Bloom Classifier", "deberta_bloom_model/\nAutoModelForSequenceClassification\nPredicts 6 Bloom Levels & Difficulty\n(Remember, Understand, Apply,\nAnalyze, Evaluate, Create)", 3.4, 4.0),
                ("FLAN-T5 Question Generator", "flan_t5_model/\nAutoModelForSeq2SeqLM\nprompt_templates.py Prompt Builder\nTarget Bloom Level Rephrasing\nBeam Search & Multi-Candidate Generation", 7.7, 4.2),
                ("Question Understanding Engine", "question_understanding.py & profile.py\nQuestionProfile Dataclass Extraction\nspaCy Syntactic Dependency Parser\nSentenceTransformers ('all-MiniLM-L6-v2')\nvia spacy_utils.py", 12.2, 4.2),
                ("Domain Knowledge Taxonomy", "domain_hierarchy_builder.py\nknowledge/ (concepts, topics, domains)\nCS Domain Taxonomy Mapping\ncandidate_ranker.py (NLP Ranker)\nBLEU & ROUGE-L Metric Calculators", 16.7, 4.3)
            ]
            for ctitle, cdesc, cx, cw in cards:
                border_c = ACCENT_BLUE if ("DeBERTa" in ctitle or "FLAN-T5" in ctitle) else '#94A3B8'
                lw = 1.4 if ("DeBERTa" in ctitle or "FLAN-T5" in ctitle) else 1.0
                c_box = patches.FancyBboxPatch((cx, layer_y + 0.15), cw, h - 0.3,
                                               boxstyle="round,pad=0.02,rounding_size=0.1",
                                               linewidth=lw, edgecolor=border_c, facecolor=CARD_BG)
                ax.add_patch(c_box)
                ax.text(cx + cw/2, layer_y + h - 0.4, ctitle, fontsize=9.5, fontweight='bold', color=PRIMARY_HEADER, ha='center', va='center')
                ax.text(cx + cw/2, layer_y + (h - 0.4)/2, cdesc, fontsize=8, color=TEXT_MUTED, ha='center', va='center')

        elif idx == 4: # Validation Layer
            # Top Orchestrator bar inside validation layer
            orch_rect = patches.FancyBboxPatch((3.4, layer_y + h - 0.5), 17.6, 0.38,
                                                boxstyle="round,pad=0.01,rounding_size=0.08",
                                                linewidth=0, edgecolor='none', facecolor=PRIMARY_HEADER)
            ax.add_patch(orch_rect)
            ax.text(12.2, layer_y + h - 0.31, "Validation Engine Orchestrator (validation_engine.py & validation_models.py) | Active Profiles: Strict / Balanced / Relaxed",
                    fontsize=9.5, fontweight='bold', color='#FFFFFF', ha='center', va='center')

            # 7 stages boxes
            v_stages = [
                ("Stage 1: Bloom & Verbs", "bloom_validator.py\nDeBERTa (Wt: 35%)", 3.4, 4.2),
                ("Stage 2: Concept Pres.", "concept_validator.py\nCosine Sim (Wt: 10%)", 7.8, 4.1),
                ("Stage 3: Entity Pres.", "entity_validator.py\nspaCy NER (Wt: 10%)", 12.1, 4.2),
                ("Stage 4: Numbers Check", "number_validator.py\nNumeric Match (Wt: 5%)", 16.5, 4.5),
                
                ("Stage 5: Knowledge Drift", "knowledge_consistency_validator.py\nDomain Drift Penalty", 3.4, 4.2),
                ("Stage 6: Semantics & Dups", "semantic_validator.py\nduplicate_validator.py", 7.8, 4.1),
                ("Stage 7: Grammar & Formatting", "grammar_validator.py\nLength Limits (Wt: 3%)", 12.1, 4.2),
                ("Domain & Topic Checks", "topic_validator.py\nDomain: 20% | Topic: 15%", 16.5, 4.5)
            ]
            
            for s_idx, (stitle, sdesc, sx, sw) in enumerate(v_stages):
                sy = layer_y + 0.85 if s_idx < 4 else layer_y + 0.12
                c_box = patches.FancyBboxPatch((sx, sy), sw, 0.6,
                                               boxstyle="round,pad=0.01,rounding_size=0.08",
                                               linewidth=1, edgecolor='#94A3B8', facecolor=CARD_BG)
                ax.add_patch(c_box)
                ax.text(sx + sw/2, sy + 0.38, stitle, fontsize=8.5, fontweight='bold', color=PRIMARY_HEADER, ha='center', va='center')
                ax.text(sx + sw/2, sy + 0.16, sdesc, fontsize=7.5, color=TEXT_MUTED, ha='center', va='center')

        elif idx == 5: # Storage Layer
            cards = [
                ("In-Memory Session Store", "MEMORY_STORE & SESSION_STATE in app.py\nBATCH_HISTORY & Question State Registry", 3.4, 5.2),
                ("Thread-Safe Embedding Cache", "EMBEDDING_CACHE & EMBEDDING_CACHE_LOCK\nHits/Misses Tracker (normalize_embedding_key)", 9.0, 5.4),
                ("Local File System Storage", "Uploads Folder (static/uploads/)\nModel Weights (model.safetensors) & JSON Benchmarks", 14.7, 5.1)
            ]
            for ctitle, cdesc, cx, cw in cards:
                border_c = ACCENT_BLUE if "Embedding Cache" in ctitle else '#94A3B8'
                lw = 1.4 if "Embedding Cache" in ctitle else 1.0
                c_box = patches.FancyBboxPatch((cx, layer_y + 0.15), cw, h - 0.3,
                                               boxstyle="round,pad=0.02,rounding_size=0.1",
                                               linewidth=lw, edgecolor=border_c, facecolor=CARD_BG)
                ax.add_patch(c_box)
                ax.text(cx + cw/2, layer_y + h/2 + 0.12, ctitle, fontsize=9.5, fontweight='bold', color=PRIMARY_HEADER, ha='center', va='center')
                ax.text(cx + cw/2, layer_y + h/2 - 0.15, cdesc, fontsize=8, color=TEXT_MUTED, ha='center', va='center')

        elif idx == 6: # Output Layer
            cards = [
                ("Rephrased Questions", "Validated Target Bloom Question Bank", 3.4, 4.0),
                ("Multi-Format Question Files", "CSV, Excel (.xlsx), Word (.docx), PDF, PPTX", 7.6, 4.4),
                ("Rejection Audit Log", "Failed Questions & Detailed Stage Reasons", 12.2, 4.2),
                ("Benchmarking Reports", "benchmark_report.md & QA metrics", 16.6, 4.4)
            ]
            for ctitle, cdesc, cx, cw in cards:
                border_c = ACCENT_BLUE if "Multi-Format" in ctitle else '#94A3B8'
                lw = 1.4 if "Multi-Format" in ctitle else 1.0
                c_box = patches.FancyBboxPatch((cx, layer_y + 0.12), cw, h - 0.24,
                                               boxstyle="round,pad=0.02,rounding_size=0.1",
                                               linewidth=lw, edgecolor=border_c, facecolor=CARD_BG)
                ax.add_patch(c_box)
                ax.text(cx + cw/2, layer_y + h/2 + 0.1, ctitle, fontsize=9, fontweight='bold', color=PRIMARY_HEADER, ha='center', va='center')
                ax.text(cx + cw/2, layer_y + h/2 - 0.12, cdesc, fontsize=7.8, color=TEXT_MUTED, ha='center', va='center')

        # Draw connecting arrows between layers
        if idx < len(layers) - 1:
            arrow_y_start = layer_y
            arrow_y_end = layer_y - 0.4
            ax.annotate('', xy=(11, arrow_y_end), xytext=(11, arrow_y_start),
                        arrowprops=dict(arrowstyle="-|>", color='#475569', lw=2, mutation_scale=15))

        current_y -= 0.4

    plt.tight_layout()
    output_png = r"C:\Users\pushp\.gemini\antigravity-ide\brain\2aa13ed8-7333-4381-9075-7e8843d0d373\bloomengine_architecture.png"
    fig.savefig(output_png, dpi=300, bbox_inches='tight', facecolor=fig.get_facecolor(), edgecolor='none')
    plt.close(fig)
    print("PNG rendered successfully at:", output_png)

if __name__ == "__main__":
    render_diagram()
