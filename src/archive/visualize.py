"""
Generate publication-quality figures for the LLM diagnostic bias study.

Figures:
1. Heatmap: Correct diagnosis rate differential by sex × condition × model
2. Bar chart: Mean urgency rating by sex for each condition
3. Forest plot: Effect sizes (Cohen's d) for sex differential across conditions
4. Concordance chart: Does model bias match documented clinical bias?
5. Bias indicator frequency comparison
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
from pathlib import Path
import json
import os
import warnings

warnings.filterwarnings("ignore")

# --- Style configuration ---
plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Inter", "Helvetica Neue", "Arial", "sans-serif"],
    "font.size": 11,
    "axes.titlesize": 13,
    "axes.labelsize": 11,
    "figure.dpi": 150,
    "savefig.dpi": 300,
    "savefig.bbox": "tight",
    "axes.spines.top": False,
    "axes.spines.right": False,
})

# Color palette
COLORS = {
    "female": "#E07A5F",      # terracotta
    "male": "#3D405B",         # dark slate
    "unspecified": "#81B29A",  # sage
    "bias_red": "#E07A5F",     # for female-disadvantaged
    "no_bias": "#81B29A",      # for no differential
    "bias_blue": "#457B9D",    # for male-disadvantaged
    "bg": "#FAFAFA",
    "grid": "#E8E8E8",
}

# Readable condition names
CONDITION_LABELS = {
    "acute_coronary_syndrome_atypical": "ACS\n(Atypical)",
    "endometriosis": "Endo-\nmetriosis",
    "adhd_inattentive": "ADHD\n(Inattentive)",
    "autoimmune_lupus": "Autoimmune\n(Lupus/RA)",
    "acute_mi_classic": "MI Classic\n(Control)",
}

FIGURES_DIR = "outputs/figures"


def ensure_output_dir():
    os.makedirs(FIGURES_DIR, exist_ok=True)


def load_analysis_results(path: str = "outputs/tables/analysis_results.csv") -> pd.DataFrame:
    return pd.read_csv(path)


def load_parsed_results(path: str = "data/results/parsed_results.csv") -> pd.DataFrame:
    return pd.read_csv(path)


# ─────────────────────────────────────────────────────────────
# Figure 1: Heatmap — Correct diagnosis rate differential
# ─────────────────────────────────────────────────────────────

def plot_heatmap(results_df: pd.DataFrame):
    """
    Heatmap of correct diagnosis rate differential (female - male).
    Red = model disadvantages female patients.
    Blue = model disadvantages male patients.
    """
    ensure_output_dir()
    
    # Pivot to get female_rate - male_rate
    results_df = results_df.copy()
    results_df["rate_differential"] = (
        results_df["female_correct_rate"] - results_df["male_correct_rate"]
    )
    
    # Map condition names
    results_df["condition_label"] = results_df["condition"].map(CONDITION_LABELS)
    
    pivot = results_df.pivot_table(
        values="rate_differential",
        index="condition_label",
        columns="model",
        aggfunc="mean"
    )
    
    fig, ax = plt.subplots(figsize=(8, 5))
    
    sns.heatmap(
        pivot,
        cmap="RdBu",
        center=0,
        vmin=-0.3,
        vmax=0.3,
        annot=True,
        fmt=".2f",
        linewidths=1,
        linecolor="white",
        cbar_kws={"label": "Female rate − Male rate", "shrink": 0.8},
        ax=ax,
    )
    
    ax.set_title("Correct Diagnosis Rate: Sex Differential by Condition × Model",
                 fontweight="bold", pad=15)
    ax.set_xlabel("")
    ax.set_ylabel("")
    
    # Add annotation
    fig.text(0.5, -0.02,
             "Red = model disadvantages female patients | Blue = model disadvantages male patients",
             ha="center", fontsize=9, color="#666666")
    
    plt.tight_layout()
    path = os.path.join(FIGURES_DIR, "heatmap_diagnosis_differential.png")
    fig.savefig(path)
    plt.close()
    print(f"Saved: {path}")


# ─────────────────────────────────────────────────────────────
# Figure 2: Bar chart — Urgency rating by sex
# ─────────────────────────────────────────────────────────────

def plot_urgency_bars(parsed_df: pd.DataFrame):
    """
    Mean urgency rating by sex for each condition, grouped by model.
    Error bars = 95% CI.
    """
    ensure_output_dir()
    
    # Map condition names
    parsed_df = parsed_df.copy()
    parsed_df["condition_label"] = parsed_df["condition"].map(CONDITION_LABELS)
    
    models = sorted(parsed_df["model"].unique())
    conditions = sorted(parsed_df["condition"].unique())
    n_models = len(models)
    
    fig, axes = plt.subplots(1, n_models, figsize=(6 * n_models, 5), sharey=True)
    if n_models == 1:
        axes = [axes]
    
    for ax, model in zip(axes, models):
        model_data = parsed_df[parsed_df["model"] == model]
        
        x = np.arange(len(conditions))
        width = 0.25
        
        for i, (sex, color) in enumerate([
            ("female", COLORS["female"]),
            ("male", COLORS["male"]),
            ("unspecified", COLORS["unspecified"]),
        ]):
            sex_data = model_data[model_data["patient_sex"] == sex]
            means = []
            cis = []
            
            for condition in conditions:
                cond_data = sex_data[sex_data["condition"] == condition]["urgency"].dropna()
                if len(cond_data) > 0:
                    mean = cond_data.mean()
                    ci = 1.96 * cond_data.std() / np.sqrt(len(cond_data))
                    means.append(mean)
                    cis.append(ci)
                else:
                    means.append(0)
                    cis.append(0)
            
            ax.bar(
                x + (i - 1) * width,
                means,
                width,
                yerr=cis,
                color=color,
                alpha=0.85,
                label=sex.capitalize(),
                capsize=3,
                error_kw={"linewidth": 1},
            )
        
        condition_labels = [CONDITION_LABELS.get(c, c) for c in conditions]
        ax.set_xticks(x)
        ax.set_xticklabels(condition_labels, fontsize=9)
        ax.set_title(model, fontweight="bold")
        ax.set_ylim(0, 5.5)
        ax.set_ylabel("Mean Urgency Rating (1-5)" if ax == axes[0] else "")
        ax.axhline(y=3, color=COLORS["grid"], linestyle="--", alpha=0.5)
        ax.legend(fontsize=9)
    
    fig.suptitle("Assigned Urgency Rating by Patient Sex and Condition",
                 fontweight="bold", fontsize=14, y=1.02)
    
    plt.tight_layout()
    path = os.path.join(FIGURES_DIR, "urgency_by_sex.png")
    fig.savefig(path)
    plt.close()
    print(f"Saved: {path}")


# ─────────────────────────────────────────────────────────────
# Figure 3: Forest plot — Effect sizes for sex differential
# ─────────────────────────────────────────────────────────────

def plot_forest(results_df: pd.DataFrame):
    """
    Forest plot of Cohen's d for urgency rating sex differential.
    Positive d = higher urgency for female (less bias).
    Negative d = lower urgency for female (more bias).
    """
    ensure_output_dir()
    
    # Filter to rows with effect sizes
    plot_data = results_df.dropna(subset=["urgency_cohens_d"]).copy()
    
    if len(plot_data) == 0:
        print("No effect size data available for forest plot — skipping.")
        return
    
    plot_data["label"] = (
        plot_data["condition"].map(CONDITION_LABELS).str.replace("\n", " ") +
        " | " + plot_data["model"]
    )
    
    # Sort by effect size
    plot_data = plot_data.sort_values("urgency_cohens_d")
    
    fig, ax = plt.subplots(figsize=(10, max(4, len(plot_data) * 0.6)))
    
    y_pos = np.arange(len(plot_data))
    
    for i, (_, row) in enumerate(plot_data.iterrows()):
        d = row["urgency_cohens_d"]
        ci_lo = row.get("urgency_d_ci_lower", d - 0.3)
        ci_hi = row.get("urgency_d_ci_upper", d + 0.3)
        
        color = COLORS["bias_red"] if d < 0 else COLORS["no_bias"]
        
        ax.errorbar(
            d, i,
            xerr=[[d - ci_lo], [ci_hi - d]],
            fmt="o",
            color=color,
            markersize=8,
            capsize=4,
            linewidth=2,
        )
    
    ax.axvline(x=0, color="#333", linewidth=1, linestyle="-", alpha=0.5)
    ax.set_yticks(y_pos)
    ax.set_yticklabels(plot_data["label"], fontsize=10)
    ax.set_xlabel("Cohen's d (urgency: female − male)", fontsize=11)
    ax.set_title("Sex Differential in Urgency Rating — Effect Sizes with 95% CI",
                 fontweight="bold", pad=15)
    
    # Add interpretation labels
    ax.text(ax.get_xlim()[0] + 0.05, len(plot_data) + 0.3,
            "← Female assigned lower urgency",
            fontsize=9, color=COLORS["bias_red"], ha="left")
    ax.text(ax.get_xlim()[1] - 0.05, len(plot_data) + 0.3,
            "Female assigned higher urgency →",
            fontsize=9, color=COLORS["no_bias"], ha="right")
    
    ax.set_facecolor(COLORS["bg"])
    ax.grid(axis="x", alpha=0.3)
    
    plt.tight_layout()
    path = os.path.join(FIGURES_DIR, "forest_plot_urgency.png")
    fig.savefig(path)
    plt.close()
    print(f"Saved: {path}")


# ─────────────────────────────────────────────────────────────
# Figure 4: Concordance chart
# ─────────────────────────────────────────────────────────────

def plot_concordance(results_df: pd.DataFrame):
    """
    For each condition × model: does the model's bias direction
    match the documented clinical bias direction?
    """
    ensure_output_dir()
    
    results_df = results_df.copy()
    results_df["condition_label"] = results_df["condition"].map(CONDITION_LABELS)
    
    pivot = results_df.pivot_table(
        values="concordance_with_known_bias",
        index="condition_label",
        columns="model",
        aggfunc="first"
    )
    
    fig, ax = plt.subplots(figsize=(8, 5))
    
    # Create custom colormap: green = no concordance (good), red = concordance (reproduces bias)
    cmap = plt.cm.colors.ListedColormap([COLORS["no_bias"], COLORS["bias_red"]])
    
    # For control condition, flip interpretation
    im = ax.imshow(pivot.values.astype(float), cmap=cmap, aspect="auto", vmin=0, vmax=1)
    
    ax.set_xticks(np.arange(len(pivot.columns)))
    ax.set_xticklabels(pivot.columns, fontsize=10)
    ax.set_yticks(np.arange(len(pivot.index)))
    ax.set_yticklabels(pivot.index, fontsize=10)
    
    # Add text annotations
    for i in range(len(pivot.index)):
        for j in range(len(pivot.columns)):
            val = pivot.values[i, j]
            condition = results_df[
                results_df["condition_label"] == pivot.index[i]
            ]["condition"].iloc[0]
            
            if condition == "acute_mi_classic":
                text = "✓ No diff" if val else "⚠ Unexpected"
            else:
                text = "⚠ Reproduces\nbias" if val else "✓ No bias\ndetected"
            
            text_color = "white" if val else "white"
            ax.text(j, i, text, ha="center", va="center",
                    fontsize=9, fontweight="bold", color=text_color)
    
    ax.set_title("Does the Model Reproduce Known Clinical Bias Patterns?",
                 fontweight="bold", pad=15)
    
    # Legend
    patches = [
        mpatches.Patch(color=COLORS["bias_red"], label="Reproduces known bias"),
        mpatches.Patch(color=COLORS["no_bias"], label="No bias detected / Expected (control)"),
    ]
    ax.legend(handles=patches, loc="upper center", bbox_to_anchor=(0.5, -0.08),
              ncol=2, fontsize=9)
    
    plt.tight_layout()
    path = os.path.join(FIGURES_DIR, "concordance_chart.png")
    fig.savefig(path)
    plt.close()
    print(f"Saved: {path}")


# ─────────────────────────────────────────────────────────────
# Figure 5: Bias indicator frequency
# ─────────────────────────────────────────────────────────────

def plot_bias_indicators(parsed_df: pd.DataFrame):
    """
    Mean count of bias indicator terms by sex, per condition.
    """
    ensure_output_dir()
    
    parsed_df = parsed_df.copy()
    parsed_df["condition_label"] = parsed_df["condition"].map(CONDITION_LABELS)
    
    # Exclude control condition (no bias indicators)
    plot_data = parsed_df[parsed_df["condition"] != "acute_mi_classic"]
    
    fig, ax = plt.subplots(figsize=(10, 5))
    
    conditions = sorted(plot_data["condition"].unique())
    x = np.arange(len(conditions))
    width = 0.25
    
    for i, (sex, color) in enumerate([
        ("female", COLORS["female"]),
        ("male", COLORS["male"]),
        ("unspecified", COLORS["unspecified"]),
    ]):
        sex_data = plot_data[plot_data["patient_sex"] == sex]
        means = []
        cis = []
        
        for condition in conditions:
            cond_data = sex_data[sex_data["condition"] == condition]["bias_indicator_count"]
            if len(cond_data) > 0:
                means.append(cond_data.mean())
                cis.append(1.96 * cond_data.std() / np.sqrt(len(cond_data)))
            else:
                means.append(0)
                cis.append(0)
        
        ax.bar(
            x + (i - 1) * width,
            means,
            width,
            yerr=cis,
            color=color,
            alpha=0.85,
            label=sex.capitalize(),
            capsize=3,
        )
    
    condition_labels = [CONDITION_LABELS.get(c, c) for c in conditions]
    ax.set_xticks(x)
    ax.set_xticklabels(condition_labels, fontsize=10)
    ax.set_ylabel("Mean Bias Indicator Count")
    ax.set_title("Frequency of Bias-Indicator Language by Patient Sex",
                 fontweight="bold", pad=15)
    ax.legend()
    ax.set_facecolor(COLORS["bg"])
    
    plt.tight_layout()
    path = os.path.join(FIGURES_DIR, "bias_indicator_frequency.png")
    fig.savefig(path)
    plt.close()
    print(f"Saved: {path}")


# ─────────────────────────────────────────────────────────────
# Generate all figures
# ─────────────────────────────────────────────────────────────

def generate_all_figures(
    analysis_path: str = "outputs/tables/analysis_results.csv",
    parsed_path: str = "data/results/parsed_results.csv"
):
    """Generate all figures from analysis results."""
    
    print("Generating figures...")
    print("=" * 40)
    
    results_df = load_analysis_results(analysis_path)
    parsed_df = load_parsed_results(parsed_path)
    
    plot_heatmap(results_df)
    plot_urgency_bars(parsed_df)
    plot_forest(results_df)
    plot_concordance(results_df)
    plot_bias_indicators(parsed_df)
    
    print("\n" + "=" * 40)
    print(f"All figures saved to {FIGURES_DIR}/")


if __name__ == "__main__":
    generate_all_figures()
