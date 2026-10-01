# Catenary Lab

**A small, dependency-free catenary and sag-tension toolkit for overhead lines.**

Catenary Lab computes the classical flexible-cable solution for a single span
with a uniform load per horizontal metre and a prescribed horizontal component
of tension. It exposes a Python API and a command-line interface, so the same
calculation can be used in a notebook, a script, or a reproducible engineering
workflow.

> **Status:** alpha. The project is intended for screening calculations,
> teaching, and reproducible research. It is not a substitute for a
> project-specific design standard, a certified design package, or a nonlinear
> finite-element model.

## What it can do

- solve level or unequal-elevation spans without an iterative root finder;
- evaluate cable elevation, slope, vertical tension, and tension magnitude;
- report arc length, attachment tensions, vertex location, and maximum sag
  below the straight attachment chord;
- sample a span into JSON-friendly rows;
- run with no runtime dependencies beyond the Python standard library.

## Quick start

Requires Python 3.10 or newer.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e .
```

Solve a 300 m level span with a 12 N/m load and 30 kN horizontal tension:

```powershell
catenary-lab `
  --span-m 300 `
  --weight-n-per-m 12 `
  --horizontal-tension-n 30000
```

For machine-readable output:

```powershell
python -m catenarylab `
  --span-m 300 `
  --weight-n-per-m 12 `
  --horizontal-tension-n 30000 `
  --left-elevation-m 10 `
  --right-elevation-m 16 `
  --samples 21 `
  --json
```

## Python API

```python
from catenarylab import Cable, Span, solve_catenary

span = Span(length_m=300.0, left_elevation_m=10.0, right_elevation_m=16.0)
cable = Cable(weight_n_per_m=12.0, horizontal_tension_n=30_000.0)
solution = solve_catenary(span, cable)

print(solution.elevation(150.0))
print(solution.max_sag_below_chord_m)
print(solution.arc_length_m)
for point in solution.sample(11):
    print(point.x_m, point.elevation_m, point.tension_n)
```

All inputs use SI units: metres, newtons, and newtons per metre. The load can
represent the cable's own weight or a deliberately lumped load case.

## Model and assumptions

The solver uses the classical catenary

```text
z(x) = c + a cosh((x - x_vertex) / a),    a = H / w
```

where `H` is the horizontal tension and `w` is the uniform load per horizontal
metre. The endpoint elevations determine `x_vertex` and `c` analytically. The
model assumes a perfectly flexible, inextensible cable and does not include
temperature strain, elastic stretch, conductor self-weight variation, wind
direction effects, insulator geometry, or tower flexibility.

## Development

Run the test suite with the standard library:

```powershell
python -m unittest discover -s tests -v
```

The project uses small, reviewable changes. Please read
[CONTRIBUTING.md](CONTRIBUTING.md) before opening a pull request. Planned work
is tracked in [docs/roadmap.md](docs/roadmap.md).

## License

Released under the [MIT License](LICENSE).
