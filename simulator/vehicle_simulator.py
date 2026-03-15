# This Vehicle Simulator generates and publishes vehicle signals to Kuksa every 2 seconds.
# Acts as the data source for the entire pipeline.

import random
import time

from kuksa_client.grpc import VSSClient
from kuksa_client.grpc import Datapoint

# Connect to Kuksa Data Broker via gRPC
client = VSSClient("127.0.0.1", 55555)
client.connect()

# Brake condition starts at 100% and degrades over time
brake_condition = 100

while True:
    # Simulate gradual brake wear — decreases by 0-2 each cycle
    brake_condition = max(0, brake_condition - random.randint(0, 2))
    brake_pad_wear = 100 - brake_condition

    # Generate VSS-compliant vehicle signals with random values
    signals = {
        "Vehicle.Speed": Datapoint(random.randint(0, 120)),
        "Vehicle.Chassis.Brake.PedalPosition": Datapoint(random.randint(0, 100)),
        "Vehicle.Chassis.Axle.Row1.Wheel.Left.Brake.PadWear": Datapoint(brake_pad_wear),
        "Vehicle.Powertrain.TractionBattery.StateOfCharge.Current": Datapoint(random.randint(50, 100)),
        "Vehicle.Powertrain.CombustionEngine.EngineOil.Temperature": Datapoint(random.randint(70, 120)),
        "Vehicle.Chassis.SteeringWheel.Angle": Datapoint(random.randint(-45, 45)),
    }

    # Publish all signals to Kuksa in one call
    client.set_current_values(signals)
    print("Simulator Sent:", {key: value.value for key, value in signals.items()})
    time.sleep(2)
