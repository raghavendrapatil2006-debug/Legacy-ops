class Grader:
    def __init__(self):
        self.total_score = 0.0

    def evaluate_step(self, stdout: str, stderr: str):
        reward = -1.0  # Efficiency penalty
        
        if stderr:
            reward -= 4.0  # Mistake penalty
        if "THIS_IS_A_TRAP" in stdout:
            reward -= 10.0 # Honeypot penalty
        if "🟢 PHASE" in stdout:
            reward += 50.0 # Phase milestone
        if "🟢 CAMPAIGN COMPLETE" in stdout:
            reward += 100.0 # Final win

        self.total_score += reward
        return reward