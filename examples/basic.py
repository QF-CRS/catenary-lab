"""Small library usage example.

Run from the repository root with::

    python examples/basic.py
"""

from catenarylab import Cable, Span, solve_catenary


span = Span(length_m=300.0, left_elevation_m=10.0, right_elevation_m=16.0)
cable = Cable(weight_n_per_m=12.0, horizontal_tension_n=30_000.0)
solution = solve_catenary(span, cable)

print(f"arc length: {solution.arc_length_m:.3f} m")
print(f"maximum sag: {solution.max_sag_below_chord_m:.3f} m")
print(f"left tension: {solution.left_tension_n:.1f} N")
print(f"right tension: {solution.right_tension_n:.1f} N")
