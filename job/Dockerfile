ARG PYTHON_VERSION=3.13
FROM python:${PYTHON_VERSION}-slim-bookworm

# 1. Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

WORKDIR /job
ENV UV_COMPILE_BYTECODE=1

# --- NEW SECTION START ---
# 2. Install Build Tools (Fixes the "g++ failed" error)
# Scientific packages like 'inmoose' often need to compile C++ code.
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*
# --- NEW SECTION END ---

# 3. Install Scientific Libraries
RUN --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    uv sync --frozen --no-dev

COPY . .

# The entrypoint is your analysis script
ENV PATH="/job/.venv/bin:$PATH"
ENTRYPOINT ["python", "main.py"]