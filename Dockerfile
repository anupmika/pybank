# ##########################################################################
# File: Dockerfile
# Author: Varnika (anupmika)
# Description: Dockerfile for a Streamlit application.
# ##########################################################################

# ##########################################################################
# License
# ##########################################################################
# This Dockerfile is licensed under the Apache 2.0 License.
# License information should be updated as necessary.
# ##########################################################################

# ##########################################################################
# Base Image
# ##########################################################################
FROM ghcr.io/astral-sh/uv:python3.12-trixie-slim

# ##########################################################################
# Maintainer
# ##########################################################################
LABEL maintainer="Varnika (anupmika)"

# Add non-root user
RUN addgroup --system nonroot \
  && adduser --system --ingroup nonroot nonroot

# ##########################################################################
# Set Working Directory
# ##########################################################################
WORKDIR /app

# Set cache directory to /tmp to avoid permission issues
ENV XDG_CACHE_HOME=/tmp/.cache

# ##########################################################################
# Copy Files
# ##########################################################################
# Copy dependency files first for better caching
COPY pyproject.toml uv.lock ./

# Install dependencies into a local folder
RUN uv sync --no-cache --frozen --no-build

# Copy source code
COPY src/ ./

# ##########################################################################
# Expose Port
# ##########################################################################
EXPOSE 8501

# ##########################################################################
# Command to Run
# ##########################################################################
# # Switch to non-root user
# USER nonroot

# # ENTRYPOINT [ "uv", "run", "--no-build", "--frozen", \
# #   "streamlit", "run", "app.py", \
# #   "--server.port=8501", \
# #   "--server.address=0.0.0.0", \
# #   "--browser.gatherUsageStats=false"]

# ENTRYPOINT [ "uv", "run", "--no-build", "--frozen", \
#   "python", "-m", "streamlit", "run", "src/app.py", \
#   "--server.port=8501", \
#   "--server.address=0.0.0.0", \
#   "--browser.gatherUsageStats=false" ]

# Force the container to explicitly work from the application root directory
WORKDIR /app

# Add both root and src directory into the Python module path
ENV PYTHONPATH="/app:/app/src"

# Use the absolute python path approach bypassing the 'File does not exist' issue
ENTRYPOINT [ "uv", "run", "--no-build", "--frozen", \
  "python", "-m", "streamlit", "run", "src/app.py", \
  "--server.port=8501", \
  "--server.address=0.0.0.0", \
  "--browser.gatherUsageStats=false" ]
