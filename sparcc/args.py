'''
Script to configure the log that is displayed during the execution process.

'''
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import argparse
from datetime import datetime
import os
import copy
import shutil

usage_s = '''\nCompute the correlation between components.\n
By default uses the SparCC algorithm to account for compositional effects. Correlation and 
covariance (when applies) matrices are written out as txt files.\n

Counts file needs to be a tab delimited text file where columns are samples and rows are components (e.g. OTUS).\n

See example/fake_data.txt for an example file.\n
    Usage:  python Compute_SparCC.py --name Experiment_1 --data_input example/fake_data.txt\n
            python Compute_SparCC.py --name Experiment_1 -di example/fake_data.txt -ni 30 -xi 15 
            -th 0.15 -scor FOLDER\n
    '''
descripion_s='SparCC Experimental'
epilog_s='If you have some problem, please send a email to help@ixulabs.com'

parser = argparse.ArgumentParser(
    description=descripion_s,
    usage=usage_s,
    epilog=epilog_s
)
parser.add_argument('-n','--name', type=str, 
default='Experiment_{:%Y_%m_%d_%H_%M_%S}'.format(datetime.now()), 
help='Experiment name and record.')

parser.add_argument('-di','--data_input', type=str, 
help="Root path where file to process.")

parser.add_argument('-m','--method', type=str, default='sparcc', 
help='Name of algorithm used to compute correlations (sparcc (default) | Future Algorithms))')

parser.add_argument('-ni','--n_iter', type=int, default=20, 
help='Number of inference iterations to average over (20 default).')

parser.add_argument('-xi','--x_iter', type=int, default=10, 
help='Number of exclusion iterations to remove strongly correlated pairs (10 default).')

parser.add_argument('-th','--threshold',type=float, default=0.1,
help= 'Correlation strength exclusion threshold (0.1 default).')

parser.add_argument('-no','--norm',type=str, default='dirichlet',
help= 'Method used to normalize the counts to fractions.(Defaul:dirichlet)')

parser.add_argument('--log',type=bool, default=True,
help= 'log-transform fraction used if method ~= SparCC/CLR(Defaul:True')

parser.add_argument('-scor','--save_cor', type=str,
help='Root path to save the correlation files.')

parser.add_argument('-scov','--save_cov', type=str,
help='Root path to save the covariance files.')

parser.add_argument('-v','--verbose', type=bool, default=True,
help='Print iteration progress?')


def _check_save_files(opt):
    if opt.save_cor==None:
        opt.save_cor='Cor_SparCC.csv'

def preprocess(opt):
    #Define Temp Folder
    setattr(opt,'savedir','./data')
    
    _check_save_files(opt)

    if os.path.exists(opt.savedir) and os.path.isdir(opt.savedir):
        try:
            shutil.rmtree("./data")

        except OSError as e:
            print("Error: {0}:{1}".format('./temp_files/*',e.strerror))
            
        opt.path_corr_file=os.path.join(opt.savedir,'corr_files')
        os.makedirs(opt.path_corr_file)
        opt.path_cov_file=os.path.join(opt.savedir,'cov_files')
        os.makedirs(opt.path_cov_file)

    else:
        os.makedirs(opt.savedir)
        opt.path_corr_file=os.path.join(opt.savedir,'corr_files')
        os.makedirs(opt.path_corr_file)
        opt.path_cov_file=os.path.join(opt.savedir,'cov_files')
        os.makedirs(opt.path_cov_file)
    
args=parser.parse_args()
preprocess(args)