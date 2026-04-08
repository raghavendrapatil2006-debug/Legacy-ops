def _safe_grade(required_phase: int, state=None) -> float:
    try:
        current_phase = int((state or {}).get("current_phase", 0))
        if current_phase >= required_phase:
            return 0.99
        return 0.01
    except Exception:
        return 0.01


def _make_task_grader(required_phase: int):
    def grader(state=None) -> float:
        return _safe_grade(required_phase, state)
    return grader


GRADERS = {
    "phase_1": _make_task_grader(1),
    "phase_2": _make_task_grader(2),
    "phase_3": _make_task_grader(3),
    "phase_4": _make_task_grader(4),
    "phase_5": _make_task_grader(5),
    "phase_6": _make_task_grader(6),
}


def get_grader(task_name: str):
    if task_name not in GRADERS:
        raise KeyError(f"No grader found for task: {task_name}")
    return GRADERS[task_name]