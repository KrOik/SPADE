import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl
import seaborn as sns

# Use a font that is widely available
mpl.rcParams['font.family'] = 'sans-serif'
mpl.rcParams['axes.unicode_minus'] = False

# Black/white friendly styling with hatches
COLORS = ['#4e79a7', '#f28e2b', '#59a14f', '#e15759']  # used on screen
HATCHES = ['/', '\\', 'x', 'o']  # used to remain distinguishable when printed B/W

PRESHOW_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(PRESHOW_DIR, "viz/output")
os.makedirs(OUTPUT_DIR, exist_ok=True)

def load_data():
    comp_path = os.path.join(PRESHOW_DIR, "data/summary/compare.csv")
    fields_path = os.path.join(PRESHOW_DIR, "data/summary/fields_coverage.csv")
    comp = pd.read_csv(comp_path)
    fields = pd.read_csv(fields_path)
    # Clean column names if needed
    comp.columns = [c.strip() for c in comp.columns]
    fields.columns = [c.strip() for c in fields.columns]
    return comp, fields

def bar_with_hatches(ax, xlabels, values, title, ylabel):
    bars = ax.bar(range(len(values)), values, color=COLORS[:len(values)], edgecolor='black')
    for i, b in enumerate(bars):
        b.set_hatch(HATCHES[i % len(HATCHES)])
        # Format numbers to be more readable
        try:
            val = float(values[i])
            value_text = f'{int(val)}' if val.is_integer() else f'{val:.1f}'
        except (ValueError, TypeError):
            value_text = values[i] # Keep as string if not a number
        ax.text(b.get_x() + b.get_width()/2, b.get_height(), value_text, ha='center', va='bottom', fontsize=9)
    ax.set_xticks(range(len(xlabels)))
    ax.set_xticklabels(xlabels, rotation=0)
    ax.set_title(title, fontsize=14)
    ax.set_ylabel(ylabel, fontsize=10)
    ax.grid(axis='y', linestyle='--', alpha=0.4)

def fig_legend(labels, fname):
    # Standalone legend figure for B/W printing reference
    fig, ax = plt.subplots(figsize=(4, 0.6))
    handles = []
    for i, lab in enumerate(labels):
        patch = mpl.patches.Patch(facecolor=COLORS[i % len(COLORS)], hatch=HATCHES[i % len(HATCHES)], edgecolor='black', label=lab)
        handles.append(patch)
    ax.legend(handles=handles, loc='center', ncol=len(labels), frameon=False)
    ax.axis('off')
    fig.tight_layout()
    fig.savefig(os.path.join(OUTPUT_DIR, fname), dpi=200)
    plt.close(fig)

def create_bar_chart(comp_df, value_col, title, ylabel, xlabel, filename, y_lim=None):
    """Helper function to create a bar chart."""
    dbs = comp_df['database'].tolist()
    vals = pd.to_numeric(comp_df[value_col], errors='coerce').fillna(0).tolist()
    fig, ax = plt.subplots(figsize=(7, 4))
    bar_with_hatches(ax, dbs, vals, title, ylabel)
    ax.set_xlabel(xlabel, fontsize=10)
    if y_lim:
        ax.set_ylim(y_lim)
    fig.tight_layout()
    fig.savefig(os.path.join(OUTPUT_DIR, filename), dpi=200)
    plt.close(fig)

def create_pie_chart(comp_df, value_col, title, filename):
    """Helper function to create a pie chart."""
    dbs = comp_df['database'].tolist()
    vals = pd.to_numeric(comp_df[value_col], errors='coerce').fillna(0).tolist()
    fig, ax = plt.subplots(figsize=(7, 5))
    ax.pie(vals, labels=dbs, autopct='%1.1f%%', startangle=90, colors=COLORS)
    ax.set_title(title, fontsize=14)
    fig.tight_layout()
    fig.savefig(os.path.join(OUTPUT_DIR, filename), dpi=200)
    plt.close(fig)

def create_heatmap(fields_df, title, filename):
    """Helper function to create a heatmap."""
    fields_df = fields_df.set_index('database')
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.heatmap(fields_df, annot=True, fmt=".0f", cmap="viridis", ax=ax)
    ax.set_title(title, fontsize=14)
    plt.xticks(rotation=45, ha='right')
    plt.yticks(rotation=0)
    fig.tight_layout()
    fig.savefig(os.path.join(OUTPUT_DIR, filename), dpi=200)
    plt.close(fig)

def create_horizontal_bar_chart(comp_df, value_col, title, xlabel, ylabel, filename, x_lim=None):
    """Helper function to create a horizontal bar chart."""
    dbs = comp_df['database'].tolist()
    vals = pd.to_numeric(comp_df[value_col], errors='coerce').fillna(0).tolist()
    fig, ax = plt.subplots(figsize=(7, 4))
    bars = ax.barh(range(len(vals)), vals, color=COLORS[:len(vals)], edgecolor='black')
    for i, b in enumerate(bars):
        b.set_hatch(HATCHES[i % len(HATCHES)])
        ax.text(b.get_width(), b.get_y() + b.get_height()/2, f'{vals[i]:.1f}', ha='left', va='center', fontsize=9)
    ax.set_yticks(range(len(dbs)))
    ax.set_yticklabels(dbs)
    ax.set_title(title, fontsize=14)
    ax.set_xlabel(xlabel, fontsize=10)
    ax.set_ylabel(ylabel, fontsize=10)
    if x_lim:
        ax.set_xlim(x_lim)
    fig.tight_layout()
    fig.savefig(os.path.join(OUTPUT_DIR, filename), dpi=200)
    plt.close(fig)

def create_latex_style_table(comp: pd.DataFrame):
    """Creates a LaTeX-style table with key data."""
    key_data_df = comp[['database', 'total_entries', 'avg_field_completeness_pct', 'updates_last_3y', 'ai_score_0_5']]
    key_data_df.columns = ['Database', 'Total Entries', 'Field Completeness (%)', 'Updates (Last 3Y)', 'AI Score (0-5)']

    fig = plt.figure(figsize=(10, 2.5))
    ax = fig.add_subplot(111)
    ax.axis('off')

    table = ax.table(cellText=key_data_df.values, colLabels=key_data_df.columns, loc='center', cellLoc='center')

    table.auto_set_font_size(False)
    table.set_fontsize(12)
    table.scale(1, 1.5)

    for (i, j), cell in table.get_celld().items():
        cell.set_edgecolor('none')
        if i == 0:
            cell.set_text_props(weight='bold')
            cell.set_edgecolor('black')
        if i > 0:
             cell.set_edgecolor('lightgrey')

    plt.savefig(os.path.join(OUTPUT_DIR, 'key_data_table.png'), bbox_inches='tight', pad_inches=0.1, dpi=300)
    plt.close(fig)

def main():
    comp, fields = load_data()
    create_latex_style_table(comp)
    print(f"Charts and tables saved to {OUTPUT_DIR}")

if __name__ == "__main__":
    main()