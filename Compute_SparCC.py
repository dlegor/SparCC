'''
SparCC is a python module for computing correlations in compositional data
@DLegorreta

'''
import os
import tempfile

from sparcc.args import parse_args
from sparcc.io_methods import read_txt, write_txt
from sparcc.logger import create_logger
from sparcc.SparCC import main_alg
from sparcc.util import clean_data_folder


def main(argv: list[str] | None = None):
    '''
    Main function for execution on command line
    '''
    args = parse_args(argv)

    logger = create_logger('%s.log' % (args.name))
    logger.info('============ Initialized logger ============')
    logger.info('\n'.join('%s: %s' % (k, str(v)) for k, v in sorted(vars(args).items())))
    logger.info('Start of Process')
    logger.info(f'Loading the file {args.data_input}')

    # Load the file. A .txt file that is actually comma-separated parses as a
    # single column, which leaves no rows after the transpose; retry with sep=','.
    L1 = read_txt(args.data_input, index_col=0)
    if L1.shape[0] == 0:
        logger.info('The file does not look tab-separated, retrying as comma-separated.')
        L1 = read_txt(args.data_input, sep=',', index_col=0)
    if L1.shape[0] == 0:
        raise ValueError(f'Could not parse any samples from "{args.data_input}".')

    logger.info('Data loading done.')
    logger.info("Calculation started")

    # Per-iteration estimates are staged as HDF5 files in a private temporary
    # directory, which is always removed afterwards.
    staging_dir = tempfile.mkdtemp(prefix='sparcc_')
    path_corr_file = os.path.join(staging_dir, 'corr_files')
    path_cov_file = os.path.join(staging_dir, 'cov_files')
    os.makedirs(path_corr_file)
    os.makedirs(path_cov_file)

    try:
        cor, cov = main_alg(frame=L1, method=args.method, norm=args.norm,
                            n_iter=args.n_iter, verbose=args.verbose, log=args.log,
                            th=args.threshold, x_iter=args.x_iter,
                            path_subdir_cor=path_corr_file,
                            path_subdir_cov=path_cov_file)
    finally:
        logger.info("Clean staging folder")
        clean_data_folder(path_folder=staging_dir)

    logger.info("Calculation done!")
    print("Shape of Correlation Matrix:", cor.shape)
    print("Shape of Covariance Matrix:", cov.shape)

    # Save Correlation
    logger.info(f"Saving Correlation file in {args.save_cor}")
    write_txt(frame=cor, file_name=args.save_cor)

    # Save Covariance
    if args.save_cov is not None:
        logger.info(f"Saving Covariance file in {args.save_cov}")
        write_txt(frame=cov, file_name=args.save_cov)

    logger.info('Finished')


if __name__ == '__main__':
    main()
