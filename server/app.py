import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel
import posixpath
import base64

app = FastAPI(title="CyberQA API")

class Action(BaseModel):
    command: str = ""
    target: str = ""

# Game state
env_state = {
    "cwd": "/",
    "stdout": "--- MISSION START ---\nSystem Breach Detected.",
    "stderr": "",
    "current_phase": 0,
    "nginx_restored": False,
    "shadow_secured": False,
    "malware_removed": False,
    "done": False,
    "total_reward": 0.0
}

expected_flags = [
    "FLAG{fragmented_auth_bypassed}",
    "FLAG{multi_layer_crypto_cracked}",
    "FLAG{root_environment_secured}",
    "FLAG{integrity_recovered}",
    "FLAG{access_control_restored}",
    "FLAG{threat_neutralized}"
]

filesystem = {
    "vault": {"hidden_auth.txt": {"content": "FLAG{fragmented_auth_bypassed}"}},
    "var": {"log": {"syslog": {"content": "RkxBR3ttdWx0aV9sYXllcl9jcnlwdG9fY3JhY2tlZH0="}}},
    "etc": {
        "nginx": {"nginx_clean.conf": {"content": "clean"}, "nginx.conf": {"content": "corrupt"}},
        "shadow": {"content": "shadow_file"}
    },
    "usr": {"bin": {"sysupdater": {"content": "malware"}}}
}

def _get_fs_node(path, fs):
    if path in ["/", ""]: return fs
    parts = [p for p in path.strip("/").split("/") if p]
    curr = fs
    for p in parts:
        if isinstance(curr, dict) and p in curr: curr = curr[p]
        else: return None
    return curr

@app.post("/reset")
def reset():
    env_state.update({
        "cwd": "/", "stdout": "--- MISSION START ---\nSystem Breach Detected.",
        "stderr": "", "current_phase": 0, "nginx_restored": False,
        "shadow_secured": False, "malware_removed": False, "done": False
    })
    obs = {"cwd": env_state["cwd"], "stdout": env_state["stdout"], "stderr": env_state["stderr"], "current_phase": 0}
    return {"observation": obs, "info": {}}

@app.post("/step")
def step(action: Action):
    if env_state["done"]:
        obs = {"cwd": env_state["cwd"], "stdout": "", "stderr": "Mission Complete.", "current_phase": env_state["current_phase"]}
        return {"observation": obs, "reward": 0.0, "done": True, "info": {}}

    cmd = action.command
    target = action.target
    env_state["stdout"] = ""
    env_state["stderr"] = ""
    step_reward = -0.01

    target_path = posixpath.normpath(posixpath.join(env_state["cwd"], target or "")).lstrip('/')

    if cmd == "ls":
        node = _get_fs_node(target_path, filesystem)
        if isinstance(node, dict) and "content" not in node:
            env_state["stdout"] = "\n".join([k for k in node.keys() if k != "metadata"])
        else: env_state["stderr"] = f"ls: {target}: No such directory"

    elif cmd == "cd":
        node = _get_fs_node(target_path, filesystem)
        if isinstance(node, dict) and "content" not in node:
            env_state["cwd"] = "/" + target_path
        else: env_state["stderr"] = f"cd: {target}: Directory not found"

    elif cmd == "cat":
        node = _get_fs_node(target_path, filesystem)
        if isinstance(node, dict) and "content" in node:
            env_state["stdout"] = str(node["content"])
        else: env_state["stderr"] = f"cat: {target}: Path is a directory or does not exist."

    elif cmd == "submit_flag":
        try:
            expected = expected_flags[env_state["current_phase"]]
            if target == expected:
                step_reward = 0.99
                env_state["current_phase"] += 1
                env_state["stdout"] = f"[SUCCESS] Step {env_state['current_phase']}/6 complete."
                if env_state["current_phase"] >= 6: env_state["done"] = True
            else:
                env_state["stderr"] = "SUBMISSION FAILED: Invalid flag."
        except IndexError: pass

    obs = {"cwd": env_state["cwd"], "stdout": env_state["stdout"], "stderr": env_state["stderr"], "current_phase": env_state["current_phase"]}
    return {"observation": obs, "reward": step_reward, "done": env_state["done"], "info": {}}

def main():
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    main()