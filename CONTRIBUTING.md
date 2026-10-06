# Contributing

1. `uv sync --extra dev --extra polars`
2. Make changes with tests and NumPy-style docstrings.
3. `uv run ruff check . && uv run ruff format . && uv run mypy && uv run pytest`
4. Open a PR. Keep one concern per PR.

To add a palette, theme or plot: one new file plus one `register_*` call (see README).
