'''
Created on Apr 8, 2013
@author: jonathanfriedman
'''

import numpy as np
from pathlib import Path
from pandas import DataFrame as DF
from sparcc.io_methods import read_txt, write_txt

def compare2sided(perm,real):
    return np.abs(perm) >= np.abs(real)

def compare1sided(perm,real): 
    inds_abs = compare2sided(perm,real)
    inds_sign = np.sign(perm) == np.sign(real)
    return inds_abs & inds_sign

def get_pvalues(cor, perm_template, nperm, test_type='two_sided',iprint=0):

    '''
    Compute pseudo p-vals from a set correlations obtained from permuted data' 
    Pseudo p-vals are the percentage of times a correlation at least 
    as extreme as the "real" one was observed in simulated datasets.
    
    Files containing the permuted correlations should be named with a 
    consistent template, and these file names cannot contain any "#" characters.

    Parameters
    ----------
    cor : DataFrame
        Inferred correlations whose p-values are to be computed.
    perm_template : str
        The template used for naming the correlation files of the 
        permuted data. The iteration number is indicated with a "#".
        For example: 'permuted/cor.sparcc.permuted_#.txt'
    nperm : int
        Number of permutations available.
    test_type : 'two_sided' (default) | 'one_sided'
        two-sided  = considering only the correlation magnitude. 
        one-sided  = accounting for the sign of correlations.
    iprint : int (default = 0)
        The interval at which iteration number is printed out.
        If iprint<=0 no printouts are made.
    
    Returns
    -------
    p_vals: frame
        Computed pseudo p-values.
    '''
    #Definition of the type of test
    if test_type == 'two_sided': 
        cmpfun = compare2sided
    elif test_type == 'one_sided':
        cmpfun = compare1sided
    else:
        raise ValueError('unsupported test type "%s"' %test_type)
    
    #DataFrame
    n_sig = DF(np.zeros(cor.shape), 
               index=cor.index,
               columns=cor.columns)

    for i in range(nperm):
        if iprint>0:
            if not i%iprint: print(i) 
        permfile = perm_template.replace('#', '%d'%i)
        cor_perm = read_txt(permfile,index_col=0).values #Read each file
        n_sig[cmpfun(cor_perm, cor)] += 1  
    
    p_vals = 1.*n_sig/nperm
    p_vals.values[np.diag_indices_from(p_vals.values)] = 1 
    
    return p_vals
    

def main(cor_file, perm_template, nperm, test_type='two_sided', outfile=None):
    '''
    Compute pseudo p-vals from a set correlations obtained from permuted data' 
    Pseudo p-vals are the percentage of times a correlation at least 
    as extreme as the "real" one was observed in simulated datasets.
    
    Files containing the permuted correlations should be named with a 
    consistent template, and these file names cannot contain any "#" characters.
    '''
    cor = read_txt(cor_file,verbose=True,index_col=0)
    if cor.shape[0]==0:
        print('A problem has occurred with the file, it will be resolved.')
        
    assert cor.shape[0]!=0,"ERROR!"


    print(f"Shape of Corr:{cor.shape}")

    p_vals = get_pvalues(cor, perm_template, nperm, test_type)
    if outfile is None:
        outfile = cor_file +'.nperm_%d.pvals' %nperm
    
    write_txt(p_vals, outfile)
    

if __name__ == '__main__':
    
    ## parse input arguments
    from optparse import OptionParser
    
    usage  = ('Compute pseudo p-vals from a set correlations obtained from permuted data.\n' 
              'Pseudo p-vals are the percentage of times a correlation at least as extreme as the "real" one was observed in simulated datasets. \n'
              'p-values can be either two-sided (considering only the correlation magnitude) or one-sided (accounting for the sign of correlations).\n'
              'Files containing the permuted correlations should be named with a consistent template, where only the iteration number changes.\n' 
              'The permutation naming template is the second input argument with the iteration number replaced with a "#" character.\n' 
              'The template cannot contain additional "#" characters.\n' 
              'The total number of simulated sets is the third.\n'
              '\n'
              'Usage:   python PseudoPvals.py real_cor_file perm_template num_simulations [options]\n'
              'Example: python PseudoPvals.py example/basis_corr/cor_sparcc.out example/pvals/perm_cor_#.txt 5 -o pvals.txt -t one_sided')
    parser = OptionParser(usage)
    parser.add_option("-t", "--type", dest="type", default='two_sided', type = 'str',
                      help="Type of p-values to computed.  one_sided | two_sided (default).")
    parser.add_option("-o", "--outfile", dest="outfile", default=None, type = 'str',
                      help="Name of file to which p-values will be written.")
    (options, args) = parser.parse_args()
    real_cor_file   = args[0]
    perm_template   = args[1]
    n               = int(args[2])
    test_type = options.type
    outfile = options.outfile
     
    main(real_cor_file, perm_template, n, test_type, outfile)
    