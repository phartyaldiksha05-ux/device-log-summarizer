"""Generate a bar chart from the JSON summary produced by main.py."""
import argparse
import json
import sys
from pathlib import Path

import matplotlib.pyplot as plt


def create_chart(input_path: Path, output_path: Path) -> None:
    if not input_path.exists():
        raise FileNotFoundError(f"Input JSON file not found: {input_path}")

    with input_path.open("r", encoding="utf-8") as json_file:
        data = json.load(json_file)

    if not isinstance(data, list):
        raise ValueError("JSON must contain a list of device summary objects.")

    devices = [item["device_id"] for item in data]
    temperatures = [float(item["average_temperature"]) for item in data]

    fig, ax = plt.subplots(figsize=(9, 5))
    if devices:
        bars = ax.bar(devices, temperatures)
        ax.bar_label(bars, fmt="%.2f", padding=3)
    else:
        ax.text(0.5, 0.5, "No devices to display", ha="center", va="center",
                transform=ax.transAxes)
    ax.set_title("Average Temperature by Device")
    ax.set_xlabel("Device ID")
    ax.set_ylabel("Average Temperature (°C)")
    ax.grid(axis="y", linestyle="--", alpha=0.35)
    ax.set_axisbelow(True)
    plt.xticks(rotation=25, ha="right")
    fig.tight_layout()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close(fig)


def main() -> int:
    parser = argparse.ArgumentParser(description="Plot average device temperatures from JSON.")
    parser.add_argument("--input", default="output.json", help="Path to summary JSON")
    parser.add_argument("--output", default="temperature_chart.png", help="Path for chart PNG")
    args = parser.parse_args()
    try:
        create_chart(Path(args.input), Path(args.output))
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    print(f"Chart saved to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
