# Benchmarking Tool

Compares SCRAM and XFTA fault tree solvers on the ARALIA dataset across three experiments:

| Experiment | SCRAM | XFTA | Comparison |
|---|---|---|---|
| 1 | BDD | BDD | Probability only |
| 2 | ZBDD + REA | ZBDD + REA | Probability + MCS count |
| 3 | ZBDD + MCUB | ZBDD + MCUB | Probability + MCS count |

XFTA also runs BDT (REA/MCUB/PUB) and ZBDD PUB for standalone timing — no SCRAM equivalent.

Cutoff: **1e-12** for all MCS runs. Timeout: **5 min** per model.

---

## Requirements

- Docker
- ARALIA dataset at `fixtures/models/aralia-fault-tree-dataset/data/openpsa`
- XFTA Linux binary at `apps/solvers/xfta/xftar`

---

## Run

From the repo root:

```bash
MSYS_NO_PATHCONV=1 docker compose \
  -f deploy/tools/benchmarking/docker-compose.yml up --build
```

Override the input dataset:

```bash
BENCHMARK_INPUT_DIR=/absolute/path/to/models \
MSYS_NO_PATHCONV=1 docker compose \
  -f deploy/tools/benchmarking/docker-compose.yml up --build
```

> **Windows / Git Bash:** `MSYS_NO_PATHCONV=1` is required to prevent path conversion.

---

## Results

All output is written to `fixtures/results/`.

### Timing (hyperfine JSON + Markdown)

| File pattern | Run |
|---|---|
| `scram_bdd_*` | SCRAM BDD |
| `scram_zbdd_rea_*` | SCRAM ZBDD REA |
| `scram_zbdd_mcub_*` | SCRAM ZBDD MCUB |
| `xfta_bdd_*` | XFTA BDD |
| `xfta_bdt_rea/mcub/pub_*` | XFTA BDT (3 approximations) |
| `xfta_zbdd_rea/mcub/pub_*` | XFTA ZBDD (3 approximations) |

### Comparisons (CSV)

| File | Experiment |
|---|---|
| `exp1_bdd_comparison_*.csv` | SCRAM BDD vs XFTA BDD — probability |
| `exp2_zbdd_rea_comparison_*.csv` | SCRAM ZBDD REA vs XFTA ZBDD REA — probability + MCS |
| `exp3_zbdd_mcub_comparison_*.csv` | SCRAM ZBDD MCUB vs XFTA ZBDD MCUB — probability + MCS |

Each CSV row contains: `model`, `scram_probability`, `xfta_probability`, `prob_rel_diff`, `prob_status`, `scram_mcs_count`, `xfta_mcs_count`, `mcs_diff`, `mcs_status`.

Status values: `OK`, `MISMATCH`, `XFTA_SKIPPED`, `SCRAM_ERROR`.

### XFTA-incompatible models

Models containing `<not>` or `<xor>` gates are skipped for all XFTA runs:
`cea9601`, `das9601`, `das9701`.
