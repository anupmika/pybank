TOP_DIR := `git rev-parse --show-toplevel`
SRC_DIR := TOP_DIR / "src"
TESTS_DIR := TOP_DIR / "tests"
COV_DIR := TOP_DIR / "coverage"

[private]
default:
    @just --list --justfile {{justfile()}}

# Install or update project dependencies with `uv`
sync:
    @uv sync --no-cache --quiet

# Run the main application entrypoint
run: sync
    @uv run main.py

# Run the test target
test: sync
    @uv run --group dev pytest {{ TESTS_DIR }} -v

# Run tests with coverage report
cov: sync
    @uv run --group dev pytest {{ TESTS_DIR }} -v --cov-report=term-missing --cov-report=html:{{ COV_DIR }} --cov-report=xml:{{ COV_DIR }}/coverage.xml

# Remove the local environment and generated Python caches
clean:
    @uv clean
    @rm -rf __pycache__ .pytest_cache .mypy_cache .venv {{ COV_DIR }}
    @find . -type d \( -name "__pycache__" -o -name ".pytest_cache" -o -name ".mypy_cache" \) -prune -exec rm -rf {} +
