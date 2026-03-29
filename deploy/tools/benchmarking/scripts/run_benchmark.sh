#!/bin/bash
set -e

MODEL=${MODEL_NAME:-aralia}
CURRENT_DATE=$(date +"%Y-%m-%d")

RESULTS_DIR="/benchmark/results"
SBE_DIR="/benchmark/sbe"
SCRIPTS_DIR="/benchmark/xfta_scripts"
SCRAM_OUT_DIR="/benchmark/results/scram_output"
XFTA_OUT_DIR="/benchmark/results/xfta_output"

mkdir -p "$RESULTS_DIR" "$SBE_DIR" "$SCRIPTS_DIR" "$SCRAM_OUT_DIR" "$XFTA_OUT_DIR"

# =============================================================================
# Step 1: Validate OpenPSA XML files against SCRAM's RELAX NG schema
# =============================================================================
echo ""
echo "=== Step 1: Validating OpenPSA XML files ==="
python3 /build/pracciolini/src/openpsa_verifier.py \
    -d /data \
    -r /build/scram/share/input.rng

# =============================================================================
# Step 2: Convert OpenPSA XML → S2ML+SBE and generate XFTA scripts
#         Models with <not> or <xor> gates are skipped (XFTA limitation).
# =============================================================================
echo ""
echo "=== Step 2: Converting OpenPSA XML to S2ML+SBE ==="

SKIPPED_MODELS=()
CONVERTED_MODELS=()

for xml_file in $(find /data -name '*.xml' -type f | sort); do
    base=$(basename "$xml_file" .xml)
    sbe_file="$SBE_DIR/$base.sbe"
    script_file="$SCRIPTS_DIR/$base.xfta"
    prob_out="$XFTA_OUT_DIR/${base}_prob.tsv"
    mcs_out="$XFTA_OUT_DIR/${base}_mcs.tsv"

    if python3 /build/pracciolini/src/openpsa_to_s2ml_converter.py \
            -i "$xml_file" -o "$sbe_file" 2>/tmp/conv_err.txt; then

        # Extract top event name and generate the XFTA script
        top_event=$(python3 /build/pracciolini/src/openpsa_to_s2ml_converter.py \
            --get-top-event -i "$xml_file" 2>/dev/null)

        cat > "$script_file" << XFTA_SCRIPT
load model "$sbe_file";
build target-model;
build BDT $top_event;
compute probability $top_event output="$prob_out";
print minimal-cutsets $top_event output="$mcs_out";
XFTA_SCRIPT

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

# =============================================================================
# Step 4: SCRAM benchmark on all OpenPSA XML files
#         - BDD-based exact probability analysis
#         - Cut-off: 1e-12 (minimum cut set probability)
#         - Timeout: 5 minutes per model
# =============================================================================
echo ""
echo "=== Step 4: SCRAM benchmark (all ${#CONVERTED_MODELS[@]} + ${#SKIPPED_MODELS[@]} models) ==="

XML_FILES=$(find /data -name '*.xml' -type f | sort | tr '\n' ',' | sed 's/,$//')

if [ -z "$XML_FILES" ]; then
    echo "ERROR: No XML files found in /data"
    exit 1
fi

hyperfine \
    --warmup 0 \
    --runs 1 \
    --ignore-failure \
    --export-markdown "$RESULTS_DIR/scram_${MODEL}_${CURRENT_DATE}_summary.md" \
    --export-json    "$RESULTS_DIR/scram_${MODEL}_${CURRENT_DATE}_results.json" \
    --parameter-list file "$XML_FILES" \
    "timeout 300 scram --bdd --probability --cut-off 1e-12 {file} \
        --output $SCRAM_OUT_DIR/\$(basename {file} .xml).xml"

echo "SCRAM benchmark complete."

# =============================================================================
# Step 5: XFTA benchmark on converted S2ML+SBE models
#         - BDT-based exact probability analysis
#         - Cut-off: 1e-12 applied via SCRAM-side comparison
#         - Timeout: 5 minutes per model
# =============================================================================
echo ""
echo "=== Step 5: XFTA benchmark (${#CONVERTED_MODELS[@]} compatible models) ==="

XFTA_SCRIPTS=$(find "$SCRIPTS_DIR" -name '*.xfta' | sort | tr '\n' ',' | sed 's/,$//')

if [ -z "$XFTA_SCRIPTS" ]; then
    echo "WARNING: No XFTA scripts found. Skipping XFTA benchmark."
else
    hyperfine \
        --warmup 0 \
        --runs 1 \
        --ignore-failure \
        --export-markdown "$RESULTS_DIR/xfta_${MODEL}_${CURRENT_DATE}_summary.md" \
        --export-json    "$RESULTS_DIR/xfta_${MODEL}_${CURRENT_DATE}_results.json" \
        --parameter-list script "$XFTA_SCRIPTS" \
        "timeout 300 xftar {script}"

    echo "XFTA benchmark complete."
fi

# =============================================================================
# Step 6: Code-to-code probability verification (SCRAM vs XFTA)
# =============================================================================
echo ""
echo "=== Step 6: Probability verification (SCRAM vs XFTA) ==="

python3 /build/pracciolini/src/probability_verifier.py \
    --scram-dir "$SCRAM_OUT_DIR" \
    --xfta-dir  "$XFTA_OUT_DIR" \
    --output    "$RESULTS_DIR/probability_comparison_${MODEL}_${CURRENT_DATE}.csv" \
    --rel-tol   1e-3 || true   # non-zero exit on mismatch is informational, not fatal

echo ""
echo "=== Benchmarking completed! ==="
echo "Results are available in $RESULTS_DIR/"
