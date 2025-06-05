import pytest
import numpy as np

from lab2.calculations_lab2 import calc_rd, find_stabilization


def test_calc_rd_basic():
    u = np.array([1.0, 2.0, 3.0])
    i_mA = np.array([10.0, 20.0, 40.0])
    n = 1.0
    Ut = 0.025
    rows = calc_rd(u, i_mA, n, Ut)
    assert len(rows) == 2

    U0, I0, rd_delta, rd_theor = rows[0]
    assert U0 == pytest.approx(1.0)
    assert I0 == pytest.approx(10.0)
    expected_rd_delta = (2.0 - 1.0) / ((20.0 - 10.0) * 0.001)
    expected_rd_theor = (n * Ut) / (I0 * 0.001)
    assert rd_delta == pytest.approx(expected_rd_delta)
    assert rd_theor == pytest.approx(expected_rd_theor)

    U1, I1, rd_delta1, rd_theor1 = rows[1]
    assert U1 == pytest.approx(2.0)
    assert I1 == pytest.approx(20.0)
    expected_rd_delta1 = (3.0 - 2.0) / ((40.0 - 20.0) * 0.001)
    expected_rd_theor1 = (n * Ut) / (I1 * 0.001)
    assert rd_delta1 == pytest.approx(expected_rd_delta1)
    assert rd_theor1 == pytest.approx(expected_rd_theor1)

def test_calc_rd_zero_current():
    u = np.array([0.0, 1.0])
    i_mA = np.array([0.0, 0.0])
    n = 2.0
    Ut = 0.03
    rows = calc_rd(u, i_mA, n, Ut)
    assert len(rows) == 1
    U0, I0, rd_delta, rd_theor = rows[0]
    assert U0 == pytest.approx(0.0)
    assert I0 == pytest.approx(0.0)
    assert np.isinf(rd_delta)
    assert np.isinf(rd_theor)

@pytest.mark.parametrize("u, i_mA, min_rd, expected_index", [
    (np.array([1.0, 2.0, 3.0]), np.array([10.0, 20.0, 40.0]), 80.0, 1),
    (np.array([1.0, 2.0, 3.0]), np.array([10.0, 20.0, 40.0]), 200.0, 0),
    (np.array([1.0, 2.0, 3.0]), np.array([10.0, 10.0, 20.0]), 90.0, -1),
    (np.array([0.0, 0.5, 1.0]), np.array([0.0, 5.0, 20.0]), 50.0, 1),
])
def test_find_stabilization(u, i_mA, min_rd, expected_index):
    idx = find_stabilization(u, i_mA, min_rd)
    assert idx == expected_index

def test_find_stabilization_empty_or_single():
    assert find_stabilization(np.array([]), np.array([]), min_rd=1.0) == -1
    assert find_stabilization(np.array([1.0]), np.array([5.0]), min_rd=1.0) == -1