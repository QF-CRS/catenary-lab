import math
import unittest

from catenarylab import Cable, Span, solve_catenary


class CatenarySolutionTests(unittest.TestCase):
    def test_level_span_is_symmetric(self) -> None:
        solution = solve_catenary(
            Span(300.0), Cable(weight_n_per_m=12.0, horizontal_tension_n=30_000.0)
        )

        self.assertAlmostEqual(solution.elevation(0.0), 0.0, places=12)
        self.assertAlmostEqual(solution.elevation(300.0), 0.0, places=12)
        self.assertAlmostEqual(solution.elevation(50.0), solution.elevation(250.0), places=12)
        self.assertAlmostEqual(solution.vertex_x_m, 150.0, places=12)
        self.assertAlmostEqual(solution.vertex_elevation_m, solution.elevation(150.0), places=12)
        self.assertGreater(solution.max_sag_below_chord_m, 0.0)

    def test_sloped_span_matches_attachments(self) -> None:
        span = Span(240.0, left_elevation_m=18.0, right_elevation_m=30.0)
        solution = solve_catenary(span, Cable(10.0, 25_000.0))

        self.assertAlmostEqual(solution.elevation(0.0), 18.0, places=11)
        self.assertAlmostEqual(solution.elevation(240.0), 30.0, places=11)
        self.assertGreater(solution.arc_length_m, span.length_m)
        self.assertTrue(math.isfinite(solution.left_tension_n))
        self.assertTrue(math.isfinite(solution.right_tension_n))

    def test_sampling_includes_endpoints(self) -> None:
        solution = solve_catenary(Span(100.0), Cable(5.0, 5_000.0))
        points = solution.sample(5)

        self.assertEqual(len(points), 5)
        self.assertAlmostEqual(points[0].x_m, 0.0)
        self.assertAlmostEqual(points[-1].x_m, 100.0)
        self.assertAlmostEqual(points[0].elevation_m, 0.0, places=11)
        self.assertAlmostEqual(points[-1].elevation_m, 0.0, places=11)

    def test_sag_is_zero_at_attachments(self) -> None:
        solution = solve_catenary(
            Span(120.0, left_elevation_m=-3.0, right_elevation_m=7.0),
            Cable(8.0, 12_000.0),
        )
        self.assertAlmostEqual(solution.sag_below_chord(0.0), 0.0, places=11)
        self.assertAlmostEqual(solution.sag_below_chord(120.0), 0.0, places=11)

    def test_steep_nearly_straight_span_preserves_endpoint(self) -> None:
        solution = solve_catenary(
            Span(1e-6, right_elevation_m=1e6),
            Cable(weight_n_per_m=1e6, horizontal_tension_n=1e6),
        )
        self.assertAlmostEqual(solution.elevation(0.0), 0.0, places=12)
        self.assertAlmostEqual(solution.elevation(1e-6), 1e6, places=6)


class ValidationTests(unittest.TestCase):
    def test_span_rejects_non_positive_length(self) -> None:
        with self.assertRaises(ValueError):
            Span(0.0)

    def test_cable_rejects_non_positive_load_and_tension(self) -> None:
        with self.assertRaises(ValueError):
            Cable(0.0, 100.0)
        with self.assertRaises(ValueError):
            Cable(1.0, 0.0)

    def test_x_must_be_inside_span(self) -> None:
        solution = solve_catenary(Span(10.0), Cable(1.0, 100.0))
        with self.assertRaises(ValueError):
            solution.elevation(10.1)

    def test_sample_count_is_valid(self) -> None:
        solution = solve_catenary(Span(10.0), Cable(1.0, 100.0))
        with self.assertRaises(ValueError):
            solution.sample(1)
        with self.assertRaises(TypeError):
            solution.sample(3.5)  # type: ignore[arg-type]


if __name__ == "__main__":
    unittest.main()
