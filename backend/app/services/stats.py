import math
from statistics import NormalDist
from typing import TypedDict


class ZTestResult(TypedDict, total=False):
    insufficient_data: bool
    cvr_control: float
    cvr_treatment: float
    z_score: float
    p_value: float
    normal_approx_warning: bool


_NORMAL = NormalDist()


def norm_cdf(value: float) -> float:
    return 0.5 * math.erfc(-value / math.sqrt(2))


def sample_size_per_variant(
    p_base: float,
    mde_abs: float,
    alpha: float = 0.05,
    power: float = 0.80,
    k: int = 1,
) -> int:
    if not 0 < p_base < 1:
        raise ValueError("p_base must be between 0 and 1")
    if mde_abs <= 0 or p_base + mde_abs >= 1:
        raise ValueError("mde_abs must keep the treatment rate below 1")
    if not 0 < alpha < 1 or not 0 < power < 1:
        raise ValueError("alpha and power must be between 0 and 1")
    if k < 1:
        raise ValueError("k must be at least 1")

    adjusted_alpha = alpha / k
    z_alpha = _NORMAL.inv_cdf(1 - adjusted_alpha / 2)
    z_power = _NORMAL.inv_cdf(power)
    p_treatment = p_base + mde_abs
    numerator = (z_alpha + z_power) ** 2 * (
        p_base * (1 - p_base) + p_treatment * (1 - p_treatment)
    )
    return math.ceil(numerator / (mde_abs**2))


def two_proportion_z_test(
    x_control: int,
    n_control: int,
    x_treatment: int,
    n_treatment: int,
) -> ZTestResult:
    if min(x_control, x_treatment) < 0:
        raise ValueError("conversion counts cannot be negative")
    if x_control > n_control or x_treatment > n_treatment:
        raise ValueError("conversions cannot exceed visitors")
    if min(n_control, n_treatment) <= 0:
        return {"insufficient_data": True}
    p_control = x_control / n_control
    p_treatment = x_treatment / n_treatment
    pooled = (x_control + x_treatment) / (n_control + n_treatment)
    standard_error = math.sqrt(pooled * (1 - pooled) * (1 / n_control + 1 / n_treatment))
    if standard_error == 0:
        return {"insufficient_data": True}
    z_score = (p_treatment - p_control) / standard_error
    return {
        "insufficient_data": False,
        "cvr_control": p_control,
        "cvr_treatment": p_treatment,
        "z_score": z_score,
        "p_value": 2 * (1 - norm_cdf(abs(z_score))),
        "normal_approx_warning": any(
            (
                x_control < 10,
                n_control - x_control < 10,
                x_treatment < 10,
                n_treatment - x_treatment < 10,
            )
        ),
    }
