# -*- coding: utf-8 -*-
import sys
import os

proto_path = os.path.abspath('D:/Documents/energyopti-pro/backend/proto')
if proto_path not in sys.path:
    sys.path.insert(0, proto_path)
print(f"Debug: sys.path = {sys.path}")  # Debug print
from tests.test_grpc.py import *  # Import the test script

if __name__ == '__main__':
    main()  # Assumes test_grpc.py has a main function; adjust if needed
