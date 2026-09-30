'''
Modificated on April, 2020
@author: Daniel Legorreta
'''
import dask
import dask.array as da
import dask.dataframe as dd
import numpy as np
from numba import njit, prange


def clr(frame: da.Array | dd.DataFrame | np.ndarray, centrality: str = 'mean', axis: int = 1):
    '''
    Do the central log-ratio (clr) transformation of frame.
    'centrality' is the metric of central tendency to subtract
    after taking the logarithm.

    Parameters
    ----------
    centrality : 'mean' (default) | 'median'
    axis : {0, 1}
        0 : transform each column
        1 : transform each row
    '''
    if isinstance(frame, np.ndarray):
        frame = da.from_array(frame)

    if isinstance(frame, dd.DataFrame):
        frame = frame.to_dask_array()

    frame_temp = da.log(frame)
    if centrality == 'mean':
        v = da.mean(frame_temp, axis=axis, keepdims=True)
    else:
        # centrality is 'median'
        v = da.median(frame_temp, axis=axis, keepdims=True)
    return frame_temp - v


def run_clr(frame: np.ndarray):
    '''CLR estimation in the matrix'''
    z = clr(frame)
    Cov_base = da.cov(z, rowvar=0)
    C_base = da.corrcoef(z, rowvar=0)

    return dask.compute(C_base, Cov_base)


@njit(parallel=True)
def variation_mat(frame):
    '''
    Return the variation matrix of frame.
    Element i,j is the variance of the log ratio of components i and j.
    '''
    k = frame.shape[1]
    V = np.zeros((k, k))

    for i in range(k - 1):
        for j in prange(i + 1, k):
            # np.var divides by n (ddof=0, the ML estimator); Numba's np.var
            # does not support the ddof argument.
            v = np.var(np.log(frame[:, i] / frame[:, j]))
            V[i, j] = v
            V[j, i] = v
    return V
