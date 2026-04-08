import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel

from src.environment import LegacyOpsEnv
from src.tasks import TASKS

app = FastAPI(title="CyberQA API")
env = LegacyOpsEnv()

class Action(BaseModel):
    command: str = ""
    target: str = ""

@app.get("/")
def health():
    return {"status": "ok", "name": "cyberqa"}

@app.get("/tasks")
def list_tasks():
    return TASKS

@app.post("/reset")
def reset():
    observation = env.reset()
    return {
        "observation": observation,
        "info": {}
    }

@app.post("/step")
def step(action: Action):
    observation, reward, done, info = env.step(action)
    return {
        "observation": observation,
        "reward": float(reward),
        "done": bool(done),
        "info": info
    }

@app.get("/state")
def state():
    return {
        "observation": {
            "cwd": env.cwd,
            "stdout": env.stdout,
            "stderr": env.stderr,
            "current_phase": env.current_phase
        },
        "reward": float(env.reward),
        "done": bool(env.done),
        "info": {
            "total_reward": float(env.total_reward)
        }
    }

def main():
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    main()