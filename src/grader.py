# src/grader.py

def grade_task_1(env, *args, **kwargs):
    """Grader for Task 1 (Phases 1 & 2). Strictly bounded (0, 1)."""
    phase = getattr(env, "current_phase", 0)
    if phase >= 2:
        return 0.99  # Fully complete (but not 1.0)
    elif phase == 1:
        return 0.50  # Partial progress
    return 0.01      # Not started (but not 0.0)

def grade_task_2(env, *args, **kwargs):
    """Grader for Task 2 (Phases 3 & 4). Strictly bounded (0, 1)."""
    phase = getattr(env, "current_phase", 0)
    if phase >= 4:
        return 0.99
    elif phase == 3:
        return 0.50
    return 0.01

def grade_task_3(env, *args, **kwargs):
    """Grader for Task 3 (Phases 5 & 6). Strictly bounded (0, 1)."""
    phase = getattr(env, "current_phase", 0)
    if phase >= 6:
        return 0.99
    elif phase == 5:
        return 0.50
    return 0.01