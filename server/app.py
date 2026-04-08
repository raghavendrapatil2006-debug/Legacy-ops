import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel
import posixpath
import base64

app = FastAPI(title="CyberQA Environment")

class Action(BaseModel):
    command: str = ""
    target: str = ""

FILESYSTEM = {
    "vault": {"hidden_auth.txt": {"content": "FLAG{fragmented_auth_bypassed}"}},
    "var": {"log": {"syslog.bak": {"content": "RkxBR3ttdWx0aV9sYXllcl9jcnlwdG9fY3JhY2tlZH0="}}},
    "root": {"root_flag.txt": {"content": "FLAG{root_environment_secured}"}},
    "etc": {
        "nginx": {"nginx_clean.conf": {"content": "clean"}, "nginx.conf": {"content": "corrupt"}},
        "shadow": {"content": "shadow_file"}
    },
    "usr": {"bin": {"sysupdater": {"content": "malware"}}}
}

EXPECTED_FLAGS = [
    "FLAG{fragmented_auth_bypassed}",
    "FLAG{multi_layer_crypto_cracked}",
    "FLAG{root_environment_secured}",
    "FLAG{integrity_recovered}",
    "FLAG{access_control_restored}",
    "FLAG{threat_neutralized}"
]

class GameState:
    def __init__(self):
        self.cwd = "/"
        self.stdout = "--- SYSTEM BREACH DETECTED ---\nInitiate CyberQA Protocol to secure the environment."
        self.stderr = ""
        self.current_phase = 0
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

@app.post("/reset")
def reset():
    global state
    state = GameState()
    return {"observation": {"cwd": state.cwd, "stdout": state.stdout, "stderr": state.stderr, "current_phase": state.current_phase}, "info": {}}

@app.post("/step")
def step(action: Action):
    global state
    if state.done:
        return {"observation": {"cwd": state.cwd, "stdout": "", "stderr": "Simulation Complete.", "current_phase": state.current_phase}, "reward": 0.0, "done": True, "info": {}}

    cmd = action.command.lower()
    target = action.target
    state.stdout = ""
    state.stderr = ""
    reward = 0.01

    target_path = posixpath.normpath(posixpath.join(state.cwd, target or "")).lstrip('/')

    if cmd == "ls":
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

    elif cmd == "decode":
        try: state.stdout = base64.b64decode(target).decode('utf-8')
        except: state.stderr = "decode: Invalid Base64 data."

    elif cmd == "cp":
        if "nginx" in target_path:
            state.stdout = "Integrity restored. Validation flag: FLAG{integrity_recovered}"
        else: state.stderr = "cp: missing file operand"

    elif cmd == "chmod":
        if "600" in target and "shadow" in target_path:
            state.stdout = "Access control secured. Validation flag: FLAG{access_control_restored}"
        else: state.stderr = "chmod: invalid mode"

    elif cmd == "rm":
        if "sysupdater" in target_path:
            state.stdout = "Threat neutralized. Validation flag: FLAG{threat_neutralized}"
        else: state.stderr = f"rm: cannot remove '{target}'"

    elif cmd == "submit_flag":
        try:
            expected = EXPECTED_FLAGS[state.current_phase]
            if target == expected:
                reward = 0.99
                state.current_phase += 1
                state.stdout = f"[SUCCESS] Phase {state.current_phase}/6 complete."
                if state.current_phase >= 6: state.done = True
            else:
                state.stderr = "SUBMISSION FAILED: Invalid flag."
        except IndexError: pass
    else:
        state.stderr = f"bash: {cmd}: command not found"

    obs = {"cwd": state.cwd, "stdout": state.stdout, "stderr": state.stderr, "current_phase": state.current_phase}
    return {"observation": obs, "reward": reward, "done": state.done, "info": {}}

def main():
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    main()