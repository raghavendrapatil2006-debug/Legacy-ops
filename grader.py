def _clamp(score: float) -> float:
    if score <= 0.0:
        return 0.01
    if score >= 1.0:
        return 0.99
    return float(score)


def grade_phase1(obs, **kwargs):
    return _clamp(0.99 if obs.get("tasks_completed", {}).get("phase1") else 0.01)

def grade_phase2(obs, **kwargs):
    return _clamp(0.99 if obs.get("tasks_completed", {}).get("phase2") else 0.01)

def grade_phase3(obs, **kwargs):
    return _clamp(0.99 if obs.get("tasks_completed", {}).get("phase3") else 0.01)

def grade_phase4(obs, **kwargs):
    return _clamp(0.99 if obs.get("tasks_completed", {}).get("phase4") else 0.01)

def grade_phase5(obs, **kwargs):
    return _clamp(0.99 if obs.get("tasks_completed", {}).get("phase5") else 0.01)

def grade_phase6(obs, **kwargs):
    return _clamp(0.99 if obs.get("tasks_completed", {}).get("phase6") else 0.01)