#!/usr/bin/env python3
"""Generate Figure 4 from the paper tables.

Data sources:
- Table I: image-based averages for Adroit, DexArt, and RoboTwin.
- Table II: cross-domain RoboTwin 2.0 average for ManiFlow and Ours.
- Table VIII: SO101 real-robot trials. The DP+RCAF bar is only reported
  for SO101, so the Real Robot group uses the SO101 block for a fair
  DP / DP+RCAF / Ours comparison.

The script prefers matplotlib. If matplotlib is not installed, it writes the
same chart as SVG and uses the project's existing sharp package to render PNG.
"""

from __future__ import annotations

import html
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PNG_OUT = ROOT / "public" / "image" / "final_chart.png"
SVG_OUT = ROOT / "public" / "image" / "final_chart.svg"

WIDTH = 3362
HEIGHT = 1928
MAX_Y = 90.0

METHODS = [
    {
        "key": "dp",
        "label": "Diffusion Policy (NFE=10)",
        "color": "#46a6e8",
        "edge": "#46a6e8",
    },
    {
        "key": "fm",
        "label": "Flow Matching (NFE=10)",
        "color": "#2fa99a",
        "edge": "#2fa99a",
    },
    {
        "key": "maniflow",
        "label": "ManiFlow (NFE=10)",
        "color": "#ffaa24",
        "edge": "#ffaa24",
    },
    {
        "key": "rcaf",
        "label": "pi0 / DP+RCAF",
        "color": "#ab47bc",
        "edge": "#ab47bc",
    },
    {
        "key": "ours",
        "label": "Ours (NFE=1)",
        "color": "#ed3434",
        "edge": "#b81f1f",
    },
]


SO101_TRIALS = [
    {"task": "Pick & Place (Random, 30 demos)", "dp": (1, 20), "rcaf": (3, 20), "ours": (5, 20)},
    {"task": "Pick & Place (Random, 60 demos)", "dp": (4, 20), "rcaf": (7, 20), "ours": (10, 20)},
    {"task": "Pick & Place (Regular)", "dp": (12, 20), "rcaf": (20, 20), "ours": (20, 20)},
    {"task": "Stand Bottle (Regular)", "dp": (2, 20), "rcaf": (14, 20), "ours": (18, 20)},
    {"task": "Drop Pen (Regular)", "dp": (8, 20), "rcaf": (8, 20), "ours": (12, 20)},
]


def trial_average(method: str) -> float:
    rates = [100.0 * row[method][0] / row[method][1] for row in SO101_TRIALS]
    return round(sum(rates) / len(rates), 1)


BENCHMARKS = [
    {
        "label": "Adroit",
        "values": {"dp": 38.1, "fm": 39.0, "maniflow": 74.3, "ours": 75.6},
        "compare_key": "maniflow",
    },
    {
        "label": "DexArt",
        "values": {"dp": 53.6, "fm": 53.3, "maniflow": 56.3, "ours": 61.3},
        "compare_key": "maniflow",
    },
    {
        "label": "RoboTwin",
        "values": {"dp": 28.8, "fm": 27.1, "maniflow": 46.1, "ours": 58.9},
        "compare_key": "maniflow",
    },
    {
        "label": "RoboTwin 2.0",
        "values": {"maniflow": 28.8, "ours": 34.5},
        "compare_key": "maniflow",
    },
    {
        "label": "Real Robot",
        "values": {
            "dp": trial_average("dp"),
            "rcaf": trial_average("rcaf"),
            "ours": trial_average("ours"),
        },
        "compare_key": "dp",
    },
]


def present_methods(benchmark: dict) -> list[dict]:
    values = benchmark["values"]
    return [method for method in METHODS if method["key"] in values]


def draw_with_matplotlib() -> None:
    import matplotlib.pyplot as plt
    from matplotlib.patches import Patch

    dpi = 200
    fig, ax = plt.subplots(figsize=(WIDTH / dpi, HEIGHT / dpi), dpi=dpi)
    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")

    bar_width = 0.155
    step = 0.17
    x_positions = list(range(len(BENCHMARKS)))

    for index, benchmark in enumerate(BENCHMARKS):
        methods = present_methods(benchmark)
        offset_start = -step * (len(methods) - 1) / 2.0

        for method_index, method in enumerate(methods):
            key = method["key"]
            value = benchmark["values"][key]
            x = x_positions[index] + offset_start + method_index * step
            is_ours = key == "ours"

            ax.bar(
                x,
                value,
                width=bar_width,
                color=method["color"],
                edgecolor=method["edge"] if is_ours else "none",
                linewidth=2.0 if is_ours else 0.0,
                zorder=3,
            )

            if is_ours:
                ax.text(
                    x,
                    value + 1.2,
                    f"{value:.1f}",
                    ha="center",
                    va="bottom",
                    fontsize=16,
                    fontweight="bold",
                    color=method["color"],
                )

                base = benchmark["values"][benchmark["compare_key"]]
                delta = value - base
                ax.text(
                    x,
                    value + 6.2,
                    f"+{delta:.1f}%",
                    ha="center",
                    va="bottom",
                    fontsize=13,
                    fontweight="bold",
                    color="white",
                    bbox={
                        "boxstyle": "round,pad=0.35,rounding_size=0.15",
                        "facecolor": method["color"],
                        "edgecolor": "none",
                    },
                )

    ax.set_title(
        "Performance Comparison Across Benchmarks",
        fontsize=24,
        fontweight="bold",
        pad=20,
    )
    ax.set_ylabel("Average Success Rate (%)", fontsize=20, fontweight="bold")
    ax.set_ylim(0, MAX_Y)
    ax.set_yticks(range(0, int(MAX_Y) + 1, 10))
    ax.set_xticks(x_positions)
    ax.set_xticklabels([b["label"] for b in BENCHMARKS], fontsize=20, fontweight="bold")
    ax.tick_params(axis="y", labelsize=15)
    ax.tick_params(axis="x", width=1.5, length=5)
    ax.grid(axis="y", linestyle="--", linewidth=1.0, color="#d7d7d7", zorder=0)

    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)
    ax.spines["left"].set_color("#999999")
    ax.spines["bottom"].set_color("#999999")

    legend_handles = [
        Patch(facecolor=method["color"], edgecolor="none", label=method["label"]) for method in METHODS
    ]
    ax.legend(
        handles=legend_handles,
        loc="upper center",
        bbox_to_anchor=(0.5, 1.12),
        ncol=5,
        frameon=False,
        fontsize=14,
        handlelength=2.0,
        columnspacing=2.0,
    )

    ax.text(
        4.15,
        82.5,
        "SOTA Performance at\n$\\bf{10x}$ Faster Inference",
        ha="right",
        va="center",
        fontsize=15,
        color="#c91e1e",
        bbox={
            "boxstyle": "round,pad=0.5,rounding_size=0.25",
            "facecolor": "#fff8f8",
            "edgecolor": "#ff4b4b",
            "linewidth": 1.4,
        },
    )

    fig.subplots_adjust(left=0.075, right=0.965, top=0.86, bottom=0.105)
    fig.savefig(PNG_OUT, dpi=dpi)
    fig.savefig(SVG_OUT)
    plt.close(fig)


def svg_attrs(attributes: dict) -> str:
    parts = []
    for key, value in attributes.items():
        if value is None:
            continue
        parts.append(f'{key}="{html.escape(str(value), quote=True)}"')
    return " ".join(parts)


def svg_tag(name: str, attributes: dict, content: str | None = "") -> str:
    attr_text = svg_attrs(attributes)
    prefix = f"<{name} {attr_text}" if attr_text else f"<{name}"
    if content is None:
        return f"{prefix}/>"
    return f"{prefix}>{content}</{name}>"


def svg_y(value: float) -> float:
    plot_y = 240
    plot_h = 1525
    return plot_y + plot_h - (value / MAX_Y) * plot_h


def svg_rect(x: float, y: float, w: float, h: float, fill: str, rx: float = 0, stroke: str | None = None) -> str:
    return svg_tag(
        "rect",
        {
            "x": round(x, 2),
            "y": round(y, 2),
            "width": round(w, 2),
            "height": round(h, 2),
            "rx": rx,
            "ry": rx,
            "fill": fill,
            "stroke": stroke,
            "stroke-width": 7 if stroke else None,
        },
        None,
    )


def write_svg_without_matplotlib() -> None:
    plot_x = 180
    plot_y = 240
    plot_w = 3000
    plot_h = 1525
    bottom = plot_y + plot_h
    group_step = plot_w / len(BENCHMARKS)
    bar_w = 95
    method_step = 105

    def group_center(index: int) -> float:
        return plot_x + group_step * (index + 0.5)

    parts = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}">',
        f'<rect width="{WIDTH}" height="{HEIGHT}" fill="#ffffff"/>',
        '<g font-family="Arial, Helvetica, sans-serif">',
    ]

    legend_x = [68, 875, 1660, 2330, 2880]
    for x, method in zip(legend_x, METHODS):
        parts.append(svg_rect(x, 46, 95, 34, method["color"]))
        parts.append(
            svg_tag(
                "text",
                {"x": x + 130, "y": 74, "font-size": 48, "fill": "#111111", "font-weight": 500},
                html.escape(method["label"]),
            )
        )

    parts.append(
        svg_tag(
            "text",
            {
                "x": WIDTH / 2,
                "y": 158,
                "font-size": 72,
                "font-weight": 800,
                "fill": "#202020",
                "text-anchor": "middle",
            },
            "Performance Comparison Across Benchmarks",
        )
    )

    for tick in range(0, int(MAX_Y) + 1, 10):
        y = svg_y(float(tick))
        parts.append(
            svg_tag(
                "line",
                {
                    "x1": plot_x,
                    "y1": round(y, 2),
                    "x2": plot_x + plot_w,
                    "y2": round(y, 2),
                    "stroke": "#999999" if tick == 0 else "#d7d7d7",
                    "stroke-width": 3,
                    "stroke-dasharray": None if tick == 0 else "12 8",
                },
                None,
            )
        )
        parts.append(
            svg_tag(
                "text",
                {
                    "x": plot_x - 30,
                    "y": round(y + 15, 2),
                    "font-size": 42,
                    "fill": "#111111",
                    "text-anchor": "end",
                },
                str(tick),
            )
        )

    parts.append(
        svg_tag(
            "line",
            {
                "x1": plot_x,
                "y1": plot_y,
                "x2": plot_x,
                "y2": bottom,
                "stroke": "#999999",
                "stroke-width": 3,
            },
            None,
        )
    )
    parts.append(
        svg_tag(
            "text",
            {
                "x": 74,
                "y": plot_y + plot_h / 2,
                "font-size": 58,
                "fill": "#222222",
                "font-weight": 700,
                "text-anchor": "middle",
                "transform": f"rotate(-90 74 {plot_y + plot_h / 2})",
            },
            "Average Success Rate (%)",
        )
    )

    for bench_index, benchmark in enumerate(BENCHMARKS):
        methods = present_methods(benchmark)
        group_w = method_step * len(methods)
        center_x = group_center(bench_index)

        for method_index, method in enumerate(methods):
            key = method["key"]
            value = benchmark["values"][key]
            x = center_x - group_w / 2 + method_index * method_step + 5
            y = svg_y(value)
            parts.append(svg_rect(x, y, bar_w, bottom - y, method["color"], stroke=method["edge"] if key == "ours" else None))

            if key == "ours":
                bar_center = x + bar_w / 2
                parts.append(
                    svg_tag(
                        "text",
                        {
                            "x": round(bar_center, 2),
                            "y": round(y - 31, 2),
                            "font-size": 52,
                            "font-weight": 800,
                            "fill": method["color"],
                            "text-anchor": "middle",
                        },
                        f"{value:.1f}",
                    )
                )
                base = benchmark["values"][benchmark["compare_key"]]
                delta = value - base
                badge = f"+{delta:.1f}%"
                badge_w = len(badge) * 31 + 52
                badge_x = bar_center - badge_w / 2
                badge_y = y - 166
                parts.append(svg_rect(badge_x, badge_y, badge_w, 64, method["color"], rx=12))
                parts.append(
                    svg_tag(
                        "text",
                        {
                            "x": round(bar_center, 2),
                            "y": round(badge_y + 46, 2),
                            "font-size": 44,
                            "font-weight": 800,
                            "fill": "#ffffff",
                            "text-anchor": "middle",
                        },
                        badge,
                    )
                )

        parts.append(
            svg_tag(
                "text",
                {
                    "x": round(center_x, 2),
                    "y": bottom + 72,
                    "font-size": 56 if benchmark["label"] == "RoboTwin 2.0" else 58,
                    "font-weight": 800,
                    "fill": "#2a2a2a",
                    "text-anchor": "middle",
                },
                html.escape(benchmark["label"]),
            )
        )

    parts.append(svg_rect(2540, 292, 600, 150, "#fff8f8", rx=20, stroke="#ff4b4b"))
    parts.append(
        svg_tag(
            "text",
            {"x": 2840, "y": 350, "font-size": 48, "fill": "#c91e1e", "text-anchor": "middle"},
            "SOTA Performance at",
        )
    )
    parts.append(
        svg_tag(
            "text",
            {"x": 2840, "y": 408, "font-size": 48, "fill": "#c91e1e", "text-anchor": "middle"},
            '<tspan font-weight="800">10x</tspan><tspan dx="16">Faster Inference</tspan>',
        )
    )

    parts.append("</g></svg>")
    SVG_OUT.write_text("\n".join(parts), encoding="utf-8")


def render_png_with_sharp() -> bool:
    script = """
const sharp = require('sharp');
sharp(process.argv[1]).png().toFile(process.argv[2]).catch((error) => {
  console.error(error);
  process.exit(1);
});
"""
    try:
        subprocess.run(["node", "-e", script, str(SVG_OUT), str(PNG_OUT)], cwd=ROOT, check=True)
    except (OSError, subprocess.CalledProcessError):
        return False
    return True


def main() -> int:
    PNG_OUT.parent.mkdir(parents=True, exist_ok=True)

    try:
        draw_with_matplotlib()
        backend = "matplotlib"
    except ModuleNotFoundError as error:
        if error.name != "matplotlib":
            raise
        write_svg_without_matplotlib()
        if not render_png_with_sharp():
            print(f"Wrote {SVG_OUT.relative_to(ROOT)}")
            print("PNG was not written because matplotlib and sharp are unavailable.")
            print("Install matplotlib, then rerun: python scripts/generate_final_chart.py")
            return 1
        backend = "svg+sharp fallback"

    print(f"Wrote {PNG_OUT.relative_to(ROOT)}")
    print(f"Wrote {SVG_OUT.relative_to(ROOT)}")
    print(f"Backend: {backend}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
