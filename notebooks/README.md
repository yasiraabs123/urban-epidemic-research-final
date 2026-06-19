# Notebooks

This directory is reserved for exploratory Jupyter notebooks that wrap the modules in `src/` for interactive analysis.

## Suggested notebook ideas

A student or contributor extending this project may find the following notebooks useful starting points. They are **not yet implemented** — contributions are welcome.

| Notebook                          | Purpose                                                                                          |
| --------------------------------- | ------------------------------------------------------------------------------------------------ |
| `01_network_demo.ipynb`           | Call `src.network.build_sbm_network` for each mu value; visualise degree distributions.          |
| `02_seir_demo.ipynb`              | Run a single dynamic / static simulation with `src.seir.simulate`; plot S/E/I/R curves.          |
| `03_results_analysis.ipynb`       | Load `results/data/summary.csv` and compute paired t-tests, ANOVA, Cohen's d.                    |
| `04_validation.ipynb`             | Fit the dense-network dynamic curve against `data/st_petersburg_winter2022.csv`; compute R², RMSE. |

## Running

From the repository root with the virtual environment active:

```bash
pip install jupyterlab
jupyter lab notebooks/
```

Notebooks can import the research modules directly:

```python
from src.network import build_sbm_network, REGIMES
from src.seir import simulate, SEIRParameters
```
