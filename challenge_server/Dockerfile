# Stage 1: React 빌드 (Docker 내에서 npm install + build)
FROM node:24-alpine AS frontend

WORKDIR /app/frontend

ENV NODE_TLS_REJECT_UNAUTHORIZED=0
RUN npm config set strict-ssl false && \
    npm config set registry https://repo.samsungds.net/artifactory/api/npm/npm-remote/

COPY frontend/package*.json ./
RUN npm install --include=dev

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
    --trusted-host repo.samsungds.net \
    || pip install --no-cache-dir -r requirements.txt

COPY server.py challenges.py prompt_challenge.py ./
COPY dashboard.html prompt_page.html settings_page.html ./
COPY financial_articles.json ./

COPY --from=frontend /app/frontend/dist ./frontend/dist

EXPOSE 47777

HEALTHCHECK --interval=10s --timeout=3s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:47777/health')" || exit 1

CMD ["python", "server.py"]
