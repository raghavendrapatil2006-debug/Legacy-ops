import gradio as gr
import json
from src.environment import LegacyOpsEnv
from src.models import AgentAction

# 1. Initialize the Environment Engine
env = LegacyOpsEnv(config_path="assets/campaign_config.json")

# 2. Try to load the README for the sidebar
try:
    with open("README.md", "r", encoding="utf-8") as f:
        readme_content = f.read()
except FileNotFoundError:
    readme_content = "*README.md not found. Please create it in the root directory.*"

# 3. Helper Function: Format outputs exactly like OpenEnv
def format_openenv_response(obs, msg="Step complete."):
    """Formats the environment state into a strict OpenEnv JSON response."""
    response_dict = {
        "observation": {
            "cwd": obs.cwd,
            "stdout": obs.stdout,
            "stderr": obs.stderr,
            "current_phase": env.current_phase
        },
        "reward": float(obs.reward),
        "done": obs.done
    }
    
    # The top header text
    header_str = f"**Reward:** {obs.reward} &nbsp;&nbsp;|&nbsp;&nbsp; **Done:** {obs.done}"
    # The raw JSON string for the code box
    raw_json_str = json.dumps(response_dict, indent=2)
    
    return header_str, msg, raw_json_str

# 4. Core API Functions
def execute_step(action_json_str):
    try:
        # Parse JSON string from UI to dict
        action_json = json.loads(action_json_str)
        cmd = action_json.get("command", "")
        tgt = action_json.get("target", "")
    except Exception as e:
        # Gracefully handle bad JSON from humans or AI
        error_dict = {
            "observation": {"cwd": env.cwd, "stdout": "", "stderr": f"SYSTEM ERROR: Invalid JSON. {str(e)}", "current_phase": env.current_phase},
            "reward": env.grader.total_score,
            "done": env.done
        }
        header = f"**Reward:** {env.grader.total_score} &nbsp;&nbsp;|&nbsp;&nbsp; **Done:** {env.done}"
        return header, "Error: Invalid JSON input.", json.dumps(error_dict, indent=2)

    action = AgentAction(command=cmd, target=tgt)
    
    # Execute step: Pass BOTH the action object and the raw dictionary 
    # to the backend so grader.py can check for repeated commands!
    obs = env.step(action, action_json)
    
    return format_openenv_response(obs, "Step complete.")

def reset_env():
    obs = env.reset()
    return format_openenv_response(obs, "Environment reset to initial state.")

def get_state():
    """Returns the current state without taking an action (Get State button)"""
    mock_dict = {
        "observation": {"cwd": env.cwd, "stdout": "[State retrieved - No action taken]", "stderr": "", "current_phase": env.current_phase},
        "reward": float(env.grader.total_score),
        "done": env.done
    }
    header = f"**Reward:** {env.grader.total_score} &nbsp;&nbsp;|&nbsp;&nbsp; **Done:** {env.done}"
    return header, "State retrieved.", json.dumps(mock_dict, indent=2)


# 5. Build the OpenEnv-Style Interface
with gr.Blocks(title="CyberQA Agentic Environment", css=".gradio-container {max-width: 1400px !important;}") as demo:
    
    with gr.Row():
        # ==============================================================
        # LEFT SIDEBAR (Quick Start & Info)
        # ==============================================================
        with gr.Column(scale=1, variant="panel"):
            gr.Markdown("### Quick Start")
            gr.Markdown("**Connect to this environment**")
            gr.Markdown("""
            Connect from Python using `gradio_client`:
            ```python
            from gradio_client import Client
            client = Client("Raghavendra-2006/Legacy-ops")
            result = client.predict(
                action_json_str, 
                api_name="/step"
            )
            ```
            """)
            
            gr.Markdown("**Contribute to this environment**")
            gr.Markdown("Submit improvements via pull request on the Hugging Face Hub.")
            
            with gr.Accordion("README (Mission Lore & Clues)", open=False):
                gr.Markdown(readme_content)

        # ==============================================================
        # RIGHT MAIN CONSOLE (Execution & Output)
        # ==============================================================
        with gr.Column(scale=3):
            # Top Header (Reward and Done Status)
            reward_done_header = gr.Markdown("**Reward:** 0.0 &nbsp;&nbsp;|&nbsp;&nbsp; **Done:** False")
            
            # Action Input Box
            action_input = gr.Code(
                label="Action (JSON format)",
                language="json",
                value='{\n  "command": "ls",\n  "target": "/"\n}'
            )
            
            # OpenEnv Style Buttons
            with gr.Row():
                step_btn = gr.Button("Step", variant="primary")
                reset_btn = gr.Button("Reset", variant="secondary")
                state_btn = gr.Button("Get state", variant="secondary")
            
            # Status Indicator
            status_indicator = gr.Textbox(label="Status", value="Ready.", interactive=False)
            
            # Raw JSON Response Output
            raw_response_box = gr.Code(
                label="Raw JSON response",
                language="json",
                interactive=False
            )

    # 6. Wire up the functionality & Expose precise API names
    step_btn.click(
        fn=execute_step, 
        inputs=[action_input], 
        outputs=[reward_done_header, status_indicator, raw_response_box],
        api_name="step"
    )
    
    reset_btn.click(
        fn=reset_env, 
        inputs=[], 
        outputs=[reward_done_header, status_indicator, raw_response_box],
        api_name="reset"
    )
    
    state_btn.click(
        fn=get_state, 
        inputs=[], 
        outputs=[reward_done_header, status_indicator, raw_response_box],
        api_name="get_state"
    )

    # Auto-load the initial state on page refresh
    demo.load(
        fn=reset_env, 
        inputs=[], 
        outputs=[reward_done_header, status_indicator, raw_response_box]
    )

if __name__ == "__main__":
    # Changed 127.0.0.1 to 0.0.0.0 so Hugging Face Spaces can access it!
    demo.launch(server_name="0.0.0.0", server_port=7860)