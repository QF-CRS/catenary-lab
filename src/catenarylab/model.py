"""Pure-Python catenary model.

The model assumes a perfectly flexible cable with a uniform distributed load
per horizontal metre and a prescribed horizontal component of tension. This
is the classical, extensible-free catenary model. It is useful for quick
screening calculations and teaching; it is not a replacement for a project-
specific design standard or a nonlinear finite-element model.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Iterable


def _finite(value: float, name: str) -> float:
    """Return *value* as a float, rejecting NaN and infinities."""

    result = float(value)
    if not math.isfinite(result):
        raise ValueError(f"{name} must be finite")
    return result


@dataclass(frozen=True, slots=True)
class Span:
    """Geometry of one span."""

    length_m: float
    left_elevation_m: float = 0.0
    right_elevation_m: float = 0.0

    def __post_init__(self) -> None:
        length = _finite(self.length_m, "length_m")
        left = _finite(self.left_elevation_m, "left_elevation_m")
        right = _finite(self.right_elevation_m, "right_elevation_m")
        if length <= 0.0:
            raise ValueError("length_m must be greater than zero")
        object.__setattr__(self, "length_m", length)
        object.__setattr__(self, "left_elevation_m", left)
        object.__setattr__(self, "right_elevation_m", right)

    @property
    def elevation_difference_m(self) -> float:
        """Right attachment elevation minus left attachment elevation."""

        return self.right_elevation_m - self.left_elevation_m


@dataclass(frozen=True, slots=True)
class Cable:
    """Uniform cable loading and horizontal tension.

    ``weight_n_per_m`` is the load per horizontal metre. It can include the
    cable's own weight and any load intentionally lumped into the model.
    """

    weight_n_per_m: float
    horizontal_tension_n: float

    def __post_init__(self) -> None:
        weight = _finite(self.weight_n_per_m, "weight_n_per_m")
        tension = _finite(self.horizontal_tension_n, "horizontal_tension_n")
        if weight <= 0.0:
            raise ValueError("weight_n_per_m must be greater than zero")
        if tension <= 0.0:
            raise ValueError("horizontal_tension_n must be greater than zero")
        object.__setattr__(self, "weight_n_per_m", weight)
        object.__setattr__(self, "horizontal_tension_n", tension)


@dataclass(frozen=True, slots=True)
class Point:
    """A sampled point along the cable."""

    x_m: float
    elevation_m: float
    sag_below_chord_m: float
    tension_n: float

    def as_dict(self) -> dict[str, float]:
        """Return a JSON-friendly representation."""

        return {
            "x_m": self.x_m,
            "elevation_m": self.elevation_m,
            "sag_below_chord_m": self.sag_below_chord_m,
            "tension_n": self.tension_n,
        }


@dataclass(frozen=True, slots=True)
class CatenarySolution:
    """Solved catenary and derived engineering quantities.

    Users normally obtain this object from :func:`solve_catenary` rather than
    constructing it directly. ``a_m`` is the catenary parameter ``H / w``.
    ``vertex_x_m`` is the horizontal coordinate of the mathematical lowest
    point; it can fall outside the span when the attachments are very unequal.
    """

    span: Span
    cable: Cable
    a_m: float
    vertex_x_m: float
    vertex_elevation_m: float
    _horizontal_shift_m: float
    _constant_m: float

    def _check_x(self, x_m: float) -> float:
        x = _finite(x_m, "x_m")
        if x < 0.0 or x > self.span.length_m:
            raise ValueError(
                f"x_m must be between 0 and {self.span.length_m:g} m"
            )
        return x

    def elevation(self, x_m: float) -> float:
        """Return cable elevation at horizontal position ``x_m``."""

        x = self._check_x(x_m)
        # Evaluate relative to the left attachment. The direct c + a*cosh
        # form loses significant digits when c and the cosh term nearly cancel.
        return self.span.left_elevation_m + 2.0 * self.a_m * math.sinh(
            x / (2.0 * self.a_m)
        ) * math.sinh((x - 2.0 * self.vertex_x_m) / (2.0 * self.a_m))

    def slope(self, x_m: float) -> float:
        """Return ``dz/dx`` at ``x_m``."""

        x = self._check_x(x_m)
        return math.sinh((x - self.vertex_x_m) / self.a_m)

    def vertical_tension_n(self, x_m: float) -> float:
        """Return the signed vertical tension component at ``x_m``."""

        x = self._check_x(x_m)
        return self.cable.horizontal_tension_n * math.sinh(
            (x - self.vertex_x_m) / self.a_m
        )

    def tension_n(self, x_m: float) -> float:
        """Return the tension magnitude at ``x_m``."""

        x = self._check_x(x_m)
        return self.cable.horizontal_tension_n * math.cosh(
            (x - self.vertex_x_m) / self.a_m
        )

    def chord_elevation(self, x_m: float) -> float:
        """Return elevation of the straight line between the attachments."""

        x = self._check_x(x_m)
        fraction = x / self.span.length_m
        return self.span.left_elevation_m + fraction * self.span.elevation_difference_m

    def sag_below_chord(self, x_m: float) -> float:
        """Return vertical sag below the attachment chord at ``x_m``."""

        return self.chord_elevation(x_m) - self.elevation(x_m)

    @property
    def arc_length_m(self) -> float:
        """Return the cable length between the two attachments."""

        left_u = -self.vertex_x_m / self.a_m
        right_u = (self.span.length_m - self.vertex_x_m) / self.a_m
        return self.a_m * (math.sinh(right_u) - math.sinh(left_u))

    @property
    def left_tension_n(self) -> float:
        """Tension magnitude at the left attachment."""

        return self.tension_n(0.0)

    @property
    def right_tension_n(self) -> float:
        """Tension magnitude at the right attachment."""

        return self.tension_n(self.span.length_m)

    @property
    def max_sag_below_chord_m(self) -> float:
        """Maximum sag below the straight attachment chord."""

        chord_slope = self.span.elevation_difference_m / self.span.length_m
        x_at_max_sag = self.vertex_x_m + self.a_m * math.asinh(chord_slope)
        x_at_max_sag = min(self.span.length_m, max(0.0, x_at_max_sag))
        return self.sag_below_chord(x_at_max_sag)

    @property
    def lowest_point_in_span(self) -> bool:
        """Whether the mathematical lowest point lies inside the span."""

        return 0.0 <= self.vertex_x_m <= self.span.length_m

    def sample(self, count: int = 11) -> tuple[Point, ...]:
        """Sample ``count`` evenly spaced points, including both attachments."""

        if isinstance(count, bool) or not isinstance(count, int):
            raise TypeError("count must be an integer")
        if count < 2:
            raise ValueError("count must be at least 2")
        step = self.span.length_m / (count - 1)
        return tuple(
            Point(
                x_m=x,
                elevation_m=self.elevation(x),
                sag_below_chord_m=self.sag_below_chord(x),
                tension_n=self.tension_n(x),
            )
            for x in (index * step for index in range(count))
        )

    def summary(self) -> dict[str, object]:
        """Return the main results as a JSON-serializable dictionary."""

        return {
            "span": {
                "length_m": self.span.length_m,
                "left_elevation_m": self.span.left_elevation_m,
                "right_elevation_m": self.span.right_elevation_m,
            },
            "cable": {
                "weight_n_per_m": self.cable.weight_n_per_m,
                "horizontal_tension_n": self.cable.horizontal_tension_n,
            },
            "catenary": {
                "parameter_a_m": self.a_m,
                "vertex_x_m": self.vertex_x_m,
                "vertex_elevation_m": self.vertex_elevation_m,
                "lowest_point_in_span": self.lowest_point_in_span,
                "arc_length_m": self.arc_length_m,
                "left_tension_n": self.left_tension_n,
                "right_tension_n": self.right_tension_n,
                "max_sag_below_chord_m": self.max_sag_below_chord_m,
            },
        }


def solve_catenary(span: Span, cable: Cable) -> CatenarySolution:
    """Solve a classical catenary for ``span`` and ``cable``.

    The horizontal tension ``H`` and load ``w`` define ``a = H / w``. The
    endpoint elevation difference determines the horizontal location of the
    catenary vertex. No iterative solver is needed, which makes this
    implementation deterministic and easy to audit.
    """

    if not isinstance(span, Span):
        raise TypeError("span must be a Span")
    if not isinstance(cable, Cable):
        raise TypeError("cable must be a Cable")

    a = cable.horizontal_tension_n / cable.weight_n_per_m
    half_span_u = span.length_m / (2.0 * a)
    try:
        denominator = 2.0 * a * math.sinh(half_span_u)
        vertex_offset_u = math.asinh(span.elevation_difference_m / denominator)
    except (OverflowError, ZeroDivisionError) as exc:
        raise ValueError(
            "the span-to-catenary scale is outside the stable numeric range"
        ) from exc

    vertex_x = span.length_m / 2.0 - a * vertex_offset_u
    try:
        constant = span.left_elevation_m - a * math.cosh(vertex_x / a)
        # Use the same cancellation-resistant form as ``elevation``.
        vertex_elevation = span.left_elevation_m + 2.0 * a * math.sinh(
            vertex_x / (2.0 * a)
        ) * math.sinh(-vertex_x / (2.0 * a))
    except OverflowError as exc:
        raise ValueError(
            "the catenary parameters are outside the stable numeric range"
        ) from exc

    return CatenarySolution(
        span=span,
        cable=cable,
        a_m=a,
        vertex_x_m=vertex_x,
        vertex_elevation_m=vertex_elevation,
        _horizontal_shift_m=vertex_x,
        _constant_m=constant,
    )


def points_to_rows(points: Iterable[Point]) -> list[dict[str, float]]:
    """Convert sampled points to JSON-friendly rows."""

    return [point.as_dict() for point in points]
