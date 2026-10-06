# plotkit conventions

- Package `plotkit`, `src/` layout, Python >=3.10, full type hints, NumPy docstrings.
- Env: `uv sync --extra dev --extra polars`. Run everything via `uv run`.
- Checks before every commit: `uv run ruff check . && uv run ruff format --check . && uv run mypy && uv run pytest`.
- Importing plotkit must never mutate matplotlib global state. Use `rc_context`.
- Only `plotkit/data/adapter.py` may touch polars. Everything else takes pandas.
- Extensions: one new file + one `register_*` call (palettes, themes, plots).
- Tests use the `Agg` backend. One commit per milestone. Never push without asking.
