import json

class Grader:
    # Rule: Max reward points available per task for critical success
    MAX_TASK_POINTS = 100.0

    def __init__(self):
        # Reset total score and environmental state flags
        self.reset()

    def reset(self):
        """Resets the Grader's entire internal state."""
        self.total_score = 0.0
        self.nginx_restored = False
        self.shadow_secured = False
        self.malware_removed = False
        # State tracker to prevent unhelpful repetitive loops
        self.previous_action_json = None 
        # State tracker to implement the 100 point per task cap
        self.points_awarded_per_task = {} # Dictionary of phase_num -> points_awarded

    def evaluate_step(self, stdout: str, stderr: str, current_phase: int, action_json: dict, crit_success: bool = False, crit_fail: bool = False):
        """
        Calculates the reward for the step, enforcing the 100pt task cap and preventing unhelpful loops.
        """
        reward_points = 0.0

        # --- Rule 1: Prevent unhelpful repetitive loops ---
        # If the action is identical to the previous one, and no critical event happened, it is non-progressive.
        if not crit_success and not crit_fail:
            # Check if the exact JSON is identical. We must convert back from Python object.
            # Convert to canonical string for reliable dictionary comparison if using dicts
            current_action_str = json.dumps(action_json, sort_keys=True)
            previous_action_str = json.dumps(self.previous_action_json, sort_keys=True) if self.previous_action_json else None
            
            if current_action_str == previous_action_str:
                # If they are just looping the same unhelpful command, reward is zero.
                reward_points = 0.0
                # Early return to not award points below
                self.total_score += reward_points
                return 

        # Update the state tracker for the next step
        self.previous_action_json = action_json

        # --- Rule 2: State-based Task Completion Rewards ---
        # Task flags are worth a strict 100 points, but they are capped per task.
        if crit_success:
            # We enforce that a specific FLAG submission (which should only happen once) is worth 100.
            # To be strict, if they manage to submit the SAME flag twice (perhaps via an exploit), we shouldn't reward it.
            # In our game logic, current_phase should have incremented *before* this call, but let's check current phase state.
            # So the task just solved is current_phase - 1.
            current_task_idx = current_phase - 1
            current_task_score = self.points_awarded_per_task.get(current_task_idx, 0.0)

            if current_task_score + 100.0 <= self.MAX_TASK_POINTS:
                reward_points = 100.0
                # Update task score state
                self.points_awarded_per_task[current_task_idx] = current_task_score + 100.0
            else:
                # Cap points if they would exceed 100 for this task
                remaining_points = self.MAX_TASK_POINTS - current_task_score
                reward_points = remaining_points
                if remaining_points > 0:
                    self.points_awarded_per_task[current_task_idx] = self.MAX_TASK_POINTS
            
        elif "[SUCCESS] PHASE" in stdout:
            # This is the "Flag Accepted" message. Points awarded here were confusing and allowed skipping. 
            # We now only reward for the strict IT tasks (coping, chmod, deleting), not just submitting flags. Zero here.
            reward_points = 0.0
            
        elif "MISSION ACCOMPLISHED" in stdout:
            # Massive un-capped end-game bonus
            reward_points = 500.0
            
        # --- Rule 3: Critical Failures ---
        elif crit_fail:
            # Harsh, standard penalty
            reward_points = -50.0
            
        # --- Rule 4: Validation Blocks ---
        elif "VALIDATION FAILED" in stderr:
            # Trying to cheat a phase gate
            reward_points = -20.0
            
        # --- Rule 5: General Errors ---
        elif stderr:
            # Syntax or path errors
            reward_points = -5.0
            
        # --- Rule 6: Standard Exploration ---
        else:
            # Exploration is good, but repetitive exploration is worthless. 
            # This block is only hit if it wasn't a loop. Give a small reward for a *new* valid move.
            reward_points = 2.0
            
        # Update the total score and return the step reward
        self.total_score += reward_points