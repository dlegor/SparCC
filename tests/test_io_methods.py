"""
Tests for sparcc/io_methods.py (read_txt, write_txt).

Run with: uv run pytest tests/test_io_methods.py
"""
import numpy as np
import pandas as pd
import pytest

from sparcc.io_methods import read_txt, write_txt


def test_write_read_round_trip(tmp_path):
    # samples as rows, OTUs as columns (the in-memory convention)
    frame = pd.DataFrame(np.arange(12).reshape(4, 3),
                         index=['s0', 's1', 's2', 's3'], columns=['otu0', 'otu1', 'otu2'])
    path = tmp_path / 'table.csv'

    write_txt(frame, path)  # written transposed: OTUs as rows
    assert pd.read_csv(path, index_col=0).shape == (3, 4)

    back = read_txt(path, index_col=0, verbose=False)  # transposed back
    pd.testing.assert_frame_equal(back, frame)


def test_read_txt_tab_separated(tmp_path):
    path = tmp_path / 'table.txt'
    path.write_text('OTU\ts0\ts1\notu0\t1\t2\notu1\t3\t4\n')
    table = read_txt(path, index_col=0, verbose=False)
    assert list(table.index) == ['s0', 's1']
    assert list(table.columns) == ['otu0', 'otu1']


def test_read_txt_unsupported_suffix(tmp_path):
    path = tmp_path / 'table.tsv'
    path.write_text('a\tb\n')
    with pytest.raises(OSError):
        read_txt(path)
