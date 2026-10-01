# Contributing to Catenary Lab

Thank you for helping make the calculations clearer, safer, and easier to
reuse.

## Before you start

For a bug, include the smallest input that reproduces it and the result you
expected. For a feature, open an issue first when the change affects the model
assumptions or public API.

## Local workflow

1. Create a virtual environment with Python 3.10 or newer.
2. Install the package in editable mode: `python -m pip install -e .`.
3. Run `python -m unittest discover -s tests -v`.
4. Keep public API changes documented in `README.md` and `CHANGELOG.md`.

## Pull requests

- Keep each pull request focused on one problem.
- Add or update tests for changed behaviour.
- Explain units and modelling assumptions in docstrings.
- Do not include proprietary project files, client data, or generated binary
  simulation output.
- Do not claim that a calculation is suitable for design approval unless the
  relevant validation evidence and design standard are included.

By contributing, you agree that your work is provided under the MIT License.
