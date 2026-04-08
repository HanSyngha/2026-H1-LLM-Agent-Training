# Python FastAPI 서버 + 로컬 빌드된 React dist 복사
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

# 로컬에서 빌드된 React dist를 직접 복사
COPY frontend/dist ./frontend/dist

EXPOSE 47777

HEALTHCHECK --interval=10s --timeout=3s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:47777/health')" || exit 1

CMD ["python", "server.py"]
