TOP_DIR := `git rev-parse --show-toplevel`
SRC_DIR := TOP_DIR / "src"
TESTS_DIR := TOP_DIR / "tests"

[private]
default:
    @just --list --justfile {{justfile()}}

# Install or update project dependencies with `uv`
sync:
    @uv sync --no-cache

# Run the test target
test: sync
    @PYTHONPATH={{ TOP_DIR }} uv run --group dev pytest {{ TESTS_DIR }} -v

# Remove the local environment and generated Python caches
clean:
    @uv clean
    @rm -rf __pycache__ .pytest_cache .mypy_cache .venv
    @find . -type d \( -name "__pycache__" -o -name ".pytest_cache" -o -name ".mypy_cache" \) -prune -exec rm -rf {} +
