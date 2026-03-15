# Zenoh-to-Ditto Bridge — subscribes to vehicle/signals on Zenoh,
# applies the engine overheating rule, and updates the Ditto digital twin via HTTP PUT.

import json
import time

import requests
import zenoh

# Ditto REST API endpoint for the car1 digital twin's telemetry properties
DITTO_URL = "http://localhost:8080/api/2/things/org.vehicle:car1/features/telemetry/properties"
DITTO_AUTH = ("ditto", "ditto")

# Open a Zenoh session to subscribe to incoming signals
session = zenoh.open(zenoh.Config())


def listener(sample):
    try:
        payload = sample.payload.to_bytes() if hasattr(sample.payload, "to_bytes") else bytes(sample.payload)
        data = json.loads(payload.decode("utf-8"))

        # Backend rule: flag engine as OVERHEATING if oil temperature exceeds 110°C
        if data.get("Vehicle.Powertrain.CombustionEngine.EngineOil.Temperature", 0) > 110:
            data["engine_status"] = "OVERHEATING"

        # Send the enriched payload to Ditto via Nginx (authenticated)
        requests.put(DITTO_URL, json=data, auth=DITTO_AUTH, timeout=5)
        print("Sent to Ditto:", data)
    except Exception as error:
        print("Error sending to Ditto:", error)


# Listen for signals on the vehicle/signals topic
session.declare_subscriber("vehicle/signals", listener)
print("Zenoh → Ditto bridge listening...")

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("Bridge stopped")
