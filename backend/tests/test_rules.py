import pytest

from app.services.rules import (
    blocked_by_guardrail,
    decide,
    feasibility,
    inconclusive,
    rule_r2_blocked,
    winner,
)


def test_winner_requires_minimum_sample_and_significance():
    assert winner(100, 100, 0.05, 0.12, 0.08)
    assert not winner(99, 100, 0.01, 0.12, 0.08)


def test_guardrail_blocks_without_approval_or_over_cap():
    assert blocked_by_guardrail(0, 100, False)
    assert blocked_by_guardrail(101, 100, True)
    assert not blocked_by_guardrail(100, 100, True)
    assert rule_r2_blocked(800, 1000, True) is False
    assert rule_r2_blocked(1200, 1000, True) is True


def test_inconclusive_requires_maximum_sample():
    assert inconclusive(200, 200, 0.20)
    assert not inconclusive(199, 200, 0.20)


@pytest.mark.parametrize(
    ("sample_size", "n_min", "n_max", "p_value", "treatment", "control", "expected"),
    [
        (300, 291, 600, 0.0047, 0.30, 0.20, "WINNER_CONFIRMED"),
        (290, 291, 600, 0.0054, 0.30, 0.20, "RUNNING"),
        (291, 291, 600, 0.05, 0.30, 0.20, "WINNER_CONFIRMED"),
        (400, 291, 400, 0.3018, 0.23, 0.20, "INCONCLUSIVE"),
        (250, 291, 250, 0.20, 0.30, 0.20, "INCONCLUSIVE"),
        (300, 291, 600, 0.0047, 0.20, 0.30, "CONTROL_WINS"),
    ],
)
def test_decide_vectors(
    sample_size, n_min, n_max, p_value, treatment, control, expected
):
    assert decide(sample_size, n_min, n_max, p_value, 0.05, treatment, control) == expected


def test_decide_handles_missing_data():
    assert decide(0, 291, 600, None, 0.05, 0.3, 0.2) == "INSUFFICIENT_DATA"


def test_feasibility_vectors():
    assert feasibility(1500, 5, 2, 291) == {"n_max": 150, "warning": True}
    assert feasibility(1500, 2, 2, 291) == {"n_max": 375, "warning": False}
