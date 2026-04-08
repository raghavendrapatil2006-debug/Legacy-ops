import gradio as gr
import json
import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel
from src.environment import LegacyOpsEnv
from src.models import AgentAction

app = FastAPI(title="CyberQA OpenEnv Server")
env = LegacyOpsEnv(config_path="assets/campaign_config.json")

class StepAction(BaseModel):
    command: str
    target: str = ""

@app.post("/reset")
def api_reset():
    obs = env.reset()
    obs_dict = {
        "cwd": getattr(obs, "cwd", "/"),
        "stdout": getattr(obs, "stdout", ""),
        "stderr": getattr(obs, "stderr", ""),
        "current_phase": getattr(env, "current_phase", 0)
    }
    return {"observation": obs_dict, "info": {}}

@app.post("/step")
def api_step(action: StepAction):
    agent_act = AgentAction(command=action.command, target=action.target)
    obs = env.step(agent_act, {"command": action.command, "target": action.target})
    
    obs_dict = {
        "cwd": getattr(obs, "cwd", "/"),
        "stdout": getattr(obs, "stdout", ""),
        "stderr": getattr(obs, "stderr", ""),
        "current_phase": getattr(env, "current_phase", 0)
    }
    
    return {
        "observation": obs_dict,
        "reward": float(getattr(obs, "reward", 0.0)),
        "done": getattr(obs, "done", getattr(env, "done", False)),
        "info": {}
    }

MISSION_README = """
### 🎯 THE 3 MAIN TASKS (Graded via Custom Python)
**TASK 1: DISCOVERY** (Phase 1 & 2)
**TASK 2: REMEDIATION** (Phase 3 & 4)
**TASK 3: CLEANUP** (Phase 5 & 6)

### ⚠️ RULES & SCORING
* **Progression:** Submit flags using `{"command": "submit_flag", "target": "FLAG{...}"}`.
* **Task Evaluation:** Backend graders use strict boundaries (0.01 to 0.99) to validate the environment for the Phase 2 judges.
* **In-Game Rewards:** To encourage exploration, every valid command you run awards **+0.01** points. Submitting a correct flag awards **+0.99** points.
"""

def execute_step_ui(action_json_str):
    try:
        action_json = json.loads(action_json_str)
        act = AgentAction(command=action_json.get("command", ""), target=action_json.get("target", ""))
        obs = env.step(act, action_json)
        
        obs_dict = {
            "cwd": getattr(obs, "cwd", "/"),
            "stdout": getattr(obs, "stdout", ""),
            "stderr": getattr(obs, "stderr", "")
        }
        
        step_reward = float(getattr(obs, "reward", 0.0))
        total_score = float(getattr(env, "total_reward", 0.0))
        done = getattr(obs, "done", getattr(env, "done", False))
        
        raw_response = {
            "observation": obs_dict, 
            "step_reward": step_reward, 
            "total_score": total_score, 
            "done": done
        }
        
        header_text = f"**Total Score:** {total_score:.2f} &nbsp;&nbsp;|&nbsp;&nbsp; **Done:** {done}"
        return header_text, "Step complete.", json.dumps(raw_response, indent=2)
    except Exception as e:
        header_text = "**Total Score:** 0.00 &nbsp;&nbsp;|&nbsp;&nbsp; **Done:** False"
        return header_text, "Error.", json.dumps({"error": str(e)}, indent=2)

def reset_env_ui():
    obs = env.reset()
    obs_dict = {
        "cwd": getattr(obs, "cwd", "/"),
        "stdout": getattr(obs, "stdout", ""),
        "stderr": getattr(obs, "stderr", "")
    }
    
    raw_response = {
        "observation": obs_dict,
        "total_score": 0.0,
        "done": False
    }
    
    header_text = "**Total Score:** 0.00 &nbsp;&nbsp;|&nbsp;&nbsp; **Done:** False"
    return header_text, "Environment reset.", json.dumps(raw_response, indent=2)

def get_state_ui():
    state_info = {
        "info": "Current environment state fetched.",
        "current_phase": getattr(env, "current_phase", 0),
        "total_score": float(getattr(env, "total_reward", 0.0))
    }
    return "State retrieved.", json.dumps(state_info, indent=2)

with gr.Blocks(title="CyberQA Agentic Environment", css=".gradio-container {max-width: 1500px !important;}") as demo:
    with gr.Row():
        with gr.Column(scale=1, min_width=400):
            with gr.Accordion("🛡️ CyberQA Mission Briefing", open=True):
                gr.Markdown(MISSION_README)
        with gr.Column(scale=3):
            header = gr.Markdown("**Total Score:** 0.00 &nbsp;&nbsp;|&nbsp;&nbsp; **Done:** False")
            action_input = gr.Code(label="Action Payload", language="json", value='{\n  "command": "ls",\n  "target": "/"\n}', lines=5)
            with gr.Row():
                step_btn = gr.Button("Step", variant="primary")
                reset_btn = gr.Button("Reset", variant="secondary")
                get_state_btn = gr.Button("Get state", variant="secondary")
            status_text = gr.Markdown("Waiting...")
            output_box = gr.Code(label="JSON response", language="json", interactive=False, lines=12)
            
    step_btn.click(fn=execute_step_ui, inputs=[action_input], outputs=[header, status_text, output_box])
    reset_btn.click(fn=reset_env_ui, inputs=[], outputs=[header, status_text, output_box])
    get_state_btn.click(fn=get_state_ui, inputs=[], outputs=[status_text, output_box])
    demo.load(fn=reset_env_ui, inputs=[], outputs=[header, status_text, output_box])

app = gr.mount_gradio_app(app, demo, path="/")

def main():
    """Required main function for OpenEnv multi-mode deployment"""
    uvicorn.run(app, host="0.0.0.0", port=7860)

if __name__ == "__main__":
    main()