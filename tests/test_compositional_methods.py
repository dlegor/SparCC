import pytest
import numpy as np 
from SparCC.sparcc.compositional_methods import clr
from SparCC.sparcc.compositional_methods import run_clr
from SparCC.sparcc.compositional_methods import variation_mat


#Data Test
L1=np.ones((50,50))

def test_clr():
    m=clr(L1).compute()

    assert m.sum()==0.0

def test_run_clr():
    a,b=run_clr(L1)
    assert np.isnan(a.sum())==True and b.sum()==0.0

def test_variation_mat():
    m=variation_mat(L1)
    assert m.sum()==0.0





    
