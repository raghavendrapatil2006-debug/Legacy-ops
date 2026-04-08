def baseline_model(observation):
    stdout = observation.get("stdout", "")

    if "MISSION START" in stdout:
        return {"command": "cat", "target": "/etc/vault/fragment.txt"}

    return {"command": "submit_flag", "target": "FLAG{fragmented_auth_bypassed}"}