from backend.src.services.guards import check_cost_cap, check_step_cap


def test_step_cap_not_exceeded():
    terminated, reason = check_step_cap(5, 20)
    assert terminated is False
    assert reason is None


def test_step_cap_exceeded():
    terminated, reason = check_step_cap(20, 20)
    assert terminated is True
    assert reason == "step_cap"


def test_step_cap_at_boundary():
    terminated, reason = check_step_cap(19, 20)
    assert terminated is False
    assert reason is None


def test_step_cap_zero_max():
    terminated, reason = check_step_cap(1, 0)
    assert terminated is True
    assert reason == "step_cap"


def test_cost_cap_not_exceeded():
    terminated, reason = check_cost_cap(0.10, 0.50)
    assert terminated is False
    assert reason is None


def test_cost_cap_exceeded():
    terminated, reason = check_cost_cap(0.60, 0.50)
    assert terminated is True
    assert reason == "cost_cap"


def test_cost_cap_at_boundary():
    terminated, reason = check_cost_cap(0.50, 0.50)
    assert terminated is False
    assert reason is None


def test_cost_cap_zero_budget():
    terminated, reason = check_cost_cap(0.01, 0.0)
    assert terminated is True
    assert reason == "cost_cap"
