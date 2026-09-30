"""
Tests for the root-level scripts MakeBootstraps.py and PseudoPvals.py.

Run with: uv run pytest tests/test_bootstraps_pvals.py
"""
import numpy as np
import pandas as pd

from MakeBootstraps import make_bootstraps, permute_w_replacement
from PseudoPvals import get_pvalues
from sparcc.io_methods import write_txt


def test_permute_w_replacement_resamples_within_columns():
    rng = np.random.default_rng(0)
    frame = pd.DataFrame({'otu0': [1, 2, 3, 4, 5], 'otu1': [10, 20, 30, 40, 50]},
                         index=[f's{i}' for i in range(5)])

    perm = permute_w_replacement(frame, axis=0, rng=rng)

    assert isinstance(perm, pd.DataFrame)
    assert perm.index.equals(frame.index) and perm.columns.equals(frame.columns)
    for col in frame.columns:
        assert set(perm[col]).issubset(set(frame[col]))


def test_make_bootstraps_writes_files(tmp_path):
    frame = pd.DataFrame(np.arange(1, 21).reshape(5, 4), columns=list('abcd'))
    make_bootstraps(frame, 3, 'perm_#.csv', outpath=str(tmp_path))
    assert sorted(p.name for p in tmp_path.iterdir()) == ['perm_0.csv', 'perm_1.csv', 'perm_2.csv']


def test_get_pvalues(tmp_path):
    labels = ['a', 'b']
    cor = pd.DataFrame([[1.0, 0.5], [0.5, 1.0]], index=labels, columns=labels)
    perms = [
        [[1.0, 0.6], [0.6, 1.0]],    # as extreme, same sign
        [[1.0, -0.7], [-0.7, 1.0]],  # as extreme, opposite sign
        [[1.0, 0.1], [0.1, 1.0]],    # less extreme
        [[1.0, 0.2], [0.2, 1.0]],    # less extreme
    ]
    for i, p in enumerate(perms):
        write_txt(pd.DataFrame(p, index=labels, columns=labels), tmp_path / f'cor_{i}.csv')
    template = str(tmp_path / 'cor_#.csv')

    two_sided = get_pvalues(cor, template, len(perms), test_type='two_sided')
    one_sided = get_pvalues(cor, template, len(perms), test_type='one_sided')

    assert two_sided.loc['a', 'b'] == 0.5
    assert one_sided.loc['a', 'b'] == 0.25
    assert (np.diag(two_sided.values) == 1).all()
