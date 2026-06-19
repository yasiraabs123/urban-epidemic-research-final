"""
Stochastic Block Model (SBM) network generation with Fermi-Dirac distance kernel.

Three urban regimes are obtained by varying the spatial-mixing parameter mu:
    mu = 5   -> Sparse        (suburban / regional)
    mu = 10  -> Polycentric   (multi-centre metropolitan)
    mu = 15  -> Dense         (high-mixing megacity)

Blocks:
    Social      435 nodes  (high intra-block contact)
    Hub          75 nodes  (high inter-block connectivity)
    Non-social  490 nodes  (low contact)
"""

from __future__ import annotations

from dataclasses import dataclass

import networkx as nx
import numpy as np


BLOCKS = {"social": 435, "hub": 75, "non_social": 490}

INTRA_INTER = {
    ("social", "social"):         0.040,
    ("social", "hub"):            0.030,
    ("social", "non_social"):     0.005,
    ("hub", "hub"):               0.120,
    ("hub", "non_social"):        0.025,
    ("non_social", "non_social"): 0.003,
}


@dataclass
class NetworkSpec:
    name: str
    mu: float
    n_nodes: int = 1000


def _block_assignment(n_nodes: int, rng: np.random.Generator) -> list[str]:
    labels = []
    for block, size in BLOCKS.items():
        labels.extend([block] * size)
    if len(labels) < n_nodes:
        labels.extend(["non_social"] * (n_nodes - len(labels)))
    labels = labels[:n_nodes]
    rng.shuffle(labels)
    return labels


def _block_prob(b_i: str, b_j: str) -> float:
    key = (b_i, b_j) if (b_i, b_j) in INTRA_INTER else (b_j, b_i)
    return INTRA_INTER[key]


def _fermi_dirac(distance: float, mu: float, temperature: float = 1.5) -> float:
    return 1.0 / (1.0 + np.exp((distance - mu) / temperature))


def build_sbm_network(mu: float,
                      n_nodes: int = 1000,
                      seed: int | None = None) -> nx.Graph:
    """Generate an undirected SBM contact network with a spatial Fermi-Dirac kernel.

    Parameters
    ----------
    mu : float
        Spatial-mixing parameter (5 = Sparse, 10 = Polycentric, 15 = Dense).
    n_nodes : int
        Number of nodes in the network.
    seed : int, optional
        Random seed for reproducibility.
    """
    rng = np.random.default_rng(seed)

    positions = rng.uniform(0, 20, size=(n_nodes, 2))
    blocks = _block_assignment(n_nodes, rng)

    G = nx.Graph()
    for i in range(n_nodes):
        G.add_node(i, block=blocks[i], pos=tuple(positions[i]))

    for i in range(n_nodes):
        for j in range(i + 1, n_nodes):
            p_block = _block_prob(blocks[i], blocks[j])
            d_ij = float(np.linalg.norm(positions[i] - positions[j]))
            p_edge = p_block * _fermi_dirac(d_ij, mu)
            if rng.random() < p_edge:
                G.add_edge(i, j)

    return G


def network_summary(G: nx.Graph) -> dict:
    degrees = [d for _, d in G.degree()]
    return {
        "n_nodes":      G.number_of_nodes(),
        "n_edges":      G.number_of_edges(),
        "avg_degree":   float(np.mean(degrees)),
        "max_degree":   int(np.max(degrees)),
        "clustering":   float(nx.average_clustering(G)),
        "n_components": nx.number_connected_components(G),
    }


REGIMES = [
    NetworkSpec(name="Sparse",      mu=5,  n_nodes=1000),
    NetworkSpec(name="Polycentric", mu=10, n_nodes=1000),
    NetworkSpec(name="Dense",       mu=15, n_nodes=1000),
]
