"""
Tests for sparcc/SparCC.py (Mesh, new_excluded_pair, basis_var, C_from_V,
run_sparcc, basic_corr, main_alg).

Run with: uv run pytest tests/test_SparCC.py
"""
import os

import numpy as np
import pytest

from sparcc.SparCC import (
    C_from_V,
    Mesh,
    basic_corr,
    basis_var,
    main_alg,
    new_excluded_pair,
    run_sparcc,
)

#Constant
######################################
M1=np.array([[-0.2, -0.2, -0.2, -0.2],
             [-0.1, -0.1, -0.1, -0.1],
             [ 0. ,  0. ,  0. ,  0. ],
             [ 0.1,  0.1,  0.1,  0.1]])


M2=np.array([0.51020408, 0.51020408, 0.51020408, 0.51020408, 0.51020408,
       0.51020408, 0.51020408, 0.51020408, 0.51020408, 0.51020408,
       0.51020408, 0.51020408, 0.51020408, 0.51020408, 0.51020408,
       0.51020408, 0.51020408, 0.51020408, 0.51020408, 0.51020408,
       0.51020408, 0.51020408, 0.51020408, 0.51020408, 0.51020408,
       0.51020408, 0.51020408, 0.51020408, 0.51020408, 0.51020408,
       0.51020408, 0.51020408, 0.51020408, 0.51020408, 0.51020408,
       0.51020408, 0.51020408, 0.51020408, 0.51020408, 0.51020408,
       0.51020408, 0.51020408, 0.51020408, 0.51020408, 0.51020408,
       0.51020408, 0.51020408, 0.51020408, 0.51020408, 0.51020408])
D=50
M = np.ones((D,D)) + np.diag([D-2]*D)
V=np.ones((50,50))

M3=np.array([[0.5, 1. , 1. , 1. , 1. , 1. , 1. , 1. , 1. , 1. ],
        [1. , 0.5, 1. , 1. , 1. , 1. , 1. , 1. , 1. , 1. ],
        [1. , 1. , 0.5, 1. , 1. , 1. , 1. , 1. , 1. , 1. ],
        [1. , 1. , 1. , 0.5, 1. , 1. , 1. , 1. , 1. , 1. ],
        [1. , 1. , 1. , 1. , 0.5, 1. , 1. , 1. , 1. , 1. ],
        [1. , 1. , 1. , 1. , 1. , 0.5, 1. , 1. , 1. , 1. ],
        [1. , 1. , 1. , 1. , 1. , 1. , 0.5, 1. , 1. , 1. ],
        [1. , 1. , 1. , 1. , 1. , 1. , 1. , 0.5, 1. , 1. ],
        [1. , 1. , 1. , 1. , 1. , 1. , 1. , 1. , 0.5, 1. ],
        [1. , 1. , 1. , 1. , 1. , 1. , 1. , 1. , 1. , 0.5]])

M4=np.array([[np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan],
       [np.nan,  1.,  1.,  1.,  1.,  1.,  1.],
       [np.nan,  1.,  1.,  1.,  1.,  1.,  1.],
       [np.nan,  1.,  1.,  1.,  1.,  1.,  1.],
       [np.nan,  1.,  1.,  1.,  1.,  1.,  1.],
       [np.nan,  1.,  1.,  1.,  1.,  1.,  1.],
       [np.nan,  1.,  1.,  1.,  1.,  1.,  1.]])

M5= np.array([[   np.nan,    np.nan,    np.nan,    np.nan,    np.nan,    np.nan,    np.nan],
       [   np.nan, 0.0001, 0.0001, 0.0001, 0.0001, 0.0001, 0.0001],
       [   np.nan, 0.0001, 0.0001, 0.0001, 0.0001, 0.0001, 0.0001],
       [   np.nan, 0.0001, 0.0001, 0.0001, 0.0001, 0.0001, 0.0001],
       [   np.nan, 0.0001, 0.0001, 0.0001, 0.0001, 0.0001, 0.0001],
       [   np.nan, 0.0001, 0.0001, 0.0001, 0.0001, 0.0001, 0.0001],
       [   np.nan, 0.0001, 0.0001, 0.0001, 0.0001, 0.0001, 0.0001]])
#Verctor for testing
x = np.arange(-0.2, 0.2, 0.1)

A= np.zeros((50,50))
##############################################################################


class  Test_Mesh:
    def test_one(self):
        a,b=Mesh(x)
        assert np.all(np.around(b,decimals=2)==M1)

    def test_two(self):
        xx,yy=np.meshgrid(x,x)
        a,b=Mesh(x)
        assert np.all(xx==a) and np.all(b==yy)


class TestNew_Excluded_Pair:

    def test_one(self):
        a=new_excluded_pair(A)
        assert a is None

    def test_two(self):
        a=new_excluded_pair(M1)
        assert a==(0,1)


def test_basis_var():
    T=basis_var(V,M)
    assert np.all(np.around(T,decimals=8)==M2)

def test_C_from_V():
    V=np.eye(10)
    x=np.ones(10)

    A,_=C_from_V(V,x)

    assert np.all(A==M3)

def test_run_sparcc():
    V=np.ones((7,7))
    A,B=run_sparcc(V)
    assert np.all(A[1:,1:]==M4[1:,1:]) and np.all(B[1:,1:]==M5[1:,1:])

def test_basic_corr():
    V=np.ones((50,50))
    A,_=basic_corr(V)
    Value=2500.0
    assert A.sum()==Value


def test_main_alg_uses_given_staging_dirs(tmp_path):
    rng = np.random.default_rng(0)
    counts = rng.integers(1, 100, size=(30, 8))
    cor_dir = tmp_path / 'cor'
    cov_dir = tmp_path / 'cov'
    cor_dir.mkdir()
    cov_dir.mkdir()

    cor, cov = main_alg(counts, n_iter=3, x_iter=2, verbose=False,
                        path_subdir_cor=str(cor_dir), path_subdir_cov=str(cov_dir))

    assert cor.shape == cov.shape == (8, 8)
    assert len(os.listdir(cor_dir)) == 3 and len(os.listdir(cov_dir)) == 3


def test_main_alg_unsupported_method(tmp_path):
    with pytest.raises(ValueError):
        main_alg(np.ones((10, 5)), method='pearson',
                 path_subdir_cor=str(tmp_path), path_subdir_cov=str(tmp_path))
