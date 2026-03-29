import csv
import os
import sys
from lxml import etree


def parse_scram_probability(xml_path: str) -> float | None:
    """
    Extract the top-event probability from a SCRAM XML report file.

    SCRAM writes the probability as an attribute on <sum-of-products>:
        <sum-of-products name="r1" probability="0.00118191" ...>

    Returns None if the file cannot be parsed or the attribute is absent.
    """
    if not os.path.exists(xml_path):
        return None
    try:
        tree = etree.parse(xml_path)
        sop = tree.find(".//sum-of-products")
        if sop is not None:
            prob = sop.get("probability")
            if prob is not None:
                return float(prob)
    except Exception:
        pass
    return None


def parse_xfta_probability(tsv_path: str) -> float | None:
    """
    Extract the probability from an XFTA TSV output file.

    XFTA writes probability output in the format:
        variable    <name>
        source-handle    BDT
        quantification-method    PUB
        time    Q
        0    <probability>

    The line starting with '0<TAB>' holds the time-0 probability.
    Returns None if the file cannot be parsed.
    """
    if not os.path.exists(tsv_path):
        return None
    try:
        with open(tsv_path, encoding="utf-8") as f:
            for line in f:
                parts = line.rstrip("\n").split("\t")
                if len(parts) >= 2 and parts[0].strip() == "0":
                    return float(parts[1].strip())
    except Exception:
        pass
    return None


def compare_probabilities(
    scram_output_dir: str,
    xfta_output_dir: str,
    output_csv: str,
    rel_tol: float = 1e-3,
) -> dict:
    """
    Compare SCRAM and XFTA top-event probabilities for each model.

    For each SCRAM XML report in scram_output_dir, look for a matching XFTA
    probability TSV in xfta_output_dir (named <model>_prob.tsv).

    Args:
        scram_output_dir: Directory containing SCRAM report XML files.
        xfta_output_dir:  Directory containing XFTA probability TSV files.
        output_csv:       Path to write the comparison CSV report.
        rel_tol:          Relative tolerance for declaring a match (default 0.1%).

    Returns:
        Summary dict with keys: matched, mismatched, xfta_skipped, scram_error.
    """
    summary = {"matched": 0, "mismatched": 0, "xfta_skipped": 0, "scram_error": 0}
    rows = []

    if not os.path.isdir(scram_output_dir):
        raise NotADirectoryError(f"SCRAM output directory not found: {scram_output_dir}")

    scram_files = sorted(
        f for f in os.listdir(scram_output_dir) if f.endswith(".xml")
    )

    for scram_fname in scram_files:
        model = os.path.splitext(scram_fname)[0]
        scram_path = os.path.join(scram_output_dir, scram_fname)
        xfta_path = os.path.join(xfta_output_dir, f"{model}_prob.tsv")

        scram_prob = parse_scram_probability(scram_path)
        xfta_prob = parse_xfta_probability(xfta_path)

        if scram_prob is None:
            status = "SCRAM_ERROR"
            rel_diff = ""
            summary["scram_error"] += 1
        elif xfta_prob is None:
            status = "XFTA_SKIPPED"
            rel_diff = ""
            summary["xfta_skipped"] += 1
        else:
            if scram_prob == 0.0 and xfta_prob == 0.0:
                rel_diff_val = 0.0
            elif scram_prob == 0.0:
                rel_diff_val = float("inf")
            else:
                rel_diff_val = abs(scram_prob - xfta_prob) / scram_prob

            rel_diff = f"{rel_diff_val:.6e}"
            if rel_diff_val <= rel_tol:
                status = "OK"
                summary["matched"] += 1
            else:
                status = "MISMATCH"
                summary["mismatched"] += 1

        rows.append({
            "model":            model,
            "scram_probability": "" if scram_prob is None else f"{scram_prob:.6e}",
            "xfta_probability":  "" if xfta_prob  is None else f"{xfta_prob:.6e}",
            "relative_diff":     rel_diff,
            "status":            status,
        })

        print(
            f"  {model:30s}  SCRAM={scram_prob or 'N/A':>12}  "
            f"XFTA={xfta_prob or 'N/A':>12}  {status}"
        )

    os.makedirs(os.path.dirname(os.path.abspath(output_csv)), exist_ok=True)
    with open(output_csv, "w", newline="", encoding="utf-8") as f:
        fieldnames = ["model", "scram_probability", "xfta_probability",
                      "relative_diff", "status"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    return summary


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Compare SCRAM and XFTA top-event probabilities for a set of models."
    )
    parser.add_argument("--scram-dir", required=True,
                        help="Directory containing SCRAM XML report files")
    parser.add_argument("--xfta-dir",  required=True,
                        help="Directory containing XFTA probability TSV files")
    parser.add_argument("--output",    required=True,
                        help="Output CSV comparison report path")
    parser.add_argument("--rel-tol",   type=float, default=1e-3,
                        help="Relative tolerance for match (default: 1e-3 = 0.1%%)")

    args = parser.parse_args()

    print("=== Probability Comparison: SCRAM vs XFTA ===")
    try:
        summary = compare_probabilities(
            args.scram_dir, args.xfta_dir, args.output, args.rel_tol
        )
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"\n--- Summary ---")
    print(f"  Matched (within {args.rel_tol*100:.2g}%): {summary['matched']}")
    print(f"  Mismatched:                              {summary['mismatched']}")
    print(f"  XFTA skipped (incompatible model):       {summary['xfta_skipped']}")
    print(f"  SCRAM parse error:                       {summary['scram_error']}")
    print(f"\nReport written to: {args.output}")

    sys.exit(1 if summary["mismatched"] > 0 else 0)


if __name__ == "__main__":
    main()
