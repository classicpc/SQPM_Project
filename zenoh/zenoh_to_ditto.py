import json
import time

import requests
import zenoh

DITTO_URL = "http://localhost:8080/api/2/things/org.vehicle:car1/features/telemetry/properties"
DITTO_AUTH = ("ditto", "ditto")

session = zenoh.open(zenoh.Config())


def listener(sample):
    try:
        payload = sample.payload.to_bytes() if hasattr(sample.payload, "to_bytes") else bytes(sample.payload)
        data = json.loads(payload.decode("utf-8"))
        if data.get("Vehicle.Powertrain.CombustionEngine.EngineOil.Temperature", 0) > 110:
            data["engine_status"] = "OVERHEATING"

        requests.put(DITTO_URL, json=data, auth=DITTO_AUTH, timeout=5)
        print("Sent to Ditto:", data)
    except Exception as error:
        print("Error sending to Ditto:", error)


session.declare_subscriber("vehicle/signals", listener)
print("Zenoh → Ditto bridge listening...")

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("Bridge stopped")
