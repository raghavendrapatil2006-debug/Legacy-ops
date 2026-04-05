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
        self.current_phase = 0 # 0=Orientation, 1=Decoding, 2=Investigation

    def reset(self) -> Observation:
        """Starts the campaign from the absolute beginning."""
        self.cwd = "/"
        self.done = False
        self.current_phase = 0
        self.grader = Grader()
        return Observation(
            cwd=self.cwd,
            stdout=f"--- MISSION START ---\n{self.config['global_hint']}",
            stderr="",
            done=self.done,
            reward=self.grader.total_score
        )

    def _get_file_content(self, node):
        if isinstance(node, dict) and "content" in node:
            metadata = node.get("metadata", {})
            if metadata.get("required_phase", 0) > self.current_phase:
                return None, f"ACCESS DENIED: Phase {metadata['required_phase']} clearance required."
            return str(node["content"]), ""
        elif isinstance(node, str):
            return node, ""
        return None, "Path is a directory or does not exist."

    def step(self, action: AgentAction) -> Observation:
        if self.done:
            return Observation(cwd=self.cwd, stdout="", stderr="Mission Complete.", done=True, reward=self.grader.total_score)

        stdout, stderr = "", ""
        
        # --- COMMAND: LS ---
        if action.command == "ls":
            target_path = posixpath.normpath(posixpath.join(self.cwd, action.target or ""))
            node = get_fs_node(self.config["filesystem"], target_path)
            if isinstance(node, dict) and "content" not in node:
                stdout = "\n".join([k for k in node.keys() if k != "metadata"])
            else:
                stderr = f"ls: {action.target}: No such directory"
                
        # --- COMMAND: CD ---
        elif action.command == "cd":
            new_path = posixpath.normpath(posixpath.join(self.cwd, action.target or ""))
            node = get_fs_node(self.config["filesystem"], new_path)
            if node is not None and isinstance(node, dict) and "content" not in node:
                meta = node.get("metadata", {})
                
                req_phase = meta.get("required_phase", 0)
                if req_phase > self.current_phase:
                    stderr = f"ACCESS DENIED: Phase {req_phase} clearance required to enter this zone."
                elif meta.get("locked") and action.password != meta.get("password"):
                    stderr = "AUTH ERROR: Incorrect password for secure directory."
                else:
                    self.cwd = new_path
            else:
                stderr = f"cd: {action.target}: Directory not found"

        # --- COMMAND: CAT ---
        elif action.command == "cat":
            target_path = posixpath.normpath(posixpath.join(self.cwd, action.target or ""))
            node = get_fs_node(self.config["filesystem"], target_path)
            content, err = self._get_file_content(node)
            if content: stdout = content
            else: stderr = f"cat: {action.target}: {err}"

        # --- COMMAND: DECODE ---
        elif action.command == "decode":
            if self.current_phase < 1:
                stderr = "SYSTEM ERROR: 'decode' utility is offline. Unlock Phase 1 to initialize."
            elif not action.target:
                stderr = "decode: No input string provided."
            else:
                try:
                    stdout = base64.b64decode(action.target).decode('utf-8')
                except:
                    stderr = "decode: Invalid Base64 data."

        # --- COMMAND: SUBMIT_FLAG ---
        elif action.command == "submit_flag":
            f = self.config["flags"]
            if action.target == f["phase1"] and self.current_phase == 0:
                self.current_phase = 1
                stdout = "🟢 PHASE 1 COMPLETE. Crypto-tools (decode) are now ONLINE."
            elif action.target == f["phase2"] and self.current_phase == 1:
                self.current_phase = 2
                stdout = "🟢 PHASE 2 COMPLETE. System logs unlocked. Old clues purged."
                
                # FIX 2: Clue Removal - Destroy the old notes so the AI doesn't get confused
                try:
                    del self.config["filesystem"]["var"]["www"]["html"]["hidden_admin"]["admin_notes.txt"]
                except KeyError:
                    pass
                    
            elif action.target == f["phase3"] and self.current_phase == 2:
                self.current_phase = 3
                stdout = "🏁 CAMPAIGN COMPLETE! All mainframes breached."
                self.done = True
            else:
                stderr = "SUBMISSION FAILED: Invalid flag or incorrect sequence."

        # FIX 1: Evaluate the step, but return the CUMULATIVE SCORE to the UI
        self.grader.evaluate_step(stdout, stderr)
        return Observation(cwd=self.cwd, stdout=stdout, stderr=stderr, done=self.done, reward=self.grader.total_score)