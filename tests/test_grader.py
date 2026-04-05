from src.grader import Grader

def test_correct_flag_submission():
    grader = Grader()
    action = {"command": "submit_flag", "target": "FLAG{test}"}
    obs = {"stdout": "Task Complete", "stderr": ""}
    
    reward = grader.evaluate_step(action, obs, "FLAG{test}")
    
    assert reward == 99.0  # +100 for flag, -1 for step
    assert grader.task_completed is True

def test_incorrect_flag_submission():
    grader = Grader()
    action = {"command": "submit_flag", "target": "WRONG_FLAG"}
    obs = {"stdout": "", "stderr": "Invalid flag"}
    
    reward = grader.evaluate_step(action, obs, "FLAG{test}")
    
    assert reward == -10.0  # -1 for step, -5 for wrong flag, -4 for the generic stderr
    assert grader.task_completed is False

def test_decoding_bonus():
    grader = Grader()
    action = {"command": "decode", "target": "c2VjcmV0"}
    obs = {"stdout": "secret", "stderr": ""}
    
    # First time decoding this specific clue
    reward1 = grader.evaluate_step(action, obs, "FLAG{test}")
    assert reward1 == 9.0  # +10 bonus, -1 step
    
    # Second time decoding the SAME clue (should not get bonus again)
    reward2 = grader.evaluate_step(action, obs, "FLAG{test}")
    assert reward2 == -1.0 # just the step penalty