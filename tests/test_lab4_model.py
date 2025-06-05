import pytest
import numpy as np

from lab4.calculations_lab4 import (
    find_stabilization_index,
    calc_stabilization_coefficients,
    compute_stabilization_coefficient,
    input_power,
    output_power,
    efficiency,
    stabilization_current,
    compute_stabilizer_metrics
)

@pytest.mark.parametrize("u_load, threshold, expected", [
    (np.array([1.0, 1.01, 1.5]), 0.02, 0),
    (np.array([0.0, 5.05, 5.1, 6.0]), 0.05, 1),
    (np.array([0.0, 0.3, 0.6]), 0.1, -1),
    (np.array([]), 0.1, -1),
    (np.array([5.0]), 0.1, -1),
])
def test_find_stabilization_index(u_load, threshold, expected):
    assert find_stabilization_index(u_load, threshold) == expected


def test_calc_stabilization_coefficients_basic():
    u_pit = np.array([1.0, 2.0, 3.0, 4.0])
    u_load = np.array([0.0, 0.0, 1.0, 1.5])
    start = 1
    k_vals = calc_stabilization_coefficients(u_pit, u_load, start)
    assert len(k_vals) == 2
    assert pytest.approx(k_vals[0], rel=1e-6) == (1/2.5)/(1/0.5)
    assert pytest.approx(k_vals[1], rel=1e-6) == (1/3.5)/(0.5/1.25)


def test_compute_stabilization_coefficient_errors():

    with pytest.raises(ValueError):
        compute_stabilization_coefficient([1.0], [1.0], min_points=2, threshold=0.1)

    u_p = [1,2,3]
    u_l = [10,20,30]
    with pytest.raises(ValueError):
        compute_stabilization_coefficient(u_p, u_l, min_points=3, threshold=0.01)

    u_p = [1,2,3,4]
    u_l = [1,1,1,1]
    with pytest.raises(ValueError):
        compute_stabilization_coefficient(u_p, u_l, min_points=4, threshold=0.1)

def test_compute_stabilization_coefficient_success():

    u_p = [1.0, 2.0, 3.0]

    u_l = [0.0, 0.2, 0.3]
    start, ks, avg = compute_stabilization_coefficient(u_p, u_l, min_points=3, threshold=0.1)
    assert start == 1
    assert ks[0] == pytest.approx(0.33333333)
    assert avg == pytest.approx(0.6666666)


def test_power_and_efficiency():
    assert input_power(5.0, 20.0) == pytest.approx(0.1)   # 5*20mA=100mW=0.1W
    assert output_power(3.0, 10.0) == pytest.approx(0.03)
    assert efficiency(0.1, 0.03) == pytest.approx(0.3)
    assert efficiency(0.0, 1.0) == 0.0
    assert stabilization_current(10.0, 7.5) == pytest.approx(2.5)


def test_compute_stabilizer_metrics_errors():
    with pytest.raises(ValueError):
        compute_stabilizer_metrics([])


def test_compute_stabilizer_metrics_basic():
    data = [
        (0, 10.0, 20.0, 5.0,  10.0),
        (1,  0.0,  0.0, 0.0,   0.0),
    ]
    pin, pout, eta, ist = compute_stabilizer_metrics(data)
    assert pin == [(0, pytest.approx(0.2)), (1, pytest.approx(0.0))]
    assert pout == [(0, pytest.approx(0.05)), (1, pytest.approx(0.0))]
    assert eta == [(0, pytest.approx(0.25)), (1, pytest.approx(0.0))]
    assert ist == [(0, pytest.approx(10.0)), (1, pytest.approx(0.0))]
