# Stage to install Python dependencies with uv
FROM ghcr.io/astral-sh/uv:0.5.29 AS uv

WORKDIR /app

# Copy dependency declarations
COPY api/pyproject.toml api/uv.lock ./

# Install packages into the system site-packages
RUN uv pip install --system -r uv.lock

FROM python:3.12-slim

# Install system dependencies required for movie rendering and Playwright
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        ffmpeg \
        libnss3 libatk-bridge2.0-0 libgtk-3-0 libxcb1 \
        libxcomposite1 libxdamage1 libxrandr2 libasound2 \
        libxss1 libxtst6 fonts-liberation libatk1.0-0 \
        libdrm2 libgbm1 libxkbcommon0 libnspr4 libx11-xcb1 \
        libxshmfence1 libu2f-udev libcups2 libdbus-1-3 \
        wget && \
    rm -rf /var/lib/apt/lists/*

# Copy installed Python packages and uv from the build stage
COPY --from=uv /usr/local /usr/local

WORKDIR /app

# Copy project files
COPY api /app

# Install Playwright browsers
RUN playwright install

CMD ["python", "examples/pipeline_test.py"]
