from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from stable_baselines3 import PPO
from stable_baselines3.common.env_util import make_vec_env
from app.core.rbac import check_role
from app.db.schemas import User

router = APIRouter()

class PredictRequest(BaseModel):
    env_data: dict

class PredictResponse(BaseModel):
    action: int
    reward_estimate: float

@router.post("/", response_model=PredictResponse)
async def predict_bess(request: PredictRequest, user: User = Depends(check_role("trader"))):
    env = make_vec_env("CustomBESSEnv-v0", n_envs=1)
    model = PPO("MlpPolicy", env)
    obs = request.env_data.get("state", [0.5, 80.0, 100.0])
    action, _ = model.predict(obs)
    _, reward, _, _ = env.step(action)
    return {"action": int(action[0]), "reward_estimate": float(reward)}