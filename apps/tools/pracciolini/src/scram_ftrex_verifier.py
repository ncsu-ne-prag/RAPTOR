import argparse
import csv
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from openpsa_s2ml_TEP_verifier import _parse_scram_report
from parse_ftrex_log import (
    parse_ftrex_exact,
    parse_ftrex_psum,
    parse_ftrex_pmcub,
    parse_ftrex_mcs_count,
)

_PROB_PARSERS = {
    "exact": parse_ftrex_exact,
    "psum":  parse_ftrex_psum,
    "pmcub": parse_ftrex_pmcub,
}


def compare_results(
    scram_output_dir: str,
    ftrex_output_dir: str,
    output_csv: str,
    rel_tol: float,
    prob_field: str,
) -> dict:
    summary = {
        "prob_matched":    0,
        "prob_mismatched": 0,
        "ftrex_missing":   0,
        "scram_error":     0,
    }
    rows = []

    if not os.path.isdir(scram_output_dir):
        raise NotADirectoryError(f"SCRAM output directory not found: {scram_output_dir}")

    ftrex_prob_fn = _PROB_PARSERS[prob_field]
    include_mcs = prob_field in ("psum", "pmcub")

    scram_files = sorted(f for f in os.listdir(scram_output_dir) if f.endswith(".xml"))

    for scram_fname in scram_files:
        model      = os.path.splitext(scram_fname)[0]
        scram_path = os.path.join(scram_output_dir, scram_fname)
        ftrex_log  = os.path.join(ftrex_output_dir, f"{model}.log")

        scram_prob, scram_mcs = _parse_scram_report(scram_path)
        ftrex_prob = ftrex_prob_fn(ftrex_log)
        ftrex_mcs  = parse_ftrex_mcs_count(ftrex_log) if include_mcs else None

        if scram_prob is None:
            prob_status = "SCRAM_ERROR"
            rel_diff    = ""
            summary["scram_error"] += 1
        elif ftrex_prob is None:
            prob_status = "FTREX_MISSING"
            rel_diff    = ""
            summary["ftrex_missing"] += 1
        else:
            if scram_prob == 0.0 and ftrex_prob == 0.0:
                rel_diff_val = 0.0
            elif scram_prob == 0.0:
                rel_diff_val = float("inf")
            else:
                rel_diff_val = abs(scram_prob - ftrex_prob) / scram_prob
            rel_diff = f"{rel_diff_val:.6e}"
            if rel_diff_val <= rel_tol:
                prob_status = "OK"
                summary["prob_matched"] += 1
            else:
                prob_status = "MISMATCH"
                summary["prob_mismatched"] += 1

        p_scram = f"{scram_prob:.6e}" if scram_prob is not None else "N/A"
        p_ftrex = f"{ftrex_prob:.6e}" if ftrex_prob  is not None else "N/A"
        m_scram = str(scram_mcs)      if scram_mcs   is not None else "N/A"
        m_ftrex = str(ftrex_mcs)      if ftrex_mcs   is not None else "N/A"

        if include_mcs:
            print(
                f"  {model:30s}  "
                f"P: SCRAM={p_scram:>12}  FTREX={p_ftrex:>12}  {prob_status:16s}  "
                f"MCS: SCRAM={m_scram:>6}  FTREX={m_ftrex:>6}"
            )
        else:
            print(
                f"  {model:30s}  "
                f"P: SCRAM={p_scram:>12}  FTREX={p_ftrex:>12}  {prob_status}"
            )

        row = {
            "model":             model,
            "scram_probability": "" if scram_prob is None else f"{scram_prob:.6e}",
            "ftrex_probability": "" if ftrex_prob is None else f"{ftrex_prob:.6e}",
            "prob_rel_diff":     rel_diff,
            "prob_status":       prob_status,
        }
        if include_mcs:
            row["scram_mcs_count"] = "" if scram_mcs is None else str(scram_mcs)
            row["ftrex_mcs_count"] = "" if ftrex_mcs is None else str(ftrex_mcs)
        rows.append(row)

    os.makedirs(os.path.dirname(os.path.abspath(output_csv)), exist_ok=True)
    fieldnames = ["model", "scram_probability", "ftrex_probability", "prob_rel_diff", "prob_status"]
    if include_mcs:
        fieldnames += ["scram_mcs_count", "ftrex_mcs_count"]

    with open(output_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    return summary


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--scram-dir",   required=True)
    parser.add_argument("--ftrex-dir",   required=True)
    parser.add_argument("--output",      required=True)
    parser.add_argument("--rel-tol",     type=float, default=1e-3)
    parser.add_argument("--prob-field",  choices=["exact", "psum", "pmcub"], default="exact")
    args = parser.parse_args()

    field_label = {"exact": "PROB(EXACT)", "psum": "PROB(SUM)", "pmcub": "PROB(MCUB)"}[args.prob_field]
    print("=== SCRAM vs FTREX: Probability & MCS Comparison ===")
    print(f"    FTREX field         : {field_label}")
    print(f"    Probability rel-tol : {args.rel_tol:.2g}")
    print()

    try:
        summary = compare_results(
            args.scram_dir, args.ftrex_dir, args.output,
            args.rel_tol, args.prob_field,
        )
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"\n--- Summary ---")
    print(f"  Probability matched (within {args.rel_tol*100:.2g}%):  {summary['prob_matched']}")
    print(f"  Probability mismatched:                                {summary['prob_mismatched']}")
    print(f"  FTREX output missing (timeout or crash):               {summary['ftrex_missing']}")
    print(f"  SCRAM parse error:                                     {summary['scram_error']}")
    print(f"\nReport written to: {args.output}")

    sys.exit(1 if summary["prob_mismatched"] > 0 else 0)


if __name__ == "__main__":
    main()
