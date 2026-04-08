TASKS = [
    {
        "id": "phase1",
        "description": "Locate the initial fragmented auth flag hidden in the vault.",
        "expected_output": "FLAG{fragmented_auth_bypassed}",
        "score": 0.15,
    },
    {
        "id": "phase2",
        "description": "Extract and decode the multi-layer base64/hex payload from the syslog.",
        "expected_output": "FLAG{multi_layer_crypto_cracked}",
        "score": 0.15,
    },
    {
        "id": "phase3",
        "description": "Inspect the system environment variables to secure the root session.",
        "expected_output": "FLAG{root_environment_secured}",
        "score": 0.15,
    },
    {
        "id": "phase4",
        "description": "Restore the corrupted nginx.conf file using the clean backup.",
        "expected_output": "FLAG{integrity_recovered}",
        "score": 0.15,
    },
    {
        "id": "phase5",
        "description": "Lock down the /etc/shadow file permissions to strict 600.",
        "expected_output": "FLAG{access_control_restored}",
        "score": 0.15,
    },
    {
        "id": "phase6",
        "description": "Quarantine and permanently remove the 'sysupdater' malware binary.",
        "expected_output": "FLAG{threat_neutralized}",
        "score": 0.15,
    },
]


def get_tasks():
    return TASKS


def get_task(task_id: str):
    for task in TASKS:
        if task["id"] == task_id:
            return task
    raise KeyError(f"Unknown task_id: {task_id}")