import pytest
import numpy as np

from lab9.calculations_lab9 import compute_s_values, compute_resistances


def test_compute_s_values_empty_and_single():
    assert compute_s_values(np.array([]), np.array([]), threshold=0.1) == []
    assert compute_s_values(np.array([1.0]), np.array([2.0]), threshold=0.1) == []


def test_compute_s_values_basic():
    Ube = np.array([0.0, 0.2, 0.5])
    Ic = np.array([0.0, 2.0, 5.0])
    S = compute_s_values(Ube, Ic, threshold=0.1)

    assert S == [pytest.approx(10.0), pytest.approx(10.0)]


def test_compute_s_values_threshold_skips_small():
    Ube = np.array([0.0, 0.05, 0.2, 0.55])
    Ic = np.array([0.0, 1.0, 3.0, 6.0])
    S = compute_s_values(Ube, Ic, threshold=0.1)

    expected = [2 / 0.15, 3 / 0.35]
    assert S[0] == pytest.approx(expected[0])
    assert S[1] == pytest.approx(expected[1])


@pytest.mark.parametrize("data, v_ohm_low, v_ohm_high, v_dyn_low, v_dyn_high, min_dI_ohm, min_dI_dyn, expected", [
    (
            [(1.0, 10.0, 20.0, 30.0, 60.0)],
            0.1, 0.5, 6.0, 9.0, 0.005, 0.01,
            [(1.0, 40.0, 100.0)]
    ),
    (
            [(2.0, 10.0, 10.0, 50.0, 50.0)],
            0.1, 0.5, 6.0, 9.0, 0.01, 0.01,
            [(2.0, None, None)]
    ),
    (
            [(3.0, 5.0, 15.0, 50.0, 50.0)],
            0.1, 0.5, 6.0, 9.0, 0.005, 0.01,
            [(3.0, 40.0, None)]
    ),
    (
            [(4.0, 10.0, 10.0, 20.0, 80.0)],
            0.1, 0.5, 6.0, 9.0, 0.01, 0.05,
            [(4.0, None, 50.0)]
    ),
])
def test_compute_resistances_various(
        data, v_ohm_low, v_ohm_high, v_dyn_low, v_dyn_high,
        min_dI_ohm, min_dI_dyn, expected
):
    results = compute_resistances(
        data,
        v_ohm_low, v_ohm_high,
        v_dyn_low, v_dyn_high,
        min_dI_ohm, min_dI_dyn
    )
    assert len(results) == len(expected)
    for (Uzi, R_ohm, R_dyn), (eU, eRo, eRd) in zip(results, expected):
        assert Uzi == pytest.approx(eU)
        if eRo is None:
            assert R_ohm is None
        else:
            assert R_ohm == pytest.approx(eRo)
        if eRd is None:
            assert R_dyn is None
        else:
            assert R_dyn == pytest.approx(eRd)
