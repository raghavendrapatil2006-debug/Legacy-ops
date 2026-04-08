import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel

from src.environment import LegacyOpsEnv
from grader import get_grader
from src.tasks import TASKS

app = FastAPI(title="CyberQA API")

# Global environment
env = LegacyOpsEnv()


# -------------------------
# MODELS
# -------------------------
class Action(BaseModel):
    command: str = ""
    target: str = ""


class GradeRequest(BaseModel):
    task_id: str
    state: dict | None = None


# -------------------------
# HEALTH CHECK (IMPORTANT)
# -------------------------
@app.get("/")
def health():
    return {"status": "ok", "env": "cyberqa"}


# -------------------------
# ENV ENDPOINTS
# -------------------------
@app.post("/reset")
def reset():
    env.reset()
    return {
        "observation": {
            "cwd": env.cwd,
            "stdout": env.stdout,
            "stderr": env.stderr,
            "current_phase": env.current_phase
        },
        "info": {}
    }


@app.post("/step")
def step(action: Action):
    env.step(action)

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


@app.get("/state")
def state():
    return {
        "cwd": env.cwd,
        "stdout": env.stdout,
        "stderr": env.stderr,
        "current_phase": env.current_phase,
        "total_reward": float(env.total_reward),
        "done": bool(env.done)
    }


# -------------------------
# TASKS ENDPOINT
# -------------------------
@app.get("/tasks")
def list_tasks():
    return {"tasks": TASKS}


# -------------------------
# GRADER ENDPOINT
# -------------------------
@app.post("/grader")
def grader(req: GradeRequest):
    state = req.state or {}

    try:
        grader_fn = get_grader(req.task_id)
        score = float(grader_fn(state))
    except Exception:
        score = 0.01

    # 🔒 Ensure strict (0,1)
    if score <= 0.0:
        score = 0.01
    if score >= 1.0:
        score = 0.99

    return {
        "task_id": req.task_id,
        "score": score
    }


# -------------------------
# MAIN ENTRYPOINT
# -------------------------
def main():
    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()