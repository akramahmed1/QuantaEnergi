from prophet import Prophet
from stable_baselines3 import PPO
from qiskit import QuantumCircuit

async def load_core_models():
    Prophet()  # Stub load
    PPO("MlpPolicy", "CartPole-v1")  # Stub
    QuantumCircuit(1)  # Stub
    print("AI models loaded")