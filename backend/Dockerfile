ARG PYTHON_VERSION=3.13
FROM python:${PYTHON_VERSION}-slim-bookworm

COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

WORKDIR /app
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy

RUN --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    uv sync --frozen --no-install-project --no-dev

COPY . .

RUN --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    uv sync --frozen --no-dev

ENV PATH="/app/.venv/bin:$PATH"

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
