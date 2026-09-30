#!/usr/bin/env python3
import shutil
import subprocess
import sys
from pathlib import Path

import typer
import yaml
from wasabi import msg

SCRIPT_DIR = Path(__file__).resolve().parent

# Keys of configuration.yml that override the matching command-line option.
CONFIG_KEYS = (
    'name', 'data_input', 'method', 'n_iteractions', 'x_iteractions', 'threshold',
    'normalization', 'log_transform', 'save_corr_file', 'save_cov_file',
    'num_simulate_data', 'perm_template', 'outpath', 'type_pvalues', 'outfile_pvals',
)
# Keys the pipeline itself needs; a Null value keeps the command-line value.
REQUIRED_KEYS = (
    'name', 'data_input', 'save_corr_file', 'num_simulate_data', 'perm_template', 'outpath',
)


def run_script(script: str, *args, **options) -> None:
    '''
    Run one of the root scripts with the current Python interpreter.

    ``options`` maps flags to values; a flag whose value is None is omitted so
    the script falls back to its own default. Raises CalledProcessError if the
    script fails, which stops the pipeline.
    '''
    cmd = [sys.executable, str(SCRIPT_DIR / script), *map(str, args)]
    for flag, value in options.items():
        if value is not None:
            cmd += [flag, str(value)]
    subprocess.run(cmd, check=True)


def main(
    configuration_file: str = typer.Option('configuration.yml', help="Configuration file."),
    name: str = typer.Option('experiment_sparCC', help="Experiment (log) name."),
    data_input: str = typer.Option('example/fake_data.txt', help="Path of the counts file."),
    method: str = typer.Option('sparcc', help="Correlation method: sparcc | clr."),
    n_iteractions: int = typer.Option(2, "--niteractions", "-nit",
                                      help="Number of inference iterations."),
    x_iteractions: int = typer.Option(2, "--xiteractions", "-xit",
                                      help="Number of exclusion iterations."),
    threshold: float = typer.Option(0.1, "--threshold", "-th",
                                    help="Exclusion threshold."),
    normalization: str = typer.Option('dirichlet', help="Counts-to-fractions method."),
    log_transform: bool = typer.Option(True, help="Log-transform fractions (reserved)."),
    save_corr_file: str = typer.Option("example/cor_sparcc.csv",
                                       help="Output correlation file."),
    save_cov_file: str = typer.Option(None, help="Output covariance file (optional)."),
    num_simulate_data: int = typer.Option(3, help="Number of bootstrap datasets."),
    perm_template: str = typer.Option('permutation_#.csv',
                                      help="Bootstrap file name template ('#' = number)."),
    outpath: str = typer.Option('example/pvals/', help="Folder for the bootstrap files."),
    type_pvalues: str = typer.Option('one_sided', help="one_sided | two_sided."),
    outfile_pvals: str = typer.Option('example/pvals/pvals_one_sided.csv',
                                      help="Output p-values file."),
    name_output_file: str = typer.Option('sparcc_test_version_kambucha',
                                         help="Currently unused."),
    ):
    """
    Script for end-to-end execution of SparCC

    Runs all the SparCC steps together. If the configuration file exists,
    every non-null value in it overrides the matching command-line option;
    null values fall back to the defaults of the underlying scripts.

    Usage:
        $ python General_Execution.py

    Note:
    The run time depends on the size of the OTU matrix. Make sure the
    process is not interrupted.
    """
    params = dict(locals())

    config_path = Path(configuration_file)
    if config_path.is_file():
        with open(config_path) as file:
            config = yaml.safe_load(file) or {}
        for key in CONFIG_KEYS:
            if key not in config:
                continue
            if config[key] is None and key in REQUIRED_KEYS:
                continue
            # Other Null values are kept: the flag is then omitted and the
            # underlying script uses its own default.
            params[key] = config[key]
    else:
        msg.warn(f'Configuration file "{configuration_file}" not found, '
                 'using command-line options.')

    name = params['name']
    outpath = params['outpath']
    perm_template = params['perm_template']
    num_simulate_data = int(params['num_simulate_data'])
    save_corr_file = params['save_corr_file']

    sparcc_options = {
        '-n': name,
        '-m': params['method'],
        '-ni': params['n_iteractions'],
        '-xi': params['x_iteractions'],
        '-th': params['threshold'],
        '-no': params['normalization'],
        '--log': params['log_transform'],
    }

    # SparCC on the real data
    msg.info('Computing SparCC on the input data')
    run_script('Compute_SparCC.py', **sparcc_options, **{
        '-di': params['data_input'],
        '-scor': save_corr_file,
        '-scov': params['save_cov_file'],
    })

    # Bootstrap datasets
    msg.info('Making bootstrap datasets')
    run_script('MakeBootstraps.py', params['data_input'], **{
        '-n': num_simulate_data,
        '-t': perm_template,
        '-p': outpath,
    })

    # SparCC on each bootstrap dataset, with the same parameters
    perm_file = str(Path(outpath) / perm_template)
    corr_file = str(Path(outpath) / 'perm_cor_#.csv')
    for i in range(num_simulate_data):
        print('#' * 100)
        print(f'Iteration: {i}')
        run_script('Compute_SparCC.py', **sparcc_options, **{
            '-di': perm_file.replace('#', str(i)),
            '-scor': corr_file.replace('#', str(i)),
        })

    # Remove the bootstrap datasets
    folder = Path(outpath)
    for f in folder.glob(perm_template.replace('#', '*')):
        f.unlink()

    # Pseudo p-values
    print("#" * 100)
    run_script('PseudoPvals.py', save_corr_file, corr_file, num_simulate_data, **{
        '-o': params['outfile_pvals'],
        '-t': params['type_pvalues'],
    })

    # Remove the per-bootstrap correlation files
    for f in folder.glob('perm_cor_*.csv'):
        f.unlink()

    # Move the log next to the correlation file
    source = Path(f'{name}.log')
    target_dir = Path(save_corr_file).parent
    if source.is_file() and target_dir.is_dir():
        shutil.move(source, target_dir / source.name)

    print(' ' * 50 + 'Execution Ended' + ' ' * 50)
    print("#" * 100)


if __name__ == "__main__":
    typer.run(main)
