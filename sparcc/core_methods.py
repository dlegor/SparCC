'''
Created on Jun 24, 2012
@author: jonathanfriedman

Modificated on Nov 15, 2019
@Daniel Legorreta
'''
import logging

import numpy as np
import pandas as pd
from numpy.random import dirichlet


def normalize(frame: np.ndarray | pd.DataFrame, axis: int = 1):
    '''
    Normalize counts by sample total.

    Parameters
    ----------
    axis : {0, 1}
        0 : normalize each column
        1 : normalize each row

    Returns new instance of same class as input frame.
    '''
    return frame / frame.sum(axis=axis, keepdims=True)


def to_fractions(frame: np.ndarray | pd.DataFrame, method: str = 'dirichlet',
                 p_counts: float = 1, axis: int = 1):
    '''
    Convert counts to fractions using the given method.

    Parameters
    ----------
    method : string {'dirichlet' (default) | 'normalize' | 'pseudo'}
        dirichlet - randomly draw from the corresponding posterior
                    Dirichlet distribution with a uniform prior.
                    That is, for a vector of counts C,
                    draw the fractions from Dirichlet(C+1).
        normalize - simply divide each row by its sum.
        pseudo    - add given pseudo count (default 1) to each count and
                    do simple normalization.
    p_counts : int/float (default 1)
        The value of the pseudo counts to add to all counts.
        Used by the 'dirichlet' and 'pseudo' methods.
    axis : {0 | 1}
        0 : normalize each column.
        1 : normalize each row.

    Returns
    -------
    fracs: array
        Estimated component fractions.
    '''
    if isinstance(frame, pd.DataFrame):
        frame = frame.values

    if method == 'normalize':
        return normalize(frame, axis)

    elif method == 'pseudo':
        return normalize(frame + p_counts, axis)

    elif method == 'dirichlet':
        return np.apply_along_axis(lambda x: dirichlet(x + p_counts), axis, frame)

    else:
        logging.info('Unsupported method "%s"', method)
        raise ValueError(f'Unsupported method "{method}"')
