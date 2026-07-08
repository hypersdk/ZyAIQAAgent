# syntax=docker/dockerfile:1

FROM node:20-bookworm AS node-base
WORKDIR /app
COPY package.json package-lock.json* ./
RUN npm install
RUN npx playwright install --with-deps chromium

FROM python:3.11-slim-bookworm AS python-base
WORKDIR /app
COPY pyproject.toml ./
COPY orchestrator/ ./orchestrator/
COPY agents/ ./agents/
COPY github/ ./github/
COPY prompts/ ./prompts/
COPY templates/ ./templates/
COPY playwright/ ./playwright/
COPY tests/ ./tests/
RUN pip install --no-cache-dir -e .

FROM python:3.11-slim-bookworm
WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libnss3 libnspr4 libdbus-1-3 libatk1.0-0 libatk-bridge2.0-0 \
    libcups2 libdrm2 libxkbcommon0 libxcomposite1 libxdamage1 \
    libxfixes3 libxrandr2 libgbm1 libpango-1.0-0 libcairo2 libasound2 \
    && rm -rf /var/lib/apt/lists/*

COPY --from=node-base /app/node_modules ./node_modules
COPY --from=node-base /root/.cache/ms-playwright /root/.cache/ms-playwright
COPY --from=python-base /app /app
COPY package.json tsconfig.json ./
COPY orchestrator/ ./orchestrator/
COPY agents/ ./agents/
COPY github/ ./github/
COPY prompts/ ./prompts/
COPY templates/ ./templates/
COPY playwright/ ./playwright/
COPY tests/ ./tests/

ENV ZYVOR_BASE_URL=https://zyvor.dev
ENV PLAYWRIGHT_BROWSERS_PATH=/root/.cache/ms-playwright

ENTRYPOINT ["zyvor-qa"]
CMD ["run", "--source", "local"]
