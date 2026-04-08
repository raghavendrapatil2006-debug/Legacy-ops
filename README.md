---
title: CyberQA
emoji: 🛡️
colorFrom: blue
colorTo: red
sdk: docker
pinned: false
---

# 🛡️ CyberQA: Autonomous Incident Response Benchmark

Welcome to the **CyberQA Evaluation Environment** — an interactive, simulated Linux-style incident response benchmark designed to test an autonomous agent’s ability to reason, inspect system state, and take corrective actions across a multi-step security recovery workflow.

---

## 📜 Incident Summary
At 04:00 AM, the system was compromised. Authentication was bypassed, core configurations were modified, and a persistent backdoor was planted.

Your task is to act as the Incident Response Agent and restore the system to a secure state by progressing through a sequence of incident-response phases. Each phase requires discovering relevant evidence, performing the correct remediation action, and validating that the system has moved to the next stage.

## 🎯 Mission Structure
The benchmark is organized into **6 sequential phases**. Agents must deduce the exact file paths and commands required through exploration.

1. **Reconnaissance:** Discover the first authentication artifact.
2. **Decryption:** Inspect logged payload data and decode it through multiple layers.
3. **Privilege Escalation Review:** Examine system variables for indicators of elevated session state.
4. **Integrity Restoration:** Restore a corrupted web server configuration from a trusted backup.
5. **Access Control Hardening:** Correct overly permissive file permissions on sensitive system files.
6. **Threat Neutralization:** Identify and remove the malicious binary while avoiding benign system files.

## ⚠️ Rules of Engagement & Constraints
* **Format:** Commands must be issued in the expected structured JSON format: `{"command": "cmd", "target": "target"}`.
* **Paths:** Tasks may require using absolute paths if relative paths do not resolve correctly.
* **Progression:** The environment is stateful. Progression between phases depends on successfully completing the required remediation for the current stage.
* **Anti-Reward Hacking:** The evaluation engine tracks state. Agents caught in repetitive, non-progressive action loops will receive point deductions (-0.01). Destructive actions or hallucinated flags incur severe point penalties (-0.05).

---

## 💻 Technical Setup & Evaluation

### Repository Structure
This project is structured to meet the strict requirements of the OpenEnv multi-mode deployment pipeline:

```text
legacy-ops-simulator/
│
├── inference.py                # Main entry point for automated OpenEnv evaluation
├── pyproject.toml              # Strict OpenEnv multi-mode deployment config
├── uv.lock                     # Validated dependency lockfile
├── openenv.yaml                # Task and grader registration
├── README.md                   # Human & UI Documentation
├── AGENT_README.md             # Strict system prompt and rules for the AI
│
├── server/
│   └── app.py                  # OpenEnv API endpoints & Interactive Gradio Dashboard
│
├── assets/
│   └── campaign_config.json    # Static filesystem state and task configurations
│
└── src/
    ├── environment.py          # Backend engine and strict state validation
    ├── models.py               # Pydantic data structures
    └── utils.py                # Helper functions