#!/usr/bin/env python
'''
SparCC is a python module for computing correlations in compositional data 
@DLegorreta

'''
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from sparcc.SparCC import main_alg
from sparcc.io_methods import read_txt
from sparcc.logger import create_logger
from sparcc.args import args
from sparcc.util import clean_data_folder
from sparcc.io_methods import write_txt


def main():
    '''
    Main function for execution on command line
    '''
    logger = create_logger('%s.log' % (args.name))
    logger.info('============ Initialized logger ============')
    logger.info('\n'.join('%s: %s' % (k, str(v)) for k, v in sorted(dict(vars(args)).items(), key=lambda x: x[0])))
    logger.info('Start of Process')
    logger.info('Loading the file {}'.format(args.data_input))
    
    #Load the file
    try:
        L1=read_txt(args.data_input,index_col=0)
    except IOError as IOE:
        raise (IOE)
    if L1.shape[0]==0:
        logger.info('A problem has occurred with the file, it will be resolved.')
        flags_write=True
        
        try:
            L1=read_txt(args.data_input,sep=',')
        except IOError as IOE:
            raise (IOE)
    assert L1.shape[0]!=0,"ERROR!"


    
    logger.info('Data loading done.')
    logger.info("Calculation started")
    
    #SparCC Algorithm
    cor,cov=main_alg(frame=L1,method=args.method,norm=args.norm,
    n_iter=args.n_iter,verbose=args.verbose,log=args.log,
    th=args.threshold,x_iter=args.x_iter,path_subdir_cor=args.path_corr_file,
    path_subdir_cov=args.path_cov_file)
    
    logger.info("Calculation done!")
    print("Shape of Correlation Matrix:",cor.shape)
    print("Shape of Covariance Matrix:",cov.shape)

    #Save Correlation
    logger.info("Saving Correlation file in {}".format(args.save_cor))
    
    write_txt(frame=cor,file_name=args.save_cor)
    print("Ok")


    #Save Covariance
    if args.save_cov !=None:
        logger.info("Saving Covariance file in {}".format(args.save_cor))
        write_txt(frame=cor,file_name=args.save_cov)

    logger.info("Clean Folder")
    clean_data_folder(path_folder=args.path_corr_file)
    clean_data_folder(path_folder=args.path_cov_file)
    logger.info('Finished')

if __name__ == '__main__':
    main()
 
