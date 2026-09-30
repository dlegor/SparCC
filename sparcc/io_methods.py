'''
Created on Dec 6, 2012
@author: jonathanfriedman

Modified on Feb 06, 2020
@author: Daniel Legorreta
'''
from pathlib import Path

import numpy as np
import pandas as pd


def read_txt(file_name: str | Path, T: bool = True, verbose: bool = True, **kwargs):
    '''
    Read a delimited file (.txt as tab-separated, .csv as comma-separated)
    into a DataFrame.

    This is a wrapper around pandas' read_table/read_csv functions.

    Note:
    By default the data is transposed!
    To avoid this behavior set the parameter 'T' to False.

    Parameters
    ----------
    file_name : string or Path
        Path to input file.
    T : bool (default True)
        Indicates whether the produced DataFrame will be transposed.
    verbose : bool (default True)
        Indicates whether to print to screen the parsed table stats.

    Returns
    -------
    table : DataFrame
        Parsed table.
    '''
    file_name = Path(file_name)
    suffix = file_name.suffix.lower()
    if suffix == '.txt':
        temp = pd.read_table(file_name, **kwargs)
    elif suffix == '.csv':
        temp = pd.read_csv(file_name, **kwargs)
    else:
        raise OSError(f'Cannot read "{file_name}": only .txt and .csv files are supported.')

    if T:
        temp = temp.T

    if verbose:
        s = ('\nFinished parsing table.\n'
             f'Table dimensions, num_rows: {temp.shape[0]} & num_colums: {temp.shape[1]}\n')
        if T:
            s += '**** Data has been transposed! ****'
        print(s)
    return temp


def write_txt(frame: pd.DataFrame | np.ndarray, file_name: str | Path, T: bool = True, **kwargs):
    '''
    Write frame to a delimited text file.

    This is a wrapper around pandas' to_csv function.

    Note:
    By default the data is transposed!
    To avoid this behavior set the parameter 'T' to False.

    Parameters
    ----------
    file_name : string or Path
        Path to output file.
    T : bool (default True)
        Indicates whether the DataFrame is transposed before writing.
    '''
    if isinstance(frame, np.ndarray):
        frame = pd.DataFrame(frame)

    if T:
        frame = frame.T
    frame.to_csv(Path(file_name), **kwargs)
