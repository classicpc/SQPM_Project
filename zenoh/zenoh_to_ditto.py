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

        # Backend rule 1: classify engine status from temperature data quality and thresholds
        engine_temp = data.get("Vehicle.Powertrain.CombustionEngine.EngineOil.Temperature")
        if engine_temp is None:
            data["engine_status"] = "NO_DATA"
        elif engine_temp > 110:
            data["engine_status"] = "OVERHEATING"
        else:
            data["engine_status"] = "NORMAL"

        # Backend rule 2: classify brake health from derived brake condition
        brake_condition = data.get("Vehicle.Brake.Condition")
        if isinstance(brake_condition, (int, float)):
            if brake_condition < 20:
                data["brake_status"] = "CRITICAL"
            elif brake_condition < 50:
                data["brake_status"] = "WORN"
            else:
                data["brake_status"] = "OK"

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
