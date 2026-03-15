import random
import time

from kuksa_client.grpc import VSSClient
from kuksa_client.grpc import Datapoint

client = VSSClient("127.0.0.1", 55555)
client.connect()

brake_condition = 100

while True:
    brake_condition = max(0, brake_condition - random.randint(0, 2))
    brake_pad_wear = 100 - brake_condition

    signals = {
        "Vehicle.Speed": Datapoint(random.randint(0, 120)),
        "Vehicle.Chassis.Brake.PedalPosition": Datapoint(random.randint(0, 100)),
        "Vehicle.Chassis.Axle.Row1.Wheel.Left.Brake.PadWear": Datapoint(brake_pad_wear),
        "Vehicle.Powertrain.TractionBattery.StateOfCharge.Current": Datapoint(random.randint(50, 100)),
        "Vehicle.Powertrain.CombustionEngine.EngineOil.Temperature": Datapoint(random.randint(70, 120)),
        "Vehicle.Chassis.SteeringWheel.Angle": Datapoint(random.randint(-45, 45)),
    }

    client.set_current_values(signals)
    print("Simulator Sent:", {key: value.value for key, value in signals.items()})
    time.sleep(2)
