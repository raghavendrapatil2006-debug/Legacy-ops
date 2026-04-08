def _clamp(score: float) -> float:
    if score <= 0.0:
        return 0.01
    if score >= 1.0:
        return 0.99
    return float(score)


def grade_phase1(observation, **kwargs):
    return _clamp(0.99 if observation.get("tasks_completed", {}).get("phase1", False) else 0.01)


def grade_phase2(observation, **kwargs):
    return _clamp(0.99 if observation.get("tasks_completed", {}).get("phase2", False) else 0.01)


def grade_phase3(observation, **kwargs):
    return _clamp(0.99 if observation.get("tasks_completed", {}).get("phase3", False) else 0.01)


def grade_phase4(observation, **kwargs):
    return _clamp(0.99 if observation.get("tasks_completed", {}).get("phase4", False) else 0.01)


def grade_phase5(observation, **kwargs):
    return _clamp(0.99 if observation.get("tasks_completed", {}).get("phase5", False) else 0.01)


def grade_phase6(observation, **kwargs):
    return _clamp(0.99 if observation.get("tasks_completed", {}).get("phase6", False) else 0.01)


GRADERS = {
    "phase1": grade_phase1,
    "phase2": grade_phase2,
    "phase3": grade_phase3,
    "phase4": grade_phase4,
    "phase5": grade_phase5,
    "phase6": grade_phase6,
}


def get_grader(task_id: str):
    if task_id not in GRADERS:
        raise KeyError(f"No grader for task_id={task_id}")
    return GRADERS[task_id]