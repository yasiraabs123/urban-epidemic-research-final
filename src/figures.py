"""
Publication figure generation from saved simulation results.

Reads CSV files from `results/data/` (produced by experiments.py) and
writes PNG figures to `figures/`.

Run from the repository root after running experiments.py:

    python -m src.figures
"""

from __future__ import annotations

import csv
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np

NAVY  = "#1F3A5F"
BLUE  = "#2E5C8A"
RED   = "#C0392B"
GREEN = "#27AE60"
GREY  = "#7F8C8D"

mpl.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 11,
    "axes.titlesize": 13,
    "axes.titleweight": "bold",
    "axes.titlecolor": NAVY,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "savefig.dpi": 200,
    "savefig.bbox": "tight",
    "savefig.facecolor": "white",
})


def _project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _data_dir() -> Path:
    return _project_root() / "results" / "data"


def _figures_dir() -> Path:
    out = _project_root() / "figures"
    out.mkdir(parents=True, exist_ok=True)
    return out


def load_curves(csv_path: Path) -> np.ndarray:
    """Load infection-count curves; return shape (n_days, n_runs)."""
    rows = []
    with csv_path.open() as f:
        reader = csv.reader(f)
        next(reader)
        for row in reader:
            rows.append([int(x) for x in row[1:]])
    return np.array(rows)


def load_summary(csv_path: Path) -> list[dict]:
    with csv_path.open() as f:
        reader = csv.DictReader(f)
        return list(reader)


def _mean_prevalence(curves: np.ndarray, n_nodes: int = 1000) -> np.ndarray:
    return curves.mean(axis=1) / n_nodes


def figure_static_vs_dynamic(data_dir: Path, out_path: Path) -> None:
    networks = ["sparse", "polycentric", "dense"]
    fig, axes = plt.subplots(1, 3, figsize=(14, 4.5), sharey=True)
    for ax, name in zip(axes, networks):
        static = load_curves(data_dir / f"curves_{name}_static.csv")
        dynamic = load_curves(data_dir / f"curves_{name}_dynamic.csv")
        ax.plot(_mean_prevalence(static) * 100, color=NAVY,
                linewidth=2, label="Static")
        ax.plot(_mean_prevalence(dynamic) * 100, color=RED,
                linewidth=2, linestyle="--", label="Dynamic")
        ax.set_title(name.capitalize())
        ax.set_xlabel("Day")
        ax.set_ylabel("Infectious (%)")
        ax.grid(alpha=0.3)
        ax.legend(loc="upper right")
    fig.suptitle("Static vs Dynamic SEIR across Urban Topologies",
                 fontsize=14, color=NAVY, fontweight="bold")
    fig.tight_layout()
    fig.savefig(out_path)
    plt.close(fig)


def figure_summary_metrics(data_dir: Path, out_path: Path) -> None:
    rows = load_summary(data_dir / "summary.csv")
    networks = ["Sparse", "Polycentric", "Dense"]
    metrics = ("peak_day", "peak_height", "attack_rate")

    summary = {n: {"static": {}, "dynamic": {}} for n in networks}
    for r in rows:
        net = r["network"]
        reg = r["regime"]
        for m in metrics:
            summary[net][reg].setdefault(m, []).append(float(r[m]))

    means = {n: {reg: {m: np.mean(summary[n][reg][m]) for m in metrics}
                 for reg in ("static", "dynamic")} for n in networks}

    fig, axes = plt.subplots(1, 3, figsize=(15, 4.5))
    titles = ["Peak Day", "Peak Height (fraction)", "Attack Rate (fraction)"]
    for ax, m, title in zip(axes, metrics, titles):
        x = np.arange(len(networks))
        static_vals  = [means[n]["static"][m] for n in networks]
        dynamic_vals = [means[n]["dynamic"][m] for n in networks]
        ax.bar(x - 0.18, static_vals,  width=0.36, color=NAVY,
               label="Static")
        ax.bar(x + 0.18, dynamic_vals, width=0.36, color=RED,
               label="Dynamic")
        ax.set_xticks(x)
        ax.set_xticklabels(networks)
        ax.set_title(title)
        ax.grid(alpha=0.3, axis="y")
        ax.legend()
    fig.suptitle("Static vs Dynamic SEIR Summary Metrics",
                 fontsize=14, color=NAVY, fontweight="bold")
    fig.tight_layout()
    fig.savefig(out_path)
    plt.close(fig)


def figure_network_stats(data_dir: Path, out_path: Path) -> None:
    rows = []
    with (data_dir / "network_stats.csv").open() as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    names      = [r["network"] for r in rows]
    avg_degree = [float(r["avg_degree"]) for r in rows]
    clustering = [float(r["clustering"]) for r in rows]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.5))
    ax1.bar(names, avg_degree, color=NAVY)
    ax1.set_title("Average Degree by Network Topology")
    ax1.set_ylabel("Average Degree")
    ax1.grid(alpha=0.3, axis="y")

    ax2.bar(names, clustering, color=BLUE)
    ax2.set_title("Clustering Coefficient by Topology")
    ax2.set_ylabel("Clustering Coefficient")
    ax2.set_ylim(0, 1)
    ax2.grid(alpha=0.3, axis="y")

    fig.suptitle("SBM Network Structural Properties",
                 fontsize=14, color=NAVY, fontweight="bold")
    fig.tight_layout()
    fig.savefig(out_path)
    plt.close(fig)


def figure_validation(data_dir: Path, project_root: Path, out_path: Path) -> None:
    real_csv = project_root / "data" / "st_petersburg_winter2022.csv"
    if not real_csv.exists():
        print(f"[warn] {real_csv} not found, skipping validation figure.")
        return
    real_days, real_values = [], []
    with real_csv.open() as f:
        reader = csv.DictReader(f)
        for row in reader:
            real_days.append(int(row["day"]))
            real_values.append(float(row["normalised_cases"]))
    real_days = np.array(real_days)
    real_values = np.array(real_values)

    dynamic = load_curves(data_dir / "curves_dense_dynamic.csv")
    pred = _mean_prevalence(dynamic)
    pred_norm = pred / pred.max() if pred.max() > 0 else pred
    common_days = np.arange(min(len(pred_norm), len(real_values)))

    fig, axes = plt.subplots(1, 2, figsize=(13, 4.5))
    axes[0].plot(real_days[common_days], real_values[common_days], color="black",
                 linewidth=2, label="St. Petersburg (real)")
    axes[0].plot(common_days, pred_norm[common_days], color=BLUE,
                 linestyle="--", linewidth=2, label="Dynamic model")
    axes[0].set_title("Validation: Predicted vs Real Outbreak Curve")
    axes[0].set_xlabel("Day")
    axes[0].set_ylabel("Normalised cases")
    axes[0].legend()
    axes[0].grid(alpha=0.3)

    n = len(common_days)
    obs = real_values[:n]
    pred_arr = pred_norm[:n]
    axes[1].scatter(obs, pred_arr, color=NAVY, alpha=0.6)
    axes[1].plot([0, 1], [0, 1], color=GREY, linestyle=":", label="y = x")
    ss_res = float(np.sum((obs - pred_arr) ** 2))
    ss_tot = float(np.sum((obs - np.mean(obs)) ** 2)) or 1e-12
    r2 = 1.0 - ss_res / ss_tot
    axes[1].set_title(f"Predicted vs Observed  (R² = {r2:.3f})")
    axes[1].set_xlabel("Observed (normalised)")
    axes[1].set_ylabel("Predicted (normalised)")
    axes[1].legend()
    axes[1].grid(alpha=0.3)

    fig.suptitle("Model Validation Against St. Petersburg Data (Winter 2022)",
                 fontsize=14, color=NAVY, fontweight="bold")
    fig.tight_layout()
    fig.savefig(out_path)
    plt.close(fig)


def figure_behavior(data_dir: Path, out_path: Path) -> None:
    curves_path = data_dir / "behavior_curves.csv"
    summary_path = data_dir / "behavior_scenarios.csv"
    if not curves_path.exists():
        print(f"[warn] {curves_path} not found, skipping behavior figure.")
        return

    with curves_path.open() as f:
        reader = csv.reader(f)
        header = next(reader)
        scenarios = sorted({h.split("_")[0] for h in header[1:]})
        cols_by_scenario = {s: [i for i, h in enumerate(header[1:])
                                if h.startswith(s + "_")] for s in scenarios}
        rows = [[int(x) for x in row[1:]] for row in reader]
    data = np.array(rows)

    scenario_order = ["none", "mild", "moderate", "strong"]
    colors = {"none": GREY, "mild": NAVY, "moderate": BLUE, "strong": GREEN}
    labels = {"none": "No intervention (0%)", "mild": "Mild (30%)",
              "moderate": "Moderate (50%)", "strong": "Strong (70%)"}

    fig, ax = plt.subplots(figsize=(10, 5.5))
    for s in scenario_order:
        if s not in cols_by_scenario:
            continue
        mean_curve = data[:, cols_by_scenario[s]].mean(axis=1) / 10
        ax.plot(mean_curve, color=colors[s], linewidth=2, label=labels[s])
    ax.set_title("Behavioral Scenario Analysis — Dense Network",
                 fontsize=14, color=NAVY, fontweight="bold")
    ax.set_xlabel("Day")
    ax.set_ylabel("Infectious (%)")
    ax.legend()
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(out_path)
    plt.close(fig)


def figure_timing(data_dir: Path, out_path: Path) -> None:
    csv_path = data_dir / "timing_scenarios.csv"
    if not csv_path.exists():
        print(f"[warn] {csv_path} not found, skipping timing figure.")
        return

    rows = []
    with csv_path.open() as f:
        reader = csv.DictReader(f)
        for r in reader:
            rows.append({
                "network": r["network"],
                "start_day": int(r["start_day"]),
                "peak_height": float(r["peak_height"]),
            })

    networks = ["Sparse", "Polycentric", "Dense"]
    colors = {"Sparse": GREEN, "Polycentric": BLUE, "Dense": RED}

    baseline_peak = {n: 0 for n in networks}
    by_network = {n: {} for n in networks}
    for r in rows:
        by_network[r["network"]].setdefault(r["start_day"], []).append(r["peak_height"])
    for n in networks:
        days = sorted(by_network[n].keys())
        peaks = [np.mean(by_network[n][d]) for d in days]
        if days:
            baseline_peak[n] = max(peaks)

    fig, ax = plt.subplots(figsize=(10, 5.5))
    for n in networks:
        days = sorted(by_network[n].keys())
        peaks = [np.mean(by_network[n][d]) for d in days]
        reductions = [100 * (baseline_peak[n] - p) / baseline_peak[n]
                      if baseline_peak[n] > 0 else 0 for p in peaks]
        ax.plot(days, reductions, color=colors[n], linewidth=2,
                marker="o", label=n)
    ax.set_title("Optimal Intervention Timing by Topology",
                 fontsize=14, color=NAVY, fontweight="bold")
    ax.set_xlabel("Intervention Start Day")
    ax.set_ylabel("Peak Reduction (%)")
    ax.legend()
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(out_path)
    plt.close(fig)


def make_all() -> None:
    root = _project_root()
    data = _data_dir()
    figs = _figures_dir()

    if not (data / "summary.csv").exists():
        raise FileNotFoundError(
            f"No simulation results found in {data}.\n"
            f"Run `python -m src.experiments` first."
        )

    figure_network_stats(data,     figs / "fig1_networks.png")
    figure_static_vs_dynamic(data, figs / "fig2_static_vs_dynamic.png")
    figure_behavior(data,          figs / "fig3_behavior.png")
    figure_timing(data,            figs / "fig4_timing.png")
    figure_validation(data, root,  figs / "fig5_validation.png")
    figure_summary_metrics(data,   figs / "fig_stats_summary.png")
    print(f"[done] Figures written to {figs}")


if __name__ == "__main__":
    make_all()
