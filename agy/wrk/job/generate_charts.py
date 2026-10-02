"""
generate_charts.py
Reads iris.csv using the built-in csv library (no pandas),
generates terminal charts with plotext (v6), and saves standalone HTML charts.
"""

import csv
import sys
import os
import collections

# ── plotext ────────────────────────────────────────────────────────────────────
try:
    import plotext as plt
except ImportError:
    print("plotext not found – install it with:  python3 -m pip install plotext")
    sys.exit(1)

# ── paths ──────────────────────────────────────────────────────────────────────
CSV_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "iris.csv")
HTML_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "iris_charts.html")

NUMERIC_COLS = ["sepal_length", "sepal_width", "petal_length", "petal_width"]
SPECIES_COL  = "species"


def load_csv(path):
    rows = []
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if not any(row.values()):     # skip blank trailing rows
                continue
            rows.append(row)
    return rows


def column_values(rows, col, cast=float):
    return [cast(r[col]) for r in rows if r[col].strip()]


def species_groups(rows):
    groups = collections.OrderedDict()
    for r in rows:
        sp = r[SPECIES_COL]
        groups.setdefault(sp, []).append(r)
    return groups


# ── terminal charts (plotext v6 API) ───────────────────────────────────────────

def _fig():
    """Return the master plotext figure, cleared and ready."""
    fig = plt.figure
    fig.clear()
    return fig


def terminal_histogram(rows, col, bins=12):
    """Overlapping histograms of a numeric column, one per species."""
    groups = species_groups(rows)
    fig = _fig()
    fig.title(f"Histogram – {col} by species")
    for sp, sp_rows in groups.items():
        vals = column_values(sp_rows, col)
        sig = fig.hist(vals, bins=bins)
        fig.draw(sig)
        sig.label(sp)
    fig.label(col, axis="x")
    fig.label("Count", axis="y")
    fig.legend()
    fig.show()


def terminal_scatter(rows, col_x, col_y):
    """Scatter plot of two numeric columns, coloured by species."""
    groups = species_groups(rows)
    fig = _fig()
    fig.title(f"Scatter – {col_x} vs {col_y}")
    for sp, sp_rows in groups.items():
        xs = column_values(sp_rows, col_x)
        ys = column_values(sp_rows, col_y)
        sig = fig.signal(xs, ys, marker="dot")
        fig.draw(sig)
        sig.label(sp)
    fig.label(col_x, axis="x")
    fig.label(col_y, axis="y")
    fig.legend()
    fig.show()


def terminal_bar_species_mean(rows):
    """Grouped bar chart: mean of each numeric feature per species."""
    groups = species_groups(rows)
    species_list = list(groups.keys())
    fig = _fig()
    fig.title("Mean Feature Values per Species")
    for col in NUMERIC_COLS:
        means = [
            sum(column_values(groups[sp], col)) / len(groups[sp])
            for sp in species_list
        ]
        sig = fig.bar(species_list, means)
        fig.draw(sig)
        sig.label(col)
    fig.label("Species", axis="x")
    fig.label("Mean (cm)", axis="y")
    fig.legend()
    fig.show()


# ── HTML chart generation (hand-rolled SVG, no extra deps) ─────────────────────

def _html_color(idx):
    palette = ["#e6194b", "#3cb44b", "#4363d8", "#f58231", "#911eb4"]
    return palette[idx % len(palette)]


def _bins(values, n_bins=20):
    lo, hi = min(values), max(values)
    width = (hi - lo) / n_bins if hi != lo else 1
    counts = [0] * n_bins
    for v in values:
        b = min(int((v - lo) / width), n_bins - 1)
        counts[b] += 1
    edges = [lo + i * width for i in range(n_bins + 1)]
    return edges, counts


def _legend_html(series):
    items = "".join(
        f'<span style="display:inline-flex;align-items:center;margin-right:16px;">'
        f'<span style="width:14px;height:14px;background:{s["color"]};'
        f'display:inline-block;margin-right:4px;border-radius:2px;"></span>'
        f'{s["label"]}</span>'
        for s in series
    )
    return f'<div style="text-align:center;margin:4px 0 8px;">{items}</div>'


def _svg_wrap(content, w, h):
    return (
        f'<svg viewBox="0 0 {w} {h}" width="{w}" height="{h}" '
        f'xmlns="http://www.w3.org/2000/svg">{content}</svg>'
    )


def _axes_svg(PAD, IW, IH, W, H, xlabel, ylabel, title):
    out  = f'<line x1="{PAD}" y1="{PAD}" x2="{PAD}" y2="{PAD+IH}" stroke="#888" stroke-width="1"/>'
    out += f'<line x1="{PAD}" y1="{PAD+IH}" x2="{PAD+IW}" y2="{PAD+IH}" stroke="#888" stroke-width="1"/>'
    out += (f'<text x="{W//2}" y="{H-4}" text-anchor="middle" '
            f'font-size="12" fill="#555">{xlabel}</text>')
    out += (f'<text x="12" y="{H//2}" text-anchor="middle" font-size="12" fill="#555" '
            f'transform="rotate(-90,12,{H//2})">{ylabel}</text>')
    out += (f'<text x="{W//2}" y="16" text-anchor="middle" font-size="14" '
            f'font-weight="bold" fill="#333">{title}</text>')
    return out


def html_histogram(rows, col):
    groups = species_groups(rows)
    series = []
    for idx, (sp, sp_rows) in enumerate(groups.items()):
        vals = column_values(sp_rows, col)
        edges, counts = _bins(vals)
        centres = [(edges[i] + edges[i+1]) / 2 for i in range(len(counts))]
        series.append({"label": sp, "x": centres, "y": counts, "color": _html_color(idx)})

    title = f"Histogram – {col}"
    W, H, PAD = 640, 400, 55
    IW, IH = W - 2*PAD, H - 2*PAD
    all_x = [v for s in series for v in s["x"]]
    all_y = [v for s in series for v in s["y"]]
    x0, x1 = min(all_x), max(all_x); xr = x1 - x0 or 1
    y1_max = max(all_y) or 1

    def px(v): return PAD + (v - x0) / xr * IW
    def py(v): return PAD + IH - v / y1_max * IH

    n_series = len(series)
    # approximate bar half-width in data units
    bin_w_data = (series[0]["x"][1] - series[0]["x"][0]) if len(series[0]["x"]) > 1 else 0.5
    bar_half = bin_w_data * 0.4 / n_series

    bars = ""
    for si, s in enumerate(series):
        offset = (si - (n_series - 1) / 2) * bin_w_data * 0.35
        for xi, yi in zip(s["x"], s["y"]):
            bx = px(xi + offset) - px(0) + PAD  # translate
            bx = PAD + (xi + offset - x0) / xr * IW
            bw = max(1, IW * bin_w_data * 0.35 / xr)
            bh = IH * yi / y1_max
            bars += (f'<rect x="{bx:.1f}" y="{py(yi):.1f}" '
                     f'width="{bw:.1f}" height="{bh:.1f}" '
                     f'fill="{s["color"]}" opacity="0.75"/>')

    axes = _axes_svg(PAD, IW, IH, W, H, col, "Count", title)
    svg = _svg_wrap(axes + bars, W, H)
    return f'<div class="chart-block"><h3>{title}</h3>{_legend_html(series)}{svg}</div>'


def html_scatter(rows, col_x, col_y):
    groups = species_groups(rows)
    series = [{"label": sp, "x": column_values(sp_rows, col_x),
               "y": column_values(sp_rows, col_y), "color": _html_color(idx)}
              for idx, (sp, sp_rows) in enumerate(groups.items())]

    title = f"Scatter – {col_x} vs {col_y}"
    W, H, PAD = 600, 400, 55
    IW, IH = W - 2*PAD, H - 2*PAD
    all_x = [v for s in series for v in s["x"]]
    all_y = [v for s in series for v in s["y"]]
    x0, x1 = min(all_x), max(all_x); xr = x1 - x0 or 1
    y0, y1 = min(all_y), max(all_y); yr = y1 - y0 or 1

    def px(v): return PAD + (v - x0) / xr * IW
    def py(v): return PAD + IH - (v - y0) / yr * IH

    dots = "".join(
        f'<circle cx="{px(xi):.1f}" cy="{py(yi):.1f}" r="4" '
        f'fill="{s["color"]}" opacity="0.75"/>'
        for s in series for xi, yi in zip(s["x"], s["y"])
    )
    axes = _axes_svg(PAD, IW, IH, W, H, col_x, col_y, title)
    svg = _svg_wrap(axes + dots, W, H)
    return f'<div class="chart-block"><h3>{title}</h3>{_legend_html(series)}{svg}</div>'


def html_species_mean_bar(rows):
    groups = species_groups(rows)
    species_list = list(groups.keys())
    series = [
        {"label": col,
         "x": species_list,
         "y": [sum(column_values(groups[sp], col)) / len(groups[sp]) for sp in species_list],
         "color": _html_color(idx)}
        for idx, col in enumerate(NUMERIC_COLS)
    ]

    title = "Mean Feature Values per Species"
    W, H, PAD = 660, 430, 60
    IW, IH = W - 2*PAD, H - 2*PAD - 20   # extra bottom for labels
    all_y = [v for s in series for v in s["y"]]
    y_max = max(all_y) or 1

    def py(v): return PAD + IH - v / y_max * IH

    n_cat, n_s = len(species_list), len(series)
    grp_w = IW / n_cat
    bar_w = max(1, grp_w / n_s - 3)

    bars, cat_labels = "", ""
    for si, s in enumerate(series):
        for ci, (cat, yi) in enumerate(zip(s["x"], s["y"])):
            bx = PAD + ci * grp_w + si * bar_w + 2
            bh = IH * yi / y_max
            bars += (f'<rect x="{bx:.1f}" y="{py(yi):.1f}" '
                     f'width="{bar_w:.1f}" height="{bh:.1f}" '
                     f'fill="{s["color"]}" opacity="0.85"/>')

    for ci, cat in enumerate(species_list):
        cx = PAD + (ci + 0.5) * grp_w
        cat_labels += (f'<text x="{cx:.1f}" y="{PAD+IH+16}" '
                       f'text-anchor="middle" font-size="11" fill="#555">{cat}</text>')

    axes = _axes_svg(PAD, IW, IH, W, H, "Species", "Mean (cm)", title)
    svg = _svg_wrap(axes + bars + cat_labels, W, H)
    return f'<div class="chart-block"><h3>{title}</h3>{_legend_html(series)}{svg}</div>'


# ── main ────────────────────────────────────────────────────────────────────────

def main():
    print(f"\n{'='*60}")
    print(f"Processing: {CSV_PATH}")
    print(f"{'='*60}\n")

    rows = load_csv(CSV_PATH)
    print(f"Loaded {len(rows)} rows.\n")

    # ── terminal charts ──────────────────────────────────────────────────────
    print("── Terminal charts ─────────────────────────────────────────\n")

    print("[1/4] Histogram: sepal_length by species")
    terminal_histogram(rows, "sepal_length")

    print("[2/4] Histogram: petal_length by species")
    terminal_histogram(rows, "petal_length")

    print("[3/4] Scatter: sepal_length vs sepal_width")
    terminal_scatter(rows, "sepal_length", "sepal_width")

    print("[4/4] Bar: mean feature values per species")
    terminal_bar_species_mean(rows)

    # ── HTML charts ──────────────────────────────────────────────────────────
    print("\n── Generating HTML charts ──────────────────────────────────\n")

    chart_types = [
        ("Histogram", "sepal_length by species"),
        ("Histogram", "petal_length by species"),
        ("Scatter",   "sepal_length vs sepal_width"),
        ("Scatter",   "petal_length vs petal_width"),
        ("Grouped Bar", "mean feature values per species"),
    ]

    html_sections = [
        html_histogram(rows, "sepal_length"),
        html_histogram(rows, "petal_length"),
        html_scatter(rows,   "sepal_length", "sepal_width"),
        html_scatter(rows,   "petal_length", "petal_width"),
        html_species_mean_bar(rows),
    ]

    html_doc = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Iris Dataset Charts</title>
<style>
  body {{ font-family: sans-serif; max-width: 900px; margin: 0 auto; padding: 24px; background:#fafafa; }}
  h1   {{ text-align:center; color:#333; }}
  .chart-block {{ background:#fff; border:1px solid #ddd; border-radius:8px;
                  padding:16px; margin-bottom:24px; box-shadow:0 1px 4px rgba(0,0,0,.08); }}
  .chart-block h3 {{ margin:0 0 8px; color:#444; font-size:15px; }}
</style>
</head>
<body>
<h1>Iris Dataset – Statistical Charts</h1>
{sections}
</body>
</html>""".format(sections="\n".join(html_sections))

    with open(HTML_PATH, "w", encoding="utf-8") as f:
        f.write(html_doc)

    print(f"HTML report saved → {HTML_PATH}")
    print("\nDone ✓")
    return chart_types


if __name__ == "__main__":
    main()
