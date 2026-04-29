import argparse, csv, glob, json, os
from datetime import datetime
import plotly.graph_objects as go

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
    ("FTREX BDD",            "exp9a_bdd_scram_ftrex_*.csv",          "ftrex_probability",     False),
    ("FTREX ZBDD REA",       "exp9b_zbdd_rea_scram_ftrex_*.csv",     "ftrex_probability",     False),
    ("FTREX ZBDD MCUB",      "exp9c_zbdd_mcub_scram_ftrex_*.csv",    "ftrex_probability",     False),
    ("PRAXIS BDD",           "exp4_bdd_scram_praxis_*.csv",          "praxis_probability",    False),
    ("PRAXIS ZBDD REA",      "exp5_zbdd_rea_scram_praxis_*.csv",     "praxis_probability",    False),
    ("PRAXIS ZBDD MCUB",     "exp6_zbdd_mcub_scram_praxis_*.csv",    "praxis_probability",    False),
    ("ZEBRA ZTDD BDD",       "exp7a_bdd_scram_zebra_*.csv",          "zebra_probability",     False),
    ("ZEBRA ZTDD REA",       "exp7b_zbdd_rea_scram_zebra_*.csv",     "zebra_probability",     False),
    ("ZEBRA ZTDD MCUB",      "exp7c_zbdd_mcub_scram_zebra_*.csv",    "zebra_probability",     False),
    ("SAPHSOLVE MOCUS+MCUB", "exp8_zbdd_mcub_scram_saphsolve_*.csv", "saphsolve_probability", False),
]

MCS_SOURCES = [
    ("SCRAM ZBDD REA",       "exp2_zbdd_rea_comparison_*.csv",       "scram_mcs_count",       True),
    ("SCRAM ZBDD MCUB",      "exp3_zbdd_mcub_comparison_*.csv",      "scram_mcs_count",       False),
    ("XFTA ZBDD REA",        "exp2_zbdd_rea_comparison_*.csv",       "xfta_mcs_count",        False),
    ("XFTA ZBDD MCUB",       "exp3_zbdd_mcub_comparison_*.csv",      "xfta_mcs_count",        False),
    ("FTREX ZBDD REA",       "exp9b_zbdd_rea_scram_ftrex_*.csv",     "ftrex_mcs_count",       False),
    ("FTREX ZBDD MCUB",      "exp9c_zbdd_mcub_scram_ftrex_*.csv",    "ftrex_mcs_count",       False),
    ("PRAXIS ZBDD REA",      "exp5_zbdd_rea_scram_praxis_*.csv",     "praxis_mcs_count",      False),
    ("PRAXIS ZBDD MCUB",     "exp6_zbdd_mcub_scram_praxis_*.csv",    "praxis_mcs_count",      False),
    ("ZEBRA ZTDD REA",       "exp7b_zbdd_rea_scram_zebra_*.csv",     "zebra_mcs_count",       False),
    ("ZEBRA ZTDD MCUB",      "exp7c_zbdd_mcub_scram_zebra_*.csv",    "zebra_mcs_count",       False),
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


def _table_rows_meta():
    seen = {}
    order = []
    for label, _, _, is_ref in PROB_SOURCES:
        if label not in seen:
            seen[label] = [is_ref, False]
            order.append(label)
        elif is_ref:
            seen[label][0] = True
    for label, _, _, is_ref in MCS_SOURCES:
        if label not in seen:
            seen[label] = [False, is_ref]
            order.append(label)
        else:
            if is_ref:
                seen[label][1] = True
    return [(lbl, seen[lbl][0], seen[lbl][1]) for lbl in order]


TABLE_META = _table_rows_meta()


def _find_file(results_dir, pattern):
    matches = sorted(glob.glob(os.path.join(results_dir, pattern)))
    return matches[-1] if matches else None


def _model_name(path, ext):
    base = os.path.basename(path)
    return base[:-len(ext)] if base.lower().endswith(ext.lower()) else os.path.splitext(base)[0]


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


def _fig_spec(model, timing_all):
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
        x=labels, y=times,
        marker=dict(color=colors, line=dict(width=0)),
        text=texts, textposition="outside", textfont=dict(size=9),
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
        x=len(labels) - 1, y=TIMEOUT_MS,
        text=f"Timeout ({int(TIMEOUT_S)}s)",
        showarrow=False, yanchor="bottom", xanchor="right",
        font=dict(size=9, color=TIMEOUT_COLOR),
        bgcolor="rgba(255,255,255,0.75)",
    )
    fig.update_layout(
        template="plotly_white", height=420,
        yaxis=dict(title="Execution time (ms)", gridcolor="#dee2e6", type="log"),
        xaxis=dict(tickangle=-38, tickfont=dict(size=9)),
        margin=dict(l=70, r=10, t=20, b=130),
        font=_FONT, showlegend=False,
        plot_bgcolor="white", paper_bgcolor="white",
    )
    return fig.to_json().replace("</", "<\\/")


def _combined_table(model, prob_all, mcs_all):
    rows = ""
    for label, is_prob_ref, is_mcs_ref in TABLE_META:
        prob_val = prob_all.get(label, {}).get(model)
        mcs_val  = mcs_all.get(label, {}).get(model)
        if prob_val is None and mcs_val is None:
            continue
        color     = _solver_color(label)
        is_ref    = is_prob_ref or is_mcs_ref
        ref_class = ' class="ref-row"' if is_ref else ""
        note      = (" †" if is_prob_ref else "") + (" ‡" if is_mcs_ref else "")
        prob_cell = (
            f'<td style="font-family:monospace;text-align:right">{prob_val:.6e}</td>'
            if prob_val is not None else
            '<td style="text-align:right;color:#aaa">—</td>'
        )
        mcs_cell = (
            f'<td style="font-family:monospace;text-align:right">{int(mcs_val):,}</td>'
            if mcs_val is not None else
            '<td style="text-align:right;color:#aaa">—</td>'
        )
        rows += (
            f'<tr{ref_class}>'
            f'<td><span class="solver-dot" style="background:{color}"></span>{label}{note}</td>'
            + prob_cell + mcs_cell +
            '</tr>'
        )
    if not rows:
        return '<p class="note">No data available</p>'
    return (
        '<table>'
        '<thead><tr>'
        '<th>Tool - Algorithm</th>'
        '<th style="text-align:right">Top Event Probability</th>'
        '<th style="text-align:right">Minimal Cut Sets</th>'
        '</tr></thead>'
        f'<tbody>{rows}</tbody>'
        '</table>'
        '<p class="note">† Probability reference (SCRAM BDD) ‡ MCS reference (SCRAM ZBDD REA)</p>'
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
        f'<strong>Timed out ({n} algorithm{"s" if n > 1 else ""})</strong>'
        f' &mdash; exceeded {int(TIMEOUT_S)}s limit: {tags}'
        '</div>'
    )


def _fragment_html(model, prob_all, mcs_all, timing_all):
    banner    = _timeout_banner(model, timing_all)
    table     = _combined_table(model, prob_all, mcs_all)
    chart_spec = _fig_spec(model, timing_all)
    chart_part = ""
    if chart_spec:
        chart_part = (
            '<p class="chart-label">Execution Time</p>'
            f'<div class="chart-container" id="chart-{model}"></div>'
            f'<script type="application/json" class="chart-spec">{chart_spec}</script>'
        )
    return (
        f'<div class="frag-section"><h2>{model}</h2>'
        + banner + table + chart_part +
        '</div>'
    )


CSS = """
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;background:#f0f2f5;color:#1a1a2e;line-height:1.5;display:flex;flex-direction:column;height:100vh;overflow:hidden}
header{background:linear-gradient(135deg,#1a1a2e 0%,#16213e 55%,#0f3460 100%);color:#fff;padding:1.1rem 2rem;flex-shrink:0}
header h1{font-size:1.35rem;font-weight:700;letter-spacing:-.02em;margin-bottom:.2rem}
header p{opacity:.6;font-size:.8rem}
.layout{display:flex;flex:1;overflow:hidden}
nav{width:210px;background:#1a1a2e;overflow-y:auto;flex-shrink:0;padding:.5rem 0}
.nav-label{font-size:.68rem;font-weight:600;text-transform:uppercase;letter-spacing:.08em;color:rgba(255,255,255,.3);padding:.5rem 1.2rem .2rem}
.nav-item{display:block;padding:.38rem 1.2rem;color:rgba(255,255,255,.6);font-size:.82rem;text-decoration:none;cursor:pointer;border-left:3px solid transparent;transition:color .1s,background .1s,border-color .1s;user-select:none}
.nav-item:hover{color:#fff;background:rgba(255,255,255,.07)}
.nav-item.active{color:#fff;border-left-color:#4361EE;background:rgba(67,97,238,.18);font-weight:600}
#content{flex:1;overflow-y:auto;padding:2rem}
.frag-section{background:#fff;border-radius:10px;padding:1.6rem 1.8rem 1.8rem;box-shadow:0 1px 4px rgba(0,0,0,.08);max-width:1160px}
h2{font-size:1.1rem;font-weight:700;color:#1a1a2e;margin-bottom:1rem;padding-bottom:.5rem;border-bottom:2px solid #f0f2f5}
table{width:100%;border-collapse:collapse;font-size:.82rem;margin-bottom:1.1rem}
th{text-align:left;padding:.32rem .6rem;background:#f8f9fa;border-bottom:2px solid #dee2e6;font-weight:600;color:#495057;white-space:nowrap}
td{padding:.28rem .6rem;border-bottom:1px solid #f0f2f5;white-space:nowrap}
tr.ref-row td{font-weight:700;background:#eef2ff}
.note{font-size:.72rem;color:#6c757d;margin-top:.3rem;margin-bottom:1.2rem}
.solver-dot{display:inline-block;width:8px;height:8px;border-radius:50%;margin-right:5px;vertical-align:middle}
.chart-label{font-size:.76rem;font-weight:600;text-transform:uppercase;letter-spacing:.06em;color:#6c757d;margin-bottom:.4rem}
.chart-container{width:100%;min-height:420px}
.timeout-banner{background:#fff5f5;border:1px solid #fca5a5;border-left:4px solid #D62828;border-radius:6px;padding:.6rem .9rem;margin-bottom:1.2rem;font-size:.82rem}
.timeout-banner strong{color:#D62828}
.timeout-tag{display:inline-block;background:#fca5a5;color:#7f1d1d;border-radius:3px;padding:.05rem .35rem;font-size:.75rem;font-weight:600;margin:.15rem .15rem 0 0}
"""

JS = """
function loadModel(name) {
    var tmpl = document.getElementById('frag-' + name);
    if (!tmpl) return;
    var content = document.getElementById('content');
    content.innerHTML = '';
    content.appendChild(tmpl.content.cloneNode(true));
    document.querySelectorAll('.nav-item').forEach(function(el) { el.classList.remove('active'); });
    var navEl = document.querySelector('.nav-item[data-model="' + name + '"]');
    if (navEl) navEl.classList.add('active');
    content.querySelectorAll('.chart-spec').forEach(function(el) {
        var fig = JSON.parse(el.textContent);
        Plotly.react(el.previousElementSibling, fig.data, fig.layout, {responsive: true, displayModeBar: true});
    });
    htmx.trigger(content, 'htmx:afterSwap', {target: content});
}
document.addEventListener('DOMContentLoaded', function() {
    var first = document.querySelector('.nav-item[data-model]');
    if (first) loadModel(first.dataset.model);
});
"""


def build_html(now, model_label, models, fragments):
    date_str  = now.strftime("%Y-%m-%d")
    date_long = now.strftime("%B %d, %Y at %H:%M")

    nav_items = "".join(
        '<a class="nav-item" data-model="' + m + '" onclick="loadModel(\'' + m + '\')">' + m + '</a>'
        for m in models
    )
    template_tags = "".join(
        '<template id="frag-' + m + '">' + fragments[m] + '</template>'
        for m in models
    )

    return (
        '<!DOCTYPE html>\n<html lang="en">\n<head>\n'
        '<meta charset="UTF-8">\n'
        '<meta name="viewport" content="width=device-width,initial-scale=1">\n'
        '<title>RAPTOR Benchmark - ' + model_label + ' - ' + date_str + '</title>\n'
        '<script src="https://unpkg.com/htmx.org@2.0.4/dist/htmx.min.js"></script>\n'
        '<script src="https://cdn.plot.ly/plotly-2.35.2.min.js" charset="utf-8"></script>\n'
        '<style>\n' + CSS + '\n</style>\n'
        '</head>\n<body>\n'
        '<header>\n'
        '<h1>RAPTOR Fault Tree Benchmark</h1>\n'
        '<p>Dataset: <strong>' + model_label + '</strong>'
        ' &nbsp;&middot;&nbsp; Generated ' + date_long +
        ' &nbsp;&middot;&nbsp; Timeout: ' + str(int(TIMEOUT_S)) + 's per run'
        ' &nbsp;&middot;&nbsp; ' + str(len(models)) + ' models</p>\n'
        '</header>\n'
        '<div class="layout">\n'
        '<nav>\n<div class="nav-label">Models</div>\n' + nav_items + '\n</nav>\n'
        '<div id="content"></div>\n'
        '</div>\n'
        + template_tags + '\n'
        '<script>\n' + JS + '\n</script>\n'
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

    fragments = {}
    for model in all_models:
        spec = _fig_spec(model, timing_all)
        if spec is None:
            continue
        fragments[model] = _fragment_html(model, prob_all, mcs_all, timing_all)

    models = [m for m in all_models if m in fragments]
    now  = datetime.now()
    html = build_html(now, args.model, models, fragments)

    os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"  Report -> {args.output}")


if __name__ == "__main__":
    main()
