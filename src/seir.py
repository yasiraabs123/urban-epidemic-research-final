"""
Discrete-time SEIR simulation on a contact network.

Supports two regimes:
    static  : fixed contact rate throughout the outbreak.
    dynamic : weekly contact rhythm (weekend = 0.6 x weekday) plus
              prevalence-threshold behavioural adaptation.

Disease parameters default to COVID-19 wild-type values (Li et al., NEJM 2020).
"""

from __future__ import annotations

from dataclasses import dataclass, field

import networkx as nx
import numpy as np


@dataclass
class SEIRParameters:
    beta: float = 0.28          # transmission rate per contact per day
    sigma: float = 1.0 / 5.2    # incubation rate (1/days)
    gamma: float = 1.0 / 7.0    # recovery rate (1/days)
    initial_infected: int = 50  # I0
    horizon_days: int = 120     # T


WEEKLY_MULTIPLIERS = {
    "weekday": 1.0,
    "weekend": 0.6,
}


def weekly_multiplier(day: int) -> float:
    is_weekend = (day % 7) >= 5
    return WEEKLY_MULTIPLIERS["weekend"] if is_weekend else WEEKLY_MULTIPLIERS["weekday"]


def behavioural_multiplier(prevalence: float) -> float:
    if prevalence < 0.01:
        return 1.0
    if prevalence < 0.05:
        return 0.7
    if prevalence < 0.10:
        return 0.5
    return 0.3


SUSCEPTIBLE, EXPOSED, INFECTIOUS, RECOVERED = 0, 1, 2, 3


@dataclass
class SimulationResult:
    S: np.ndarray
    E: np.ndarray
    I: np.ndarray
    R: np.ndarray
    peak_day: int
    peak_height: float
    attack_rate: float
    network_name: str
    dynamic: bool
    seed: int


def simulate(graph: nx.Graph,
             params: SEIRParameters | None = None,
             dynamic: bool = True,
             network_name: str = "",
             seed: int | None = None,
             intervention_reduction: float | None = None,
             intervention_start_day: int = 0) -> SimulationResult:
    """Run one stochastic SEIR simulation on the given contact network.

    Parameters
    ----------
    graph : networkx.Graph
        Contact network. Nodes are integers 0..N-1.
    params : SEIRParameters, optional
        Disease parameters.
    dynamic : bool
        If True, apply weekly rhythm and behavioural adaptation multipliers.
    network_name : str
        Tag stored on the result for downstream reporting.
    seed : int, optional
        Random seed.
    intervention_reduction : float, optional
        If set, replaces threshold-based behavioural adaptation with a fixed
        contact-reduction fraction (0.30 = 30%% reduction). Use for scenario
        analysis (Mild / Moderate / Strong).
    intervention_start_day : int
        Day on which the intervention activates. Before this day no
        behavioural reduction is applied (only weekly rhythm if dynamic).
    """
    if params is None:
        params = SEIRParameters()

    rng = np.random.default_rng(seed)
    n_nodes = graph.number_of_nodes()
    T = params.horizon_days

    states = np.zeros(n_nodes, dtype=np.int8)
    initial = rng.choice(n_nodes, size=params.initial_infected, replace=False)
    states[initial] = INFECTIOUS

    adjacency = [list(graph.neighbors(i)) for i in range(n_nodes)]

    S_t = np.zeros(T, dtype=np.int32)
    E_t = np.zeros(T, dtype=np.int32)
    I_t = np.zeros(T, dtype=np.int32)
    R_t = np.zeros(T, dtype=np.int32)

    for t in range(T):
        prevalence = float(np.mean(states == INFECTIOUS))
        intervention_active = t >= intervention_start_day
        if dynamic:
            w_t = weekly_multiplier(t)
            if intervention_reduction is not None and intervention_active:
                a_t = 1.0 - intervention_reduction
            elif intervention_reduction is not None:
                a_t = 1.0
            else:
                a_t = behavioural_multiplier(prevalence) if intervention_active else 1.0
            c_t = w_t * a_t
        else:
            c_t = 1.0

        new_states = states.copy()

        susceptible_idx = np.where(states == SUSCEPTIBLE)[0]
        for i in susceptible_idx:
            n_infectious_neighbors = sum(1 for j in adjacency[i] if states[j] == INFECTIOUS)
            if n_infectious_neighbors == 0:
                continue
            p_infection = 1.0 - (1.0 - params.beta * c_t) ** n_infectious_neighbors
            if rng.random() < p_infection:
                new_states[i] = EXPOSED

        exposed_idx = np.where(states == EXPOSED)[0]
        progress_mask = rng.random(len(exposed_idx)) < params.sigma
        new_states[exposed_idx[progress_mask]] = INFECTIOUS

        infectious_idx = np.where(states == INFECTIOUS)[0]
        recover_mask = rng.random(len(infectious_idx)) < params.gamma
        new_states[infectious_idx[recover_mask]] = RECOVERED

        states = new_states

        S_t[t] = int(np.sum(states == SUSCEPTIBLE))
        E_t[t] = int(np.sum(states == EXPOSED))
        I_t[t] = int(np.sum(states == INFECTIOUS))
        R_t[t] = int(np.sum(states == RECOVERED))

    peak_day = int(np.argmax(I_t))
    peak_height = float(I_t[peak_day] / n_nodes)
    attack_rate = float(R_t[-1] / n_nodes)

    return SimulationResult(
        S=S_t, E=E_t, I=I_t, R=R_t,
        peak_day=peak_day,
        peak_height=peak_height,
        attack_rate=attack_rate,
        network_name=network_name,
        dynamic=dynamic,
        seed=seed or 0,
    )
