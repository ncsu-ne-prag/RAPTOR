#!/bin/bash
set -e

MODEL=${MODEL_NAME:-aralia}
CURRENT_DATE=$(date +"%Y-%m-%d")

# =============================================================================
# Directory layout
#
# XFTA runs  (7 algorithms):
#   1. BDD
#   2. BDT  REA  (rare-event approximation)
#   3. BDT  MCUB (mincut upper bound)
#   4. BDT  PUB  (pivotal upper bound)      [XFTA-only, no SCRAM equivalent]
#   5. ZBDD REA
#   6. ZBDD MCUB
#   7. ZBDD PUB                             [XFTA-only, no SCRAM equivalent]
#
# SCRAM runs (3 algorithms):
#   1. BDD             (exact, --bdd)
#   2. ZBDD + REA      (--zbdd --rare-event --cut-off 1e-12)
#   3. ZBDD + MCUB     (--zbdd --mcub      --cut-off 1e-12)
#
# Comparisons (3, paired by equivalent algorithm):
#   Exp 1: SCRAM BDD       vs XFTA BDD       — probability only
#   Exp 2: SCRAM ZBDD REA  vs XFTA ZBDD REA  — probability + MCS count
#   Exp 3: SCRAM ZBDD MCUB vs XFTA ZBDD MCUB — probability + MCS count
# =============================================================================
RESULTS_DIR="/benchmark/results"
SBE_DIR="/benchmark/sbe"

# XFTA script directories
XFTA_SCRIPTS_BDD="$RESULTS_DIR/xfta_scripts/bdd"
XFTA_SCRIPTS_BDT_REA="$RESULTS_DIR/xfta_scripts/bdt_rea"
XFTA_SCRIPTS_BDT_MCUB="$RESULTS_DIR/xfta_scripts/bdt_mcub"
XFTA_SCRIPTS_BDT_PUB="$RESULTS_DIR/xfta_scripts/bdt_pub"
XFTA_SCRIPTS_ZBDD_REA="$RESULTS_DIR/xfta_scripts/zbdd_rea"
XFTA_SCRIPTS_ZBDD_MCUB="$RESULTS_DIR/xfta_scripts/zbdd_mcub"
XFTA_SCRIPTS_ZBDD_PUB="$RESULTS_DIR/xfta_scripts/zbdd_pub"

# SCRAM output directories (one per SCRAM run)
SCRAM_OUT_BDD="$RESULTS_DIR/scram_bdd_output"
SCRAM_OUT_ZBDD_REA="$RESULTS_DIR/scram_zbdd_rea_output"
SCRAM_OUT_ZBDD_MCUB="$RESULTS_DIR/scram_zbdd_mcub_output"

# XFTA output directories (one per XFTA algorithm)
XFTA_OUT_BDD="$RESULTS_DIR/xfta_bdd_output"
XFTA_OUT_BDT_REA="$RESULTS_DIR/xfta_bdt_rea_output"
XFTA_OUT_BDT_MCUB="$RESULTS_DIR/xfta_bdt_mcub_output"
XFTA_OUT_BDT_PUB="$RESULTS_DIR/xfta_bdt_pub_output"
XFTA_OUT_ZBDD_REA="$RESULTS_DIR/xfta_zbdd_rea_output"
XFTA_OUT_ZBDD_MCUB="$RESULTS_DIR/xfta_zbdd_mcub_output"
XFTA_OUT_ZBDD_PUB="$RESULTS_DIR/xfta_zbdd_pub_output"

mkdir -p "$RESULTS_DIR" "$SBE_DIR" \
    "$XFTA_SCRIPTS_BDD" "$XFTA_SCRIPTS_BDT_REA" "$XFTA_SCRIPTS_BDT_MCUB" "$XFTA_SCRIPTS_BDT_PUB" \
    "$XFTA_SCRIPTS_ZBDD_REA" "$XFTA_SCRIPTS_ZBDD_MCUB" "$XFTA_SCRIPTS_ZBDD_PUB" \
    "$SCRAM_OUT_BDD" "$SCRAM_OUT_ZBDD_REA" "$SCRAM_OUT_ZBDD_MCUB" \
    "$XFTA_OUT_BDD" \
    "$XFTA_OUT_BDT_REA" "$XFTA_OUT_BDT_MCUB" "$XFTA_OUT_BDT_PUB" \
    "$XFTA_OUT_ZBDD_REA" "$XFTA_OUT_ZBDD_MCUB" "$XFTA_OUT_ZBDD_PUB"

# =============================================================================
# Step 1: Validate OpenPSA XML files against SCRAM's RELAX NG schema
# =============================================================================
echo ""
echo "=== Step 1: Validating OpenPSA XML files ==="
python3 /build/pracciolini/src/openpsa_verifier.py \
    -d /data \
    -r /build/scram/share/input.rng

# =============================================================================
# Step 2: Convert OpenPSA XML → S2ML+SBE and generate all 7 XFTA script sets
#
#   Models with <not> or <xor> gates are skipped — XFTA cannot evaluate them.
#
#   ZBDD scripts share a common structure:
#     build BDD  (required as input to ZBDD-from-BDD)
#     set option minimum-probability 1e-12
#     build ZBDD-from-BDD
#     compute probability source-handle=ZBDD quantification-method=<method>
#     print minimal-cutsets source-handle=ZBDD
#
#   BDT scripts share a common structure:
#     set option minimum-probability 1e-12
#     build BDT
#     compute probability source-handle=BDT quantification-method=<method>
#     print minimal-cutsets source-handle=BDT
# =============================================================================
echo ""
echo "=== Step 2: Converting OpenPSA XML to S2ML+SBE and generating XFTA scripts ==="

SKIPPED_MODELS=()
CONVERTED_MODELS=()

for xml_file in $(find /data -name '*.xml' -type f | sort); do
    base=$(basename "$xml_file" .xml)
    sbe_file="$SBE_DIR/$base.sbe"

    if python3 /build/pracciolini/src/openpsa_to_s2ml_converter.py \
            -i "$xml_file" -o "$sbe_file" 2>/tmp/conv_err.txt; then

        top_event=$(python3 /build/pracciolini/src/openpsa_to_s2ml_converter.py \
            --get-top-event -i "$xml_file" 2>/dev/null)

        # ── 1. XFTA BDD (exact probability, no MCS, no cutoff) ───────────────
        cat > "$XFTA_SCRIPTS_BDD/$base.xfta" << XFTA_BDD
load model "$sbe_file";
build target-model;
build BDD $top_event;
compute probability $top_event output="$XFTA_OUT_BDD/${base}_prob.tsv";
XFTA_BDD

        # ── 2. XFTA BDT REA ──────────────────────────────────────────────────
        cat > "$XFTA_SCRIPTS_BDT_REA/$base.xfta" << XFTA_BDT_REA
load model "$sbe_file";
build target-model;
set option minimum-probability 1e-12;
build BDT $top_event;
compute probability $top_event source-handle=BDT quantification-method=rare-event-approximation output="$XFTA_OUT_BDT_REA/${base}_prob.tsv";
print minimal-cutsets $top_event source-handle=BDT output="$XFTA_OUT_BDT_REA/${base}_mcs.tsv";
XFTA_BDT_REA

        # ── 3. XFTA BDT MCUB ─────────────────────────────────────────────────
        cat > "$XFTA_SCRIPTS_BDT_MCUB/$base.xfta" << XFTA_BDT_MCUB
load model "$sbe_file";
build target-model;
set option minimum-probability 1e-12;
build BDT $top_event;
compute probability $top_event source-handle=BDT quantification-method=mincut-upper-bound output="$XFTA_OUT_BDT_MCUB/${base}_prob.tsv";
print minimal-cutsets $top_event source-handle=BDT output="$XFTA_OUT_BDT_MCUB/${base}_mcs.tsv";
XFTA_BDT_MCUB

        # ── 4. XFTA BDT PUB (default quantification in BDT) ─────────────────
        cat > "$XFTA_SCRIPTS_BDT_PUB/$base.xfta" << XFTA_BDT_PUB
load model "$sbe_file";
build target-model;
set option minimum-probability 1e-12;
build BDT $top_event;
compute probability $top_event source-handle=BDT quantification-method=pivotal-upper-bound output="$XFTA_OUT_BDT_PUB/${base}_prob.tsv";
print minimal-cutsets $top_event source-handle=BDT output="$XFTA_OUT_BDT_PUB/${base}_mcs.tsv";
XFTA_BDT_PUB

        # ── 5. XFTA ZBDD REA ─────────────────────────────────────────────────
        cat > "$XFTA_SCRIPTS_ZBDD_REA/$base.xfta" << XFTA_ZBDD_REA
load model "$sbe_file";
build target-model;
build BDD $top_event;
set option minimum-probability 1e-12;
build ZBDD-from-BDD $top_event;
compute probability $top_event source-handle=ZBDD quantification-method=rare-event-approximation output="$XFTA_OUT_ZBDD_REA/${base}_prob.tsv";
print minimal-cutsets $top_event source-handle=ZBDD output="$XFTA_OUT_ZBDD_REA/${base}_mcs.tsv";
XFTA_ZBDD_REA

        # ── 6. XFTA ZBDD MCUB ────────────────────────────────────────────────
        cat > "$XFTA_SCRIPTS_ZBDD_MCUB/$base.xfta" << XFTA_ZBDD_MCUB
load model "$sbe_file";
build target-model;
build BDD $top_event;
set option minimum-probability 1e-12;
build ZBDD-from-BDD $top_event;
compute probability $top_event source-handle=ZBDD quantification-method=mincut-upper-bound output="$XFTA_OUT_ZBDD_MCUB/${base}_prob.tsv";
print minimal-cutsets $top_event source-handle=ZBDD output="$XFTA_OUT_ZBDD_MCUB/${base}_mcs.tsv";
XFTA_ZBDD_MCUB

        # ── 7. XFTA ZBDD PUB ─────────────────────────────────────────────────
        cat > "$XFTA_SCRIPTS_ZBDD_PUB/$base.xfta" << XFTA_ZBDD_PUB
load model "$sbe_file";
build target-model;
build BDD $top_event;
set option minimum-probability 1e-12;
build ZBDD-from-BDD $top_event;
compute probability $top_event source-handle=ZBDD quantification-method=pivotal-upper-bound output="$XFTA_OUT_ZBDD_PUB/${base}_prob.tsv";
print minimal-cutsets $top_event source-handle=ZBDD output="$XFTA_OUT_ZBDD_PUB/${base}_mcs.tsv";
XFTA_ZBDD_PUB

        echo "  Converted: $base  (top event: $top_event)"
        CONVERTED_MODELS+=("$base")
    else
        reason=$(cat /tmp/conv_err.txt | tail -1)
        echo "  SKIPPED:   $base  ($reason)"
        SKIPPED_MODELS+=("$base")
    fi
done

echo ""
echo "Converted: ${#CONVERTED_MODELS[@]} models"
echo "Skipped:   ${#SKIPPED_MODELS[@]} models (incompatible gates: NOT/XOR)"
if [ ${#SKIPPED_MODELS[@]} -gt 0 ]; then
    echo "  Skipped list: ${SKIPPED_MODELS[*]}"
fi

# =============================================================================
# Step 3: Validate S2ML+SBE files
# =============================================================================
echo ""
echo "=== Step 3: Validating S2ML+SBE files ==="
python3 /build/pracciolini/src/s2ml_verifier.py -d "$SBE_DIR"

# ── Shared helpers ────────────────────────────────────────────────────────────
XML_FILES=$(find /data -name '*.xml' -type f | sort | tr '\n' ',' | sed 's/,$//')
if [ -z "$XML_FILES" ]; then
    echo "ERROR: No XML files found in /data"
    exit 1
fi

scripts_list() { find "$1" -name '*.xfta' -type f | sort | tr '\n' ',' | sed 's/,$//'; }

N_ALL=$(( ${#CONVERTED_MODELS[@]} + ${#SKIPPED_MODELS[@]} ))
N_COMPAT=${#CONVERTED_MODELS[@]}

run_xfta() {
    # run_xfta <label> <scripts_dir> <json_out> <md_out>
    local label="$1" scripts_dir="$2" json_out="$3" md_out="$4"
    local scripts
    scripts=$(scripts_list "$scripts_dir")
    if [ -z "$scripts" ]; then
        echo "WARNING: No scripts in $scripts_dir — skipping."
        return
    fi
    echo ""
    echo "--- $label ($N_COMPAT compatible models) ---"
    hyperfine \
        --warmup 0 --runs 1 --ignore-failure \
        --export-markdown "$md_out" \
        --export-json    "$json_out" \
        --parameter-list script "$scripts" \
        "timeout 300 xftar {script}"
    echo "$label complete."
}

run_comparison() {
    # run_comparison <label> <scram_dir> <xfta_dir> <csv_out> [--mcs-cutoff 1e-12]
    local label="$1" scram_dir="$2" xfta_dir="$3" csv_out="$4"
    shift 4
    echo ""
    echo "--- Comparison: $label ---"
    python3 /build/pracciolini/src/openpsa_s2ml_TEP_verifier.py \
        --scram-dir "$scram_dir" \
        --xfta-dir  "$xfta_dir" \
        --output    "$csv_out" \
        --rel-tol   1e-3 \
        "$@" || true
}

# =============================================================================
# SCRAM BENCHMARKS
# =============================================================================
echo ""
echo "###################################################################"
echo "  SCRAM BENCHMARKS"
echo "###################################################################"

# ── SCRAM BDD ─────────────────────────────────────────────────────────────────
echo ""
echo "--- SCRAM BDD ($N_ALL models) ---"
hyperfine \
    --warmup 0 --runs 1 --ignore-failure \
    --export-markdown "$RESULTS_DIR/scram_bdd_${MODEL}_${CURRENT_DATE}_summary.md" \
    --export-json    "$RESULTS_DIR/scram_bdd_${MODEL}_${CURRENT_DATE}_results.json" \
    --parameter-list file "$XML_FILES" \
    "timeout 300 scram --bdd {file} \
        --output $SCRAM_OUT_BDD/\$(basename {file} .xml).xml"
echo "SCRAM BDD complete."

# ── SCRAM ZBDD REA ────────────────────────────────────────────────────────────
echo ""
echo "--- SCRAM ZBDD REA ($N_ALL models) ---"
hyperfine \
    --warmup 0 --runs 1 --ignore-failure \
    --export-markdown "$RESULTS_DIR/scram_zbdd_rea_${MODEL}_${CURRENT_DATE}_summary.md" \
    --export-json    "$RESULTS_DIR/scram_zbdd_rea_${MODEL}_${CURRENT_DATE}_results.json" \
    --parameter-list file "$XML_FILES" \
    "timeout 300 scram --zbdd --rare-event --cut-off 1e-12 {file} \
        --output $SCRAM_OUT_ZBDD_REA/\$(basename {file} .xml).xml"
echo "SCRAM ZBDD REA complete."

# ── SCRAM ZBDD MCUB ───────────────────────────────────────────────────────────
echo ""
echo "--- SCRAM ZBDD MCUB ($N_ALL models) ---"
hyperfine \
    --warmup 0 --runs 1 --ignore-failure \
    --export-markdown "$RESULTS_DIR/scram_zbdd_mcub_${MODEL}_${CURRENT_DATE}_summary.md" \
    --export-json    "$RESULTS_DIR/scram_zbdd_mcub_${MODEL}_${CURRENT_DATE}_results.json" \
    --parameter-list file "$XML_FILES" \
    "timeout 300 scram --zbdd --mcub --cut-off 1e-12 {file} \
        --output $SCRAM_OUT_ZBDD_MCUB/\$(basename {file} .xml).xml"
echo "SCRAM ZBDD MCUB complete."

# =============================================================================
# XFTA BENCHMARKS  (all 7 algorithms)
# =============================================================================
echo ""
echo "###################################################################"
echo "  XFTA BENCHMARKS"
echo "###################################################################"

run_xfta "XFTA BDD" \
    "$XFTA_SCRIPTS_BDD" \
    "$RESULTS_DIR/xfta_bdd_${MODEL}_${CURRENT_DATE}_results.json" \
    "$RESULTS_DIR/xfta_bdd_${MODEL}_${CURRENT_DATE}_summary.md"

run_xfta "XFTA BDT REA" \
    "$XFTA_SCRIPTS_BDT_REA" \
    "$RESULTS_DIR/xfta_bdt_rea_${MODEL}_${CURRENT_DATE}_results.json" \
    "$RESULTS_DIR/xfta_bdt_rea_${MODEL}_${CURRENT_DATE}_summary.md"

run_xfta "XFTA BDT MCUB" \
    "$XFTA_SCRIPTS_BDT_MCUB" \
    "$RESULTS_DIR/xfta_bdt_mcub_${MODEL}_${CURRENT_DATE}_results.json" \
    "$RESULTS_DIR/xfta_bdt_mcub_${MODEL}_${CURRENT_DATE}_summary.md"

run_xfta "XFTA BDT PUB" \
    "$XFTA_SCRIPTS_BDT_PUB" \
    "$RESULTS_DIR/xfta_bdt_pub_${MODEL}_${CURRENT_DATE}_results.json" \
    "$RESULTS_DIR/xfta_bdt_pub_${MODEL}_${CURRENT_DATE}_summary.md"

run_xfta "XFTA ZBDD REA" \
    "$XFTA_SCRIPTS_ZBDD_REA" \
    "$RESULTS_DIR/xfta_zbdd_rea_${MODEL}_${CURRENT_DATE}_results.json" \
    "$RESULTS_DIR/xfta_zbdd_rea_${MODEL}_${CURRENT_DATE}_summary.md"

run_xfta "XFTA ZBDD MCUB" \
    "$XFTA_SCRIPTS_ZBDD_MCUB" \
    "$RESULTS_DIR/xfta_zbdd_mcub_${MODEL}_${CURRENT_DATE}_results.json" \
    "$RESULTS_DIR/xfta_zbdd_mcub_${MODEL}_${CURRENT_DATE}_summary.md"

run_xfta "XFTA ZBDD PUB" \
    "$XFTA_SCRIPTS_ZBDD_PUB" \
    "$RESULTS_DIR/xfta_zbdd_pub_${MODEL}_${CURRENT_DATE}_results.json" \
    "$RESULTS_DIR/xfta_zbdd_pub_${MODEL}_${CURRENT_DATE}_summary.md"

# =============================================================================
# COMPARISONS  (3 paired experiments)
# =============================================================================
echo ""
echo "###################################################################"
echo "  COMPARISONS"
echo "###################################################################"

# ── Experiment 1: SCRAM BDD vs XFTA BDD (probability only) ───────────────────
run_comparison \
    "Exp 1: SCRAM BDD vs XFTA BDD (probability only)" \
    "$SCRAM_OUT_BDD" "$XFTA_OUT_BDD" \
    "$RESULTS_DIR/exp1_bdd_comparison_${MODEL}_${CURRENT_DATE}.csv"

# ── Experiment 2: SCRAM ZBDD REA vs XFTA ZBDD REA (prob + MCS) ───────────────
run_comparison \
    "Exp 2: SCRAM ZBDD REA vs XFTA ZBDD REA (probability + MCS)" \
    "$SCRAM_OUT_ZBDD_REA" "$XFTA_OUT_ZBDD_REA" \
    "$RESULTS_DIR/exp2_zbdd_rea_comparison_${MODEL}_${CURRENT_DATE}.csv" \
    --mcs-cutoff 1e-12

# ── Experiment 3: SCRAM ZBDD MCUB vs XFTA ZBDD MCUB (prob + MCS) ────────────
run_comparison \
    "Exp 3: SCRAM ZBDD MCUB vs XFTA ZBDD MCUB (probability + MCS)" \
    "$SCRAM_OUT_ZBDD_MCUB" "$XFTA_OUT_ZBDD_MCUB" \
    "$RESULTS_DIR/exp3_zbdd_mcub_comparison_${MODEL}_${CURRENT_DATE}.csv" \
    --mcs-cutoff 1e-12

# =============================================================================
# Done
# =============================================================================
echo ""
echo "###################################################################"
echo "  All benchmarks and comparisons completed!"
echo "###################################################################"
echo ""
echo "Timing results  (JSON + Markdown) in $RESULTS_DIR/:"
echo "  scram_bdd_*           scram_zbdd_rea_*         scram_zbdd_mcub_*"
echo "  xfta_bdd_*"
echo "  xfta_bdt_rea_*        xfta_bdt_mcub_*          xfta_bdt_pub_*"
echo "  xfta_zbdd_rea_*       xfta_zbdd_mcub_*         xfta_zbdd_pub_*"
echo ""
echo "Comparison CSVs  (probability + MCS count) in $RESULTS_DIR/:"
echo "  exp1_bdd_comparison_*          — SCRAM BDD       vs XFTA BDD"
echo "  exp2_zbdd_rea_comparison_*     — SCRAM ZBDD REA  vs XFTA ZBDD REA"
echo "  exp3_zbdd_mcub_comparison_*    — SCRAM ZBDD MCUB vs XFTA ZBDD MCUB"
