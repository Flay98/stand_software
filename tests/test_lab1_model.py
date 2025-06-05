import pytest
import numpy as np

from lab1.calculations_lab1 import (
    calc_dynamic_resistance,
    compute_shockley_experimental,
    shockley_model,
    theoretical_dynamic_resistance
)


@pytest.mark.parametrize("u, i_mA, n, Ut, expected", [
    (
            np.array([1.0, 2.0, 3.0]),
            np.array([10.0, 20.0, 40.0]),
            1.0,
            0.0253,
            [
                # (U0, I0, rd_delta, rd_theor)
                (1.0, 10.0, 100.0, 2.53),
                (2.0, 20.0, 50.0, 1.265),
            ]
    ),
    (
            np.array([0.0, 1.0]),
            np.array([0.0, 0.0]),
            2.0,
            0.026,
            [
                (0.0, 0.0, float('inf'), float('inf')),
            ]
    ),
])
def test_calc_dynamic_resistance(u, i_mA, n, Ut, expected):
    rows = calc_dynamic_resistance(u, i_mA, n, Ut)
    assert len(rows) == len(expected)
    for (U0, I0, rd_d, rd_t), (eU, eI, erd_d, erd_t) in zip(rows, expected):
        assert U0 == pytest.approx(eU)
        assert I0 == pytest.approx(eI)

        if np.isinf(erd_d):
            assert np.isinf(rd_d)
        else:
            assert rd_d == pytest.approx(erd_d, rel=1e-6)
        if np.isinf(erd_t):
            assert np.isinf(rd_t)
        else:
            assert rd_t == pytest.approx(erd_t, rel=1e-6)



def test_compute_shockley_experimental_monotonic():
    U = np.array([0.0, 0.1, 0.2, 0.3])  # В
    Is = 1e-9
    n = 2.0
    Rs = 0.0
    Ut = 0.0253
    I_mA = compute_shockley_experimental(U, Is, n, Rs, Ut)
    # проверим длину и неубывающий характер
    assert I_mA.shape == U.shape
    assert np.all(np.diff(I_mA) >= 0)


def test_shockley_model_empty_raises():
    with pytest.raises(ValueError):
        shockley_model(np.array([]), np.array([]), Ut=0.0253)


def test_shockley_model_no_positive_current():
    u = np.array([-1.0, -0.5, 0.0])
    i_mA = np.array([0.0, 0.0, 0.0])
    with pytest.raises(ValueError):
        shockley_model(u, i_mA, Ut=0.0253)


def test_shockley_model_basic():

    u = np.array([0.1, 0.2, 0.3, 0.4])

    Ut = 0.0253
    I_mA = (1e-6 * (np.exp(u / Ut) - 1)) * 1000.0
    U_th, I_th, Is_fit, n_fit = shockley_model(u, I_mA, Ut=Ut)

    assert Is_fit == pytest.approx(1e-6, rel=1e-1)
    assert n_fit == pytest.approx(1.0, rel=0.5)

    assert U_th.shape[0] == 300
    assert I_th.shape[0] == 300



def test_theoretical_dynamic_resistance_length():
    U_vals = np.array([0.0, 0.1, 0.2])
    Is = 1e-9
    n = 1.0
    Rs = 0.0
    Ut = 0.0253
    rows = theoretical_dynamic_resistance(U_vals, Is, n, Rs, Ut)

    assert len(rows) == len(U_vals) - 1

    for row in rows:
        assert len(row) == 4

        U0, I0, rd_d, rd_t = row
        if I0 != 0:
            assert not np.isinf(rd_t)
