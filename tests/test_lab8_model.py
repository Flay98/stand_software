import pytest
from lab8.calculations_lab8 import compute_avg_beta


def test_compute_avg_beta_empty():
    assert compute_avg_beta([]) == []


def test_compute_avg_beta_all_zero_ib():
    data = [
        (5.0, [10.0, 20.0], [0.0, 0.0]),
        (3.3, [5.0], [0.0])
    ]
    assert compute_avg_beta(data) == []


def test_compute_avg_beta_negative_ib_skipped():
    data = [
        (1.2, [10.0, 20.0, 30.0], [-1.0, 0.0, 5.0]),
    ]
    assert compute_avg_beta(data) == [(1.2, pytest.approx(6.0))]


def test_compute_avg_beta_basic():
    data = [
        (1.0, [10.0, 20.0, 30.0], [1.0, 2.0, 3.0]),
        (2.0, [5.0, 15.0, 25.0], [1.0, 0.0, 5.0]),
    ]

    expected = [(1.0, pytest.approx(10.0)), (2.0, pytest.approx(5.0))]
    assert compute_avg_beta(data) == expected


@pytest.mark.parametrize("ic_list, ib_list, expected_avg", [
    ([1.0, 2.0, 3.0], [1.0, 1.0, 1.0], 2.0),
    ([0.0, 5.0], [1.0, 5.0], (0.0 / 1.0 + 5.0 / 5.0) / 2),
])
def test_compute_avg_beta_parametrized(ic_list, ib_list, expected_avg):
    result = compute_avg_beta([(0.5, ic_list, ib_list)])
    assert len(result) == 1
    u_ce, avg_beta = result[0]
    assert u_ce == pytest.approx(0.5)
    assert avg_beta == pytest.approx(expected_avg)
