"""Device Log Summarizer CLI.

Reads device telemetry CSV, summarizes records by device, filters devices whose
average temperature is above the configured threshold, and exports JSON.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import statistics
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any


def clean_sensor_readings(values: list[Any]) -> list[float]:
    """Convert usable readings to floats, discard invalid/negative values, cap at 500."""
    cleaned: list[float] = []
    for value in values:
        if value is None:
            continue
        try:
            number = float(value)
        except (TypeError, ValueError):
            continue
        if not math.isfinite(number) or number < 0:
            continue
        cleaned.append(min(number, 500.0))
    return cleaned


def summarize_csv(input_path: Path, output_path: Path, threshold: float = 80.0) -> list[dict[str, Any]]:
    """Summarize telemetry by device and export qualifying devices to JSON."""
    if not input_path.exists():
        raise FileNotFoundError(f"Input CSV file not found: {input_path}")

    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    with input_path.open("r", newline="", encoding="utf-8-sig") as csv_file:
        reader = csv.DictReader(csv_file)
        required = {"device_id", "status", "temperature"}
        if reader.fieldnames is None or not required.issubset(set(reader.fieldnames)):
            raise ValueError(
                "CSV must contain these columns: device_id, status, temperature"
            )

        for line_number, row in enumerate(reader, start=2):
            device_id = (row.get("device_id") or "").strip()
            status = (row.get("status") or "").strip().upper()
            raw_temperature = row.get("temperature")

            if not device_id:
                print(f"Warning: skipping row {line_number}: missing device_id", file=sys.stderr)
                continue
            try:
                temperature = float(raw_temperature) if raw_temperature is not None else float("nan")
            except (TypeError, ValueError):
                print(f"Warning: skipping row {line_number}: invalid temperature", file=sys.stderr)
                continue
            if not math.isfinite(temperature):
                print(f"Warning: skipping row {line_number}: invalid temperature", file=sys.stderr)
                continue

            grouped[device_id].append({"status": status, "temperature": temperature})

    results: list[dict[str, Any]] = []
    for device_id in sorted(grouped):
        records = grouped[device_id]
        average_temperature = statistics.mean(record["temperature"] for record in records)
        if average_temperature > threshold:
            continue
        results.append({
            "device_id": device_id,
            "total_records": len(records),
            "average_temperature": round(average_temperature, 2),
            "error_count": sum(record["status"] == "ERROR" for record in records),
        })

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as json_file:
        json.dump(results, json_file, indent=2)
        json_file.write("\n")
    return results


def print_summary(results: list[dict[str, Any]]) -> None:
    """Print a compact summary table."""
    if not results:
        print("No devices met the average-temperature threshold.")
        return
    headers = ("DEVICE_ID", "TOTAL_RECORDS", "AVG_TEMP", "ERROR_COUNT")
    rows = [
        (str(r["device_id"]), str(r["total_records"]),
         f'{r["average_temperature"]:.2f}', str(r["error_count"]))
        for r in results
    ]
    widths = [max(len(headers[i]), *(len(row[i]) for row in rows)) for i in range(len(headers))]
    print(" | ".join(headers[i].ljust(widths[i]) for i in range(len(headers))))
    print("-+-".join("-" * width for width in widths))
    for row in rows:
        print(" | ".join(row[i].ljust(widths[i]) for i in range(len(headers))))


def main() -> int:
    parser = argparse.ArgumentParser(description="Summarize device telemetry from a CSV file.")
    parser.add_argument("--input", default="device_telemetry.csv", help="Path to telemetry CSV")
    parser.add_argument("--output", default="output.json", help="Path to output JSON")
    parser.add_argument("--threshold", type=float, default=80.0, help="Exclude devices above this average")
    args = parser.parse_args()

    try:
        results = summarize_csv(Path(args.input), Path(args.output), args.threshold)
    except (OSError, ValueError, csv.Error) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    print_summary(results)
    print(f"\nSaved {len(results)} device summary record(s) to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
