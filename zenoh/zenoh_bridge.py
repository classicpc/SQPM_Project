# Zenoh Bridge: reads signals from Kuksa every 2 seconds,
# derives the Brake.Condition value, and publishes all signals as JSON to the Zenoh router.

import json
import time

import zenoh
from kuksa_client.grpc import VSSClient

# Connect to Kuksa Data Broker via gRPC
client = VSSClient("127.0.0.1", 55555)
client.connect()

# Open a Zenoh session and declare a publisher on the vehicle/signals topic
session = zenoh.open(zenoh.Config())
pub = session.declare_publisher("vehicle/signals")

while True:
    # Poll Kuksa for the latest 6 VSS signal values
    datapoints = client.get_current_values(
        [
            "Vehicle.Speed",
            "Vehicle.Chassis.Brake.PedalPosition",
            "Vehicle.Chassis.Axle.Row1.Wheel.Left.Brake.PadWear",
            "Vehicle.Powertrain.TractionBattery.StateOfCharge.Current",
            "Vehicle.Powertrain.CombustionEngine.EngineOil.Temperature",
            "Vehicle.Chassis.SteeringWheel.Angle",
        ]
    )

    values = {
        path: datapoint.value if hasattr(datapoint, "value") else datapoint
        for path, datapoint in datapoints.items()
    }

    # Derive Brake.Condition as the inverse of pad wear (100 = new, 0 = fully worn)
    pad_wear = values.get("Vehicle.Chassis.Axle.Row1.Wheel.Left.Brake.PadWear")
    if isinstance(pad_wear, (int, float)):
        values["Vehicle.Brake.Condition"] = max(0, 100 - pad_wear)

    # Publish all signals (including derived Brake.Condition) as JSON to Zenoh
    pub.put(json.dumps(values))
    print("Forwarded to Zenoh:", values)
    time.sleep(2)
