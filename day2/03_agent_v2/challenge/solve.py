"""
Agent 설계 과제 — 바이브 코딩으로 에이전트를 만드세요!

이 스크립트를 바이브 코딩 도구(Cursor, Claude Code 등)에게 주고
"이 미로를 푸는 에이전트를 만들어줘"라고 요청하세요.

=== 미로 규칙 ===
1. /start 호출 → 5개 작업 목록이 나옵니다
2. /task/{id} 호출 → 작업 실행 (순서대로!)
   - 일부 작업은 랜덤으로 실패합니다 → 재시도 필요!
   - 각 작업은 데이터를 반환합니다 → 수집해야 합니다
3. /end 호출 → 5개 다 완료해야 completion_code 발급

=== API 목록 ===
GET /challenges/agent_v2/start?token=TOKEN    → 시작
GET /challenges/agent_v2/task/{id}?token=TOKEN → 작업 실행
GET /challenges/agent_v2/end?token=TOKEN      → 완료

=== 성공 시 ===
completion_code를 강의 슬라이드에 입력하면 통과!

실행: python solve.py
"""

# ============================================
# 서버 정보 — 수정하지 마세요
# ============================================
CHALLENGE_SERVER = "http://a2g.samsungds.net:47777"
LLM_GATEWAY = "http://a2g.samsungds.net:8090/v1"
SERVICE_ID = "test-service"
MODEL = "testmodel"

# ============================================
# 여기에 본인 정보를 입력하세요
# ============================================
TOKEN = ""  # SSO access_token (로그인 후 획득)
USER_ID = ""  # SSO user ID

# ============================================
# 바이브 코딩으로 아래를 완성하세요!
#
# 힌트:
# - requests로 API 호출
# - LLM에게 tool을 정의하고 호출하게 하거나
# - 직접 로직을 짜서 API를 순서대로 호출해도 됩니다
# - 실패하는 작업은 재시도해야 합니다
# - 최종 completion_code를 출력하세요
# ============================================

print("🔄 에이전트를 구현하세요!")
print(f"서버: {CHALLENGE_SERVER}")
print(f"LLM: {LLM_GATEWAY}")
print()
print("바이브 코딩 도구에게 이 파일을 주고:")
print('"이 미로를 푸는 에이전트를 만들어줘"라고 요청하세요.')
