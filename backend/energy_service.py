import grpc
from concurrent import futures
import sys
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

sys.path.append(os.path.join(os.path.dirname(__file__), 'proto'))
import energy_pb2
import energy_pb2_grpc

class EnergyService(energy_pb2_grpc.EnergyServiceServicer):
    def StreamEnergyData(self, request, context):
        try:
            for i in range(5):
                price = 75.0 + i
                yield energy_pb2.EnergyResponse(price=price)
                logger.info(f"Sent price: {price}")
        except Exception as e:
            logger.error(f"Error in StreamEnergyData: {e}")
            context.set_details(f"Error: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    energy_pb2_grpc.add_EnergyServiceServicer_to_server(EnergyService(), server)
    server.add_insecure_port('127.0.0.1:50052')
    logger.info("Starting gRPC server on 127.0.0.1:50052")
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    serve()
