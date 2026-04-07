# Stage 1: React 빌드
FROM node:24-alpine AS frontend

ARG HTTP_PROXY=""
ARG HTTPS_PROXY=""
ENV HTTP_PROXY=${HTTP_PROXY} HTTPS_PROXY=${HTTPS_PROXY}

WORKDIR /app/frontend

# npm 프록시 + SSL 설정 (사내망)
RUN npm config set strict-ssl false

COPY frontend/package*.json ./
RUN npm install --legacy-peer-deps

COPY frontend/ ./
RUN npm run build

# Stage 2: Python FastAPI 서버
FROM python:3.11-slim

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
