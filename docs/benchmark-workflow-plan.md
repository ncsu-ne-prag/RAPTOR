# Plan: Aralia Benchmark GitHub Actions Workflow

## Resolved Configuration

| Item | Value |
|------|-------|
| Registry | `registry.openpra.org` (HTTPS, Traefik + Cloudflare TLS) |
| Registry software | Docker Distribution `registry:2` |
| Registry auth | htpasswd — secrets `REGISTRY_USERNAME` / `REGISTRY_PASSWORD` |
| Image name | `registry.openpra.org/c2c-benchmark:latest` |
| Existing image | None — must be built and pushed first |
| Aralia fixture | `fixtures/aralia/` (43 XML files, flat) |
| Proprietary solver dirs | Local Windows machine only (`apps/solvers/{ftrex,zebra,saphsolve}/`) |
| Runner | `self-hosted` on cluster (`gaia`) |
| Registry secrets in RAPTOR | Not yet added — must be copied from the other repo |

---

## Architecture

```
Local Windows machine
━━━━━━━━━━━━━━━━━━━━
docker build (Dockerfile + proprietary solver dirs)
docker push → registry.openpra.org/c2c-benchmark:latest
                        │
                        ▼
              registry.openpra.org  (Docker Distribution, on gaia)
                        │
GitHub (public)         │                     Your Cluster (gaia)
━━━━━━━━━━━━━━━━━━━━━━━━┼━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
benchmark.yml trigger   │
        │               │
        ▼               │
  GH Actions ──────── self-hosted runner ──── docker login registry.openpra.org
  (checkout repo)               │              docker pull c2c-benchmark:latest
  fixtures/aralia/ ─────────────┤
  deploy/.../scripts/ ──────────┤              docker run:
  fixtures/results/ (empty) ────┘                /data        ← aralia XML
                                                 /benchmark/scripts ← run_benchmark.sh
                                                 /benchmark/results ← output
                                                        │
                                                        ▼
                                               upload as GH Actions artifact
                                               (HTML report, CSVs, JSON timing)
```

---

## Key Design Decisions

### 1. Pre-built image in the private registry

Build once locally (where proprietary files live), push to registry. CI only pulls and runs.

- Serial keys for FTREX/ZEBRA baked in alongside executables — never touch GitHub
- Rebuild and push manually when any solver changes

### 2. Workflow triggers

- `workflow_dispatch` — manual, primary trigger
- `schedule` cron — can be added later (e.g., weekly)

### 3. Volume mounts at runtime (scripts not baked in)

Same pattern as `docker-compose.yml`:
- `fixtures/aralia/` → `/data`
- `deploy/tools/benchmarking/scripts/` → `/benchmark/scripts`
- `fixtures/results/` → `/benchmark/results`

Keeps scripts editable without rebuilding the image.

### 4. Registry auth in workflow

`docker/login-action@v3` using secrets `REGISTRY_USERNAME` / `REGISTRY_PASSWORD`.
Secret names already match what exists in the other repo — just needs to be added to RAPTOR.

### 5. Results as GitHub Actions artifacts, 90-day retention

---

## Implementation Steps

### Step 1 — Build and push `c2c-benchmark` image  ← **CURRENT**

Run locally (PowerShell, from repo root):

```powershell
docker build `
  -f deploy/tools/benchmarking/Dockerfile `
  -t registry.openpra.org/c2c-benchmark:latest `
  .

docker login registry.openpra.org -u hasibul

docker push registry.openpra.org/c2c-benchmark:latest
```

### Step 2 — Add secrets to RAPTOR repo

GitHub → RAPTOR repo → Settings → Secrets and variables → Actions → add:
- `REGISTRY_USERNAME` (same value as the other repo)
- `REGISTRY_PASSWORD` (same value as the other repo)

### Step 3 — Create `.github/workflows/benchmark.yml`

New workflow file. I write this after Step 1 confirms the image pushed successfully.

Key steps inside the workflow:
1. `actions/checkout@v4` (no submodules needed — Aralia is in-repo)
2. `docker/login-action@v3` → `registry.openpra.org`
3. `docker pull registry.openpra.org/c2c-benchmark:latest`
4. `docker run` with three volume mounts (aralia, scripts, results)
5. `actions/upload-artifact@v4` → everything under `fixtures/results/`

### Step 4 — Test run

Trigger `workflow_dispatch` on `benchmark` branch. Paste log output here to debug.

### Step 5 — Iterate

One fix at a time until clean run.

---

## What Will NOT Change

- `deploy/tools/benchmarking/Dockerfile`
- `deploy/tools/benchmarking/scripts/run_benchmark.sh`
- `apps/solvers/{ftrex,zebra,saphsolve}/`
- `.gitignore`
- `cd.yml`, `ci.yml`
