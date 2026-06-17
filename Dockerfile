FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Install dependencies first (layer caching)
COPY pyproject.toml ./
RUN uv sync --no-dev --no-install-project

# Copy source
COPY . .
RUN uv sync --no-dev

EXPOSE 8000

CMD ["uv", "run", "python", "main.py", "api"]
