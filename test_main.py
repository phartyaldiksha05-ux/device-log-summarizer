import json
import tempfile
import unittest
from pathlib import Path

from main import clean_sensor_readings, summarize_csv


class CleanSensorReadingsTests(unittest.TestCase):
    def test_converts_filters_and_clips(self):
        self.assertEqual(
            clean_sensor_readings(["12", None, "bad", -2, 501, 4.5]),
            [12.0, 500.0, 4.5],
        )

    def test_empty_and_all_invalid(self):
        self.assertEqual(clean_sensor_readings([]), [])
        self.assertEqual(clean_sensor_readings([None, "x", -1]), [])

    def test_discards_non_finite_numbers(self):
        self.assertEqual(clean_sensor_readings(["nan", "inf", 5]), [5.0])


class SummarizeCsvTests(unittest.TestCase):
    def test_aggregates_and_filters(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            folder = Path(temp_dir)
            csv_path = folder / "telemetry.csv"
            json_path = folder / "output.json"
            csv_path.write_text(
                "device_id,status,temperature\n"
                "DEV_A,ACTIVE,40\n"
                "DEV_A,ERROR,60\n"
                "DEV_B,WARNING,90\n"
                "DEV_C,ERROR,70\n",
                encoding="utf-8",
            )
            results = summarize_csv(csv_path, json_path)
            self.assertEqual(results, [
                {"device_id": "DEV_A", "total_records": 2,
                 "average_temperature": 50.0, "error_count": 1},
                {"device_id": "DEV_C", "total_records": 1,
                 "average_temperature": 70.0, "error_count": 1},
            ])
            self.assertEqual(json.loads(json_path.read_text(encoding="utf-8")), results)

    def test_missing_file(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            with self.assertRaises(FileNotFoundError):
                summarize_csv(Path(temp_dir) / "missing.csv", Path(temp_dir) / "out.json")


if __name__ == "__main__":
    unittest.main()
