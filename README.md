# 🕵️‍♂️ Legacy Ops Simulator

A deterministic, OpenEnv-compliant reinforcement learning environment where an AI agent acts as an incident responder navigating a corrupted legacy server filesystem.

## 📖 Overview
This environment is designed to rigorously test an AI agent's ability to plan, use tools, parse system outputs, and navigate directory structures without the security risks or unpredictability of a live shell environment. The agent must locate a hidden "flag" representing a successful operational recovery outcome.

### 🎯 Key Features
* **100% Deterministic:** Backed by a static JSON virtual filesystem. No live shell execution, no timeouts, no network dependencies.
* **Structured JSON Action Space:** Forces the agent to use strict tool schemas.
* **Granular Reward Function:** +100 for success, +10 for solving clues, -1 per step for efficiency, -5 for hitting decoys or making invalid actions.

---

## 📈 Task Difficulty Progression

The environment contains three built-in tasks defined in `assets/sample_config.json`:

1. **Task 1: Basic Navigation (Easy)**
   * Shallow 3-level directory tree.
   * Tests basic `ls`, `cd`, and `cat` usage.
   * Flag is stored in plaintext.

2. **Task 2: Tool Use & Permissions (Medium)**
   * Introduces barriers and encrypted text.
   * Agent must use the `decode` tool to translate a Base64 string to find a hidden directory.
   * Agent must pass a `password` parameter to bypass a locked directory.

3. **Task 3: Logic & Decoys (Hard)**
   * Complex, deep filesystem tree.
   * Contains "honeypot" decoy log files that penalize the agent.
   * Requires correlating hints from multiple directories and applying string transformations (e.g., reversing text) to deduce passwords.

---

## 🚀 Installation & Setup

1. **Clone the repository and navigate to the root:**
   ```bash
   cd legacy-ops-simulator