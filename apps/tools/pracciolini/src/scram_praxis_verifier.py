import argparse
import csv
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from openpsa_s2ml_TEP_verifier import _parse_scram_report, parse_praxis_probability, parse_praxis_mcs_count


def compare_results(
    scram_output_dir: str,
    praxis_output_dir: str,
    output_csv: str,
    rel_tol: float = 1e-3,
    check_mcs: bool = False,
) -> dict:
    summary = {
        "prob_matched":    0,
        "prob_mismatched": 0,
        "mcs_matched":     0,
        "mcs_mismatched":  0,
        "praxis_missing":  0,
        "scram_error":     0,
    }
    rows = []

    if not os.path.isdir(scram_output_dir):
        raise NotADirectoryError(f"SCRAM output directory not found: {scram_output_dir}")

    scram_files = sorted(
        f for f in os.listdir(scram_output_dir) if f.endswith(".xml")
    )

    for scram_fname in scram_files:
        model        = os.path.splitext(scram_fname)[0]
        scram_path   = os.path.join(scram_output_dir, scram_fname)
        praxis_path  = os.path.join(praxis_output_dir, scram_fname)

        scram_prob, scram_mcs = _parse_scram_report(scram_path)
        praxis_prob  = parse_praxis_probability(praxis_path)
        praxis_mcs   = parse_praxis_mcs_count(praxis_path) if check_mcs else None

        if scram_prob is None:
            prob_status  = "SCRAM_ERROR"
            rel_diff     = ""
            summary["scram_error"] += 1
        elif praxis_prob is None:
            prob_status  = "PRAXIS_MISSING"
            rel_diff     = ""
            summary["praxis_missing"] += 1
        else:
            if scram_prob == 0.0 and praxis_prob == 0.0:
                rel_diff_val = 0.0
            elif scram_prob == 0.0:
                rel_diff_val = float("inf")
            else:
                rel_diff_val = abs(scram_prob - praxis_prob) / scram_prob
            rel_diff = f"{rel_diff_val:.6e}"
            if rel_diff_val <= rel_tol:
                prob_status = "OK"
                summary["prob_matched"] += 1
            else:
                prob_status = "MISMATCH"
                summary["prob_mismatched"] += 1

        if not check_mcs:
            mcs_status = "N/A"
            mcs_diff   = ""
        elif prob_status in ("SCRAM_ERROR", "PRAXIS_MISSING"):
            mcs_status = prob_status
            mcs_diff   = ""
        elif scram_mcs is None:
            mcs_status = "SCRAM_MCS_MISSING"
            mcs_diff   = ""
        elif praxis_mcs is None:
            mcs_status = "PRAXIS_MCS_MISSING"
            mcs_diff   = ""
        else:
            mcs_diff = str(praxis_mcs - scram_mcs)
            if scram_mcs == praxis_mcs:
                mcs_status = "OK"
                summary["mcs_matched"] += 1
            else:
                mcs_status = "MISMATCH"
                summary["mcs_mismatched"] += 1

        p_scram  = f"{scram_prob:.6e}"  if scram_prob  is not None else "N/A"
        p_praxis = f"{praxis_prob:.6e}" if praxis_prob  is not None else "N/A"
        m_scram  = str(scram_mcs)       if scram_mcs   is not None else "N/A"
        m_praxis = str(praxis_mcs)      if praxis_mcs  is not None else "N/A"
        print(
            f"  {model:30s}  "
            f"P: SCRAM={p_scram:>12}  PRAXIS={p_praxis:>12}  {prob_status:16s}  "
            f"MCS: SCRAM={m_scram:>6}  PRAXIS={m_praxis:>6}  {mcs_status}"
        )

        rows.append({
            "model":              model,
            "scram_probability":  "" if scram_prob  is None else f"{scram_prob:.6e}",
            "praxis_probability": "" if praxis_prob  is None else f"{praxis_prob:.6e}",
            "prob_rel_diff":      rel_diff,
            "prob_status":        prob_status,
            "scram_mcs_count":    "" if scram_mcs   is None else str(scram_mcs),
            "praxis_mcs_count":   "" if praxis_mcs  is None else str(praxis_mcs),
            "mcs_diff":           mcs_diff,
            "mcs_status":         mcs_status,
        })

    os.makedirs(os.path.dirname(os.path.abspath(output_csv)), exist_ok=True)
    with open(output_csv, "w", newline="", encoding="utf-8") as f:
        fieldnames = [
            "model",
            "scram_probability", "praxis_probability", "prob_rel_diff", "prob_status",
            "scram_mcs_count",   "praxis_mcs_count",   "mcs_diff",      "mcs_status",
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    return summary


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Compare SCRAM and PRAXIS top-event probabilities and minimal cut set "
            "counts for a set of fault tree models."
        )
    )
    parser.add_argument("--scram-dir",   required=True,
                        help="Directory containing SCRAM XML report files")
    parser.add_argument("--praxis-dir",  required=True,
                        help="Directory containing PRAXIS XML report files")
    parser.add_argument("--output",      required=True,
                        help="Output CSV comparison report path")
    parser.add_argument("--rel-tol",     type=float, default=1e-3,
                        help="Relative tolerance for probability match (default: 1e-3 = 0.1%%)")
    parser.add_argument("--check-mcs",   action="store_true",
                        help="Also compare MCS counts (use for ZBDD runs, not BDD)")

    args = parser.parse_args()

    print("=== SCRAM vs PRAXIS: Probability & Minimal Cut Set Comparison ===")
    print(f"    Probability rel-tol : {args.rel_tol:.2g}")
    print(f"    MCS comparison      : {'enabled' if args.check_mcs else 'disabled (BDD mode)'}")
    print()
    try:
        summary = compare_results(
            args.scram_dir, args.praxis_dir, args.output,
            args.rel_tol, args.check_mcs,
        )
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"\n--- Summary ---")
    print(f"  Probability matched (within {args.rel_tol*100:.2g}%):  {summary['prob_matched']}")
    print(f"  Probability mismatched:                                {summary['prob_mismatched']}")
    if args.check_mcs:
        print(f"  MCS count matched:                                     {summary['mcs_matched']}")
        print(f"  MCS count mismatched:                                  {summary['mcs_mismatched']}")
    print(f"  PRAXIS output missing (timeout or crash):              {summary['praxis_missing']}")
    print(f"  SCRAM parse error:                                     {summary['scram_error']}")
    print(f"\nReport written to: {args.output}")

    sys.exit(1 if (summary["prob_mismatched"] > 0 or summary["mcs_mismatched"] > 0) else 0)


if __name__ == "__main__":
    main()
