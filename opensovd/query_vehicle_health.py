# OpenSOVD Query: retrieves the current vehicle health state from the Ditto digital twin.
# Returns all telemetry signals and any active flags (e.g. engine_status = OVERHEATING).

import requests

# Query the full digital twin for car1 via the Ditto REST API (through Nginx)
url = "http://localhost:8080/api/2/things/org.vehicle:car1"
response = requests.get(url, auth=("ditto", "ditto"), timeout=5)
print(response.json())
