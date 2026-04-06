FROM python:3.13-slim

RUN apt-get update && \
    apt-get install -y --no-install-recommends curl && \
    rm -rf /var/lib/apt/lists/*

RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:$PATH"

WORKDIR /app

COPY pyproject.toml uv.lock README.md ./
COPY anonbr/ anonbr/

RUN uv sync --no-dev

COPY . .

RUN uv sync --no-dev

ENTRYPOINT ["uv", "run", "python", "-m", "main"]