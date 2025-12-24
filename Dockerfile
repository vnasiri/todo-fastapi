# syntax=docker/dockerfile:1

# -------------------------------------------------
# 1️⃣ Base image (stable Python release)
# -------------------------------------------------
ARG PYTHON_VERSION=3.14.2-slim
FROM python:${PYTHON_VERSION} AS base

LABEL maintainer="your-org@example.com"
LABEL description="Modern Todo API with FastAPI and PostgreSQL"
LABEL version="1.0.0"

# Global environment – deterministic, reproducible Python behaviour
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_TOOL_BIN_DIR=/usr/local/bin \
    PATH="/app/.venv/bin:$PATH" \
    VIRTUAL_ENV="/app/.venv" \
    PYTHONHASHSEED=random \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Create a non‑root user (early, so all later layers inherit it)
ARG UID=10001 GID=10001
RUN addgroup --system --gid "${GID}" appuser && \
    adduser --system --uid "${UID}" --ingroup appuser \
            --home /home/appuser --shell /sbin/nologin appuser

WORKDIR /app

# -------------------------------------------------
# 2️⃣ Builder stage – compile dependencies only
# -------------------------------------------------
FROM base AS builder

# Build‑time only packages
ARG BUILD_DEPS="build-essential gcc libpq-dev"
RUN apt-get update && \
    apt-get install -y --no-install-recommends ${BUILD_DEPS} && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Pull the verified uv binary (fixed digest from upstream)
COPY --from=ghcr.io/astral-sh/uv:0.8.23 /uv /uvx /usr/local/bin/

# Copy only lockfiles – this keeps the Docker cache happy
COPY --chown=appuser:appuser pyproject.toml uv.lock ./

# Install Python deps into a virtualenv (cached)
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-install-project --no-editable

# -------------------------------------------------
# 3️⃣ Runtime stage – final minimal image
# -------------------------------------------------
FROM base AS runtime

# Runtime‑only OS packages
ARG RUN_DEPS="libpq5 curl ca-certificates"
RUN apt-get update && \
    apt-get install -y --no-install-recommends ${RUN_DEPS} && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Bring the compiled virtualenv from the builder
COPY --from=builder --chown=appuser:appuser /app/.venv /app/.venv

ENV PATH="/app/.venv/bin:$PATH"

# Create flower data dir and set permissions
RUN mkdir -p /var/lib/flower && chown -R appuser:appuser /var/lib/flower

RUN chown -R appuser:appuser /app/

# Switch to the non‑root user explicitly (clarity)
USER appuser

# Copy the application source (read‑only for the container)
COPY --chown=appuser:appuser . /app/

EXPOSE 8000

CMD [ "./entrypoint.sh" ]