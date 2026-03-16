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

## Stop everything

```bash
docker compose down
docker compose -f ditto-docker-compose.yml down
```
## Screenshots

### Docker Services Running
![Docker Compose](Screenshots/docker%20compose%201.png)
![Docker Compose Ditto](Screenshots/Docker%20compose%202.png)

### Vehicle Simulator Publishing Signals
![Vehicle Simulator](Screenshots/vehicle%20sim.png)

### Kuksa Reading Back Signals
![Kuksa Reader](Screenshots/kuksa%20reader.png)

### Zenoh Bridge Forwarding Data
![Zenoh Bridge](Screenshots/zenoh%20bridge.png)

### Zenoh to Ditto Bridge
![Zenoh to Ditto](Screenshots/zenoh%20to%20ditto.png)

### Digital Twin State in Ditto
![Ditto Twin](Screenshots/ditto%20twinning.png)

### Engine Overheating Rule Triggered
![Overheating](Screenshots/overheatting.png)

### OpenSOVD Health Query
![OpenSOVD Query](Screenshots/Screenshot%202026-03-15%20203848.png)

## Contributors

| Name | Contribution |
|---|---|
| Khushi Patel | Kuksa setup, vehicle simulator, report formatting |
| Prabhnoor Saini | Eclipse Ditto setup, digital twin creation, evidence collection |
| Harsh Patel | Eclipse Zenoh bridge, Kuksa-Ditto data transport |
| Lawrence Arryl Lopez | System architecture diagram, sequence diagram |
| Pranav Ashok Chaudhari | Functional modification (Vehicle.Brake.Condition), OpenSOVD integration, GitHub repository management |
