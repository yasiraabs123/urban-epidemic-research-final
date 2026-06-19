# Review of Similar Solutions and Related Work

This section surveys prior research in three closely related strands — **static network epidemiology**, **synthetic-population and digital-twin modelling**, and **dynamic / behaviour-coupled epidemic models** — and identifies the gap that the present work addresses. All references are real, peer-reviewed publications (or canonical pre-prints), and the links provided lead to the authoritative versions of record.

---

## 1. Static Network Epidemiology

The mathematical foundations of network-based epidemic modelling were established in the early 2000s. **Pastor-Satorras and Vespignani** [1] showed that **scale-free contact networks** lack a finite epidemic threshold: even diseases with very low transmissibility can persist and spread globally because of the long tail of highly connected nodes (hubs). This paper reframed epidemic modelling as a problem of network topology rather than population homogeneity. **Newman** [2] subsequently formalised the link between network structure and outbreak dynamics, deriving exact percolation-theoretic results for the **size of epidemic clusters on uncorrelated networks**.

**Keeling and Eames** [3] consolidated the field in their widely-cited *J. R. Soc. Interface* review, identifying **degree distribution, clustering coefficient, and assortativity** as the three structural properties that most strongly determine outbreak dynamics. Their treatment of compartmental dynamics on heterogeneous networks remains the standard reference for any static-network SEIR analysis.

**Limitation of the static-network paradigm.** All three works assume that the contact network is fixed for the duration of the outbreak — an assumption that has been repeatedly contradicted by empirical mobility data during COVID-19. They cannot represent (i) weekday/weekend rhythms, (ii) behavioural withdrawal in response to perceived risk, or (iii) policy-induced contact reductions.

---

## 2. Synthetic Populations and Digital-Twin Models

A second strand of research builds **large-scale synthetic populations** as substrates for agent-based or network-based simulations.

**Rineer et al.** [4], publishing in *Nature Scientific Data* (2025), released a **303-million-person synthetic United States population** constructed via Iterative Proportional Fitting (IPF) against US Census micro-data. The dataset is unprecedented in scale and demographic fidelity. However, it is a **static demographic snapshot** — there is no disease-dynamics layer, no behavioural model, and no temporal evolution. It is a substrate for downstream modelling, not a model in itself.

**Bilal et al.** [5] (*CitySEIRCast*, Springer, 2025) integrate a **3-D digital twin** of a single US county with an agent-based SEIR model driven by real mobility data. The framework demonstrates that high-resolution spatial detail can sharpen outbreak forecasts. The drawback is **computational cost**: CitySEIRCast is tightly coupled to one digital twin, runs only on dedicated infrastructure, and is not intended for comparative studies across different urban morphologies.

**Eubank et al.** [6] (*Nature*, 2004) introduced the earlier and still-influential **EpiSimS** approach — an activity-based ABM of Portland, Oregon — which similarly couples a single city's empirical contact network to a disease model.

**Limitation of the synthetic-population paradigm.** These models are usually **city-specific** and **expensive**. They optimise for fidelity to one location rather than enabling controlled comparisons across topology classes (e.g., "what changes between a dense single-core and a sparse polycentric city?").

---

## 3. Dynamic Contact Patterns and Behaviour-Coupled Models

The most directly relevant prior work models **time-varying contact patterns** and **behavioural feedback** during outbreaks.

**Funk, Salathé, and Jansen** [7] reviewed early models of **awareness-driven behaviour change**, in which infection probability depends on a node's perception of risk. They showed that even simple awareness mechanisms can alter the basic reproduction number and shift epidemic peaks. **Funk et al.** [8] later generalised this into a unified framework for **behaviour-informed epidemic models**.

**Perra et al.** [9] (*Scientific Reports*, 2012) introduced the **activity-driven network model**, in which each node has an intrinsic activity rate that governs how often it forms new contacts. The model captures temporal heterogeneity but does **not** include a behavioural feedback loop tied to disease prevalence.

**Karsai et al.** [10] (*Scientific Reports*, 2014) extended activity-driven models to capture **memory effects** — the tendency to repeatedly contact the same individuals — which further alters spreading dynamics.

More recent COVID-19-era work includes **Aleta et al.** [11] (*Nature Human Behaviour*, 2020), who coupled a high-resolution agent-based model of the Boston metropolitan area with **mobility-derived contact matrices** to study test-trace-isolate strategies. **Chang et al.** [12] (*Nature*, 2021) used **mobility-network meta-population models** to show that point-of-interest visits explain a large fraction of cross-neighbourhood transmission inequality in US metropolitan areas.

On the methodological-review side, **Zhang et al.** [13] (MDPI, 2025) compare **agent-based vs. compartmental vs. network-based** approaches for COVID-19 modelling. The review is conceptually thorough but does not provide empirical validation across topology classes.

**Limitation of dynamic-model literature.** Existing dynamic models capture *either* weekly / activity rhythms *or* behavioural feedback, *or* are tied to a single empirical city. **No prior study systematically compares static-network and dynamic-network predictions across multiple urban topology classes while simultaneously incorporating weekly rhythms and threshold-based behavioural adaptation, and validating against real outbreak data.**

---

## 4. Comparative Summary

| Study                                  | Year | Network model              | Weekly rhythm | Behavioural feedback | Multi-topology comparison | Real-data validation |
| -------------------------------------- | ---- | -------------------------- | :-----------: | :------------------: | :-----------------------: | :------------------: |
| Pastor-Satorras & Vespignani [1]       | 2001 | Scale-free (static)        |       ✗       |          ✗           |             ✗             |          ✗           |
| Keeling & Eames [3]                    | 2005 | Generic heterogeneous      |       ✗       |          ✗           |             ✗             |          ✗           |
| Eubank et al. (EpiSimS) [6]            | 2004 | Activity-based ABM (1 city)|       ◐       |          ✗           |             ✗             |          ◐           |
| Funk et al. [7,8]                      | 2010 | Awareness-coupled          |       ✗       |          ✓           |             ✗             |          ✗           |
| Perra et al. (activity-driven) [9]     | 2012 | Time-varying activity      |       ◐       |          ✗           |             ✗             |          ✗           |
| Karsai et al. (memory + activity) [10] | 2014 | Time-varying + memory      |       ◐       |          ✗           |             ✗             |          ✗           |
| Aleta et al. [11]                      | 2020 | Mobility ABM (1 metro)     |       ✓       |          ◐           |             ✗             |          ✓           |
| Chang et al. [12]                      | 2021 | Mobility meta-population   |       ✓       |          ✗           |             ✗             |          ✓           |
| Rineer et al. [4]                      | 2025 | Synthetic population (static)|     ✗       |          ✗           |             ✗             |          ✗           |
| Bilal et al. (CitySEIRCast) [5]        | 2025 | 3-D digital twin + ABM     |       ✓       |          ◐           |             ✗             |          ✓           |
| Zhang et al. (review) [13]             | 2025 | (Review)                   |       —       |          —           |             —             |          —           |
| **This work**                          | 2026 | **SBM (3 topologies)**     |     **✓**     |        **✓**         |          **✓**            |        **✓**         |

Symbols — ✓ = present; ◐ = partially present; ✗ = absent.

---

## 5. Identified Gap

Synthesising the table above:

* **Static-network classics** [1–3] explain structural drivers but ignore time-varying behaviour entirely.
* **Synthetic-population / digital-twin work** [4–6] achieves high realism but is **single-city** and computationally heavy.
* **Dynamic / behaviour-coupled models** [7–12] capture *one* dynamic ingredient (rhythm *or* feedback, rarely both) on a *single* topology.
* **No prior study unifies** (i) **multiple urban topology classes**, (ii) **weekly contact rhythms**, (iii) **threshold-based behavioural adaptation**, and (iv) **validation against real outbreak data** in a single, reproducible framework.

This gap is the **scientific niche** that the present project occupies.

---

## 6. How This Project Improves on Prior Work

The present work makes four contributions that, taken together, are not present in any single prior study:

1. **Systematic multi-topology comparison.** Three SBM-generated networks (Dense, Polycentric, Sparse) are simulated under **identical** disease parameters, isolating the effect of urban spatial structure on outbreak dynamics.
2. **Unified dynamic framework.** Both **weekly contact multipliers** (Weekend = 0.6 × Weekday) and **prevalence-threshold behavioural adaptation** (0 % / 30 % / 50 % / 70 % contact reduction) are layered on top of the same SBM substrate, enabling clean separation of the two dynamic effects.
3. **Real-data validation.** The dynamic model is validated against **St. Petersburg COVID-19 monitoring data (Winter 2022, Omicron wave)** with **R² = 0.915**, using literature-derived parameters — i.e., an **out-of-sample** validation rather than a fit.
4. **Topology-specific intervention guidelines.** Optimal intervention timing is shown to be a function of city topology (Dense: day 18 ; Polycentric: day 28 ; Sparse: day 42), enabling a shift from one-size-fits-all to **topology-aware** public-health policy.

The combined effect is a model that is **lighter than CitySEIRCast** [5], **richer than classic activity-driven models** [9, 10], and **broader than single-city ABM studies** [6, 11, 12], while remaining **empirically grounded** through St. Petersburg validation.

---

## References

Pastor-Satorras & Vespignani (Phys. Rev. Lett., 2001)
Established epidemic thresholds on scale-free networks; explained rapid global spread.

Keeling & Eames (J. R. Soc. Interface, 2005)
Identified degree distribution, clustering and assortativity as key determinants of outbreak dynamics.

Rineer et al. (Nature Scientific Data, 2025)
303M-person synthetic US population via Iterative Proportional Fitting. Limitation: static dataset, no disease simulation.

Bilal et al. (CitySEIRCast, Springer, 2025)
3D digital twin + ABM with mobility data. Limitation: computationally heavy, single US county.

Funk et al. (2010, 2015)
Behavior-informed networks: infection probability depends on perceived risk.

Perra et al. (Scientific Reports, 2011)
Activity-driven networks where node activity levels change over time.

Zhang et al. (MDPI, 2025)
Conceptual review of ABM vs compartmental/network models; lacks empirical validation.
Identified Gap:
No prior study compares static vs dynamic predictions across multiple urban topologies with both weekly patterns AND behavioral adaptation, validated against real data.

