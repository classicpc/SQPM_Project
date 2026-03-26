# Vehicle Simulator for Iteration 2:
# publishes baseline signals while injecting periodic faults to validate pipeline robustness.

import random
import time
import os

from kuksa_client.grpc import Datapoint
from kuksa_client.grpc import VSSClient

# Connect to Kuksa Data Broker via gRPC
client = VSSClient("127.0.0.1", 55555)
client.connect()

# Brake condition starts healthy and degrades over time
brake_condition = 100
cycle = 0
prev_steering_angle = 0
enable_faults = os.getenv("ENABLE_FAULTS", "1") not in ("0", "false", "False")

while True:
    cycle += 1

    # Simulate gradual brake wear: decreases by 0-2 each cycle
    brake_condition = max(0, brake_condition - random.randint(0, 2))
    brake_pad_wear = 100 - brake_condition

    speed = random.randint(0, 120)
    brake_pedal = random.randint(0, 100)
    battery_soc = random.randint(50, 100)
    engine_temp = random.randint(70, 120)
    steering_angle = random.randint(-45, 45)

    fault_labels = []

    # Fault 1: noisy brake pedal signal every 10th cycle
    if enable_faults and cycle % 10 == 0:
        brake_pedal = min(100, max(0, brake_pedal + random.randint(-40, 40)))
        fault_labels.append("noisy_brake_pedal")

    # Fault 2: delayed steering signal every 12th cycle (publish previous value)
    if enable_faults and cycle % 12 == 0:
        steering_to_publish = prev_steering_angle
        fault_labels.append("delayed_steering")
    else:
        steering_to_publish = steering_angle

    signals = {
        "Vehicle.Speed": Datapoint(speed),
        "Vehicle.Chassis.Brake.PedalPosition": Datapoint(brake_pedal),
        "Vehicle.Chassis.Axle.Row1.Wheel.Left.Brake.PadWear": Datapoint(brake_pad_wear),
        "Vehicle.Powertrain.TractionBattery.StateOfCharge.Current": Datapoint(battery_soc),
        "Vehicle.Powertrain.CombustionEngine.EngineOil.Temperature": Datapoint(engine_temp),
        "Vehicle.Chassis.SteeringWheel.Angle": Datapoint(steering_to_publish),
    }

    # Fault 3: missing engine temperature update every 8th cycle
    if enable_faults and cycle % 8 == 0:
        signals.pop("Vehicle.Powertrain.CombustionEngine.EngineOil.Temperature")
        fault_labels.append("missing_engine_temp")

    # Publish all currently available signals in one call
    client.set_current_values(signals)

    payload = {key: value.value for key, value in signals.items()}
    payload["cycle"] = cycle
    payload["faults"] = fault_labels if fault_labels else ["none"]
    print("Simulator Sent:", payload)

    prev_steering_angle = steering_angle
    time.sleep(2)
