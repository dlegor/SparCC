"""
Tests for sparcc/args.py (command-line parsing for Compute_SparCC.py).

Run with: uv run pytest tests/test_args.py
"""
import argparse

import pytest

from sparcc.args import parse_args, str2bool


@pytest.mark.parametrize('value, expected', [
    ('True', True), ('true', True), ('1', True), ('yes', True),
    ('False', False), ('false', False), ('0', False), ('no', False),
])
def test_str2bool(value, expected):
    assert str2bool(value) is expected


def test_str2bool_invalid():
    with pytest.raises(argparse.ArgumentTypeError):
        str2bool('maybe')


def test_parse_args_has_no_side_effects(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    args = parse_args(['-di', 'counts.txt', '--verbose', 'False', '-ni', '5'])

    assert args.data_input == 'counts.txt'
    assert args.verbose is False
    assert args.n_iter == 5
    assert args.save_cor == 'Cor_SparCC.csv'
    assert list(tmp_path.iterdir()) == []
