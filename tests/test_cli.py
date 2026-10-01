import json
import unittest
from contextlib import redirect_stdout
from io import StringIO

from catenarylab.cli import main


class CliTests(unittest.TestCase):
    def test_json_output_contains_summary_and_samples(self) -> None:
        output = StringIO()
        with redirect_stdout(output):
            exit_code = main(
                [
                    "--span-m",
                    "100",
                    "--weight-n-per-m",
                    "5",
                    "--horizontal-tension-n",
                    "5000",
                    "--samples",
                    "3",
                    "--json",
                ]
            )

        payload = json.loads(output.getvalue())
        self.assertEqual(exit_code, 0)
        self.assertIn("catenary", payload)
        self.assertEqual(len(payload["samples"]), 3)


if __name__ == "__main__":
    unittest.main()
