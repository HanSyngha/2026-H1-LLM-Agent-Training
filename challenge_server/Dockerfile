FROM python:3.11-slim

# 사내 프록시 환경
ARG HTTP_PROXY=""
ARG HTTPS_PROXY=""
ARG NO_PROXY="localhost,127.0.0.1,.samsungds.net"
ENV HTTP_PROXY=${HTTP_PROXY} \
    HTTPS_PROXY=${HTTPS_PROXY} \
    NO_PROXY=${NO_PROXY} \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    TZ=Asia/Seoul

WORKDIR /app

# 의존성 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
    -i http://repo.samsungds.net/artifactory/api/pypi/pypi-remote/simple \
    --trusted-host repo.samsungds.net

# 애플리케이션 복사
COPY server.py challenges.py prompt_challenge.py dashboard.html prompt_page.html settings_page.html ./

EXPOSE 47777

HEALTHCHECK --interval=10s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:47777/health')" || exit 1

CMD ["python", "server.py"]
