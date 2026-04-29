import argparse
import csv
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from openpsa_s2ml_TEP_verifier import _parse_scram_report
from parse_jscut import parse_jscut_mcs_count, parse_jscut_probability


def compare_results(
    scram_output_dir: str,
    saphsolve_output_dir: str,
    output_csv: str,
    rel_tol: float,
) -> dict:
    summary = {
        "prob_matched":    0,
        "prob_mismatched": 0,
        "mcs_matched":     0,
        "mcs_mismatched":  0,
        "saphsolve_missing": 0,
        "scram_error":     0,
    }
    rows = []

    if not os.path.isdir(scram_output_dir):
        raise NotADirectoryError(f"SCRAM output directory not found: {scram_output_dir}")

    scram_files = sorted(f for f in os.listdir(scram_output_dir) if f.endswith(".xml"))

    for scram_fname in scram_files:
        model      = os.path.splitext(scram_fname)[0]
        scram_path = os.path.join(scram_output_dir, scram_fname)
        jscut_path = os.path.join(saphsolve_output_dir, f"{model}.JSCut")

        scram_prob, scram_mcs = _parse_scram_report(scram_path)
        saph_prob  = parse_jscut_probability(jscut_path)
        saph_mcs   = parse_jscut_mcs_count(jscut_path)

        if scram_prob is None:
            prob_status = "SCRAM_ERROR"
            mcs_status  = "SCRAM_ERROR"
            rel_diff    = ""
            summary["scram_error"] += 1
        elif saph_prob is None:
            prob_status = "SAPHSOLVE_MISSING"
            mcs_status  = "SAPHSOLVE_MISSING"
            rel_diff    = ""
            summary["saphsolve_missing"] += 1
        else:
            if scram_prob == 0.0 and saph_prob == 0.0:
                rel_diff_val = 0.0
            elif scram_prob == 0.0:
                rel_diff_val = float("inf")
            else:
                rel_diff_val = abs(scram_prob - saph_prob) / scram_prob
            rel_diff = f"{rel_diff_val:.6e}"
            if rel_diff_val <= rel_tol:
                prob_status = "OK"
                summary["prob_matched"] += 1
            else:
                prob_status = "MISMATCH"
                summary["prob_mismatched"] += 1

            if scram_mcs is not None and saph_mcs is not None:
                if scram_mcs == saph_mcs:
                    mcs_status = "OK"
                    summary["mcs_matched"] += 1
                else:
                    mcs_status = "MISMATCH"
                    summary["mcs_mismatched"] += 1
            else:
                mcs_status = "N/A"

        p_scram = f"{scram_prob:.6e}" if scram_prob is not None else "N/A"
        p_saph  = f"{saph_prob:.6e}"  if saph_prob  is not None else "N/A"
        m_scram = str(scram_mcs)      if scram_mcs  is not None else "N/A"
        m_saph  = str(saph_mcs)       if saph_mcs   is not None else "N/A"

        print(
            f"  {model:30s}  "
            f"P: SCRAM={p_scram:>12}  SAPH={p_saph:>12}  {prob_status:16s}  "
            f"MCS: SCRAM={m_scram:>6}  SAPH={m_saph:>6}  {mcs_status}"
        )

        rows.append({
            "model":                model,
            "scram_probability":    "" if scram_prob is None else f"{scram_prob:.6e}",
            "saphsolve_probability": "" if saph_prob  is None else f"{saph_prob:.6e}",
            "prob_rel_diff":        rel_diff,
            "prob_status":          prob_status,
            "scram_mcs_count":      "" if scram_mcs is None else str(scram_mcs),
            "saphsolve_mcs_count":  "" if saph_mcs  is None else str(saph_mcs),
            "mcs_status":           mcs_status,
        })

    os.makedirs(os.path.dirname(os.path.abspath(output_csv)), exist_ok=True)
    fieldnames = [
        "model", "scram_probability", "saphsolve_probability",
        "prob_rel_diff", "prob_status",
        "scram_mcs_count", "saphsolve_mcs_count", "mcs_status",
    ]
    with open(output_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    return summary


def main():
    parser = argparse.ArgumentParser(
        description="Compare SCRAM and SAPHSOLVE MOCUS+MCUB results for a set of fault tree models."
    )
    parser.add_argument("--scram-dir",      required=True,
                        help="Directory containing SCRAM XML report files")
    parser.add_argument("--saphsolve-dir",  required=True,
                        help="Directory containing SAPHSOLVE .JSCut output files")
    parser.add_argument("--output",         required=True,
                        help="Output CSV comparison report path")
    parser.add_argument("--rel-tol",        type=float, default=1e-3,
                        help="Relative tolerance for probability match (default: 1e-3 = 0.1%%)")

    args = parser.parse_args()

    print("=== SCRAM vs SAPHSOLVE: MOCUS+MCUB Comparison ===")
    print(f"    Probability rel-tol : {args.rel_tol:.2g}")
    print()

    try:
        summary = compare_results(
            args.scram_dir, args.saphsolve_dir, args.output, args.rel_tol
        )
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"\n--- Summary ---")
    print(f"  Probability matched (within {args.rel_tol*100:.2g}%):  {summary['prob_matched']}")
    print(f"  Probability mismatched:                                {summary['prob_mismatched']}")
    print(f"  MCS count matched:                                     {summary['mcs_matched']}")
    print(f"  MCS count mismatched:                                  {summary['mcs_mismatched']}")
    print(f"  SAPHSOLVE output missing (skipped or timeout):         {summary['saphsolve_missing']}")
    print(f"  SCRAM parse error:                                     {summary['scram_error']}")
    print(f"\nReport written to: {args.output}")

    sys.exit(1 if (summary["prob_mismatched"] > 0 or summary["mcs_mismatched"] > 0) else 0)


if __name__ == "__main__":
    main()
