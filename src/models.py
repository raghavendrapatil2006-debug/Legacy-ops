from pydantic import BaseModel
from typing import Dict


# -------------------------
# ACTION (input from agent)
# -------------------------
class Action(BaseModel):
    command: str = ""
    target: str = ""


# -------------------------
# OBSERVATION (state output)
# -------------------------
class Observation(BaseModel):
    cwd: str
    stdout: str
    stderr: str
    current_phase: int

    # 🔥 IMPORTANT (for grader)
    tasks_completed: Dict[str, bool]


# -------------------------
# STEP RESPONSE (optional, but clean)
# -------------------------
class StepResponse(BaseModel):
    observation: Observation
    reward: float
    done: bool
    info: Dict


# -------------------------
# RESET RESPONSE (optional)
# -------------------------
class ResetResponse(BaseModel):
    observation: Observation
    info: Dict