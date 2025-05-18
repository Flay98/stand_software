import pytest
import numpy as np

from lab9.calculations_lab9 import compute_s_values, compute_resistances

# Тесты для compute_s_values

def test_compute_s_values_empty_and_single():
    # Меньше двух точек — всегда пустой список
    assert compute_s_values(np.array([]), np.array([]), threshold=0.1) == []
    assert compute_s_values(np.array([1.0]), np.array([2.0]), threshold=0.1) == []

def test_compute_s_values_basic():
    # Простой случай с двумя интервалами
    Ube = np.array([0.0, 0.2, 0.5])
    Ic  = np.array([0.0, 2.0, 5.0])
    S = compute_s_values(Ube, Ic, threshold=0.1)
    # dU=0.2→dI=2 → 2/0.2=10; dU=0.3→dI=3 → 3/0.3=10
    assert S == [pytest.approx(10.0), pytest.approx(10.0)]

def test_compute_s_values_threshold_skips_small():
    # Первый интервал dU=0.05<0.1 пропускается, затем два валидных
    Ube = np.array([0.0, 0.05, 0.2, 0.55])
    Ic  = np.array([0.0, 1.0, 3.0, 6.0])
    S = compute_s_values(Ube, Ic, threshold=0.1)
    # Интервал 0: пропуск;
    # 1→2: dU=0.15→dI=2 → 2/0.15≈13.333
    # 2→3: dU=0.35→dI=3 → 3/0.35≈8.571
    expected = [2/0.15, 3/0.35]
    assert S[0] == pytest.approx(expected[0])
    assert S[1] == pytest.approx(expected[1])

# Тесты для compute_resistances

@pytest.mark.parametrize("data, v_ohm_low, v_ohm_high, v_dyn_low, v_dyn_high, min_dI_ohm, min_dI_dyn, expected", [
    # Оба сопротивления рассчитываем корректно
    (
        [(1.0, 10.0, 20.0, 30.0, 60.0)],
        0.1, 0.5, 6.0, 9.0, 0.005, 0.01,
        [(1.0, 40.0, 100.0)]
    ),
    # Ни одно сопротивление не считается (дельты тока малы)
    (
        [(2.0, 10.0, 10.0, 50.0, 50.0)],
        0.1, 0.5, 6.0, 9.0, 0.01, 0.01,
        [(2.0, None, None)]
    ),
    # Только R_ohm считается
    (
        [(3.0, 5.0, 15.0, 50.0, 50.0)],
        0.1, 0.5, 6.0, 9.0, 0.005, 0.01,
        [(3.0, 40.0, None)]
    ),
    # Только R_dyn считается
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
