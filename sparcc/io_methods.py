'''
Created on Dec 6, 2012
@author: jonathanfriedman

Modified on Feb 06, 2020
@author: Daniel Legorreta
'''
import numpy as np
import pandas as pd 
from pandas.io.parsers import read_csv as _read_csv
from pandas.io.parsers import read_table as _read_txt

from pandas.io.feather_format import read_feather
import logging
from typing import Union
from pathlib import Path

def read_txt(file_name:str, T:bool=True, verbose:bool=True, **kwargs):
    '''
    Read general delimited file into DataFrame.
    
    This a wrapper around pandas' read_table function which adds
    optional parsing of lineage information, and sets some default
    parameter values.
    
    Note: 
    By default the data is transposed!
    To avoid this behavior set the parameter 'T' to False.
    
    Parameters
    ----------
    file : string 
        Path to input file.  
    T : bool (default True)
        Indicated whether the produced DataFrame will be transposed.
    verbose : bool (default True)
        Indicated whether to print to screen the parsed table stats.
    
    Returns
    -------
    table : DataFrame
        Parsed table.
    '''
    #Check file
    file_name=Path(file_name)
    if '.txt' in file_name.name:
        temp=_read_txt(file_name,**kwargs)

    elif '.csv' in file_name.name:
        temp = _read_csv(file_name,**kwargs)
    else:
        raise IOError("ERROR - The file cannot be read.")


    #Validation of the minimum size required-Transposed Matrix
    ncol = min(temp.shape[0],3)
    nrow = min(temp.shape[1],3)
    assert (ncol <= 3),"The data size is insufficient to apply the algorithm!"
    assert (nrow <= 3),"The data size is insufficient to apply the algorithm!"
    
    if T:
        temp=temp.T
        s = """\nFinished parsing table.\nTable dimensions, num_rows: {0} & num_colums: {1}\n"""\
            .format(temp.shape[0],temp.shape[1])
        s += '**** Data has been transposed! ****'
    else:
        s = """\nFinished parsing table.\nTable dimensions, num_rows: {0} & num_colums: {1}\n"""\
            .format(temp.shape[0],temp.shape[1])
    
    #Verbose
    if verbose:
        print(s)
        return temp
    else:
        return temp 

def write_txt(frame:Union[pd.DataFrame,np.ndarray], file_name:Union[str,Path], T:bool=True, **kwargs):
    '''
    Write frame to txt file.
    
    This a wrapper around pandas' to_csv function which adds
    optional writing of lineage information, and sets some default
    parameter values.
    
    Note: 
    By default the data is transposed!
    To avoid this behavior set the parameter 'T' to False.        
    
    Parameters
    ----------
    file : string 
        Path to input file.  
    T : bool (default True)
        Indicated whether the produced DataFrame will be transposed.
    '''
    if isinstance(frame,np.ndarray):
        frame=pd.DataFrame(frame)
    
    file_name=Path(file_name)

    #index
    if T:
        frame.T.to_csv(file_name,**kwargs)
    else:
        frame.to_csv(file_name,**kwargs)