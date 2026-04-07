# Stage 1: React 빌드
FROM node:24-alpine AS frontend

ARG HTTP_PROXY=""
ARG HTTPS_PROXY=""
ARG NO_PROXY="localhost,127.0.0.1,.samsungds.net"
ENV HTTP_PROXY=${HTTP_PROXY} \
    HTTPS_PROXY=${HTTPS_PROXY} \
    NO_PROXY=${NO_PROXY} \
    NODE_TLS_REJECT_UNAUTHORIZED=0

WORKDIR /app/frontend

RUN npm config set strict-ssl false && \
    if [ -n "$HTTP_PROXY" ]; then npm config set proxy $HTTP_PROXY && npm config set https-proxy $HTTP_PROXY; fi

COPY frontend/package*.json ./
RUN npm install --legacy-peer-deps

COPY frontend/ ./
RUN npm run build

# Stage 2: Python FastAPI 서버
FROM python:3.11-slim

ARG HTTP_PROXY=""
ARG HTTPS_PROXY=""
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    TZ=Asia/Seoul

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
    -i http://repo.samsungds.net/artifactory/api/pypi/pypi-remote/simple \
    --trusted-host repo.samsungds.net

COPY server.py challenges.py prompt_challenge.py ./
COPY dashboard.html prompt_page.html settings_page.html ./
COPY financial_articles.json ./

COPY --from=frontend /app/frontend/dist ./frontend/dist

EXPOSE 47777

HEALTHCHECK --interval=10s --timeout=3s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:47777/health')" || exit 1

CMD ["python", "server.py"]
