import gradio as gr
import json
import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel

# Import your specific environment and actions
from src.environment import LegacyOpsEnv
from src.models import AgentAction

# =====================================================================
# 1. INITIALIZE FASTAPI & ENVIRONMENT
# =====================================================================
app = FastAPI(title="Legacy Ops OpenEnv Server")
env = LegacyOpsEnv(config_path="assets/campaign_config.json")

# Define strict Pydantic schemas for the Evaluator Bot
class StepAction(BaseModel):
    command: str
    target: str = ""

# =====================================================================
# 2. STRICT OPENENV API ENDPOINTS (For the Automated Hackathon Judge)
# =====================================================================
@app.post("/reset")
def api_reset():
    """Strict OpenEnv /reset endpoint"""
    obs = env.reset()
    return {
        "observation": {
            "cwd": getattr(obs, "cwd", ""),
            "stdout": getattr(obs, "stdout", ""),
            "stderr": getattr(obs, "stderr", ""),
            "current_phase": getattr(env, "current_phase", 1)
        },
        "info": {}
    }

@app.post("/step")
def api_step(action: StepAction):
    """Strict OpenEnv /step endpoint"""
    agent_act = AgentAction(command=action.command, target=action.target)
    obs = env.step(agent_act, {"command": action.command, "target": action.target})
    
    return {
        "observation": {
            "cwd": getattr(obs, "cwd", ""),
            "stdout": getattr(obs, "stdout", ""),
            "stderr": getattr(obs, "stderr", ""),
            "current_phase": getattr(env, "current_phase", 1)
        },
        "reward": float(getattr(obs, "reward", 0.0)),
        "done": getattr(obs, "done", getattr(env, "done", False)),
        "info": {}
    }

# =====================================================================
# 3. GRADIO UI (For You / Human Testing)
# =====================================================================
def execute_step_ui(action_json_str):
    try:
        action_json = json.loads(action_json_str)
        cmd = action_json.get("command", "")
        tgt = action_json.get("target", "")
        
        act = AgentAction(command=cmd, target=tgt)
        obs = env.step(act, action_json)
        
        obs_dict = {
            "cwd": getattr(obs, "cwd", ""), 
            "stdout": getattr(obs, "stdout", ""), 
            "stderr": getattr(obs, "stderr", "")
        }
        reward = float(getattr(obs, "reward", 0.0))
        done = getattr(obs, "done", getattr(env, "done", False))
        
        return f"**Reward:** {reward} &nbsp;&nbsp;|&nbsp;&nbsp; **Done:** {done}", json.dumps(obs_dict, indent=2)
    except Exception as e:
        return f"**Error**", str(e)

def reset_env_ui():
    obs = env.reset()
    obs_dict = {
        "cwd": getattr(obs, "cwd", ""), 
        "stdout": getattr(obs, "stdout", ""), 
        "stderr": getattr(obs, "stderr", "")
    }
    return "**Reward:** 0.0 &nbsp;&nbsp;|&nbsp;&nbsp; **Done:** False", json.dumps(obs_dict, indent=2)

# Build the visual layout
with gr.Blocks(title="Legacy Ops Testing UI", css=".gradio-container {max-width: 1400px !important;}") as demo:
    gr.Markdown("### 🛡️ Legacy Ops Human Testing Panel")
    
    with gr.Row():
        with gr.Column(scale=1):
            action_input = gr.Code(
                label="Action (JSON format)", 
                language="json", 
                value='{\n  "command": "ls",\n  "target": "/"\n}'
            )
            with gr.Row():
                step_btn = gr.Button("Step", variant="primary")
                reset_btn = gr.Button("Reset", variant="secondary")
                
        with gr.Column(scale=2):
            header = gr.Markdown("**Reward:** 0.0 &nbsp;&nbsp;|&nbsp;&nbsp; **Done:** False")
            output_box = gr.Code(label="Observation State", language="json", interactive=False)
            
    # Wire up the buttons
    step_btn.click(fn=execute_step_ui, inputs=[action_input], outputs=[header, output_box])
    reset_btn.click(fn=reset_env_ui, inputs=[], outputs=[header, output_box])
    demo.load(fn=reset_env_ui, inputs=[], outputs=[header, output_box])

# Mount the Gradio UI directly onto the root path ("/") so it loads instantly
app = gr.mount_gradio_app(app, demo, path="/")

# =====================================================================
# 4. SERVER LAUNCHER
# =====================================================================
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=7860)