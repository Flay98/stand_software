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

# 1) find_stabilization_index
@pytest.mark.parametrize("u_load, threshold, expected", [
    (np.array([1.0, 1.01, 1.5]), 0.02, 0),    # first delta 0.01 < 0.02
    (np.array([0.0, 5.05, 5.1, 6.0]), 0.05, 1), # delta at index 1 is 0.1? no, index 2 is 0.1 > thresh, index 1 is 5.0-5.0=0? nope. Let's pick threshold 0.2 => index 1
    (np.array([0.0, 0.3, 0.6]), 0.1, -1),     # no small delta
    (np.array([]), 0.1, -1),                 # empty
    (np.array([5.0]), 0.1, -1),              # single element
])
def test_find_stabilization_index(u_load, threshold, expected):
    assert find_stabilization_index(u_load, threshold) == expected

# 2) calc_stabilization_coefficients
def test_calc_stabilization_coefficients_basic():
    u_pit = np.array([1.0, 2.0, 3.0, 4.0])
    u_load = np.array([0.0, 0.0, 1.0, 1.5])
    # start at 1 -> iterate from 0 to len-2
    start = 1
    k_vals = calc_stabilization_coefficients(u_pit, u_load, start)
    # only intervals 0->1,1->2,2->3 but skipping where dl==0 at 0->1
    # interval 1->2: dp=3-2=1, avg_p=2.5; dl=1-0=1, avg_l=0.5; k=(1/2.5)/(1/0.5)=0.4/2=0.2
    # interval 2->3: dp=4-3=1, avg_p=3.5; dl=1.5-1.0=0.5, avg_l=1.25; k=(1/3.5)/(0.5/1.25)=0.285714/(0.4)=~0.714285
    assert len(k_vals) == 2
    assert pytest.approx(k_vals[0], rel=1e-6) == (1/2.5)/(1/0.5)
    assert pytest.approx(k_vals[1], rel=1e-6) == (1/3.5)/(0.5/1.25)

# 3) compute_stabilization_coefficient
def test_compute_stabilization_coefficient_errors():
    # too few points
    with pytest.raises(ValueError):
        compute_stabilization_coefficient([1.0], [1.0], min_points=2, threshold=0.1)
    # no stabilization at all
    u_p = [1,2,3]
    u_l = [10,20,30]
    with pytest.raises(ValueError):
        compute_stabilization_coefficient(u_p, u_l, min_points=3, threshold=0.01)
    # stabilization found but no k_vals (all dl zero)
    u_p = [1,2,3,4]
    u_l = [1,1,1,1]
    with pytest.raises(ValueError):
        compute_stabilization_coefficient(u_p, u_l, min_points=4, threshold=0.1)

def test_compute_stabilization_coefficient_success():
    # Construct data where stabilization at index 1
    u_p = [1.0, 2.0, 3.0]
    # u_load: 1->1->1.05 (delta at 1->2 = 0.05 < threshold)
    u_l = [0.0, 0.2, 0.3]
    start, ks, avg = compute_stabilization_coefficient(u_p, u_l, min_points=3, threshold=0.1)
    assert start == 1
    # Only interval from max(0, start-1)=0 to 1:
    # dp=2-1=1, avg_p=1.5; dl=0-0=0 skip; next interval dp=3-2=1, avg_p=2.5; dl=0.05-0=0.05, avg_l=0.025 => k=(1/2.5)/(0.05/0.025)=0.4/2=0.2
    assert len(ks) == 2
    assert ks[0] == pytest.approx(0.33333333)
    assert avg == pytest.approx(0.6666666)

# 4) input/output power, efficiency, stabilization_current
def test_power_and_efficiency():
    assert input_power(5.0, 20.0) == pytest.approx(0.1)   # 5*20mA=100mW=0.1W
    assert output_power(3.0, 10.0) == pytest.approx(0.03)
    assert efficiency(0.1, 0.03) == pytest.approx(0.3)
    assert efficiency(0.0, 1.0) == 0.0
    assert stabilization_current(10.0, 7.5) == pytest.approx(2.5)

# 5) compute_stabilizer_metrics
def test_compute_stabilizer_metrics_errors():
    with pytest.raises(ValueError):
        compute_stabilizer_metrics([])

def test_compute_stabilizer_metrics_basic():
    # data rows: (col, u_pit, i_pit, u_load, i_load)
    data = [
        (0, 10.0, 20.0, 5.0,  10.0),
        (1,  0.0,  0.0, 0.0,   0.0),
    ]
    pin, pout, eta, ist = compute_stabilizer_metrics(data)
    # pin: col 0 -> 10*20mA=0.2; col1 -> 0
    assert pin == [(0, pytest.approx(0.2)), (1, pytest.approx(0.0))]
    # pout: col0 -> 5*10mA=0.05
    assert pout == [(0, pytest.approx(0.05)), (1, pytest.approx(0.0))]
    # eta: 0.05/0.2 = 0.25; second row p_in=0->eta=0
    assert eta == [(0, pytest.approx(0.25)), (1, pytest.approx(0.0))]
    # ist: i_pit-i_load: col0 20-10=10; col1 0-0=0
    assert ist == [(0, pytest.approx(10.0)), (1, pytest.approx(0.0))]
