import csv
import os
import sys
from lxml import etree


def _parse_scram_report(xml_path: str) -> tuple:
    """
    Stream-parse a SCRAM XML report and return (probability, mcs_count).

    Uses iterparse so only the <sum-of-products> start tag is read — the rest
    of the file (potentially millions of <product> elements) is never loaded
    into memory.  Both values come from attributes on that single element:
        probability="<float>"  products="<int>"
    Returns (None, None) if the file is missing or cannot be parsed.
    """
    if not os.path.exists(xml_path):
        return None, None
    try:
        prob = None
        mcs_count = None
        for _event, elem in etree.iterparse(xml_path, events=("start",), recover=True):
            if elem.tag == "sum-of-products":
                p = elem.get("probability")
                if p is not None:
                    prob = float(p)
                n = elem.get("products")
                if n is not None:
                    mcs_count = int(n)
                elem.clear()
                break
        return prob, mcs_count
    except Exception:
        return None, None


def parse_scram_probability(xml_path: str) -> float | None:
    prob, _ = _parse_scram_report(xml_path)
    return prob


def parse_xfta_probability(tsv_path: str) -> float | None:
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


def parse_scram_mcs_count(xml_path: str) -> int | None:
    _, mcs_count = _parse_scram_report(xml_path)
    return mcs_count


def parse_xfta_mcs_count(tsv_path: str, cutoff: float = 1e-12) -> int | None:
    if not os.path.exists(tsv_path):
        return None
    try:
        count = 0
        with open(tsv_path, encoding="utf-8") as f:
            for line in f:
                parts = line.rstrip("\n").split("\t")
                if not parts or not parts[0].strip():
                    continue
                try:
                    int(parts[0].strip())
                except ValueError:
                    continue
                if len(parts) >= 2:
                    try:
                        prob = float(parts[1].strip())
                        if prob >= cutoff:
                            count += 1
                    except ValueError:
                        count += 1
                else:
                    count += 1
        return count
    except Exception:
        pass
    return None


def parse_praxis_probability(xml_path: str) -> float | None:
    if not os.path.exists(xml_path):
        return None
    try:
        for _event, elem in etree.iterparse(xml_path, events=("end",), recover=True):
            if elem.tag == "top-event-probability":
                text = (elem.text or "").strip()
                if text:
                    return float(text)
                elem.clear()
        return None
    except Exception:
        return None


def parse_praxis_mcs_count(xml_path: str) -> int | None:
    if not os.path.exists(xml_path):
        return None
    try:
        for _event, elem in etree.iterparse(xml_path, events=("start",), recover=True):
            if elem.tag == "minimal-cut-sets":
                n = elem.get("count")
                if n is not None:
                    return int(n)
                elem.clear()
                break
        return None
    except Exception:
        return None


def compare_results(
    scram_output_dir: str,
    xfta_output_dir: str,
    output_csv: str,
    rel_tol: float = 1e-3,
    mcs_cutoff: float = 1e-12,
) -> dict:
    summary = {
        "prob_matched":    0,
        "prob_mismatched": 0,
        "mcs_matched":     0,
        "mcs_mismatched":  0,
        "xfta_skipped":    0,
        "scram_error":     0,
    }
    rows = []

    if not os.path.isdir(scram_output_dir):
        raise NotADirectoryError(f"SCRAM output directory not found: {scram_output_dir}")

    scram_files = sorted(
        f for f in os.listdir(scram_output_dir) if f.endswith(".xml")
    )

    for scram_fname in scram_files:
        model       = os.path.splitext(scram_fname)[0]
        scram_path  = os.path.join(scram_output_dir, scram_fname)
        xfta_prob_path = os.path.join(xfta_output_dir, f"{model}_prob.tsv")
        xfta_mcs_path  = os.path.join(xfta_output_dir, f"{model}_mcs.tsv")

        scram_prob, scram_mcs = _parse_scram_report(scram_path)
        xfta_prob  = parse_xfta_probability(xfta_prob_path)
        xfta_mcs   = parse_xfta_mcs_count(xfta_mcs_path, mcs_cutoff)

        # Probability comparison
        if scram_prob is None:
            prob_status = "SCRAM_ERROR"
            rel_diff = ""
            summary["scram_error"] += 1
        elif xfta_prob is None:
            prob_status = "XFTA_SKIPPED"
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
                prob_status = "OK"
                summary["prob_matched"] += 1
            else:
                prob_status = "MISMATCH"
                summary["prob_mismatched"] += 1

        # MCS count comparison
        if prob_status in ("SCRAM_ERROR", "XFTA_SKIPPED"):
            mcs_status = prob_status
            mcs_diff   = ""
        elif scram_mcs is None:
            mcs_status = "SCRAM_MCS_ERROR"
            mcs_diff   = ""
        elif xfta_mcs is None:
            mcs_status = "XFTA_MCS_MISSING"
            mcs_diff   = ""
        else:
            mcs_diff = str(xfta_mcs - scram_mcs)
            if scram_mcs == xfta_mcs:
                mcs_status = "OK"
                summary["mcs_matched"] += 1
            else:
                mcs_status = "MISMATCH"
                summary["mcs_mismatched"] += 1

        # Console output
        p_scram = f"{scram_prob:.6e}" if scram_prob is not None else "N/A"
        p_xfta  = f"{xfta_prob:.6e}"  if xfta_prob  is not None else "N/A"
        m_scram = str(scram_mcs)       if scram_mcs  is not None else "N/A"
        m_xfta  = str(xfta_mcs)        if xfta_mcs   is not None else "N/A"
        print(
            f"  {model:30s}  "
            f"P: SCRAM={p_scram:>12}  XFTA={p_xfta:>12}  {prob_status:16s}  "
            f"MCS: SCRAM={m_scram:>6}  XFTA={m_xfta:>6}  {mcs_status}"
        )

        rows.append({
            "model":             model,
            "scram_probability": "" if scram_prob is None else f"{scram_prob:.6e}",
            "xfta_probability":  "" if xfta_prob  is None else f"{xfta_prob:.6e}",
            "prob_rel_diff":     rel_diff,
            "prob_status":       prob_status,
            "scram_mcs_count":   "" if scram_mcs  is None else str(scram_mcs),
            "xfta_mcs_count":    "" if xfta_mcs   is None else str(xfta_mcs),
            "mcs_diff":          mcs_diff,
            "mcs_status":        mcs_status,
        })

    os.makedirs(os.path.dirname(os.path.abspath(output_csv)), exist_ok=True)
    with open(output_csv, "w", newline="", encoding="utf-8") as f:
        fieldnames = [
            "model",
            "scram_probability", "xfta_probability", "prob_rel_diff", "prob_status",
            "scram_mcs_count",   "xfta_mcs_count",   "mcs_diff",      "mcs_status",
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    return summary


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description=(
            "Compare SCRAM and XFTA top-event probabilities and minimal cut set "
            "counts for a set of fault tree models."
        )
    )
    parser.add_argument("--scram-dir",  required=True,
                        help="Directory containing SCRAM XML report files")
    parser.add_argument("--xfta-dir",   required=True,
                        help="Directory containing XFTA probability and MCS TSV files")
    parser.add_argument("--output",     required=True,
                        help="Output CSV comparison report path")
    parser.add_argument("--rel-tol",    type=float, default=1e-3,
                        help="Relative tolerance for probability match (default: 1e-3 = 0.1%%)")
    parser.add_argument("--mcs-cutoff", type=float, default=1e-12,
                        help="Probability cutoff applied to XFTA MCS count (default: 1e-12)")

    args = parser.parse_args()

    print("=== SCRAM vs XFTA: Probability & Minimal Cut Set Comparison ===")
    print(f"    Probability rel-tol : {args.rel_tol:.2g}")
    print(f"    MCS cutoff          : {args.mcs_cutoff:.2g}")
    print()
    try:
        summary = compare_results(
            args.scram_dir, args.xfta_dir, args.output,
            args.rel_tol, args.mcs_cutoff,
        )
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"\n--- Summary ---")
    print(f"  Probability matched (within {args.rel_tol*100:.2g}%):  {summary['prob_matched']}")
    print(f"  Probability mismatched:                                {summary['prob_mismatched']}")
    print(f"  MCS count matched:                                     {summary['mcs_matched']}")
    print(f"  MCS count mismatched:                                  {summary['mcs_mismatched']}")
    print(f"  XFTA skipped (incompatible model or timeout):          {summary['xfta_skipped']}")
    print(f"  SCRAM parse error:                                     {summary['scram_error']}")
    print(f"\nReport written to: {args.output}")

    sys.exit(1 if (summary["prob_mismatched"] > 0 or summary["mcs_mismatched"] > 0) else 0)


if __name__ == "__main__":
    main()
