import json
import posixpath
import base64


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
            "FLAG{threat_neutralized}",
        ]
        self.reset()

    def reset(self, task=None):
        self.cwd = "/"
        self.stdout = f"--- MISSION START ---\n{self.global_hint}"
        self.stderr = ""
        self.current_phase = 0
        self.done = False
        self.reward = 0.01
        self.total_reward = 0.01

        self.nginx_restored = False
        self.shadow_secured = False
        self.malware_removed = False

        return self._obs()

    def _obs(self):
        return {
            "cwd": self.cwd,
            "stdout": self.stdout,
            "stderr": self.stderr,
            "current_phase": self.current_phase,
            "tasks_completed": {
                "phase1": self.current_phase >= 1,
                "phase2": self.current_phase >= 2,
                "phase3": self.current_phase >= 3,
                "phase4": self.current_phase >= 4,
                "phase5": self.current_phase >= 5,
                "phase6": self.current_phase >= 6,
            },
        }

    def _get_fs_node(self, path):
        if path in ["/", ""]:
            return self.filesystem
        parts = [p for p in path.strip("/").split("/") if p]
        curr = self.filesystem
        for p in parts:
            if isinstance(curr, dict) and p in curr:
                curr = curr[p]
            else:
                return None
        return curr

    def _file_content(self, node):
        if isinstance(node, dict) and "content" in node:
            return str(node["content"])
        return None

    def step(self, action):
        if self.done:
            self.stdout = ""
            self.stderr = "Mission Complete."
            self.reward = 0.01
            return self._obs(), self.reward, self.done, {}

        cmd = action.get("command", "") if isinstance(action, dict) else getattr(action, "command", "")
        target = action.get("target", "") if isinstance(action, dict) else getattr(action, "target", "")

        self.stdout = ""
        self.stderr = ""
        self.reward = 0.01

        target_path = posixpath.normpath(posixpath.join(self.cwd, target or "")).lstrip("/")

        if cmd == "ls":
            node = self._get_fs_node(target_path)
            if isinstance(node, dict) and "content" not in node:
                self.stdout = "\n".join(k for k in node.keys() if k != "metadata")
            else:
                self.stderr = f"ls: {target}: No such directory"

        elif cmd == "cd":
            node = self._get_fs_node(target_path)
            if isinstance(node, dict) and "content" not in node:
                self.cwd = "/" + target_path if target_path else "/"
            else:
                self.stderr = f"cd: {target}: Directory not found"

        elif cmd == "cat":
            node = self._get_fs_node(target_path)
            content = self._file_content(node)
            if content is not None:
                self.stdout = content
            else:
                self.stderr = f"cat: {target}: Path is a directory or does not exist."

        elif cmd == "decode":
            try:
                raw = base64.b64decode(target).decode("utf-8")
                try:
                    self.stdout = bytes.fromhex(raw).decode("utf-8")
                except Exception:
                    self.stdout = raw
            except Exception:
                self.stderr = "decode: Invalid encoded payload."

        elif cmd == "env":
            self.stdout = (
                "USER=agent\n"
                "SHELL=/bin/bash\n"
                "ROOT_PIN=FLAG{root_environment_secured}\n"
                "PATH=/usr/bin\n"
                "SESSION=active"
            )

        elif cmd == "cp":
            if target == "/mnt/backups/nginx_clean.conf /etc/nginx/nginx.conf":
                self.nginx_restored = True
                self.stdout = "STATE UPDATE: nginx restored. Validation: FLAG{integrity_recovered}"
            else:
                self.stderr = f"cp: invalid target '{target}'"

        elif cmd == "chmod":
            if target == "600 /etc/shadow":
                self.shadow_secured = True
                self.stdout = "STATE UPDATE: /etc/shadow secured. Validation: FLAG{access_control_restored}"
            else:
                self.stderr = "chmod: Invalid permissions or target."

        elif cmd == "rm":
            if target == "/tmp/sysupdater":
                self.malware_removed = True
                self.stdout = "STATE UPDATE: Malware removed. Validation: FLAG{threat_neutralized}"
            elif target == "/tmp/safe_cache.tmp":
                self.stderr = "WARNING: Cannot delete safe system file!"
            else:
                self.stderr = f"rm: cannot remove '{target}'"

        elif cmd == "submit_flag":
            if self.current_phase >= len(self.expected_flags):
                self.stderr = "ERROR: All phases complete."
            else:
                expected = self.expected_flags[self.current_phase]

                if self.current_phase == 3 and not self.nginx_restored:
                    self.stderr = "VALIDATION FAILED: nginx.conf state still corrupted."
                elif self.current_phase == 4 and not self.shadow_secured:
                    self.stderr = "VALIDATION FAILED: /etc/shadow vulnerable."
                elif self.current_phase == 5 and not self.malware_removed:
                    self.stderr = "VALIDATION FAILED: Malware 'sysupdater' still active."
                elif target == expected:
                    self.current_phase += 1
                    self.reward = 0.99
                    self.stdout = f"[SUCCESS] Step {self.current_phase}/6 complete."
                    if self.current_phase >= 6:
                        self.done = True
                        self.stdout += " MISSION SECURED."
                else:
                    self.stderr = "SUBMISSION FAILED: Invalid flag."

        else:
            self.stderr = f"bash: {cmd}: command not found"

        self.total_reward += self.reward
        return self._obs(), self.reward, self.done, {}