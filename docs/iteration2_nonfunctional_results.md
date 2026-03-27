# Iteration 2 Non-Functional Results

## Metric: Reliability and API Latency

The experiment compares two scenarios over identical sampling windows:
1) baseline without injected simulator faults,
2) Iteration 2 with injected faults enabled.

| Scenario | Samples | Avg Latency (ms) | P95 Latency (ms) | Query Success Rate (%) | Freshness Ratio (%) | Engine NORMAL | Engine OVERHEATING | Engine NO_DATA |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Baseline (Faults Disabled) | 20 | 59.71 | 71.3 | 100.0 | 89.47 | 15 | 5 | 0 |
| Iteration 2 (Faults Enabled) | 20 | 51.77 | 72.07 | 100.0 | 100.0 | 17 | 3 | 0 |

## Analysis

1. End-to-end reliability stayed stable after the Iteration 2 extension.
Both scenarios achieved a 100 percent query success rate, which shows that the added fault logic did not break data flow from simulator to Ditto.

2. Latency impact was minimal.
Average latency was slightly lower in the fault-enabled run, while P95 latency stayed in the same range. This indicates that the new rule logic and injected signal variations did not introduce noticeable API overhead in this environment.

3. Health-state behavior remained consistent and interpretable.
In both scenarios, engine status values were generated correctly and OVERHEATING states were still detected when high temperatures occurred.

4. Observed differences are expected for stochastic simulation.
Since signal values are random, some metric variation between runs is normal. The key result is that the system remained responsive and produced valid interpreted states under both baseline and fault-enabled operation.

## Conclusion

The Iteration 2 extension improved behavioral realism by introducing controlled signal anomalies while maintaining reliable pipeline operation and stable response characteristics. Overall, the experiment confirms that the architecture supports functional extension without degrading core system availability.
