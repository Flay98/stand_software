import pytest
from lab8.calculations_lab8 import compute_avg_beta

def test_compute_avg_beta_empty():
    """Пустой список даёт пустой результат."""
    assert compute_avg_beta([]) == []

def test_compute_avg_beta_all_zero_ib():
    """Если во всех записях ib=0, для этого Uce не возвращается ни одного β."""
    data = [
        (5.0, [10.0, 20.0], [0.0, 0.0]),
        (3.3, [5.0], [0.0])
    ]
    assert compute_avg_beta(data) == []

def test_compute_avg_beta_negative_ib_skipped():
    """Отрицательные или нулевые ib пропускаются."""
    data = [
        (1.2, [10.0, 20.0, 30.0], [-1.0, 0.0, 5.0]),
    ]
    # Только третий элемент годится: 30/5 = 6.0
    assert compute_avg_beta(data) == [(1.2, pytest.approx(6.0))]

def test_compute_avg_beta_basic():
    """Обычный случай: несколько наборов данных."""
    data = [
        (1.0, [10.0, 20.0, 30.0], [1.0, 2.0, 3.0]),
        (2.0, [5.0, 15.0, 25.0], [1.0, 0.0, 5.0]),
    ]
    # Для Uce=1: betas = [10/1, 20/2, 30/3] = [10, 10, 10], avg = 10
    # Для Uce=2: пары (5,1)->5, (15,0)->skip, (25,5)->5 => avg = (5+5)/2 = 5
    expected = [(1.0, pytest.approx(10.0)), (2.0, pytest.approx(5.0))]
    assert compute_avg_beta(data) == expected

@pytest.mark.parametrize("ic_list, ib_list, expected_avg", [
    ([1.0, 2.0, 3.0], [1.0, 1.0, 1.0], 2.0),      # простое среднее (1+2+3)/3
    ([0.0, 5.0], [1.0, 5.0], (0.0/1.0 + 5.0/5.0)/2),  # содержит ноль I_C
])
def test_compute_avg_beta_parametrized(ic_list, ib_list, expected_avg):
    result = compute_avg_beta([(0.5, ic_list, ib_list)])
    assert len(result) == 1
    u_ce, avg_beta = result[0]
    assert u_ce == pytest.approx(0.5)
    assert avg_beta == pytest.approx(expected_avg)