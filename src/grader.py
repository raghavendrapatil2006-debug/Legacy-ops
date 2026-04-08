# src/grader.py

def grade_task_1(env):
    """Grader for Task 1 (Phases 1 & 2). Returns strictly between 0 and 1."""
    if env.current_phase >= 2:
        return 0.75  # Both steps complete
    elif env.current_phase == 1:
        return 0.25  # Partial completion
    return 0.1       # Not 0.0, per the advice

def grade_task_2(env):
    """Grader for Task 2 (Phases 3 & 4). Returns strictly between 0 and 1."""
    if env.current_phase >= 4:
        return 0.75
    elif env.current_phase == 3:
        return 0.25
    return 0.1

def grade_task_3(env):
    """Grader for Task 3 (Phases 5 & 6). Returns strictly between 0 and 1."""
    if env.current_phase >= 6:
        return 0.75
    elif env.current_phase == 5:
        return 0.25
    return 0.1