# Legacy Ops: Enterprise Agent Benchmark

**Legacy Ops** is a lightweight, pure-state interactive terminal simulator designed specifically for OpenEnv evaluation. It evaluates an AI agent's ability to autonomously perform multi-stage threat mitigation—ranging from basic reconnaissance to advanced Media Forensics—in a mathematically stable, crash-proof environment.

## Requirements
Tests and evaluations will automatically skip or fail if required dependencies aren't installed.

* **Python:** 3.10+
* **Engine:** Docker Desktop or Docker Engine
* **Backend:** FastAPI >= 0.104.0, Uvicorn >= 0.24.0, Pydantic
* **Dashboard UI:** Gradio >= 4.0.0
* *Note: This environment runs entirely in-memory and requires no external OS dependencies or live file system mounts.*

## Core Architecture
The goal of this project is to support a broad set of agentic evaluations without the heavy resource overhead of standard VMs. 

* **Pure-State Engine:** Operates entirely in memory via FastAPI, perfectly mimicking a Linux terminal environment. Deployments are instantaneous and deterministic.
* **Defensive Parsing:** Designed to handle malformed AI-generated JSON payloads and invalid bash commands safely, returning simulated terminal errors rather than triggering 500 Server Errors.
* **Heuristic Fractional Grader:** Moves beyond sparse binary rewards. Agents receive partial positive rewards (+0.2 to +0.3) for logical discovery and tool usage, while receiving penalties (-0.1 to -0.2) for infinite loops, redundant commands, or destructive actions.

## Mission Catalog (The 7-Phase Operation)
Agents must navigate the simulated file system and execute logical workflows to secure the environment. The environment supports the following escalating threat scenarios:

| Phase | Mission Environment | Description |
| :--- | :--- | :--- |
| **Phase 1** | Reconnaissance | Investigate the secure `/vault` and extract the initial system signature. |
| **Phase 2** | Cryptographic Reversal | Locate and decode the obfuscated backup file in `/var/log` using base64. |
| **Phase 3** | Privilege Validation | Navigate to the restricted `/root` directory to verify access controls. |
| **Phase 4** | Integrity Restoration | Identify corrupted web server configs in `/etc/nginx` and restore from clean backups. |
| **Phase 5** | System Hardening | Modify file permissions on the shadow credential file to prevent unauthorized access. |
| **Phase 6** | Threat Neutralization | Locate and permanently delete the unauthorized payload binary. |
| **Phase 7** | Media Forensics | Run `vidscan` on a quarantined executive video to detect AI Tokens (C2PA/SynthID), extract the attacker IP, and update the firewall. |

## Quickstart & Deployment

**Run Locally via Python:**
```bash
pip install fastapi uvicorn pydantic gradio
python server/app.py