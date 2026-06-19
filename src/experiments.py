"""
Experiment driver.

Builds the three SBM networks, runs N stochastic SEIR simulations per network
under both static and dynamic regimes, and persists the results as CSV files
in `results/data/` for downstream analysis and figure generation.

Run from the repository root:

    python -m src.experiments --runs 30 --seed 42
"""

from __future__ import annotations

import argparse
import csv
import os
from pathlib import Path

import numpy as np

from .network import REGIMES, build_sbm_network, network_summary
from .seir import SEIRParameters, simulate


def _project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _output_dir() -> Path:
    out = _project_root() / "results" / "data"
    out.mkdir(parents=True, exist_ok=True)
    return out


def save_curves(results: list, csv_path: Path) -> None:
    n_days = len(results[0].I)
    with csv_path.open("w", newline="") as f:
        writer = csv.writer(f)
        header = ["day"] + [f"run_{r.seed}_I" for r in results]
        writer.writerow(header)
        for day in range(n_days):
            row = [day] + [int(r.I[day]) for r in results]
            writer.writerow(row)


def save_summary(results: list, csv_path: Path) -> None:
    with csv_path.open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["network", "regime", "seed", "peak_day",
                         "peak_height", "attack_rate"])
        for r in results:
            writer.writerow([
                r.network_name,
                "dynamic" if r.dynamic else "static",
                r.seed,
                r.peak_day,
                round(r.peak_height, 6),
                round(r.attack_rate, 6),
            ])


def save_network_stats(networks: dict, csv_path: Path) -> None:
    with csv_path.open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["network", "mu", "n_nodes", "n_edges",
                         "avg_degree", "clustering"])
        for spec, G in networks.items():
            stats = network_summary(G)
            writer.writerow([
                spec.name, spec.mu,
                stats["n_nodes"], stats["n_edges"],
                round(stats["avg_degree"], 3),
                round(stats["clustering"], 3),
            ])


BEHAVIOR_SCENARIOS = [
    ("none",     0.0),
    ("mild",     0.30),
    ("moderate", 0.50),
    ("strong",   0.70),
]

TIMING_DAYS = [10, 18, 28, 35, 42, 50, 60]


def run_baseline(networks: dict, n_runs: int, base_seed: int,
                 params: SEIRParameters, out: Path) -> None:
    all_results = []
    for spec, G in networks.items():
        for regime_name, dynamic in [("dynamic", True), ("static", False)]:
            print(f"[sim] {spec.name}  regime={regime_name}  runs={n_runs}")
            results = []
            for i in range(n_runs):
                r = simulate(G, params,
                             dynamic=dynamic,
                             network_name=spec.name,
                             seed=base_seed + i)
                results.append(r)
            curves_path = out / f"curves_{spec.name.lower()}_{regime_name}.csv"
            save_curves(results, curves_path)
            all_results.extend(results)
    save_summary(all_results, out / "summary.csv")


def run_behavior_scenarios(network_spec, G, n_runs: int, base_seed: int,
                           params: SEIRParameters, out: Path) -> None:
    print(f"[behavior] Sweeping contact reductions on {network_spec.name}")
    rows = []
    for scenario_name, reduction in BEHAVIOR_SCENARIOS:
        for i in range(n_runs):
            r = simulate(G, params,
                         dynamic=True,
                         network_name=network_spec.name,
                         seed=base_seed + i,
                         intervention_reduction=reduction)
            rows.append({
                "scenario": scenario_name,
                "reduction": reduction,
                "seed": r.seed,
                "peak_day": r.peak_day,
                "peak_height": r.peak_height,
                "attack_rate": r.attack_rate,
                "I": r.I,
            })

    csv_path = out / "behavior_scenarios.csv"
    with csv_path.open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["scenario", "reduction", "seed",
                         "peak_day", "peak_height", "attack_rate"])
        for r in rows:
            writer.writerow([r["scenario"], r["reduction"], r["seed"],
                             r["peak_day"],
                             round(r["peak_height"], 6),
                             round(r["attack_rate"], 6)])

    n_days = len(rows[0]["I"])
    curves_path = out / "behavior_curves.csv"
    with curves_path.open("w", newline="") as f:
        writer = csv.writer(f)
        header = ["day"] + [f"{r['scenario']}_{r['seed']}" for r in rows]
        writer.writerow(header)
        for d in range(n_days):
            writer.writerow([d] + [int(r["I"][d]) for r in rows])


def run_timing_scenarios(networks: dict, n_runs: int, base_seed: int,
                         params: SEIRParameters, out: Path) -> None:
    print(f"[timing] Sweeping intervention start day across topologies")
    rows = []
    for spec, G in networks.items():
        for start_day in TIMING_DAYS:
            for i in range(n_runs):
                r = simulate(G, params,
                             dynamic=True,
                             network_name=spec.name,
                             seed=base_seed + i,
                             intervention_reduction=0.50,
                             intervention_start_day=start_day)
                rows.append({
                    "network":   spec.name,
                    "start_day": start_day,
                    "seed":      r.seed,
                    "peak_day":  r.peak_day,
                    "peak_height": r.peak_height,
                    "attack_rate": r.attack_rate,
                })

    csv_path = out / "timing_scenarios.csv"
    with csv_path.open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["network", "start_day", "seed",
                         "peak_day", "peak_height", "attack_rate"])
        for r in rows:
            writer.writerow([r["network"], r["start_day"], r["seed"],
                             r["peak_day"],
                             round(r["peak_height"], 6),
                             round(r["attack_rate"], 6)])


def run_all(n_runs: int = 30, base_seed: int = 42,
            include_scenarios: bool = True) -> None:
    out = _output_dir()
    params = SEIRParameters()

    networks = {}
    for spec in REGIMES:
        print(f"[network] Building {spec.name} (mu={spec.mu}) ...")
        networks[spec] = build_sbm_network(spec.mu, spec.n_nodes,
                                           seed=base_seed)

    save_network_stats(networks, out / "network_stats.csv")
    run_baseline(networks, n_runs, base_seed, params, out)

    if include_scenarios:
        dense_spec = next(s for s in networks if s.name == "Dense")
        run_behavior_scenarios(dense_spec, networks[dense_spec],
                               n_runs, base_seed, params, out)
        run_timing_scenarios(networks, n_runs, base_seed, params, out)

    print(f"[done] Results written to {out}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the full experiment suite.")
    parser.add_argument("--runs", type=int, default=30,
                        help="Number of stochastic runs per network and regime.")
    parser.add_argument("--seed", type=int, default=42,
                        help="Base random seed.")
    parser.add_argument("--no-scenarios", action="store_true",
                        help="Skip behavior and timing scenario sweeps.")
    args = parser.parse_args()
    run_all(n_runs=args.runs, base_seed=args.seed,
            include_scenarios=not args.no_scenarios)


if __name__ == "__main__":
    main()
