import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel

from src.environment import LegacyOpsEnv
from grader import (
    grade_phase_1, grade_phase_2, grade_phase_3,
    grade_phase_4, grade_phase_5, grade_phase_6
)

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
        "done": env.done,
        "info": {
            "total_reward": env.total_reward
        }
    }


@app.get("/state")
def state():
    return {
        "cwd": env.cwd,
        "stdout": env.stdout,
        "stderr": env.stderr,
        "current_phase": env.current_phase,
        "total_reward": env.total_reward,
        "done": env.done
    }


# -------------------------
# TASKS ENDPOINT
# -------------------------
@app.get("/tasks")
def tasks():
    return [
        {"id": "phase_1", "difficulty": "easy"},
        {"id": "phase_2", "difficulty": "easy"},
        {"id": "phase_3", "difficulty": "medium"},
        {"id": "phase_4", "difficulty": "medium"},
        {"id": "phase_5", "difficulty": "medium"},
        {"id": "phase_6", "difficulty": "hard"},
    ]


# -------------------------
# GRADER ENDPOINT
# -------------------------
@app.post("/grader")
def grader(req: GradeRequest):
    state = req.state or {}

    if req.task_id == "phase_1":
        score = grade_phase_1(state)
    elif req.task_id == "phase_2":
        score = grade_phase_2(state)
    elif req.task_id == "phase_3":
        score = grade_phase_3(state)
    elif req.task_id == "phase_4":
        score = grade_phase_4(state)
    elif req.task_id == "phase_5":
        score = grade_phase_5(state)
    elif req.task_id == "phase_6":
        score = grade_phase_6(state)
    else:
        score = 0.01

    # 🔒 Clamp strictly between (0,1)
    if score <= 0.0:
        score = 0.01
    if score >= 1.0:
        score = 0.99

    return {"score": float(score)}


# -------------------------
# MAIN ENTRYPOINT (IMPORTANT)
# -------------------------
def main():
    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()