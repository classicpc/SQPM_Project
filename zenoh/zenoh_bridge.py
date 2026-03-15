import json
import time

import zenoh
from kuksa_client.grpc import VSSClient

client = VSSClient("127.0.0.1", 55555)
client.connect()

session = zenoh.open(zenoh.Config())
pub = session.declare_publisher("vehicle/signals")

while True:
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

    pad_wear = values.get("Vehicle.Chassis.Axle.Row1.Wheel.Left.Brake.PadWear")
    if isinstance(pad_wear, (int, float)):
        values["Vehicle.Brake.Condition"] = max(0, 100 - pad_wear)

    pub.put(json.dumps(values))
    print("Forwarded to Zenoh:", values)
    time.sleep(2)
