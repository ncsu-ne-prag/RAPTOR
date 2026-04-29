import argparse
import csv
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from openpsa_s2ml_TEP_verifier import _parse_scram_report
from parse_zebra_log import (
    parse_zebra_probability,
    parse_zebra_mcs_count,
    parse_zebra_psum,
    parse_zebra_pmcub,
)

_PROB_PARSERS = {
    "bdd":   parse_zebra_probability,
    "psum":  parse_zebra_psum,
    "pmcub": parse_zebra_pmcub,
}


def compare_results(
    scram_output_dir: str,
    zebra_output_dir: str,
    output_csv: str,
    rel_tol: float,
    prob_field: str,
) -> dict:
    summary = {
        "prob_matched":    0,
        "prob_mismatched": 0,
        "zebra_missing":   0,
        "scram_error":     0,
    }
    rows = []

    if not os.path.isdir(scram_output_dir):
        raise NotADirectoryError(f"SCRAM output directory not found: {scram_output_dir}")

    zebra_prob_fn = _PROB_PARSERS[prob_field]
    include_mcs = prob_field in ("psum", "pmcub")

    scram_files = sorted(f for f in os.listdir(scram_output_dir) if f.endswith(".xml"))

    for scram_fname in scram_files:
        model       = os.path.splitext(scram_fname)[0]
        scram_path  = os.path.join(scram_output_dir, scram_fname)
        zebra_log   = os.path.join(zebra_output_dir, f"{model}.log")

        scram_prob, scram_mcs = _parse_scram_report(scram_path)
        zebra_prob  = zebra_prob_fn(zebra_log)
        zebra_mcs   = parse_zebra_mcs_count(zebra_log) if include_mcs else None

        if scram_prob is None:
            prob_status  = "SCRAM_ERROR"
            rel_diff     = ""
            summary["scram_error"] += 1
        elif zebra_prob is None:
            prob_status  = "ZEBRA_MISSING"
            rel_diff     = ""
            summary["zebra_missing"] += 1
        else:
            if scram_prob == 0.0 and zebra_prob == 0.0:
                rel_diff_val = 0.0
            elif scram_prob == 0.0:
                rel_diff_val = float("inf")
            else:
                rel_diff_val = abs(scram_prob - zebra_prob) / scram_prob
            rel_diff = f"{rel_diff_val:.6e}"
            if rel_diff_val <= rel_tol:
                prob_status = "OK"
                summary["prob_matched"] += 1
            else:
                prob_status = "MISMATCH"
                summary["prob_mismatched"] += 1

        p_scram = f"{scram_prob:.6e}" if scram_prob is not None else "N/A"
        p_zebra = f"{zebra_prob:.6e}" if zebra_prob  is not None else "N/A"
        m_scram = str(scram_mcs)      if scram_mcs   is not None else "N/A"
        m_zebra = str(zebra_mcs)      if zebra_mcs   is not None else "N/A"

        if include_mcs:
            print(
                f"  {model:30s}  "
                f"P: SCRAM={p_scram:>12}  ZEBRA={p_zebra:>12}  {prob_status:16s}  "
                f"MCS(info): SCRAM={m_scram:>6}  ZEBRA={m_zebra:>6}"
            )
        else:
            print(
                f"  {model:30s}  "
                f"P: SCRAM={p_scram:>12}  ZEBRA={p_zebra:>12}  {prob_status}"
            )

        row = {
            "model":             model,
            "scram_probability": "" if scram_prob is None else f"{scram_prob:.6e}",
            "zebra_probability": "" if zebra_prob  is None else f"{zebra_prob:.6e}",
            "prob_rel_diff":     rel_diff,
            "prob_status":       prob_status,
        }
        if include_mcs:
            row["scram_mcs_count"] = "" if scram_mcs is None else str(scram_mcs)
            row["zebra_mcs_count"] = "" if zebra_mcs is None else str(zebra_mcs)
            row["mcs_note"]        = "ZTDD_FACTORIZATION_DIFFERENCE"
        rows.append(row)

    os.makedirs(os.path.dirname(os.path.abspath(output_csv)), exist_ok=True)
    fieldnames = ["model", "scram_probability", "zebra_probability", "prob_rel_diff", "prob_status"]
    if include_mcs:
        fieldnames += ["scram_mcs_count", "zebra_mcs_count", "mcs_note"]

    with open(output_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    return summary


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Compare SCRAM and ZEBRA top-event probabilities for a set of fault tree models. "
            "ZEBRA ZTDD MCS counts differ from BDD/ZBDD solvers by design (ZTDD factorization); "
            "MCS counts are reported as informational only, not as pass/fail."
        )
    )
    parser.add_argument("--scram-dir",   required=True,
                        help="Directory containing SCRAM XML report files")
    parser.add_argument("--zebra-dir",   required=True,
                        help="Directory containing ZEBRA stdout log files (.log)")
    parser.add_argument("--output",      required=True,
                        help="Output CSV comparison report path")
    parser.add_argument("--rel-tol",     type=float, default=1e-3,
                        help="Relative tolerance for probability match (default: 1e-3 = 0.1%%)")
    parser.add_argument("--prob-field",  choices=["bdd", "psum", "pmcub"], default="bdd",
                        help="ZEBRA log field to use: bdd=PROB, psum=P_SUM, pmcub=P_MCUB")

    args = parser.parse_args()

    field_label = {"bdd": "PROB", "psum": "P_SUM", "pmcub": "P_MCUB"}[args.prob_field]
    print("=== SCRAM vs ZEBRA: Probability Comparison ===")
    print(f"    ZEBRA field         : {field_label}")
    print(f"    Probability rel-tol : {args.rel_tol:.2g}")
    print()

    try:
        summary = compare_results(
            args.scram_dir, args.zebra_dir, args.output,
            args.rel_tol, args.prob_field,
        )
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"\n--- Summary ---")
    print(f"  Probability matched (within {args.rel_tol*100:.2g}%):  {summary['prob_matched']}")
    print(f"  Probability mismatched:                                {summary['prob_mismatched']}")
    print(f"  ZEBRA output missing (timeout or crash):               {summary['zebra_missing']}")
    print(f"  SCRAM parse error:                                     {summary['scram_error']}")
    print(f"\nReport written to: {args.output}")

    sys.exit(1 if summary["prob_mismatched"] > 0 else 0)


if __name__ == "__main__":
    main()
