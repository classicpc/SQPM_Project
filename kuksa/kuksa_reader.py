# Kuksa Reader: reads current vehicle signal values from the data broker

from kuksa_client.grpc import VSSClient

# Connect to Kuksa Data Broker via gRPC
client = VSSClient("127.0.0.1", 55555)
client.connect()

# Read the latest values for all 6 VSS signals
values = client.get_current_values(
    [
        "Vehicle.Speed",
        "Vehicle.Chassis.Brake.PedalPosition",
        "Vehicle.Chassis.Axle.Row1.Wheel.Left.Brake.PadWear",
        "Vehicle.Powertrain.TractionBattery.StateOfCharge.Current",
        "Vehicle.Powertrain.CombustionEngine.EngineOil.Temperature",
        "Vehicle.Chassis.SteeringWheel.Angle",
    ]
)

print({path: datapoint.value for path, datapoint in values.items()})
