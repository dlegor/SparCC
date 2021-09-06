import pytest
import numpy as np 
from SparCC.sparcc.core_methods import normalize
from SparCC.sparcc.core_methods import to_fractions


#Data Test
L1=np.ones((50,50))
L2=np.zeros((50,50))

def test_normalize():
    m=normalize(L1)
    assert m.mean()==0.02

def test_to_fractions():
    m=to_fractions(L2)
    assert m.mean()==0.02



