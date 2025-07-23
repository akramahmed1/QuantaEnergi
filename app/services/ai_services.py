from prophet import Prophet
from stable_baselines3 import PPO
from qiskit import QuantumCircuit

async def load_core_models():
    # Load forecasting, optimization, and simulation models
    Prophet()
    PPO("MlpPolicy", "CartPole-v1")
    QuantumCircuit(1)
    print("Core models loaded")
