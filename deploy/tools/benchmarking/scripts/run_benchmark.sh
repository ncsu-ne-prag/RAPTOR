#!/bin/bash
set -e

# Ensure results directory exists
mkdir -p /benchmark/results

echo "Starting OpenPSA model validation..."

# Wait for validation using python verifier script mapped in /build/pracciolini/src/openpsa_verifier.py
python3 /build/pracciolini/src/openpsa_verifier.py \
    -d /data \
    -r /build/scram/share/input.rng

if [ $? -ne 0 ]; then
    echo "Validation failed! Halting benchmarking process."
    exit 1
fi

echo "All files passed validation!"
echo "Starting benchmarking for XML files in /data..."

# Check if there are any XML files in the mounted directory
if [ -z "$(find /data -name '*.xml' -type f -print -quit)" ]; then
    echo "Error: No XML files found in /data."
    echo "Please ensure the dataset is mounted correctly."
    exit 1
fi

# Get comma-separated list of XML files for hyperfine parameterization
FILES=$(find /data -name '*.xml' -type f | tr '\n' ',' | sed 's/,$//')

CURRENT_DATE=$(date +"%Y-%m-%d")
MODEL=${MODEL_NAME:-unknown}
TOOL="scram"

# Run hyperfine
# Parameter '{file}' will be replaced by each file from the FILES list
# Results will be exported as JSON and Markdown in the results directory
hyperfine --export-markdown "/benchmark/results/${TOOL}_${MODEL}_${CURRENT_DATE}_summary.md" \
          --export-json "/benchmark/results/${TOOL}_${MODEL}_${CURRENT_DATE}_results.json" \
          --parameter-list file "$FILES" \
          "scram --bdd {file} --output /benchmark/results/${TOOL}_${MODEL}_${CURRENT_DATE}_\$(basename {file})-output.xml"

echo "Benchmarking completed successfully!"
echo "Results are available in /benchmark/results/"
