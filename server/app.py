import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel
import posixpath
import base64
import json
import gradio as gr

app_api = FastAPI(title="CyberQA Environment V3")

class Action(BaseModel):
    command: str = ""
    target: str = ""

FILESYSTEM = {
    "vault": {"hidden_auth.txt": {"content": "FLAG{recon_complete}"}},
    "var": {"log": {"syslog.bak": {"content": "RkxBR3tjcnlwdG9fZGVjb2RlZH0="}}},
    "root": {"root_flag.txt": {"content": "FLAG{root_accessed}"}},
    "etc": {
        "nginx": {"nginx_clean.conf": {"content": "clean"}, "nginx.conf": {"content": "corrupt"}},
        "shadow": {"content": "shadow_file"}
    },
    "usr": {"bin": {"sysupdater": {"content": "malware"}}}
}

EXPECTED_FLAGS = [
    "FLAG{recon_complete}",
    "FLAG{crypto_decoded}",
    "FLAG{root_accessed}",
    "FLAG{integrity_restored}",
    "FLAG{access_secured}",
    "FLAG{threat_purged}"
]

class GameState:
    def __init__(self):
        self.cwd = "/"
        self.stdout = "--- SYSTEM BREACH DETECTED ---\nInitiate CyberQA Protocol to secure the environment."
        self.stderr = ""
        self.current_phase = 0
        self.steps_taken = 0
        self.destructive_actions = 0
        self.done = False

state = GameState()

def get_node(path):
    if path in ["/", ""]: return FILESYSTEM
    parts = [p for p in path.strip("/").split("/") if p]
    curr = FILESYSTEM
    for p in parts:
        if isinstance(curr, dict) and p in curr: curr = curr[p]
        else: return None
    return curr

@app_api.post("/reset")
def reset():
    global state
    state = GameState()
    return {"observation": {"cwd": state.cwd, "stdout": state.stdout, "stderr": state.stderr, "current_phase": state.current_phase, "steps_taken": state.steps_taken, "destructive_actions": state.destructive_actions}, "info": {}}

@app_api.post("/step")
def step(action: Action):
    global state
    if state.done:
        return {"observation": {"cwd": state.cwd, "stdout": "", "stderr": "Simulation Complete.", "current_phase": state.current_phase, "steps_taken": state.steps_taken, "destructive_actions": state.destructive_actions}, "reward": 0.0, "done": True, "info": {}}

    cmd = action.command.lower()
    target = action.target
    state.stdout = ""
    state.stderr = ""
    state.steps_taken += 1
    reward = 0.01

    target_path = posixpath.normpath(posixpath.join(state.cwd, target or "")).lstrip('/')

    if cmd == "pwd":
        state.stdout = state.cwd

    elif cmd == "ls":
        node = get_node(target_path)
        if isinstance(node, dict) and "content" not in node:
            state.stdout = "\n".join([k for k in node.keys()])
        else: state.stderr = f"ls: {target}: No such directory"

    elif cmd == "cd":
        node = get_node(target_path)
        if isinstance(node, dict) and "content" not in node:
            state.cwd = "/" + target_path
        else: state.stderr = f"cd: {target}: Directory not found"

    elif cmd == "cat":
        node = get_node(target_path)
        if isinstance(node, dict) and "content" in node:
            state.stdout = str(node["content"])
        else: state.stderr = f"cat: {target}: Path is a directory or does not exist."

    elif cmd == "grep":
        try:
            term, filename = target.split(" ", 1)
            file_path = posixpath.normpath(posixpath.join(state.cwd, filename)).lstrip('/')
            node = get_node(file_path)
            if isinstance(node, dict) and "content" in node:
                if term in str(node["content"]):
                    state.stdout = str(node["content"])
                else: state.stdout = ""
            else: state.stderr = f"grep: {filename}: No such file"
        except ValueError:
            state.stderr = "grep: missing operand. Format: grep <term> <file>"

    elif cmd == "decode":
        try: state.stdout = base64.b64decode(target).decode('utf-8')
        except: state.stderr = "decode: Invalid Base64 data."

    elif cmd == "cp":
        if "nginx" in target_path:
            state.stdout = "Integrity restored. Validation signature: FLAG{integrity_restored}"
        else: state.stderr = "cp: missing file operand"

    elif cmd == "chmod":
        if "600" in target and "shadow" in target_path:
            state.stdout = "Access control secured. Validation signature: FLAG{access_secured}"
        else: state.stderr = "chmod: invalid mode"

    elif cmd == "rm":
        if "sysupdater" in target_path:
            state.stdout = "Threat neutralized. Validation signature: FLAG{threat_purged}"
        else: 
            state.stderr = f"rm: cannot remove '{target}': Operation restricted."
            state.destructive_actions += 1

    elif cmd == "submit_flag":
        try:
            if target == EXPECTED_FLAGS[state.current_phase]:
                reward = 0.99
                state.current_phase += 1
                state.stdout = f"[SUCCESS] Milestone {state.current_phase}/6 verified."
                if state.current_phase >= 6: state.done = True
            else:
                state.stderr = "SUBMISSION FAILED: Invalid signature."
                state.destructive_actions += 1
        except IndexError: pass
    else:
        state.stderr = f"bash: {cmd}: command not found"

    obs = {"cwd": state.cwd, "stdout": state.stdout, "stderr": state.stderr, "current_phase": state.current_phase, "steps_taken": state.steps_taken, "destructive_actions": state.destructive_actions}
    return {"observation": obs, "reward": reward, "done": state.done, "info": {}}

# --- GRADIO UI ---
def ui_step(action_str):
    try:
        action_dict = json.loads(action_str)
        action_obj = Action(**action_dict)
    except Exception as e:
        return f"**Reward:** 0.0 | **Done:** {state.done}", "Error: Invalid JSON format.", json.dumps({"error": str(e)}, indent=2)
    
    res = step(action_obj)
    reward_val = res.get("reward", 0.01)
    done_val = res.get("done", False)
    header = f"**Reward:** {reward_val} | **Done:** {done_val}"
    status = "Step complete." if not done_val else "Mission Complete!"
    return header, status, json.dumps(res, indent=2)

def ui_reset():
    res = reset()
    header = "**Reward:** 0.0 | **Done:** False"
    return header, "Environment reset to starting state.", json.dumps(res, indent=2)

def ui_get_state():
    res = {"observation": {"cwd": state.cwd, "stdout": state.stdout, "stderr": state.stderr, "current_phase": state.current_phase, "steps_taken": state.steps_taken}}
    header = f"**Reward:** 0.0 | **Done:** {state.done}"
    return header, "Current state retrieved.", json.dumps(res, indent=2)

with gr.Blocks(theme=gr.themes.Soft()) as demo:
    with gr.Row():
        with gr.Column(scale=1):
            gr.Markdown("### CyberQA Protocol V3\n\n**System breach detected.** Navigate the simulated file system to verify and patch vulnerabilities.")
            with gr.Accordion("Mission Workflow", open=True):
                gr.Markdown("**Phases:**\n1. Recon: Investigate `/vault`.\n2. Crypto: Decode backup in `/var/log`.\n3. Privilege: Verify `/root` access.\n4. Integrity: Restore config in `/etc/nginx`.\n5. Hardening: Restrict `/etc/shadow`.\n6. Purge: Delete `/usr/bin/sysupdater`.\n\n**Commands:** `pwd`, `ls`, `cd`, `cat`, `grep`, `decode`, `cp`, `chmod`, `rm`, `submit_flag`")
        with gr.Column(scale=3):
            header_text = gr.Markdown("**Reward:** 0.0 | **Done:** False")
            action_input = gr.Code(label="Action (JSON format)", language="json", value='{\n  "command": "ls",\n  "target": "/"\n}')
            with gr.Row():
                step_btn = gr.Button("Step", variant="primary")
                reset_btn = gr.Button("Reset")
                state_btn = gr.Button("Get state")
            status_output = gr.Textbox(label="Status")
            json_output = gr.Code(label="Raw JSON response", language="json")

            step_btn.click(fn=ui_step, inputs=action_input, outputs=[header_text, status_output, json_output])
            reset_btn.click(fn=ui_reset, outputs=[header_text, status_output, json_output])
            state_btn.click(fn=ui_get_state, outputs=[header_text, status_output, json_output])

app = gr.mount_gradio_app(app_api, demo, path="/")

def main(): uvicorn.run(app, host="0.0.0.0", port=8000)
if __name__ == "__main__": main()