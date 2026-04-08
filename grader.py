import re

def evaluate_phase(required_phase, *args, **kwargs):
    try:
        state_dump = str(args) + str(kwargs)
        match = re.search(r"'current_phase':\s*(\d+)", state_dump)
        if match and int(match.group(1)) >= required_phase:
            return 0.99
    except Exception:
        pass
    return 0.01

def grade_phase_1(*args, **kwargs): return evaluate_phase(1, *args, **kwargs)
def grade_phase_2(*args, **kwargs): return evaluate_phase(2, *args, **kwargs)
def grade_phase_3(*args, **kwargs): return evaluate_phase(3, *args, **kwargs)
def grade_phase_4(*args, **kwargs): return evaluate_phase(4, *args, **kwargs)
def grade_phase_5(*args, **kwargs): return evaluate_phase(5, *args, **kwargs)
def grade_phase_6(*args, **kwargs): return evaluate_phase(6, *args, **kwargs)