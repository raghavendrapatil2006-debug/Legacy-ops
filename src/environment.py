import json
import posixpath
import base64
from src.models import AgentAction

class LegacyOpsEnv:
    def __init__(self, config_path="assets/campaign_config.json"):
        with open(config_path, "r") as f:
            self.config = json.load(f)
        
        self.filesystem = self.config.get("filesystem", {})
        self.global_hint = self.config.get("global_hint", "System Breach Detected.")
        
        self.expected_flags = [
            "FLAG{fragmented_auth_bypassed}",
            "FLAG{multi_layer_crypto_cracked}",
            "FLAG{root_environment_secured}",
            "FLAG{integrity_recovered}",
            "FLAG{access_control_restored}",
            "FLAG{threat_neutralized}"
        ]
        self.reset()

    def reset(self):
        self.cwd = "/"
        self.stdout = f"--- MISSION START ---\n{self.global_hint}"
        self.stderr = ""
        self.current_phase = 0
        self.total_reward = 0.0
        self.reward = 0.0
        self.done = False
        
        self.nginx_restored = False
        self.shadow_secured = False
        self.malware_removed = False
        return self

    def _get_fs_node(self, path):
        if path in ["/", ""]: return self.filesystem
        parts = [p for p in path.strip("/").split("/") if p]
        curr = self.filesystem
        for p in parts:
            if isinstance(curr, dict) and p in curr: curr = curr[p]
            else: return None
        return curr

    def _get_file_content(self, node):
        if isinstance(node, dict) and "content" in node:
            metadata = node.get("metadata", {})
            if metadata.get("required_phase", 0) > self.current_phase:
                return None, f"ACCESS DENIED: Phase {metadata['required_phase']} required."
            return str(node["content"]), ""
        elif isinstance(node, str): return node, ""
        return None, "Path is a directory or does not exist."

    def step(self, action, raw_json=None):
        if self.done:
            self.stdout, self.stderr, self.reward = "", "Mission Complete.", 0.0
            return self

        cmd = getattr(action, "command", "")
        target = getattr(action, "target", "")
        
        self.stdout, self.stderr = "", ""
        
        # 🟢 Give 0.01 points for every forward step / standard action taken
        step_reward = 0.01  
        
        target_path = posixpath.normpath(posixpath.join(self.cwd, target or "")).lstrip('/')

        if cmd == "ls":
            node = self._get_fs_node(target_path)
            if isinstance(node, dict) and "content" not in node: 
                self.stdout = "\n".join([k for k in node.keys() if k != "metadata"])
            else: self.stderr = f"ls: {target}: No such directory"
                
        elif cmd == "cd":
            node = self._get_fs_node(target_path)
            if node is not None and isinstance(node, dict) and "content" not in node:
                self.cwd = "/" + target_path
            else: self.stderr = f"cd: {target}: Directory not found"

        elif cmd == "cat":
            node = self._get_fs_node(target_path)
            content, err = self._get_file_content(node)
            if content: self.stdout = content
            else: self.stderr = f"cat: {target}: {err}"

        elif cmd == "env":
            if self.current_phase < 2: self.stderr = "SYSTEM ERROR: Env monitoring offline."
            else: self.stdout = "USER=agent\nSHELL=/bin/bash\nROOT_PIN=FLAG{root_environment_secured}\nPATH=/usr/bin\nSESSION=active"

        elif cmd == "decode":
            if self.current_phase < 1: self.stderr = "SYSTEM ERROR: Utility offline."
            else:
                try: self.stdout = base64.b64decode(target).decode('utf-8')
                except: self.stderr = "decode: Invalid Base64 data."
                    
        elif cmd == "cp":
            if "nginx_clean.conf" in target_path and "nginx.conf" in target_path:
                self.nginx_restored = True
                self.stdout = "STATE UPDATE: nginx.conf overwritten. Validation: FLAG{integrity_recovered}"
            else: self.stderr = f"cp: invalid target '{target}'"

        elif cmd == "chmod":
            if "600" in (target or "") and "shadow" in target_path:
                self.shadow_secured = True
                self.stdout = "STATE UPDATE: /etc/shadow secured. Validation: FLAG{access_control_restored}"
            else: self.stderr = "chmod: Invalid permissions or target."

        elif cmd == "rm":
            if "safe_cache" in target_path: self.stderr = "WARNING: Cannot delete safe system file!"
            elif "sysupdater" in target_path:
                self.malware_removed = True
                self.stdout = "STATE UPDATE: Malware removed. Validation: FLAG{threat_neutralized}"
            else: self.stderr = f"rm: cannot remove '{target}'"

        elif cmd == "submit_flag":
            try:
                expected_flag = self.expected_flags[self.current_phase]
                
                if self.current_phase == 3 and not self.nginx_restored:
                    self.stderr = "VALIDATION FAILED: nginx.conf state still corrupted."
                    step_reward = 0.0 # No points for failing constraints
                elif self.current_phase == 4 and not self.shadow_secured:
                    self.stderr = "VALIDATION FAILED: /etc/shadow vulnerable."
                    step_reward = 0.0
                elif self.current_phase == 5 and not self.malware_removed:
                    self.stderr = "VALIDATION FAILED: Malware 'sysupdater' still active."
                    step_reward = 0.0
                
                elif target == expected_flag:
                    # 🟢 Give exactly 0.99 points for a correct answer
                    step_reward = 0.99  
                    
                    self.current_phase += 1
                    self.stdout = f"[SUCCESS] Step {self.current_phase}/6 complete."
                    if self.current_phase >= 6:
                        self.stdout += " 🏆 MISSION SECURED."
                        self.done = True
                else:
                    self.stderr = "SUBMISSION FAILED: Invalid flag."
                    step_reward = 0.0 # No points for a wrong guess
            except IndexError:
                self.stderr = "ERROR: All phases complete."
        else:
            if cmd not in ["grep", "hex_decode"]:
                self.stderr = f"bash: {cmd}: command not found"

        # Apply the rewards
        self.reward = step_reward
        self.total_reward += step_reward
        return self