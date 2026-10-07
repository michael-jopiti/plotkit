# Contributing

1. `uv sync --extra dev --extra polars`
2. Make changes with tests and NumPy-style docstrings.
3. `uv run ruff check . && uv run ruff format . && uv run mypy && uv run pytest`
4. Open a PR. Keep one concern per PR.

To add a palette, theme or plot: one new file plus one `register_*` call (see README).

A new built-in plot also needs a typed function in `src/plotkit/api.py` whose keyword-only options match the plot's `defaults` exactly (`tests/test_api.py` fails otherwise), and an entry in the README plot reference.
