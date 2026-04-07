import posixpath
import base64
from .models import Observation, AgentAction
from .utils import load_config, get_fs_node
from .grader import Grader

class LegacyOpsEnv:
    def __init__(self, config_path: str = "assets/campaign_config.json"):
        self.config = load_config(config_path)
        self.grader = Grader()
        self.cwd = "/"
        self.done = False
        self.current_phase = 0

    def reset(self) -> Observation:
        self.cwd = "/"
        self.done = False
        self.current_phase = 0
        self.grader.reset()
        return Observation(cwd=self.cwd, stdout=f"--- MISSION START ---\n{self.config.get('global_hint')}", stderr="", done=self.done, reward=self.grader.total_score)

    def _get_file_content(self, node):
        if isinstance(node, dict) and "content" in node:
            metadata = node.get("metadata", {})
            if metadata.get("required_phase", 0) > self.current_phase:
                return None, f"ACCESS DENIED: Phase {metadata['required_phase']} required."
            return str(node["content"]), ""
        elif isinstance(node, str): return node, ""
        return None, "Path is a directory or does not exist."

    def step(self, action: AgentAction, action_json: dict) -> Observation:
        if self.done: return Observation(cwd=self.cwd, stdout="", stderr="Mission Complete.", done=True, reward=self.grader.total_score)

        stdout, stderr = "", ""
        target_path = posixpath.normpath(posixpath.join(self.cwd, action.target or "")).lstrip('/')
        crit_success, crit_fail = False, False

        if action.command == "ls":
            node = get_fs_node(self.config["filesystem"], target_path)
            if isinstance(node, dict) and "content" not in node: stdout = "\n".join([k for k in node.keys() if k != "metadata"])
            else: stderr = f"ls: {action.target}: No such directory"
                
        elif action.command == "cd":
            node = get_fs_node(self.config["filesystem"], target_path)
            if node is not None and isinstance(node, dict) and "content" not in node:
                meta = node.get("metadata", {})
                req_phase = meta.get("required_phase", 0)
                if req_phase > self.current_phase: stderr = f"ACCESS DENIED: Phase {req_phase} required."
                else: self.cwd = "/" + target_path
            else: stderr = f"cd: {action.target}: Directory not found"

        elif action.command == "cat":
            node = get_fs_node(self.config["filesystem"], target_path)
            content, err = self._get_file_content(node)
            if content: stdout = content
            else: stderr = f"cat: {action.target}: {err}"

        elif action.command == "grep":
            parts = (action.target or "").split(" ", 1)
            if len(parts) < 2: stderr = "grep: Missing pattern or path."
            else:
                pattern, file_path = parts[0], parts[1]
                search_path = posixpath.normpath(posixpath.join(self.cwd, file_path)).lstrip('/')
                node = get_fs_node(self.config["filesystem"], search_path)
                content, err = self._get_file_content(node)
                if content:
                    lines = [line for line in content.split('\n') if pattern in line]
                    if lines: stdout = "\n".join(lines)
                else: stderr = f"grep: {file_path}: {err}"

        elif action.command == "env":
            if self.current_phase < 2: stderr = "SYSTEM ERROR: Env monitoring offline."
            else: stdout = "USER=agent\nSHELL=/bin/bash\nROOT_PIN=FLAG{root_environment_secured}\nPATH=/usr/bin\nSESSION=active"

        elif action.command == "decode":
            if self.current_phase < 1: stderr = "SYSTEM ERROR: 'decode' utility offline."
            else:
                try: stdout = base64.b64decode(action.target).decode('utf-8')
                except: stderr = "decode: Invalid Base64 data."
                    
        elif action.command == "hex_decode":
            if self.current_phase < 1: stderr = "SYSTEM ERROR: 'hex_decode' utility offline."
            else:
                try: stdout = bytes.fromhex(action.target).decode('utf-8')
                except: stderr = "hex_decode: Invalid Hexadecimal data."

        elif action.command == "cp":
            if "nginx_clean.conf" in target_path and "nginx.conf" in target_path:
                self.grader.nginx_restored = True
                stdout = "STATE UPDATE: nginx.conf overwritten. Validation: FLAG{integrity_recovered}"
                crit_success = True
            else: stderr = f"cp: invalid operation or target '{action.target}'"

        elif action.command == "chmod":
            if "600" in (action.target or "") and "shadow" in target_path:
                self.grader.shadow_secured = True
                stdout = "STATE UPDATE: /etc/shadow secured. Validation: FLAG{access_control_restored}"
                crit_success = True
            elif "shadow" in target_path:
                stderr = "chmod: Invalid permissions. Shadow requires strict 600."
                crit_fail = True
            else: stderr = f"chmod: cannot access '{action.target}'"

        elif action.command == "rm":
            if "safe_cache" in target_path:
                stderr = "CRITICAL SYSTEM WARNING: Attempted to delete safe system file!"
                crit_fail = True
            elif "sysupdater" in target_path:
                self.grader.malware_removed = True
                stdout = "STATE UPDATE: Malware removed. Validation: FLAG{threat_neutralized}"
                crit_success = True
            else: stderr = f"rm: cannot remove '{action.target}'"

        elif action.command == "submit_flag":
            f = self.config["flags"]
            if action.target == f["phase1"] and self.current_phase == 0:
                self.current_phase = 1
                stdout = "[SUCCESS] PHASE 1 UNLOCKED. Crypto-tools ONLINE."
            elif action.target == f["phase2"] and self.current_phase == 1:
                self.current_phase = 2
                stdout = "[SUCCESS] PHASE 2 UNLOCKED. System env monitoring ONLINE."
            elif action.target == f["phase3"] and self.current_phase == 2:
                self.current_phase = 3
                stdout = "[SUCCESS] PHASE 3 UNLOCKED. Root Access Granted."
            elif action.target == f.get("phase4") and self.current_phase == 3:
                if not self.grader.nginx_restored: stderr = "VALIDATION FAILED: nginx.conf state still corrupted."
                else:
                    self.current_phase = 4
                    stdout = "[SUCCESS] PHASE 4 UNLOCKED. Web services restored."
            elif action.target == f.get("phase5") and self.current_phase == 4:
                if not self.grader.shadow_secured: stderr = "VALIDATION FAILED: /etc/shadow permissions are vulnerable (777)."
                else:
                    self.current_phase = 5
                    stdout = "[SUCCESS] PHASE 5 UNLOCKED. Identity secured."
            elif action.target == f.get("phase6") and self.current_phase == 5:
                if not self.grader.malware_removed: stderr = "VALIDATION FAILED: Malware 'sysupdater' still active."
                else:
                    self.current_phase = 6
                    stdout = "🏆 MISSION ACCOMPLISHED! System is 100% Secure."
                    self.done = True
            else: stderr = "SUBMISSION FAILED: Invalid flag or incorrect sequence."

        self.grader.evaluate_step(stdout, stderr, self.current_phase, action_json, crit_success, crit_fail)
        return Observation(cwd=self.cwd, stdout=stdout, stderr=stderr, done=self.done, reward=self.grader.total_score)