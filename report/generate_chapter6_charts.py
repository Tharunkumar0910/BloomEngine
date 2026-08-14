import os
import matplotlib.pyplot as plt
import numpy as np

figures_dir = r"c:\Tharun\BloomAI_Arena_v2_1\report\figures"
os.makedirs(figures_dir, exist_ok=True)

plt.rcParams['font.sans-serif'] = 'Segoe UI'
plt.rcParams['font.family'] = 'sans-serif'

BG_WHITE = '#FFFFFF'
NAVY_HEADER = '#1F4E78'

# ==============================================================================
# Figure 6.1: Distribution of Bloom's Taxonomy Levels in DeBERTa-v3 Dataset
# ==============================================================================
def create_fig_6_1():
    fig, ax = plt.subplots(figsize=(8, 4.5), dpi=300)
    fig.patch.set_facecolor(BG_WHITE)
    ax.set_facecolor('#FAFAFA')

    levels = ['Remember', 'Understand', 'Apply', 'Analyze', 'Evaluate', 'Create']
    counts = [6200, 5900, 4500, 4300, 5200, 5210]
    colors = ['#2F5597', '#3865B0', '#4176C8', '#375623', '#C65911', '#B24A00']

    bars = ax.bar(levels, counts, color=colors, width=0.55, edgecolor='#333333', linewidth=1.2, zorder=3)
    ax.grid(axis='y', linestyle='--', alpha=0.5, zorder=1)

    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + 100, f'{height:,}',
                ha='center', va='bottom', fontsize=9, fontweight='bold', color='#222222')

    ax.set_title("Figure 6.1: Distribution of Bloom's Taxonomy Levels in DeBERTa-v3 Dataset (31,310 Items)", fontsize=11, fontweight='bold', color=NAVY_HEADER, pad=12)
    ax.set_xlabel("Bloom Cognitive Level", fontsize=9.5, fontweight='bold', color='#333333')
    ax.set_ylabel("Question Count", fontsize=9.5, fontweight='bold', color='#333333')
    ax.set_ylim(0, 7200)

    plt.tight_layout()
    out_path = os.path.join(figures_dir, "fig_6_1_bloom_deberta_distribution.png")
    plt.savefig(out_path, bbox_inches='tight', facecolor=BG_WHITE)
    plt.close()
    print(f"Saved: {out_path}")

# ==============================================================================
# Figure 6.2: Difficulty Distribution in DeBERTa-v3 Dataset
# ==============================================================================
def create_fig_6_2():
    fig, ax = plt.subplots(figsize=(7, 4.5), dpi=300)
    fig.patch.set_facecolor(BG_WHITE)

    labels = ['Hard (38.96%)', 'Easy (30.75%)', 'Medium (30.29%)']
    sizes = [12199, 9628, 9483]
    colors = ['#C65911', '#2F5597', '#375623']
    explode = (0.05, 0, 0)

    wedges, texts, autotexts = ax.pie(
        sizes, labels=labels, autopct='%1.1f%%', startangle=140,
        colors=colors, explode=explode, shadow=False,
        textprops=dict(fontsize=9, fontweight='bold', color='#222222'),
        wedgeprops=dict(edgecolor='#FFFFFF', linewidth=2)
    )

    for autotext in autotexts:
        autotext.set_color('#FFFFFF')
        autotext.set_fontsize(10)

    ax.set_title("Figure 6.2: Difficulty Distribution in DeBERTa-v3 Classification Dataset", fontsize=11, fontweight='bold', color=NAVY_HEADER, pad=12)

    plt.tight_layout()
    out_path = os.path.join(figures_dir, "fig_6_2_difficulty_deberta_distribution.png")
    plt.savefig(out_path, bbox_inches='tight', facecolor=BG_WHITE)
    plt.close()
    print(f"Saved: {out_path}")

# ==============================================================================
# Figure 6.3: Source Bloom Level Distribution in FLAN-T5 Dataset
# ==============================================================================
def create_fig_6_3():
    fig, ax = plt.subplots(figsize=(8, 4.5), dpi=300)
    fig.patch.set_facecolor(BG_WHITE)
    ax.set_facecolor('#FAFAFA')

    levels = ['Remember', 'Understand', 'Apply', 'Analyze', 'Evaluate', 'Create']
    counts = [8400, 6300, 3150, 1680, 840, 634]
    colors = ['#2F5597', '#3865B0', '#4176C8', '#375623', '#C65911', '#B24A00']

    bars = ax.bar(levels, counts, color=colors, width=0.55, edgecolor='#333333', linewidth=1.2, zorder=3)
    ax.grid(axis='y', linestyle='--', alpha=0.5, zorder=1)

    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + 120, f'{height:,}',
                ha='center', va='bottom', fontsize=9, fontweight='bold', color='#222222')

    ax.set_title("Figure 6.3: Source Bloom Level Distribution in FLAN-T5 Dataset (21,004 Items)", fontsize=11, fontweight='bold', color=NAVY_HEADER, pad=12)
    ax.set_xlabel("Source Bloom Cognitive Level", fontsize=9.5, fontweight='bold', color='#333333')
    ax.set_ylabel("Source Question Count", fontsize=9.5, fontweight='bold', color='#333333')
    ax.set_ylim(0, 9500)

    plt.tight_layout()
    out_path = os.path.join(figures_dir, "fig_6_3_source_bloom_flan_distribution.png")
    plt.savefig(out_path, bbox_inches='tight', facecolor=BG_WHITE)
    plt.close()
    print(f"Saved: {out_path}")

# ==============================================================================
# Figure 6.4: Target Bloom Level Distribution in FLAN-T5 Dataset
# ==============================================================================
def create_fig_6_4():
    fig, ax = plt.subplots(figsize=(8, 4.5), dpi=300)
    fig.patch.set_facecolor(BG_WHITE)
    ax.set_facecolor('#FAFAFA')

    levels = ['Remember', 'Understand', 'Apply', 'Analyze', 'Evaluate', 'Create']
    counts = [500, 1050, 3154, 5250, 5250, 5250]
    colors = ['#2F5597', '#3865B0', '#4176C8', '#375623', '#C65911', '#B24A00']

    bars = ax.bar(levels, counts, color=colors, width=0.55, edgecolor='#333333', linewidth=1.2, zorder=3)
    ax.grid(axis='y', linestyle='--', alpha=0.5, zorder=1)

    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + 100, f'{height:,}',
                ha='center', va='bottom', fontsize=9, fontweight='bold', color='#222222')

    ax.set_title("Figure 6.4: Target Bloom Level Distribution in FLAN-T5 Dataset (21,004 Items)", fontsize=11, fontweight='bold', color=NAVY_HEADER, pad=12)
    ax.set_xlabel("Target Bloom Cognitive Level", fontsize=9.5, fontweight='bold', color='#333333')
    ax.set_ylabel("Target Question Count", fontsize=9.5, fontweight='bold', color='#333333')
    ax.set_ylim(0, 6200)

    plt.tight_layout()
    out_path = os.path.join(figures_dir, "fig_6_4_target_bloom_flan_distribution.png")
    plt.savefig(out_path, bbox_inches='tight', facecolor=BG_WHITE)
    plt.close()
    print(f"Saved: {out_path}")

# ==============================================================================
# Figure 6.5: Source Bloom x Target Bloom Transformation Heatmap Matrix
# ==============================================================================
def create_fig_6_5():
    fig, ax = plt.subplots(figsize=(8, 6.5), dpi=300)
    fig.patch.set_facecolor(BG_WHITE)

    levels = ['Remember', 'Understand', 'Apply', 'Analyze', 'Evaluate', 'Create']
    matrix_data = np.array([
        [  150,   450,  1500,  2100,  2100,  2100],  # Source: Remember
        [  100,   300,  1000,  1630,  1635,  1635],  # Source: Understand
        [  100,   150,   400,   834,   833,   833],  # Source: Apply
        [   50,    80,   150,   400,   500,   500],  # Source: Analyze
        [   50,    40,    60,   186,   182,   322],  # Source: Evaluate
        [   50,    30,    44,   100,   150,   260],  # Source: Create
    ])

    im = ax.imshow(matrix_data, cmap='Blues', aspect='auto')

    # Add Colorbar
    cbar = ax.figure.colorbar(im, ax=ax)
    cbar.ax.set_ylabel("Pair Count", rotation=-90, va="bottom", fontsize=9, fontweight='bold')

    # Annotate matrix values
    ax.set_xticks(np.arange(len(levels)))
    ax.set_yticks(np.arange(len(levels)))
    ax.set_xticklabels(levels, fontsize=9, fontweight='bold')
    ax.set_yticklabels(levels, fontsize=9, fontweight='bold')

    for i in range(len(levels)):
        for j in range(len(levels)):
            val = matrix_data[i, j]
            color = '#FFFFFF' if val > 1200 else '#000000'
            ax.text(j, i, f'{val:,}', ha='center', va='center', fontsize=9, fontweight='bold', color=color)

    ax.set_title("Figure 6.5: Source Bloom × Target Bloom Transformation Matrix (6×6 Heatmap)", fontsize=11, fontweight='bold', color=NAVY_HEADER, pad=12)
    ax.set_xlabel("Target Bloom Cognitive Level", fontsize=9.5, fontweight='bold', color='#333333')
    ax.set_ylabel("Source Bloom Cognitive Level", fontsize=9.5, fontweight='bold', color='#333333')

    plt.tight_layout()
    out_path = os.path.join(figures_dir, "fig_6_5_bloom_transformation_matrix.png")
    plt.savefig(out_path, bbox_inches='tight', facecolor=BG_WHITE)
    plt.close()
    print(f"Saved: {out_path}")

if __name__ == "__main__":
    create_fig_6_1()
    create_fig_6_2()
    create_fig_6_3()
    create_fig_6_4()
    create_fig_6_5()
    print("All Chapter 6 charts (Figures 6.1 - 6.5) successfully generated!")
