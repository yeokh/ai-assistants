import csv, glob, html, math, os
import plotext as plt

HERE = os.path.dirname(os.path.abspath(__file__))
COLORS = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b"]


def load(path):
    with open(path, newline="") as f:
        rows = list(csv.DictReader(f))
    num, cat = [], []
    for c in rows[0]:
        vals = [r[c] for r in rows]
        try:
            [float(v) for v in vals if v != ""]
            num.append(c)
        except ValueError:
            cat.append(c)
    cat = [c for c in cat if len({r[c] for r in rows}) <= 12]
    return rows, num, cat


def col(rows, c, group=None, g=None):
    return [float(r[c]) for r in rows if r[c] != "" and (group is None or r[group] == g)]


def corr(x, y):
    n = len(x); mx, my = sum(x) / n, sum(y) / n
    sx = math.sqrt(sum((a - mx) ** 2 for a in x)); sy = math.sqrt(sum((b - my) ** 2 for b in y))
    return sum((a - mx) * (b - my) for a, b in zip(x, y)) / (sx * sy) if sx and sy else 0


def best_pair(rows, num):
    good = [r for r in rows if all(r[c] != "" for c in num)]
    best = max(((abs(corr(col(good, a), col(good, b))), a, b) for i, a in enumerate(num) for b in num[i + 1:]), default=None)
    return best[1:] if best else None


def svg_hist(vals, title, bins=15):
    lo, hi = min(vals), max(vals); w = (hi - lo) / bins or 1
    cnt = [0] * bins
    for v in vals: cnt[min(int((v - lo) / w), bins - 1)] += 1
    m = max(cnt); s = f'<svg viewBox="0 0 400 220" width="400"><text x="200" y="14" text-anchor="middle" font-size="13">{html.escape(title)}</text>'
    for i, c in enumerate(cnt):
        h = 160 * c / m
        s += f'<rect x="{20 + i * 24}" y="{190 - h:.1f}" width="22" height="{h:.1f}" fill="{COLORS[0]}"><title>{lo + i * w:.2f}: {c}</title></rect>'
    return s + f'<text x="20" y="210" font-size="11">{lo:.2f}</text><text x="380" y="210" font-size="11" text-anchor="end">{hi:.2f}</text></svg>'


def svg_scatter(rows, a, b, grp):
    xs, ys = col(rows, a), col(rows, b)
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    groups = sorted({r[grp] for r in rows}) if grp else [None]
    s = f'<svg viewBox="0 0 440 300" width="440"><text x="220" y="14" text-anchor="middle" font-size="13">{html.escape(b)} vs {html.escape(a)}</text>'
    for i, g in enumerate(groups):
        for r in rows:
            if r[a] == "" or r[b] == "" or (grp and r[grp] != g): continue
            px = 40 + 380 * (float(r[a]) - x0) / ((x1 - x0) or 1); py = 260 - 230 * (float(r[b]) - y0) / ((y1 - y0) or 1)
            s += f'<circle cx="{px:.1f}" cy="{py:.1f}" r="3" fill="{COLORS[i % 6]}" opacity=".7"/>'
        if g: s += f'<circle cx="{60 + i * 110}" cy="284" r="4" fill="{COLORS[i % 6]}"/><text x="{68 + i * 110}" y="288" font-size="11">{html.escape(g)}</text>'
    return s + f'<text x="40" y="276" font-size="10">{x0:.2f}</text><text x="420" y="276" font-size="10" text-anchor="end">{x1:.2f}</text></svg>'


def svg_bars(labels, vals, title):
    m = max(vals) or 1
    s = f'<svg viewBox="0 0 400 {40 + 28 * len(vals)}" width="400"><text x="200" y="14" text-anchor="middle" font-size="13">{html.escape(title)}</text>'
    for i, (l, v) in enumerate(zip(labels, vals)):
        s += f'<text x="90" y="{47 + i * 28}" text-anchor="end" font-size="11">{html.escape(l)}</text><rect x="95" y="{32 + i * 28}" width="{270 * v / m:.1f}" height="20" fill="{COLORS[i % 6]}"/><text x="{100 + 270 * v / m:.1f}" y="{47 + i * 28}" font-size="11">{v:.2f}</text>'
    return s + "</svg>"


def process(path):
    name = os.path.basename(path)
    rows, num, cat = load(path)
    grp = cat[0] if cat else None
    svgs, kinds = [], []
    print(f"\n===== {name}: {len(rows)} rows =====")
    for c in num[:4]:  # histograms
        v = col(rows, c)
        plt.clear_figure(); plt.hist(v, 15); plt.title(f"Histogram: {c}"); plt.plotsize(70, 15); plt.show()
        svgs.append(svg_hist(v, f"Histogram: {c}"))
    if "Histogram" not in kinds and num: kinds.append("histogram")
    pair = best_pair(rows, num) if len(num) > 1 else None
    if pair:
        a, b = pair
        plt.clear_figure(); plt.title(f"Scatter: {b} vs {a}"); plt.plotsize(70, 20)
        for g in (sorted({r[grp] for r in rows}) if grp else [None]):
            sub = [r for r in rows if r[a] != "" and r[b] != "" and (grp is None or r[grp] == g)]
            plt.scatter([float(r[a]) for r in sub], [float(r[b]) for r in sub], label=g)
        plt.show()
        svgs.append(svg_scatter(rows, a, b, grp)); kinds.append("scatter")
    if grp and num:
        gs = sorted({r[grp] for r in rows})
        cnt = [sum(r[grp] == g for r in rows) for g in gs]
        plt.clear_figure(); plt.bar(gs, cnt); plt.title(f"Count by {grp}"); plt.plotsize(70, 15); plt.show()
        svgs.append(svg_bars(gs, cnt, f"Count by {grp}"))
        mv = [sum(col(rows, num[0], grp, g)) / len(col(rows, num[0], grp, g)) for g in gs]
        plt.clear_figure(); plt.bar(gs, mv); plt.title(f"Mean {num[0]} by {grp}"); plt.plotsize(70, 15); plt.show()
        svgs.append(svg_bars(gs, mv, f"Mean {num[0]} by {grp}")); kinds.append("bar")
    out = os.path.join(HERE, os.path.splitext(name)[0] + "_charts.html")
    with open(out, "w") as f:
        f.write(f"<!doctype html><meta charset=utf-8><title>{html.escape(name)}</title><body style='font-family:sans-serif'><h1>{html.escape(name)}</h1><div style='display:flex;flex-wrap:wrap;gap:20px'>"
                + "".join(svgs) + "</div></body>")
    return kinds


if __name__ == "__main__":
    with open(os.path.join(HERE, "execution_log.txt"), "w") as log:
        for p in sorted(glob.glob(os.path.join(HERE, "*.csv"))):
            try:
                k = process(p)
                log.write(f"{os.path.basename(p)} | charts: {', '.join(k)} (terminal + HTML) | Success\n")
            except Exception as e:
                log.write(f"{os.path.basename(p)} | Failed: {e}\n")
