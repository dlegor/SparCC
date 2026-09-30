'''
Command-line argument parsing for Compute_SparCC.py.

Nothing here runs at import time: call ``parse_args()`` to parse ``sys.argv``
(or an explicit list of arguments, which is handy in tests).
'''
import argparse
from datetime import datetime

usage_s = '''\nCompute the correlation between components.\n
By default uses the SparCC algorithm to account for compositional effects. Correlation and
covariance (when applies) matrices are written out as txt files.\n

Counts file needs to be a tab delimited text file where columns are samples and rows are
components (e.g. OTUS).\n

See example/fake_data.txt for an example file.\n
    Usage:  python Compute_SparCC.py --name Experiment_1 --data_input example/fake_data.txt\n
            python Compute_SparCC.py --name Experiment_1 -di example/fake_data.txt -ni 30 -xi 15
            -th 0.15 -scor FOLDER\n
    '''
description_s = 'SparCC Experimental'
epilog_s = 'If you run into a problem, please open an issue on the project repository.'


def str2bool(value: str | bool) -> bool:
    '''
    Parse a boolean command-line value.

    argparse's ``type=bool`` treats any non-empty string (including "False")
    as True, so the flags use this converter instead.
    '''
    if isinstance(value, bool):
        return value
    lowered = value.strip().lower()
    if lowered in ('true', 't', 'yes', 'y', '1'):
        return True
    if lowered in ('false', 'f', 'no', 'n', '0'):
        return False
    raise argparse.ArgumentTypeError(f'Boolean value expected, got "{value}".')


def build_parser() -> argparse.ArgumentParser:
    '''Build the argument parser used by Compute_SparCC.py.'''
    parser = argparse.ArgumentParser(
        description=description_s,
        usage=usage_s,
        epilog=epilog_s
    )
    parser.add_argument('-n', '--name', type=str,
                        default=f'Experiment_{datetime.now():%Y_%m_%d_%H_%M_%S}',
                        help='Experiment name, also used for the log file name.')

    parser.add_argument('-di', '--data_input', type=str, required=True,
                        help='Path to the counts file to process.')

    parser.add_argument('-m', '--method', type=str, default='sparcc',
                        help='Algorithm used to compute correlations: sparcc (default) | clr.')

    parser.add_argument('-ni', '--n_iter', type=int, default=20,
                        help='Number of inference iterations to average over (20 default).')

    parser.add_argument('-xi', '--x_iter', type=int, default=10,
                        help='Number of exclusion iterations to remove strongly correlated pairs '
                             '(10 default).')

    parser.add_argument('-th', '--threshold', type=float, default=0.1,
                        help='Correlation strength exclusion threshold (0.1 default).')

    parser.add_argument('-no', '--norm', type=str, default='dirichlet',
                        help='Method used to normalize the counts to fractions: '
                             'dirichlet (default) | normalize | pseudo.')

    parser.add_argument('--log', type=str2bool, default=True,
                        help='Log-transform fractions (reserved for methods other than '
                             'SparCC/CLR; default True).')

    parser.add_argument('-scor', '--save_cor', type=str, default='Cor_SparCC.csv',
                        help='Path of the output correlation file (default Cor_SparCC.csv).')

    parser.add_argument('-scov', '--save_cov', type=str,
                        help='Path of the output covariance file (not written if omitted).')

    parser.add_argument('-v', '--verbose', type=str2bool, default=True,
                        help='Print iteration progress? (default True)')
    return parser


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    '''Parse ``argv`` (defaults to ``sys.argv[1:]``).'''
    return build_parser().parse_args(argv)
