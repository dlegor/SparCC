# **SparCC**

SparCC is a Python module for computing correlations in compositional data (16S rRNA, metagenomics, etc.). It closely follows the [original SparCC algorithm](https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1002687) (Friedman & Alm, 2012), and uses [Dask](https://www.dask.org/) and [Numba](https://numba.pydata.org/) for speed and out-of-core processing.

You can run SparCC in two ways:

- **Step by step**, calling each script yourself (see [Running the scripts](#running-the-scripts)).
- **End to end**, with every parameter set in a configuration file (see [Running with a configuration file](#running-with-a-configuration-file)).

********************************
## **Installation**
********************************

The project uses [`uv`](https://docs.astral.sh/uv/) and requires **Python 3.12 or later**. From the repository root, run:

~~~bash
uv sync
~~~

This creates a `.venv` and installs the exact dependency versions pinned in `uv.lock`. Run any script through `uv run`, for example:

~~~bash
uv run python Compute_SparCC.py -h
~~~

> **Note:** Earlier versions used a conda `environment.yml`. It has been replaced by `pyproject.toml`/`uv.lock`, and the dependency list now contains only the packages the code actually imports.

********************************
## **Running the tests**
********************************

The test suite uses [pytest](https://docs.pytest.org/). The dev dependencies (`pytest`, `ruff`, `mypy`) are installed by `uv sync`. Run all commands from the repository root:

~~~bash
uv run pytest -q                                   # run the whole suite
uv run pytest tests/test_SparCC.py                 # run a single file
uv run pytest tests/test_SparCC.py::test_run_sparcc  # run a single test
uv run pytest -k clr                               # run tests whose name matches "clr"
uv run pytest -x -v                                # verbose; stop at the first failure
~~~

The tests live in `tests/`, with one file per module:

| Test file | Covers |
|---|---|
| `tests/test_SparCC.py` | Core algorithm (`sparcc/SparCC.py`) |
| `tests/test_compositional_methods.py` | CLR transform and variation matrix |
| `tests/test_core_methods.py` | Counts-to-fractions normalization |
| `tests/test_io_methods.py` | Reading and writing tables |
| `tests/test_args.py` | Command-line parsing for `Compute_SparCC.py` |
| `tests/test_bootstraps_pvals.py` | `MakeBootstraps.py` and `PseudoPvals.py` |

pytest is configured in `pyproject.toml` under `[tool.pytest.ini_options]`. That configuration also puts the repository root on the import path, so the tests can import the root-level scripts. The first run is a few seconds slower because Numba compiles the `@njit` functions.

Linting and type checking:

~~~bash
uv run ruff check .
uv run mypy sparcc/
~~~

********************************
## **Running the scripts**
********************************

Run the scripts in the repository root with Python, as in the examples below. To run one directly as an executable, first give it execute permission (e.g. `chmod +x Compute_SparCC.py`).

Each script prints its help with `-h`:

~~~bash
uv run python Compute_SparCC.py -h
uv run python MakeBootstraps.py -h
uv run python PseudoPvals.py -h
~~~

### Example: the "fake" dataset

The commands below analyze the example dataset in `example/`:

- `example/fake_data.txt` contains simulated abundances of 50 OTUs in 200 samples, drawn from a multinomial log-normal distribution.
- `example/true_basis_cor.txt` contains the true basis correlations used to generate the data.
- OTU 0 is very dominant. Pearson or Spearman correlations therefore make it look negatively correlated with most other OTUs, although it is not negatively correlated with any of them. SparCC corrects for this compositional effect.

Input files are delimited text: `.txt` files are read as tab-separated and `.csv` files as comma-separated. Components (OTUs) are rows and samples are columns.

#### 1. Correlation estimation

Compute the SparCC correlations between all OTUs:

~~~bash
uv run python Compute_SparCC.py -n Experiment_SparCC -di example/fake_data.txt -ni 5 --save_cor example/basis_corr/cor_sparcc.csv
~~~

Add `--save_cov <file>` to also write the covariance matrix. Intermediate results are staged in a private temporary directory, which is removed when the run finishes.

#### 2. Pseudo p-values

Pseudo p-values are computed with a bootstrap procedure. First, create resampled datasets. In each one, every OTU's abundance in each sample is drawn with replacement from that OTU's abundances across all samples:

~~~bash
uv run python MakeBootstraps.py example/fake_data.txt -n 5 -t permutation_#.csv -p example/pvals/
~~~

This creates 5 datasets. That is far too few for meaningful p-values and is only meant to keep the example quick. Use at least 100, which is the default.

Next, run SparCC on each resampled dataset. **Use exactly the same parameters as for the real data.** Name the output files consistently and number them sequentially, since the `#` in the template stands for the number.

One at a time:

~~~bash
uv run python Compute_SparCC.py -di example/pvals/permutation_0.csv -ni 5 --save_cor example/pvals/perm_cor_0.csv
uv run python Compute_SparCC.py -di example/pvals/permutation_1.csv -ni 5 --save_cor example/pvals/perm_cor_1.csv
# ... and so on up to permutation_4.csv
~~~

Or in a bash loop:

~~~bash
for i in $(seq 0 4); do
  uv run python Compute_SparCC.py -n Experiment_PVals -di example/pvals/permutation_$i.csv -ni 5 \
    --save_cor example/pvals/perm_cor_$i.csv --verbose False
done
~~~

Finally, compare the real correlations with the resampled ones.

- **One-sided** p-values take the sign of the correlation into account:

  ~~~bash
  uv run python PseudoPvals.py example/basis_corr/cor_sparcc.csv example/pvals/perm_cor_#.csv 5 -o example/pvals/pvals_one_sided.csv -t one_sided
  ~~~

- **Two-sided** p-values consider only the magnitude:

  ~~~bash
  uv run python PseudoPvals.py example/basis_corr/cor_sparcc.csv example/pvals/perm_cor_#.csv 5 -o example/pvals/pvals_two_sided.csv -t two_sided
  ~~~

********************************
## **Running with a configuration file**
********************************

`General_Execution.py` runs the whole pipeline: correlation, bootstraps, a correlation for each bootstrap, then p-values. It reads its parameters from `configuration.yml`:

~~~yaml
# Correlation calculation
name: 'experiment_sparCC'
data_input: 'example/fake_data.txt'
method: 'sparcc'
n_iteractions: 5          # recommended: 50-100
x_iteractions: 10
threshold: 0.1
normalization: 'dirichlet'
log_transform: True
save_corr_file: 'example/cor_sparcc.csv'
save_cov_file: Null

# Pseudo p-value calculation
num_simulate_data: 5      # recommended: >= 100
perm_template: 'permutation_#.csv'
outpath: 'example/pvals/'
type_pvalues: 'one_sided'
outfile_pvals: 'example/pvals/pvals_one_sided.csv'

# Output file
name_output_file: 'sparcc_version1'
~~~

If a field is set to `Null`, the script that uses it falls back to its default. For example, `x_iteractions: Null` uses the `Compute_SparCC.py` default of 10. `save_cov_file: Null` means no covariance file is written. To run the pipeline:

~~~bash
uv run python General_Execution.py
# or with another configuration file:
uv run python General_Execution.py --configuration-file my_config.yml
~~~

With the configuration above, the run produces:

- `example/cor_sparcc.csv`: the correlation matrix.
- `example/pvals/pvals_one_sided.csv`: the pseudo p-values.

The intermediate bootstrap files are deleted automatically. If any step fails, the pipeline stops.

********************
## **Worked example with your own data**
********************

A typical analysis of your own OTU table (replace `path/to/otu_table.txt` with your file) has five steps.

**Step 1:** Estimate the SparCC correlations.

~~~bash
uv run python Compute_SparCC.py -n Experiment_SparCC -di path/to/otu_table.txt -xi 50 -ni 100 --save_cor sparcc_output/cor_sparcc.csv
~~~

**Step 2:** Create the bootstrap datasets.

~~~bash
uv run python MakeBootstraps.py path/to/otu_table.txt -n 100 -t permutation_#.csv -p pvals/
~~~

**Step 3:** Run SparCC on every bootstrap dataset from Step 2, with the same parameters as Step 1.

~~~bash
for i in $(seq 0 99); do
  uv run python Compute_SparCC.py -n Experiment_PVals -di pvals/permutation_$i.csv -xi 50 -ni 100 \
    --save_cor pvals/perm_cor_$i.csv --verbose False
done
~~~

**Step 4:** Compute the pseudo p-values from the 100 bootstrap correlations.

~~~bash
uv run python PseudoPvals.py sparcc_output/cor_sparcc.csv pvals/perm_cor_#.csv 100 -o sparcc_output/pvals_one_sided.csv -t one_sided
~~~

**Step 5:** Keep only the OTU pairs whose p-value is at or below your significance level, e.g. `p <= 0.05`.

**Note:** You can run the same analysis with `General_Execution.py` by putting these parameters in the configuration file.

*********
## **Reference**
*********

Friedman J, Alm EJ (2012). *Inferring Correlation Networks from Genomic Survey Data.* PLoS Comput Biol 8(9): e1002687. [Publication](https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1002687)
