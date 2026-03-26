# Iteration 2 Non-Functional Results

## Metric: Reliability and API Latency

The experiment compares two scenarios over identical sampling windows:
1) baseline without injected simulator faults,
2) Iteration 2 with injected faults enabled.

| Scenario | Samples | Avg Latency (ms) | P95 Latency (ms) | Query Success Rate (%) | Freshness Ratio (%) | Engine NORMAL | Engine OVERHEATING | Engine NO_DATA |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Baseline (Faults Disabled) | 20 | 59.71 | 71.3 | 100.0 | 89.47 | 15 | 5 | 0 |
| Iteration 2 (Faults Enabled) | 20 | 51.77 | 72.07 | 100.0 | 100.0 | 17 | 3 | 0 |
