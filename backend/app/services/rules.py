from math import floor


def rule_r2_blocked(
    proposed_spend: float,
    approved_cap: float,
    has_human_approval: bool,
) -> bool:
    return proposed_spend > approved_cap or not has_human_approval


def blocked_by_guardrail(
    proposed_spend: float,
    approved_cap: float,
    has_human_approval: bool,
) -> bool:
    """Compatibility name for the current API while callers migrate to R2."""
    return rule_r2_blocked(proposed_spend, approved_cap, has_human_approval)


def decide(
    sample_size: int,
    n_min: int,
    n_max: int,
    p_value: float | None,
    alpha_adjusted: float,
    treatment_cvr: float,
    control_cvr: float,
) -> str:
    if p_value is None:
        return "INSUFFICIENT_DATA"
    if sample_size >= n_min and p_value <= alpha_adjusted:
        if treatment_cvr > control_cvr:
            return "WINNER_CONFIRMED"
        if treatment_cvr < control_cvr:
            return "CONTROL_WINS"
    if sample_size >= n_max:
        return "INCONCLUSIVE"
    return "RUNNING"


def feasibility(
    budget_cap: float,
    cost_per_visitor: float,
    number_of_variants: int,
    minimum_sample: int,
) -> dict[str, int | bool]:
    if budget_cap <= 0 or cost_per_visitor <= 0:
        raise ValueError("budget_cap and cost_per_visitor must be positive")
    if number_of_variants < 1:
        raise ValueError("number_of_variants must be at least 1")
    if minimum_sample < 1:
        raise ValueError("minimum_sample must be at least 1")
    n_max = floor(budget_cap / (cost_per_visitor * number_of_variants))
    return {"n_max": n_max, "warning": n_max < minimum_sample}


def winner(
    sample_size: int,
    minimum_sample: int,
    p_value: float,
    treatment_cvr: float,
    control_cvr: float,
) -> bool:
    return decide(
        sample_size,
        minimum_sample,
        minimum_sample,
        p_value,
        0.05,
        treatment_cvr,
        control_cvr,
    ) == "WINNER_CONFIRMED"


def inconclusive(sample_size: int, max_budget_sample: int, p_value: float) -> bool:
    return decide(
        sample_size,
        max_budget_sample,
        max_budget_sample,
        p_value,
        0.05,
        0.0,
        0.0,
    ) == "INCONCLUSIVE"
