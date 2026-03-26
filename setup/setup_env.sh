#!/usr/bin/env bash
# ──────────────────────────────────────────────
# WSL/Linux 환경 설정 스크립트
#
# 가상환경 생성, 프록시 설정, 패키지 설치를 수행합니다.
# 사용법: bash setup/setup_env.sh
# ──────────────────────────────────────────────

set -euo pipefail

# 프로젝트 루트 디렉토리 (이 스크립트의 상위 디렉토리)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "========================================"
echo " 환경 설정을 시작합니다"
echo " 프로젝트 경로: $PROJECT_ROOT"
echo "========================================"

# ──────────────────────────────────────────────
# 1. 프록시 환경 변수 설정
# ──────────────────────────────────────────────
PROXY="${HTTP_PROXY:-http://your-proxy-host:8000}"

export HTTP_PROXY="$PROXY"
export HTTPS_PROXY="$PROXY"
export http_proxy="$PROXY"
export https_proxy="$PROXY"
export NO_PROXY="localhost,127.0.0.1,.your-company.net"
export no_proxy="localhost,127.0.0.1,.your-company.net"
export NODE_TLS_REJECT_UNAUTHORIZED=0

echo "[1/4] 프록시 설정 완료: $PROXY"
echo "       NO_PROXY: $NO_PROXY"

# ──────────────────────────────────────────────
# 2. Python 가상환경 생성
# ──────────────────────────────────────────────
VENV_DIR="$PROJECT_ROOT/.venv"

if [ -d "$VENV_DIR" ]; then
    echo "[2/4] 기존 가상환경이 존재합니다: $VENV_DIR"
else
    echo "[2/4] 가상환경을 생성합니다: $VENV_DIR"
    python3 -m venv "$VENV_DIR"
fi

# 가상환경 활성화
source "$VENV_DIR/bin/activate"
echo "       가상환경 활성화 완료 (Python: $(python --version))"

# ──────────────────────────────────────────────
# 3. pip 업그레이드 및 패키지 설치
# ──────────────────────────────────────────────
echo "[3/4] 패키지를 설치합니다..."

# SSL 검증 비활성화 (사내 프록시 인증서 이슈)
pip config set global.trusted-host "pypi.org files.pythonhosted.org pypi.python.org"

# pip 먼저 업그레이드
pip install --upgrade pip --proxy "$PROXY" --quiet

# npm strict-ssl 비활성화 (Node.js 패키지 사용 시)
command -v npm &>/dev/null && npm config set strict-ssl false

# requirements.txt에서 패키지 설치
REQUIREMENTS="$SCRIPT_DIR/requirements.txt"

if [ ! -f "$REQUIREMENTS" ]; then
    echo "오류: requirements.txt를 찾을 수 없습니다: $REQUIREMENTS"
    exit 1
fi

pip install -r "$REQUIREMENTS" --proxy "$PROXY"

echo "       패키지 설치 완료"

# ──────────────────────────────────────────────
# 4. Playwright 브라우저(Chromium) 설치
# ──────────────────────────────────────────────
echo "[4/4] Playwright Chromium 브라우저를 설치합니다..."
playwright install chromium
echo "       Playwright 설치 완료"

# ──────────────────────────────────────────────
# 완료 메시지
# ──────────────────────────────────────────────
echo ""
echo "========================================"
echo " 환경 설정이 완료되었습니다!"
echo "========================================"
echo ""
echo " 가상환경 활성화:"
echo "   source $VENV_DIR/bin/activate"
echo ""
echo " 연결 테스트:"
echo "   python setup/test_connection.py"
echo ""
echo " .env 파일을 프로젝트 루트에 생성하고"
echo " 게이트웨이 URL과 API 키를 설정하세요."
echo "   cp .env.example .env"
echo "========================================"
