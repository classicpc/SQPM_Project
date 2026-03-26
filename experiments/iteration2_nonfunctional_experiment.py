import csv
import os
import statistics
import subprocess
import sys
import time
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[1]
DITTO_URL = "http://localhost:8080/api/2/things/org.vehicle:car1/features/telemetry/properties"
AUTH = ("ditto", "ditto")
SAMPLE_INTERVAL_SECONDS = 2
SAMPLES_PER_SCENARIO = 20


def start_process(cmd, env=None):
    return subprocess.Popen(
        cmd,
        cwd=str(ROOT),
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def stop_process(proc):
    if proc.poll() is None:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()


def percentile(values, p):
    if not values:
        return 0.0
    sorted_values = sorted(values)
    idx = int(round((p / 100) * (len(sorted_values) - 1)))
    return float(sorted_values[idx])


def run_scenario(name, enable_faults):
    env = os.environ.copy()
    env["ENABLE_FAULTS"] = "1" if enable_faults else "0"

    processes = [
        start_process([sys.executable, "simulator/vehicle_simulator.py"], env=env),
        start_process([sys.executable, "zenoh/zenoh_bridge.py"]),
        start_process([sys.executable, "zenoh/zenoh_to_ditto.py"]),
    ]

    time.sleep(8)

    latencies = []
    query_success = 0
    stale_samples = 0
    overheat_count = 0
    normal_count = 0
    no_data_count = 0
    prev_speed = None

    for _ in range(SAMPLES_PER_SCENARIO):
        start = time.perf_counter()
        try:
            response = requests.get(DITTO_URL, auth=AUTH, timeout=5)
            latency_ms = (time.perf_counter() - start) * 1000.0
            latencies.append(latency_ms)

            if response.ok:
                query_success += 1
                payload = response.json()
                speed = payload.get("Vehicle.Speed")
                engine_status = payload.get("engine_status")

                if prev_speed is not None and speed == prev_speed:
                    stale_samples += 1
                prev_speed = speed

                if engine_status == "OVERHEATING":
                    overheat_count += 1
                elif engine_status == "NORMAL":
                    normal_count += 1
                elif engine_status == "NO_DATA":
                    no_data_count += 1
        except Exception:
            latencies.append(5000.0)

        time.sleep(SAMPLE_INTERVAL_SECONDS)

    for proc in processes:
        stop_process(proc)

    samples = SAMPLES_PER_SCENARIO
    success_rate = (query_success / samples) * 100.0
    freshness_ratio = ((samples - 1 - stale_samples) / max(1, samples - 1)) * 100.0

    return {
        "scenario": name,
        "samples": samples,
        "avg_latency_ms": round(statistics.mean(latencies), 2) if latencies else 0.0,
        "p95_latency_ms": round(percentile(latencies, 95), 2),
        "query_success_rate_pct": round(success_rate, 2),
        "freshness_ratio_pct": round(freshness_ratio, 2),
        "engine_normal_count": normal_count,
        "engine_overheating_count": overheat_count,
        "engine_no_data_count": no_data_count,
    }


def write_outputs(results):
    docs_dir = ROOT / "docs"
    docs_dir.mkdir(parents=True, exist_ok=True)

    csv_path = docs_dir / "iteration2_nonfunctional_results.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(results[0].keys()))
        writer.writeheader()
        writer.writerows(results)

    md_path = docs_dir / "iteration2_nonfunctional_results.md"
    with md_path.open("w", encoding="utf-8") as f:
        f.write("# Iteration 2 Non-Functional Results\n\n")
        f.write("## Metric: Reliability and API Latency\n\n")
        f.write(
            "The experiment compares two scenarios over identical sampling windows:\n"
            "1) baseline without injected simulator faults,\n"
            "2) Iteration 2 with injected faults enabled.\n\n"
        )
        f.write("| Scenario | Samples | Avg Latency (ms) | P95 Latency (ms) | Query Success Rate (%) | Freshness Ratio (%) | Engine NORMAL | Engine OVERHEATING | Engine NO_DATA |\n")
        f.write("|---|---:|---:|---:|---:|---:|---:|---:|---:|\n")
        for row in results:
            f.write(
                f"| {row['scenario']} | {row['samples']} | {row['avg_latency_ms']} | {row['p95_latency_ms']} | "
                f"{row['query_success_rate_pct']} | {row['freshness_ratio_pct']} | {row['engine_normal_count']} | "
                f"{row['engine_overheating_count']} | {row['engine_no_data_count']} |\n"
            )


if __name__ == "__main__":
    # Assumes Docker services are already up.
    baseline = run_scenario("Baseline (Faults Disabled)", enable_faults=False)
    faults = run_scenario("Iteration 2 (Faults Enabled)", enable_faults=True)
    write_outputs([baseline, faults])
    print("Experiment complete. Outputs:")
    print("- docs/iteration2_nonfunctional_results.csv")
    print("- docs/iteration2_nonfunctional_results.md")
