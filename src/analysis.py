"""
Statistical analysis utilities.

Implements the metrics reported in the preprint:
    - Paired t-test
    - Cohen's d effect size
    - One-way ANOVA
    - Goodness-of-fit: R^2, RMSE, MAE, Pearson r

Run from the repository root after `src.experiments`:

    python -m src.analysis
"""

from __future__ import annotations

import csv
from pathlib import Path

import numpy as np
from scipy import stats


def _project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _data_dir() -> Path:
    return _project_root() / "results" / "data"


def cohens_d(x: np.ndarray, y: np.ndarray) -> float:
    nx, ny = len(x), len(y)
    pooled = np.sqrt(((nx - 1) * x.var(ddof=1) + (ny - 1) * y.var(ddof=1))
                     / (nx + ny - 2))
    return float((x.mean() - y.mean()) / pooled) if pooled > 0 else 0.0


def paired_t_test(x: np.ndarray, y: np.ndarray) -> tuple[float, float]:
    t, p = stats.ttest_rel(x, y)
    return float(t), float(p)


def anova_one_way(*groups: np.ndarray) -> tuple[float, float]:
    f, p = stats.f_oneway(*groups)
    return float(f), float(p)


def fit_metrics(observed: np.ndarray, predicted: np.ndarray) -> dict:
    obs = np.asarray(observed, dtype=float)
    pred = np.asarray(predicted, dtype=float)
    n = min(len(obs), len(pred))
    obs, pred = obs[:n], pred[:n]

    ss_res = float(np.sum((obs - pred) ** 2))
    ss_tot = float(np.sum((obs - obs.mean()) ** 2)) or 1e-12
    r2 = 1.0 - ss_res / ss_tot
    rmse = float(np.sqrt(np.mean((obs - pred) ** 2)))
    mae = float(np.mean(np.abs(obs - pred)))
    pearson_r = float(np.corrcoef(obs, pred)[0, 1]) if obs.std() > 0 else 0.0

    return {"r2": r2, "rmse": rmse, "mae": mae, "pearson_r": pearson_r}


def load_summary(csv_path: Path) -> dict:
    rows = []
    with csv_path.open() as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    out = {}
    for r in rows:
        net = r["network"]
        reg = r["regime"]
        out.setdefault(net, {}).setdefault(reg, []).append({
            "peak_day": float(r["peak_day"]),
            "peak_height": float(r["peak_height"]),
            "attack_rate": float(r["attack_rate"]),
        })
    return out


def static_vs_dynamic_report(summary: dict) -> None:
    print("\n=== Static vs Dynamic SEIR ===")
    networks = ["Sparse", "Polycentric", "Dense"]
    static_peaks, dynamic_peaks = [], []
    static_ars, dynamic_ars = [], []

    for net in networks:
        s_peak = np.array([r["peak_day"] for r in summary[net]["static"]])
        d_peak = np.array([r["peak_day"] for r in summary[net]["dynamic"]])
        s_ar   = np.array([r["attack_rate"] for r in summary[net]["static"]])
        d_ar   = np.array([r["attack_rate"] for r in summary[net]["dynamic"]])

        static_peaks.append(s_peak.mean())
        dynamic_peaks.append(d_peak.mean())
        static_ars.append(s_ar.mean())
        dynamic_ars.append(d_ar.mean())

        print(f"\n[{net}]")
        print(f"  peak day      static={s_peak.mean():.1f}  "
              f"dynamic={d_peak.mean():.1f}  shift=+{d_peak.mean()-s_peak.mean():.1f}d")
        print(f"  attack rate   static={s_ar.mean():.3f}  "
              f"dynamic={d_ar.mean():.3f}  reduction={(s_ar.mean()-d_ar.mean())*100:.1f}pp")

    static_peaks = np.array(static_peaks)
    dynamic_peaks = np.array(dynamic_peaks)
    t, p = paired_t_test(static_peaks, dynamic_peaks)
    d = cohens_d(dynamic_peaks, static_peaks)
    print(f"\nPaired t-test (peak day, city-level means)")
    print(f"  t = {t:.3f}   p = {p:.4f}   Cohen's d = {d:.3f}")


def validation_report() -> None:
    print("\n=== Model Validation vs St. Petersburg ===")
    real_csv = _project_root() / "data" / "st_petersburg_winter2022.csv"
    if not real_csv.exists():
        print(f"  [warn] {real_csv} not found, skipping.")
        return

    real = []
    with real_csv.open() as f:
        reader = csv.DictReader(f)
        for r in reader:
            real.append(float(r["normalised_cases"]))
    real = np.array(real)

    dense_csv = _data_dir() / "curves_dense_dynamic.csv"
    if not dense_csv.exists():
        print(f"  [warn] {dense_csv} not found.")
        return
    with dense_csv.open() as f:
        reader = csv.reader(f)
        next(reader)
        pred = np.array([np.mean([int(x) for x in row[1:]])
                         for row in reader])
    pred_norm = pred / pred.max() if pred.max() > 0 else pred

    metrics = fit_metrics(real, pred_norm)
    print(f"  R^2       = {metrics['r2']:.3f}")
    print(f"  RMSE      = {metrics['rmse']:.3f}")
    print(f"  MAE       = {metrics['mae']:.3f}")
    print(f"  Pearson r = {metrics['pearson_r']:.3f}")


def main() -> None:
    summary = load_summary(_data_dir() / "summary.csv")
    static_vs_dynamic_report(summary)
    validation_report()


if __name__ == "__main__":
    main()
