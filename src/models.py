from pydantic import BaseModel
from typing import Optional

class AgentAction(BaseModel):
    """The strict schema the AI Agent must follow to interact with the system."""
    command: str
    target: Optional[str] = None
    password: Optional[str] = None

class Observation(BaseModel):
    """The state of the environment returned to the AI Agent after every step."""
    cwd: str
    stdout: str
    stderr: str
    done: bool
    reward: float