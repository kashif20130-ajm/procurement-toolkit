from __future__ import annotations

import html
import math

import pandas as pd


PROCUREMENT_RADAR_DIMENSIONS = [
    "Governance",
    "Strategic Sourcing",
    "Supplier Management",
    "Contract Management",
    "Risk Management",
    "Category Management",
    "Analytics",
    "Digitalization",
    "ESG Procurement",
    "Performance Management",
]


def build_procurement_radar_table(scores: dict[str, int]) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "Dimension": PROCUREMENT_RADAR_DIMENSIONS,
            "Maturity 1-5": [int(scores.get(dimension, 1)) for dimension in PROCUREMENT_RADAR_DIMENSIONS],
        }
    )


def build_procurement_radar_svg(scores: dict[str, int]) -> str:
    width = 720
    height = 620
    center_x = width / 2
    center_y = height / 2
    radius = 215
    label_radius = 275
    dimensions = PROCUREMENT_RADAR_DIMENSIONS
    count = len(dimensions)

    axis_points = []
    value_points = []
    label_elements = []

    for index, dimension in enumerate(dimensions):
        angle = -math.pi / 2 + (2 * math.pi * index / count)
        axis_x = center_x + radius * math.cos(angle)
        axis_y = center_y + radius * math.sin(angle)
        axis_points.append((axis_x, axis_y))

        value = max(1, min(5, int(scores.get(dimension, 1))))
        value_radius = radius * (value / 5)
        value_x = center_x + value_radius * math.cos(angle)
        value_y = center_y + value_radius * math.sin(angle)
        value_points.append((value_x, value_y))

        label_x = center_x + label_radius * math.cos(angle)
        label_y = center_y + label_radius * math.sin(angle)
        label_anchor = "middle"
        if label_x < center_x - 20:
            label_anchor = "end"
        elif label_x > center_x + 20:
            label_anchor = "start"

        label_elements.append(
            f'<text x="{label_x:.1f}" y="{label_y:.1f}" text-anchor="{label_anchor}" '
            f'class="radar-label">{html.escape(dimension)}</text>'
        )

    ring_elements = []
    for level in range(1, 6):
        level_radius = radius * (level / 5)
        ring_points = []
        for index in range(count):
            angle = -math.pi / 2 + (2 * math.pi * index / count)
            x = center_x + level_radius * math.cos(angle)
            y = center_y + level_radius * math.sin(angle)
            ring_points.append(f"{x:.1f},{y:.1f}")
        ring_elements.append(
            f'<polygon points="{" ".join(ring_points)}" class="radar-ring" />'
        )
        ring_elements.append(
            f'<text x="{center_x + 8:.1f}" y="{center_y - level_radius + 4:.1f}" '
            f'class="radar-level">{level}</text>'
        )

    axis_elements = [
        f'<line x1="{center_x:.1f}" y1="{center_y:.1f}" x2="{x:.1f}" y2="{y:.1f}" class="radar-axis" />'
        for x, y in axis_points
    ]
    value_polygon = " ".join(f"{x:.1f},{y:.1f}" for x, y in value_points)
    marker_elements = [
        f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4.5" class="radar-marker" />'
        for x, y in value_points
    ]

    return f"""
<div class="radar-wrap">
  <svg viewBox="0 0 {width} {height}" role="img" aria-label="Procurement maturity radar chart">
    <style>
      .radar-wrap {{
        width: 100%;
        max-width: 860px;
        margin: 0 auto;
      }}
      .radar-ring {{
        fill: none;
        stroke: #d9e1ea;
        stroke-width: 1;
      }}
      .radar-axis {{
        stroke: #c5cfdb;
        stroke-width: 1;
      }}
      .radar-area {{
        fill: rgba(31, 119, 180, 0.28);
        stroke: #1f77b4;
        stroke-width: 3;
      }}
      .radar-marker {{
        fill: #1f77b4;
        stroke: #ffffff;
        stroke-width: 2;
      }}
      .radar-label {{
        fill: #1f2937;
        font-size: 15px;
        font-family: Arial, sans-serif;
      }}
      .radar-level {{
        fill: #64748b;
        font-size: 12px;
        font-family: Arial, sans-serif;
      }}
    </style>
    {"".join(ring_elements)}
    {"".join(axis_elements)}
    <polygon points="{value_polygon}" class="radar-area" />
    {"".join(marker_elements)}
    {"".join(label_elements)}
  </svg>
</div>
""".strip()
