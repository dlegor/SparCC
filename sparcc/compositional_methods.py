'''
Modificated on April, 2020
@author: Daniel Legorreta
'''
import numpy as np
import dask
import dask.array as da 
import dask.dataframe as dd 

from numba import njit,prange
from typing import Union

def clr(frame:Union[da.Array,dd.DataFrame,np.ndarray], centrality:str='mean', axis:int=1):
    '''
    Do the central log-ratio (clr) transformation of frame.
    'centraility' is the metric of central tendency to divide by 
    after taking the logarithm.
    
    Parameters
    ----------
    centrality : 'mean' (default) | 'median'    
    axis : {0, 1}
        0 : transform each column
        1 : transform each row
    '''
    if isinstance(frame,np.ndarray):
        frame=da.from_array(frame)

    if isinstance(frame, dd.DataFrame):
        frame=frame.to_dask_array()

    frame_temp = da.log(frame)
    if centrality =='mean':
        v=da.mean(frame_temp,axis=axis,keepdims=True)
        R= frame_temp-v
        return R
    else :
        #centrality is 'median':
        v=da.median(frame_temp,axis=axis,keepdims=True)
        R=frame-v
        return R

def run_clr(frame:np.ndarray):
    '''CLR estimation in the matrix'''
    z        = clr(frame)
    Cov_base = da.cov(z, rowvar=0)
    C_base   = da.corrcoef(z,rowvar=0)

    return  dask.compute(C_base, Cov_base)

@njit(parallel=True)
def variation_mat(frame):
    '''
    Return the variation matrix of frame.
    Element i,j is the variance of the log ratio of components i and j.
    Slower version to be used in case the fast version runs out of memory.
    '''
    k = frame.shape[1]
    V = np.zeros((k,k))
    
    for i in range(k-1):
        for j in prange(i+1,k):
            v=np.log(frame[:,i]/frame[:,j])
            v=np.var(v)
            # Changed-DL ddof=0, set ddof to divide by (n-1), 
            # rather than n, thus getting an unbiased estimator (rather than the ML one). 
            V[i,j] = v
            V[j,i] = v
    return V
