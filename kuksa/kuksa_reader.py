from kuksa_client.grpc import VSSClient

client = VSSClient("127.0.0.1", 55555)
client.connect()

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
