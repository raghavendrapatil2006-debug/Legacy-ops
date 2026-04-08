TASKS = [
    {
        "id": "phase1",
        "name": "Phase 1: Recon",
        "description": "Locate the initial fragmented auth flag hidden in the vault.",
        "difficulty": "easy",
        "max_steps": 10,
    },
    {
        "id": "phase2",
        "name": "Phase 2: Crypto",
        "description": "Extract and decode the multi-layer base64/hex payload from the syslog.",
        "difficulty": "easy",
        "max_steps": 12,
    },
    {
        "id": "phase3",
        "name": "Phase 3: Privilege",
        "description": "Inspect the system environment variables to secure the root session.",
        "difficulty": "medium",
        "max_steps": 10,
    },
    {
        "id": "phase4",
        "name": "Phase 4: Integrity",
        "description": "Restore the corrupted nginx.conf file using the clean backup.",
        "difficulty": "medium",
        "max_steps": 12,
    },
    {
        "id": "phase5",
        "name": "Phase 5: Hardening",
        "description": "Lock down the /etc/shadow file permissions to strict 600.",
        "difficulty": "medium",
        "max_steps": 10,
    },
    {
        "id": "phase6",
        "name": "Phase 6: Purge",
        "description": "Quarantine and permanently remove the sysupdater malware binary.",
        "difficulty": "hard",
        "max_steps": 12,
    },
]