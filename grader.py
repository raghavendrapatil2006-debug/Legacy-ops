# grader.py (PLACE THIS IN THE ROOT FOLDER)

def _safe_grade(required_phase, args, kwargs):
    """Safely extracts the environment state without ever crashing."""
    try:
        # Try to find the environment object passed by the platform
        env = kwargs.get('env') or (args[0] if args else None)
        
        # Check if the agent has completed this phase
        if env and getattr(env, 'current_phase', 0) >= required_phase:
            return 0.99  # Safe upper boundary
    except Exception:
        pass
    
    return 0.01  # Safe lower boundary (not 0.0)

def grade_task_1(*args, **kwargs): return _safe_grade(1, args, kwargs)
def grade_task_2(*args, **kwargs): return _safe_grade(2, args, kwargs)
def grade_task_3(*args, **kwargs): return _safe_grade(3, args, kwargs)
def grade_task_4(*args, **kwargs): return _safe_grade(4, args, kwargs)
def grade_task_5(*args, **kwargs): return _safe_grade(5, args, kwargs)
def grade_task_6(*args, **kwargs): return _safe_grade(6, args, kwargs)