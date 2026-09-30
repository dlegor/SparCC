"""
Tests for sparcc/core_methods.py (normalize, to_fractions).

Run with: uv run pytest tests/test_core_methods.py
"""
import numpy as np
import pytest

from sparcc.core_methods import normalize, to_fractions

#Data Test
L1=np.ones((50,50))
L2=np.zeros((50,50))

def test_normalize():
    m=normalize(L1)
    assert m.mean()==0.02

def test_to_fractions():
    m=to_fractions(L2)
    assert m.mean()==0.02

def test_to_fractions_pseudo():
    counts = np.array([[0.0, 1.0, 2.0]])
    m = to_fractions(counts, method='pseudo', p_counts=1)
    np.testing.assert_allclose(m, [[1 / 6, 2 / 6, 3 / 6]])

def test_to_fractions_unsupported_method():
    with pytest.raises(ValueError):
        to_fractions(L1, method='unknown')
