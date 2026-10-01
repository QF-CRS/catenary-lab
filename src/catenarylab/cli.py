"""Command-line interface for :mod:`catenarylab`."""

from __future__ import annotations

import argparse
import json

from .model import Cable, Span, points_to_rows, solve_catenary


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="catenary-lab",
        description="Compute catenary geometry, sag, and tension for one span.",
    )
    parser.add_argument("--span-m", type=float, required=True, help="span length in metres")
    parser.add_argument(
        "--weight-n-per-m",
        type=float,
        required=True,
        help="uniform load per horizontal metre in newtons",
    )
    parser.add_argument(
        "--horizontal-tension-n",
        type=float,
        required=True,
        help="horizontal component of tension in newtons",
    )
    parser.add_argument("--left-elevation-m", type=float, default=0.0)
    parser.add_argument("--right-elevation-m", type=float, default=0.0)
    parser.add_argument(
        "--samples",
        type=int,
        default=11,
        help="number of evenly spaced output points (default: 11)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="print a machine-readable JSON document",
    )
    return parser


def _format_table(solution, samples: int) -> str:
    summary = solution.summary()["catenary"]
    lines = [
        "Catenary Lab",
        "============",
        f"catenary parameter a: {summary['parameter_a_m']:.6f} m",
        f"vertex: x={summary['vertex_x_m']:.6f} m, z={summary['vertex_elevation_m']:.6f} m",
        f"lowest point inside span: {'yes' if summary['lowest_point_in_span'] else 'no'}",
        f"arc length: {summary['arc_length_m']:.6f} m",
        f"maximum sag below chord: {summary['max_sag_below_chord_m']:.6f} m",
        f"left / right tension: {summary['left_tension_n']:.3f} / {summary['right_tension_n']:.3f} N",
        "",
        "x (m)       elevation (m)   sag below chord (m)   tension (N)",
        "-" * 65,
    ]
    for point in solution.sample(samples):
        lines.append(
            f"{point.x_m:8.3f}   {point.elevation_m:14.6f}   "
            f"{point.sag_below_chord_m:19.6f}   {point.tension_n:12.3f}"
        )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        solution = solve_catenary(
            Span(
                length_m=args.span_m,
                left_elevation_m=args.left_elevation_m,
                right_elevation_m=args.right_elevation_m,
            ),
            Cable(
                weight_n_per_m=args.weight_n_per_m,
                horizontal_tension_n=args.horizontal_tension_n,
            ),
        )
        if args.json:
            payload = solution.summary()
            payload["samples"] = points_to_rows(solution.sample(args.samples))
            print(json.dumps(payload, indent=2))
        else:
            print(_format_table(solution, args.samples))
    except (TypeError, ValueError, OverflowError) as exc:
        parser.error(str(exc))
    return 0
