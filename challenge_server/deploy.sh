#!/bin/bash
# ============================================
# Challenge Server 배포 스크립트
# ============================================
#
# 사용법:
#   ./deploy.sh              # 빌드 + 시작
#   ./deploy.sh stop         # 중지
#   ./deploy.sh restart      # 재빌드 + 재시작
#   ./deploy.sh logs         # 실시간 로그
#   ./deploy.sh status       # 상태 확인
#   ./deploy.sh test         # 헬스체크 + 과제 목록
#

set -euo pipefail

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

log()  { echo -e "${GREEN}[CHALLENGE]${NC} $*"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $*"; }
err()  { echo -e "${RED}[ERROR]${NC} $*" >&2; }
info() { echo -e "${CYAN}[INFO]${NC} $*"; }

cd "$(dirname "$0")"

# .env 로드
if [ -f .env ]; then
    set -a; source .env; set +a
    log ".env 로드 완료"
else
    if [ -f .env.example ]; then
        cp .env.example .env
        warn ".env 파일이 없어서 .env.example을 복사했습니다. 설정을 확인해주세요."
    fi
fi

CHALLENGE_PORT="${CHALLENGE_PORT:-47777}"
AUTH_SERVER="${AUTH_SERVER:-http://12.81.222.45:8090}"

case "${1:-start}" in
    start|up|"")
        log "Challenge 서버를 시작합니다..."
        log "포트: ${CHALLENGE_PORT}"
        log "인증 서버: ${AUTH_SERVER}"
        echo ""

        # React 프론트엔드 빌드 (로컬 node 사용)
        log "프론트엔드 빌드 중..."
        cd frontend
        npm install --include=dev 2>&1 | tail -3
        npm run build 2>&1 | tail -5
        cd ..
        log "프론트엔드 빌드 완료"

        log "Docker 이미지 빌드 중..."
        docker compose down --rmi local 2>/dev/null
        docker compose build --no-cache --progress=plain 2>&1 | tail -20
        log "Docker 이미지 빌드 완료"

        log "컨테이너 시작 중..."
        docker compose up -d 2>&1
        log "시작 완료. 헬스체크 대기 중..."
        sleep 3

        # 헬스체크
        if curl -sf "http://localhost:${CHALLENGE_PORT}/health" > /dev/null 2>&1; then
            log "✅ 서버 정상 동작"
            echo ""
            info "대시보드:  http://$(hostname -I | awk '{print $1}'):${CHALLENGE_PORT}"
            info "설정:      http://$(hostname -I | awk '{print $1}'):${CHALLENGE_PORT}/settings"
            info "헬스체크:  http://$(hostname -I | awk '{print $1}'):${CHALLENGE_PORT}/health"
            echo ""

            # 과제 목록 표시
            CHALLENGES=$(curl -sf "http://localhost:${CHALLENGE_PORT}/challenges" 2>/dev/null)
            if [ -n "$CHALLENGES" ]; then
                log "등록된 과제:"
                echo "$CHALLENGES" | python3 -c "
import sys, json
for c in json.load(sys.stdin):
    print(f\"  [{c['id']}] {c['name']}\")
" 2>/dev/null || echo "  (과제 목록 파싱 실패)"
            fi
        else
            err "서버 시작 실패. 로그를 확인하세요:"
            err "  ./deploy.sh logs"
            exit 1
        fi
        ;;

    stop|down)
        log "Challenge 서버를 중지합니다..."
        docker compose down
        log "중지 완료"
        ;;

    restart)
        log "Challenge 서버를 재시작합니다..."
        docker compose down
        docker compose build --no-cache
        docker compose up -d
        sleep 3

        if curl -sf "http://localhost:${CHALLENGE_PORT}/health" > /dev/null 2>&1; then
            log "✅ 재시작 완료"
        else
            err "재시작 실패"
            exit 1
        fi
        ;;

    logs)
        docker compose logs -f --tail=50
        ;;

    status)
        echo ""
        info "=== Challenge Server Status ==="
        docker compose ps
        echo ""

        if curl -sf "http://localhost:${CHALLENGE_PORT}/health" > /dev/null 2>&1; then
            HEALTH=$(curl -sf "http://localhost:${CHALLENGE_PORT}/health")
            log "✅ 서버 정상"
            echo "  $HEALTH" | python3 -m json.tool 2>/dev/null || echo "  $HEALTH"
        else
            err "❌ 서버 응답 없음"
        fi

        echo ""
        COMPLETIONS=$(curl -sf "http://localhost:${CHALLENGE_PORT}/completions" 2>/dev/null)
        if [ -n "$COMPLETIONS" ]; then
            info "=== 성공자 현황 ==="
            echo "$COMPLETIONS" | python3 -c "
import sys, json
data = json.load(sys.stdin)
for cid, info in data['challenges'].items():
    count = len(info['completions'])
    names = ', '.join(c['name'] for c in info['completions'][:5])
    print(f\"  [{cid}] {info['name']}: {count}명 {('— ' + names) if names else ''}\")
" 2>/dev/null || echo "  (파싱 실패)"
        fi
        ;;

    test)
        echo ""
        info "=== 헬스체크 ==="
        curl -sf "http://localhost:${CHALLENGE_PORT}/health" | python3 -m json.tool 2>/dev/null
        echo ""

        info "=== 과제 목록 ==="
        curl -sf "http://localhost:${CHALLENGE_PORT}/challenges" | python3 -c "
import sys, json
for c in json.load(sys.stdin):
    print(f\"  [{c['id']}] {c['name']} — {c['completions']}명 통과\")
" 2>/dev/null

        echo ""
        info "=== 브라우저 타겟 페이지 ==="
        BODY=$(curl -sf "http://localhost:${CHALLENGE_PORT}/browser-target" 2>/dev/null)
        if echo "$BODY" | grep -q "데이터 로드 중"; then
            log "✅ JS 렌더링 페이지 정상 (curl로는 '데이터 로드 중'만 보임)"
        else
            warn "⚠ 페이지 응답 이상"
        fi

        echo ""
        info "=== wiki 데이터 API ==="
        curl -sf "http://localhost:${CHALLENGE_PORT}/api/wiki-data" | python3 -c "
import sys, json
data = json.load(sys.stdin)
for p in data:
    print(f\"  {p['name']}: {p['price']:,}원\")
" 2>/dev/null
        ;;

    *)
        echo "사용법: ./deploy.sh [start|stop|restart|logs|status|test]"
        exit 1
        ;;
esac
