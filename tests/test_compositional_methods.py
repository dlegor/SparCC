"""
Tests for sparcc/compositional_methods.py (clr, run_clr, variation_mat).

Run with: uv run pytest tests/test_compositional_methods.py
"""
import numpy as np

from sparcc.compositional_methods import clr, run_clr, variation_mat

#Data Test
L1=np.ones((50,50))

def test_clr():
    m=clr(L1).compute()

    assert m.sum()==0.0

def test_clr_median_uses_log_values():
    frame = np.array([[1.0, 2.0, 4.0], [1.0, 1.0, 8.0]])
    m = clr(frame, centrality='median').compute()
    logs = np.log(frame)
    expected = logs - np.median(logs, axis=1, keepdims=True)
    np.testing.assert_allclose(m, expected)

def test_run_clr():
    a,b=run_clr(L1)
    assert np.isnan(a.sum()) and b.sum()==0.0

def test_variation_mat():
    m=variation_mat(L1)
    assert m.sum()==0.0
