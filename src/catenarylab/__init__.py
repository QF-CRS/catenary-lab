"""Catenary and sag-tension calculations for overhead lines.

The public API intentionally stays small. Start with :func:`solve_catenary`
and inspect the returned :class:`CatenarySolution`.
"""

from .model import Cable, CatenarySolution, Span, solve_catenary

__all__ = ["Cable", "CatenarySolution", "Span", "solve_catenary"]

__version__ = "0.1.0"
