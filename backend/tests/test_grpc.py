# -*- coding: utf-8 -*-
import sys
import os
import importlib.util
import grpc

# Load the proto module dynamically
proto_path = os.path.abspath('D:/Documents/energyopti-pro/backend/proto')
if proto_path not in sys.path:
    sys.path.insert(0, proto_path)
print(f"Debug: sys.path = {sys.path}")

# Dynamically import energy_pb2
spec = importlib.util.spec_from_file_location("proto.energy_pb2", os.path.join(proto_path, "energy_pb2.py"))
energy_pb2 = importlib.util.module_from_spec(spec)
sys.modules["proto.energy_pb2"] = energy_pb2
spec.loader.exec_module(energy_pb2)

# Dynamically import energy_pb2_grpc
spec = importlib.util.spec_from_file_location("proto.energy_pb2_grpc", os.path.join(proto_path, "energy_pb2_grpc.py"))
energy_pb2_grpc = importlib.util.module_from_spec(spec)
sys.modules["proto.energy_pb2_grpc"] = energy_pb2_grpc
spec.loader.exec_module(energy_pb2_grpc)

from proto.energy_pb2 import EnergyRequest
from proto.energy_pb2_grpc import EnergyServiceStub

def test_grpc_client():
    with grpc.insecure_channel('127.0.0.1:50052') as channel:
        stub = EnergyServiceStub(channel)
        responses = [response.price for response in stub.StreamEnergyData(EnergyRequest(source='oil'))]
        expected = [75.0, 76.0, 77.0, 78.0, 79.0]
        assert responses == expected, f"Expected {expected}, got {responses}"
        print("gRPC client test passed!")

if __name__ == "__main__":
    test_grpc_client()
