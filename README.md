# SDV Pipeline – Iteration 1 (SQPM Project)

End-to-end pipeline:

Vehicle Simulator → Kuksa → Zenoh → Ditto → OpenSOVD-style query

## What this implements

- Core required stack for Iteration 1: **Kuksa + Ditto**
- Middleware layer: **Zenoh**
- Vehicle telemetry simulator in Python
- Digital twin update path into Ditto
- Initial functional modification:
	- Added `Vehicle.Brake.Condition`
	- Basic degradation behavior over time in simulator
	- Backend rule example: engine temp > 110°C marks `engine_status=OVERHEATING`

## Project structure

```text
SQPM_Project/
├── docker-compose.yml
├── ditto-docker-compose.yml
├── requirements.txt
├── nginx.conf
├── nginx-cors.conf
├── nginx.htpasswd
├── simulator/
│   └── vehicle_simulator.py
├── kuksa/
│   └── kuksa_reader.py
├── zenoh/
│   ├── zenoh_bridge.py
│   └── zenoh_to_ditto.py
├── ditto/
│   └── create_digital_twin.sh
└── opensovd/
		└── query_vehicle_health.py
```

## Prerequisites

- Docker Desktop (with Compose)
- Python 3.9+

Install Python dependencies:

```bash
pip install -r requirements.txt
```

Equivalent explicit packages:

```bash
pip install kuksa-client eclipse-zenoh requests
```

## Start infrastructure

From `SQPM_Project`:

```bash
docker compose up -d
docker compose -f ditto-docker-compose.yml up -d
```

## Initialize digital twin

In Git Bash / WSL:

```bash
bash ditto/create_digital_twin.sh
```

Or in PowerShell:

```powershell
Invoke-RestMethod -Method Put -Uri "http://localhost:8080/api/2/things/org.vehicle:car1" -Headers @{Authorization="Basic ZGl0dG86ZGl0dG8="} -ContentType "application/json" -Body '{"attributes":{"vehicleId":"car1"},"features":{"telemetry":{"properties":{"speed":0}}}}'
```

Ditto API auth credentials used by scripts: `ditto` / `ditto` (via nginx on `localhost:8080`).

## Run the pipeline

Open separate terminals in `SQPM_Project`:

1) Start simulator

```bash
python simulator/vehicle_simulator.py
```

2) Start Kuksa → Zenoh bridge

```bash
python zenoh/zenoh_bridge.py
```

3) Start Zenoh → Ditto bridge

```bash
python zenoh/zenoh_to_ditto.py
```

4) Query vehicle health / twin state

```bash
python opensovd/query_vehicle_health.py
```

## Evidence to capture for report

Take screenshots of:

1. `docker compose ps` showing Kuksa, Zenoh, Ditto services running
2. Simulator terminal showing published signals (Speed, Brake.Condition, Battery SoC, Engine Oil Temp, Steering Angle)
3. Kuksa readback via:

```bash
python kuksa/kuksa_reader.py
```

4. Zenoh bridge terminal showing forwarding logs
5. Zenoh → Ditto bridge terminal showing `Sent to Ditto`
6. Twin output from:

```bash
python opensovd/query_vehicle_health.py
```

## Stop everything

```bash
docker compose down
docker compose -f ditto-docker-compose.yml down
```

## Contributors

| Name | Contribution |
|---|---|
| Khushi Patel | Kuksa setup, vehicle simulator, report formatting |
| Prabhnoor Saini | Eclipse Ditto setup, digital twin creation, evidence collection |
| Pranav Ashok Chaudhari | Eclipse Zenoh bridge, Kuksa-Ditto data transport |
| Lawrence Arryl Lopez | System architecture diagram, sequence diagram |
| Harsh Patel | Functional modification (Vehicle.Brake.Condition), OpenSOVD integration, GitHub repository management |
