import gradio as gr
import json
from src.environment import LegacyOpsEnv
from src.models import AgentAction

def start_mission():
    env = LegacyOpsEnv()
    obs = env.reset()
    return env, 0, format_ui(obs, 0), '{\n  "command": "ls"\n}'

def format_ui(obs, step):
    status = "🟢 CAMPAIGN COMPLETE" if obs.done else "🟡 MISSION ACTIVE"
    md = f"### {status} | Step: {step} | Score: {obs.reward}\n\n"
    md += f"**Current Directory:** `{obs.cwd}`\n\n"
    
    if obs.stdout:
        md += f"**Output:**\n```text\n{obs.stdout}\n```\n\n"
    if obs.stderr:
        md += f"**<span style='color:red;'>Error:</span>**\n```text\n{obs.stderr}\n```\n"
    
    if obs.done:
        md += f"\n# 🏆 Gibson Hacked!\n**Final Score:** {obs.reward} points."
        
    return md

def run_step(env, step_num, action_str):
    if env is None: return env, step_num, "⚠️ Click 'Boot Campaign' first.", action_str
    try:
        action_dict = json.loads(action_str)
        action = AgentAction(**action_dict)
        obs = env.step(action)
        step_num += 1
        return env, step_num, format_ui(obs, step_num), ""
    except json.JSONDecodeError:
        return env, step_num, "⚠️ Invalid JSON format.", action_str
    except Exception as e:
        return env, step_num, f"⚠️ System Error: {str(e)}", action_str

with gr.Blocks(theme=gr.themes.Monochrome()) as demo:
    gr.Markdown("# 🛡️ CyberQA: Campaign Mode")
    env_state = gr.State(None)
    step_state = gr.State(0)

    with gr.Row():
        with gr.Column(scale=1):
            start_btn = gr.Button("🚀 Boot Campaign", variant="primary")
            action_input = gr.Code(language="json", label="Agent Action", value='{\n  "command": "ls"\n}')
            step_btn = gr.Button("⚡ Execute Step")
        with gr.Column(scale=2):
            output_display = gr.Markdown("> Waiting for initialization...")

    start_btn.click(start_mission, inputs=[], outputs=[env_state, step_state, output_display, action_input])
    step_btn.click(run_step, inputs=[env_state, step_state, action_input], outputs=[env_state, step_state, output_display, action_input])

if __name__ == "__main__":
    demo.launch(inbrowser=True)