import pytest

from app.services.stats import sample_size_per_variant, two_proportion_z_test


def test_stats_returns_insufficient_data_for_empty_variant():
    assert two_proportion_z_test(0, 0, 1, 10)["insufficient_data"]


def test_stats_returns_rates_and_p_value():
    result = two_proportion_z_test(4, 100, 8, 100)
    assert not result["insufficient_data"]
    assert result["cvr_control"] == 0.04
    assert result["cvr_treatment"] == 0.08
    assert 0 < result["p_value"] < 1


@pytest.mark.parametrize(
    ("p_base", "mde_abs", "alpha", "power", "k", "expected"),
    [
        (0.20, 0.10, 0.05, 0.80, 1, 291),
        (0.10, 0.10, 0.05, 0.80, 1, 197),
        (0.10, 0.05, 0.05, 0.80, 1, 683),
        (0.20, 0.10, 0.05, 0.80, 3, 388),
    ],
)
def test_sample_size_vectors(p_base, mde_abs, alpha, power, k, expected):
    assert sample_size_per_variant(p_base, mde_abs, alpha, power, k) == expected


@pytest.mark.parametrize(
    ("x_control", "n_control", "x_treatment", "n_treatment", "expected_z", "expected_p"),
    [
        (60, 300, 90, 300, 2.8284, 0.0047),
        (80, 400, 92, 400, 1.0327, 0.3018),
        (90, 300, 60, 300, -2.8284, 0.0047),
        (58, 290, 87, 290, 2.7809, 0.0054),
    ],
)
def test_z_test_vectors(
    x_control, n_control, x_treatment, n_treatment, expected_z, expected_p
):
    result = two_proportion_z_test(x_control, n_control, x_treatment, n_treatment)
    assert result["z_score"] == pytest.approx(expected_z, abs=0.001)
    assert result["p_value"] == pytest.approx(expected_p, abs=0.0005)


def test_normal_approximation_warning_is_non_blocking():
    result = two_proportion_z_test(4, 100, 8, 100)
    assert result["normal_approx_warning"]
