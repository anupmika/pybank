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

# Run the Streamlit application development server
dev-ui: sync
    @uv run streamlit run streamlit_app.py \
    --server.headless=true \
    --server.address=0.0.0.0

# Run the test target
test: sync
    @uv run --group dev pytest {{ TESTS_DIR }} -v

# Run tests with coverage report
coverage: sync
    @uv run --group dev pytest {{ TESTS_DIR }} -v \
    --cov-report=html:{{ COV_DIR }} \
    --cov-report=xml:{{ COV_DIR }}/coverage.xml \
    --cov-report=lcov:{{ COV_DIR }}/lcov.info

# Run tests and generate coverage report for Codecov Coverage
codecov-coverage: sync
    @uv run --group dev pytest --cov --cov-branch --cov-report=xml

# Run tests and generate coverage report for Codecov Tests
codecov-tests: sync
    @uv run --group dev pytest --cov --junitxml=junit.xml -o junit_family=legacy

# Remove the local environment and generated Python caches
clean:
    @uv clean
    @rm -rf __pycache__ .pytest_cache .mypy_cache .venv {{ COV_DIR }}
    @find . -type d \( -name "__pycache__" -o -name ".pytest_cache" -o -name ".mypy_cache" \) -prune -exec rm -rf {} +
