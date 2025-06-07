FROM python:3.12-slim
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

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

COPY . /app

RUN uv pip install -e . --break-system-packages --system

CMD ["fastapi", "run", "src/lecturia/server.py"]
