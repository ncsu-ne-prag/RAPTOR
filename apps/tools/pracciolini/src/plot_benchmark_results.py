import argparse
import csv
import glob
import json
import os
from datetime import datetime

import plotly.graph_objects as go
import plotly.io as pio


TIMEOUT_S  = 30.0
TIMEOUT_MS = TIMEOUT_S * 1000

TIMING_CONFIGS = [
    ("SCRAM BDD",            "scram_bdd_*_results.json",         "file",   ".xml",   "SCRAM"),
    ("SCRAM ZBDD REA",       "scram_zbdd_rea_*_results.json",    "file",   ".xml",   "SCRAM"),
    ("SCRAM ZBDD MCUB",      "scram_zbdd_mcub_*_results.json",   "file",   ".xml",   "SCRAM"),
    ("XFTA BDD",             "xfta_bdd_*_results.json",          "script", ".xfta",  "XFTA"),
    ("XFTA BDT REA",         "xfta_bdt_rea_*_results.json",      "script", ".xfta",  "XFTA"),
    ("XFTA BDT MCUB",        "xfta_bdt_mcub_*_results.json",     "script", ".xfta",  "XFTA"),
    ("XFTA BDT PUB",         "xfta_bdt_pub_*_results.json",      "script", ".xfta",  "XFTA"),
    ("XFTA ZBDD REA",        "xfta_zbdd_rea_*_results.json",     "script", ".xfta",  "XFTA"),
    ("XFTA ZBDD MCUB",       "xfta_zbdd_mcub_*_results.json",    "script", ".xfta",  "XFTA"),
    ("XFTA ZBDD PUB",        "xfta_zbdd_pub_*_results.json",     "script", ".xfta",  "XFTA"),
    ("FTREX BDD",            "ftrex_bdd_*_results.json",         "file",   ".ftp",   "FTREX"),
    ("FTREX ZBDD",           "ftrex_zbdd_*_results.json",        "file",   ".ftp",   "FTREX"),
    ("PRAXIS BDD",           "praxis_bdd_*_results.json",        "file",   ".xml",   "PRAXIS"),
    ("PRAXIS ZBDD REA",      "praxis_zbdd_rea_*_results.json",   "file",   ".xml",   "PRAXIS"),
    ("PRAXIS ZBDD MCUB",     "praxis_zbdd_mcub_*_results.json",  "file",   ".xml",   "PRAXIS"),
    ("ZEBRA ZTDD BDD",       "zebra_ztdd_bdd_*_results.json",    "file",   ".ftp",   "ZEBRA"),
    ("ZEBRA ZTDD MCS",       "zebra_ztdd_mcs_*_results.json",    "file",   ".ftp",   "ZEBRA"),
    ("SAPHSOLVE MOCUS+MCUB", "saphsolve_*_results.json",         "file",   ".JSInp", "SAPHSOLVE"),
]

PROB_SOURCES = [
    ("SCRAM BDD",            "exp1_bdd_comparison_*.csv",            "scram_probability",     True),
    ("SCRAM ZBDD REA",       "exp2_zbdd_rea_comparison_*.csv",       "scram_probability",     False),
    ("SCRAM ZBDD MCUB",      "exp3_zbdd_mcub_comparison_*.csv",      "scram_probability",     False),
    ("XFTA BDD",             "exp1_bdd_comparison_*.csv",            "xfta_probability",      False),
    ("XFTA ZBDD REA",        "exp2_zbdd_rea_comparison_*.csv",       "xfta_probability",      False),
    ("XFTA ZBDD MCUB",       "exp3_zbdd_mcub_comparison_*.csv",      "xfta_probability",      False),
    ("PRAXIS BDD",           "exp4_bdd_scram_praxis_*.csv",          "praxis_probability",    False),
    ("PRAXIS ZBDD REA",      "exp5_zbdd_rea_scram_praxis_*.csv",     "praxis_probability",    False),
    ("PRAXIS ZBDD MCUB",     "exp6_zbdd_mcub_scram_praxis_*.csv",    "praxis_probability",    False),
    ("SAPHSOLVE MOCUS+MCUB", "exp8_zbdd_mcub_scram_saphsolve_*.csv", "saphsolve_probability", False),
]

MCS_SOURCES = [
    ("SCRAM ZBDD REA",       "exp2_zbdd_rea_comparison_*.csv",       "scram_mcs_count",       True),
    ("SCRAM ZBDD MCUB",      "exp3_zbdd_mcub_comparison_*.csv",      "scram_mcs_count",       False),
    ("XFTA ZBDD REA",        "exp2_zbdd_rea_comparison_*.csv",       "xfta_mcs_count",        False),
    ("XFTA ZBDD MCUB",       "exp3_zbdd_mcub_comparison_*.csv",      "xfta_mcs_count",        False),
    ("PRAXIS ZBDD REA",      "exp5_zbdd_rea_scram_praxis_*.csv",     "praxis_mcs_count",      False),
    ("PRAXIS ZBDD MCUB",     "exp6_zbdd_mcub_scram_praxis_*.csv",    "praxis_mcs_count",      False),
    ("SAPHSOLVE MOCUS+MCUB", "exp8_zbdd_mcub_scram_saphsolve_*.csv", "saphsolve_mcs_count",   False),
]

SOLVER_PALETTE = {
    "SCRAM":     "#4361EE",
    "XFTA":      "#3A86FF",
    "FTREX":     "#FB8500",
    "PRAXIS":    "#8338EC",
    "ZEBRA":     "#E63946",
    "SAPHSOLVE": "#2DC653",
}

TIMEOUT_COLOR = "#D62828"

_FONT = dict(
    family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
    size=12,
)

CSS = """
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    background: #f0f2f5;
    color: #1a1a2e;
    line-height: 1.5;
}
header {
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 55%, #0f3460 100%);
    color: #fff;
    padding: 2rem 3rem 1.8rem;
}
header h1 { font-size: 1.75rem; font-weight: 700; letter-spacing: -0.02em; margin-bottom: .4rem; }
header p  { opacity: .6; font-size: .875rem; }
main { max-width: 1400px; margin: 0 auto; padding: 2rem 2rem 3rem; }
section {
    background: #fff;
    border-radius: 10px;
    padding: 1.6rem 1.8rem 1.8rem;
    margin-bottom: 2rem;
    box-shadow: 0 1px 4px rgba(0,0,0,.08);
}
h2 {
    font-size: 1.1rem;
    font-weight: 700;
    color: #1a1a2e;
    margin-bottom: 1.1rem;
    padding-bottom: .5rem;
    border-bottom: 2px solid #f0f2f5;
}
.ref-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1.4rem;
    margin-bottom: 1.4rem;
}
.ref-block h3 {
    font-size: .76rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: .06em;
    color: #6c757d;
    margin-bottom: .5rem;
}
table {
    width: 100%;
    border-collapse: collapse;
    font-size: .82rem;
}
th {
    text-align: left;
    padding: .32rem .6rem;
    background: #f8f9fa;
    border-bottom: 2px solid #dee2e6;
    font-weight: 600;
    color: #495057;
    white-space: nowrap;
}
td {
    padding: .28rem .6rem;
    border-bottom: 1px solid #f0f2f5;
    white-space: nowrap;
}
tr.ref-row td { font-weight: 700; background: #eef2ff; }
.note { font-size: .72rem; color: #6c757d; margin-top: .4rem; }
.solver-dot {
    display: inline-block;
    width: 8px; height: 8px;
    border-radius: 50%;
    margin-right: 5px;
    vertical-align: middle;
}
.chart-wrap { width: 100%; overflow-x: auto; }
.chart-label {
    font-size: .76rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: .06em;
    color: #6c757d;
    margin-bottom: .4rem;
}
.timeout-banner {
    background: #fff5f5;
    border: 1px solid #fca5a5;
    border-left: 4px solid #D62828;
    border-radius: 6px;
    padding: .6rem .9rem;
    margin-bottom: 1.2rem;
    font-size: .82rem;
}
.timeout-banner strong { color: #D62828; }
.timeout-tag {
    display: inline-block;
    background: #fca5a5;
    color: #7f1d1d;
    border-radius: 3px;
    padding: .05rem .35rem;
    font-size: .75rem;
    font-weight: 600;
    margin: .15rem .15rem 0 0;
}
"""


def _find_file(results_dir, pattern):
    matches = sorted(glob.glob(os.path.join(results_dir, pattern)))
    return matches[-1] if matches else None


def _model_name(path, ext):
    base = os.path.basename(path)
    return base[: -len(ext)] if base.lower().endswith(ext.lower()) else os.path.splitext(base)[0]


def load_timing(results_dir, pattern, param_key, ext):
    path = _find_file(results_dir, pattern)
    if not path:
        return {}
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        return {}
    out = {}
    for entry in data.get("results", []):
        params = entry.get("parameters", {})
        raw = params.get(param_key) or next(iter(params.values()), "")
        if not raw:
            continue
        model = _model_name(raw, ext)
        out[model] = {
            "mean":      entry.get("mean", TIMEOUT_S),
            "timed_out": 124 in entry.get("exit_codes", []),
        }
    return out


def load_csv_column(results_dir, pattern, col):
    path = _find_file(results_dir, pattern)
    if not path:
        return {}
    out = {}
    try:
        with open(path, encoding="utf-8", newline="") as f:
            for row in csv.DictReader(f):
                m = row.get("model", "")
                v = row.get(col, "")
                if m and v:
                    try:
                        out[m] = float(v)
                    except ValueError:
                        pass
    except Exception:
        pass
    return out


def _solver_color(label):
    for solver, color in SOLVER_PALETTE.items():
        if solver in label:
            return color
    return "#999999"


def _rgba(hex_color, alpha=0.85):
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f"rgba({r},{g},{b},{alpha})"


def fig_timing(model, timing_all):
    labels, times, colors, texts = [], [], [], []
    for label, *_, solver in TIMING_CONFIGS:
        t = timing_all.get(label, {}).get(model)
        if t is None:
            continue
        mean_ms   = t["mean"] * 1000
        timed_out = t["timed_out"]
        labels.append(label)
        times.append(min(mean_ms, TIMEOUT_MS))
        colors.append(_rgba(TIMEOUT_COLOR, 0.85) if timed_out else _rgba(_solver_color(label)))
        texts.append("TIMEOUT" if timed_out else f"{mean_ms:.1f} ms")

    if not labels:
        return None

    fig = go.Figure(go.Bar(
        x=labels,
        y=times,
        marker=dict(color=colors, line=dict(width=0)),
        text=texts,
        textposition="outside",
        textfont=dict(size=9),
        hovertemplate="<b>%{x}</b><br>%{y:.2f} ms<extra></extra>",
    ))

    fig.add_shape(
        type="line",
        x0=-0.5, x1=len(labels) - 0.5,
        y0=TIMEOUT_MS, y1=TIMEOUT_MS,
        line=dict(color=TIMEOUT_COLOR, width=1.5, dash="dash"),
        layer="above",
    )
    fig.add_annotation(
        x=len(labels) - 1,
        y=TIMEOUT_MS,
        text=f"Timeout ({int(TIMEOUT_S)}s)",
        showarrow=False,
        yanchor="bottom",
        xanchor="right",
        font=dict(size=9, color=TIMEOUT_COLOR),
        bgcolor="rgba(255,255,255,0.75)",
    )

    fig.update_layout(
        template="plotly_white",
        height=420,
        yaxis=dict(
            title="Execution time (ms)",
            gridcolor="#dee2e6",
            type="log",
        ),
        xaxis=dict(tickangle=-38, tickfont=dict(size=9)),
        margin=dict(l=70, r=10, t=20, b=130),
        font=_FONT,
        showlegend=False,
        plot_bgcolor="white",
        paper_bgcolor="white",
    )
    return fig


def _prob_table(model, prob_all):
    rows = ""
    for label, _, _, is_ref in PROB_SOURCES:
        val = prob_all.get(label, {}).get(model)
        if val is None:
            continue
        color = _solver_color(label)
        ref_class = ' class="ref-row"' if is_ref else ""
        star = " *" if is_ref else ""
        rows += (
            f'<tr{ref_class}>'
            f'<td><span class="solver-dot" style="background:{color}"></span>{label}{star}</td>'
            f'<td style="font-family:monospace;text-align:right">{val:.6e}</td>'
            f'</tr>'
        )
    if not rows:
        return '<p class="note">No data available</p>'
    return (
        '<table>'
        '<thead><tr><th>Solver / Algorithm</th><th style="text-align:right">Probability</th></tr></thead>'
        f'<tbody>{rows}</tbody>'
        '</table>'
        '<p class="note">* Reference (SCRAM BDD — exact)</p>'
    )


def _mcs_table(model, mcs_all):
    rows = ""
    for label, _, _, is_ref in MCS_SOURCES:
        val = mcs_all.get(label, {}).get(model)
        if val is None:
            continue
        color = _solver_color(label)
        ref_class = ' class="ref-row"' if is_ref else ""
        star = " *" if is_ref else ""
        rows += (
            f'<tr{ref_class}>'
            f'<td><span class="solver-dot" style="background:{color}"></span>{label}{star}</td>'
            f'<td style="font-family:monospace;text-align:right">{int(val):,}</td>'
            f'</tr>'
        )
    if not rows:
        return '<p class="note">No data available</p>'
    return (
        '<table>'
        '<thead><tr><th>Solver / Algorithm</th><th style="text-align:right">Cut Sets</th></tr></thead>'
        f'<tbody>{rows}</tbody>'
        '</table>'
        '<p class="note">* Reference (SCRAM ZBDD REA)</p>'
    )


def _timeout_banner(model, timing_all):
    timed_out = [
        label
        for label, *_ in TIMING_CONFIGS
        if timing_all.get(label, {}).get(model, {}).get("timed_out", False)
    ]
    if not timed_out:
        return ""
    tags = "".join(f'<span class="timeout-tag">{t}</span>' for t in timed_out)
    n = len(timed_out)
    return (
        '<div class="timeout-banner">'
        f'<strong>Timed out ({n} algorithm{"s" if n > 1 else ""})</strong> '
        f'&mdash; exceeded {int(TIMEOUT_S)}s limit: {tags}'
        '</div>'
    )


def _to_div(fig, first=False):
    return pio.to_html(
        fig,
        full_html=False,
        include_plotlyjs=True if first else False,
        config={"displayModeBar": True, "responsive": True},
    )


def build_html(now, model_label, body_html):
    date_str  = now.strftime("%Y-%m-%d")
    date_long = now.strftime("%B %d, %Y at %H:%M")
    return (
        '<!DOCTYPE html>\n<html lang="en">\n<head>\n'
        '<meta charset="UTF-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        f'<title>RAPTOR Benchmark - {model_label} - {date_str}</title>\n'
        f'<style>\n{CSS}\n</style>\n'
        '</head>\n<body>\n'
        '<header>\n'
        '<h1>RAPTOR Fault Tree Benchmark</h1>\n'
        f'<p>Dataset: <strong>{model_label}</strong> &nbsp;&middot;&nbsp; Generated {date_long}'
        f' &nbsp;&middot;&nbsp; Timeout: {int(TIMEOUT_S)}s per run</p>\n'
        '</header>\n'
        f'<main>\n{body_html}</main>\n'
        '</body>\n</html>\n'
    )


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--results-dir", required=True)
    ap.add_argument("--output",      required=True)
    ap.add_argument("--model",       default="aralia")
    args = ap.parse_args()

    timing_all = {
        label: load_timing(args.results_dir, pattern, param_key, ext)
        for label, pattern, param_key, ext, _ in TIMING_CONFIGS
    }
    prob_all = {
        label: load_csv_column(args.results_dir, pattern, col)
        for label, pattern, col, _ in PROB_SOURCES
    }
    mcs_all = {
        label: load_csv_column(args.results_dir, pattern, col)
        for label, pattern, col, _ in MCS_SOURCES
    }

    all_models = sorted({m for t in timing_all.values() for m in t})
    print(f"  Models found: {len(all_models)}")

    sections = []
    first_fig = True

    for model in all_models:
        fig = fig_timing(model, timing_all)
        if fig is None:
            continue

        banner    = _timeout_banner(model, timing_all)
        chart_div = _to_div(fig, first=first_fig)
        first_fig = False

        sections.append(
            f'<section id="{model}">\n'
            f'<h2>{model}</h2>\n'
            + banner +
            '<div class="ref-grid">\n'
            '<div class="ref-block"><h3>Top Event Probability</h3>'
            + _prob_table(model, prob_all) +
            '</div>\n'
            '<div class="ref-block"><h3>Minimal Cut Sets</h3>'
            + _mcs_table(model, mcs_all) +
            '</div>\n'
            '</div>\n'
            '<p class="chart-label">Execution Time</p>\n'
            '<div class="chart-wrap">' + chart_div + '</div>\n'
            '</section>\n'
        )

    now  = datetime.now()
    html = build_html(now, args.model, ''.join(sections))

    os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"  Report -> {args.output}")


if __name__ == "__main__":
    main()
