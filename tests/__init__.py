"""
Test suite for SparCC.

How to run the tests (from the repository root)::

    uv sync                                   # once: create .venv with the dev dependencies
    uv run pytest -q                          # whole suite
    uv run pytest tests/test_SparCC.py        # a single file
    uv run pytest -k clr                      # tests whose name matches "clr"
    uv run pytest -x -v                       # verbose, stop at the first failure

pytest is configured in pyproject.toml ([tool.pytest.ini_options]): it collects
from ``tests/`` and puts the repository root on ``sys.path`` so the root-level
scripts (MakeBootstraps.py, PseudoPvals.py) can be imported. The first run is
slower because Numba compiles the ``@njit`` functions.
"""
