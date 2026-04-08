def _safe_grade(required_phase, state=None):
    try:
        current_phase = int((state or {}).get("current_phase", 0))
        return 0.99 if current_phase >= required_phase else 0.01
    except Exception:
        return 0.01

def grade_phase_1(state=None): return _safe_grade(1, state)
def grade_phase_2(state=None): return _safe_grade(2, state)
def grade_phase_3(state=None): return _safe_grade(3, state)
def grade_phase_4(state=None): return _safe_grade(4, state)
def grade_phase_5(state=None): return _safe_grade(5, state)
def grade_phase_6(state=None): return _safe_grade(6, state)