"""
SSO 연동 후 API 사용법

SSO로 받은 access_token을 사용하여
인증이 필요한 API를 호출하는 방법을 보여줍니다.

이것이 실무에서 가장 많이 쓰는 패턴입니다:
1. SSO 로그인 → access_token 획득
2. 이후 모든 API 호출에 토큰 포함
"""

import sys
import os

import requests

# ============================================
# 1. SSO 로그인 시뮬레이션 (토큰 획득)
# ============================================
def get_access_token_from_sso():
    """
    실제 서비스에서는 브라우저 SSO 플로우를 통해 토큰을 받지만,
    스크립트에서는 Mock SSO API를 직접 호출하여 토큰을 받습니다.
    """
    import jwt as pyjwt
    import time

    SSO_SECRET = "mock-sso-secret-key"

    # Mock SSO에서 사용자 정보 가져오기
    resp = requests.get("http://localhost:9999/mock-sso/users")
    users = resp.json()

    # 첫 번째 사용자로 id_token 생성 (실제로는 SSO 서버가 해줌)
    user = users["user1"]
    now = int(time.time())
    id_token = pyjwt.encode(
        {**user, "iat": now, "exp": now + 3600, "iss": "mock-sso", "aud": "our-platform"},
        SSO_SECRET,
        algorithm="HS256",
    )

    # 우리 서비스에 id_token 제출 → access_token 교환
    # (실제로는 form_post callback으로 처리됨)
    # 여기서는 직접 token exchange API를 호출
    print(f"[1] SSO id_token 획득 완료 (사용자: {user['username']})")
    print(f"    id_token: {id_token[:50]}...")

    # 자체 access_token 생성 (실제로는 callback 엔드포인트가 해줌)
    OUR_JWT_SECRET = "our-service-secret-key"
    access_token = pyjwt.encode(
        {
            "sub": user["loginid"],
            "role": user.get("role", "USER"),
            "department": user["deptid"],
            "department_kr": user["deptname"],
            "exp": now + 43200,  # 12시간
            "iat": now,
        },
        OUR_JWT_SECRET,
        algorithm="HS256",
    )

    print(f"[2] access_token 발급 완료 (12시간 유효)")
    print(f"    access_token: {access_token[:50]}...")
    return access_token


# ============================================
# 2. 인증된 API 호출 패턴
# ============================================
def call_authenticated_api(access_token: str):
    """
    모든 API 호출 시 Authorization 헤더에 토큰을 포함합니다.

    이것이 SSO 연동의 핵심입니다:
    - 한번 받은 토큰으로 모든 API 호출 가능
    - 12시간 동안 유효
    - 만료되면 다시 SSO 로그인
    """
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }

    print("\n[3] 인증된 API 호출")
    print(f"    Authorization: Bearer {access_token[:30]}...")

    try:
        resp = requests.get(
            "http://localhost:8000/api/me",
            headers=headers,
            timeout=10,
        )

        if resp.status_code == 200:
            data = resp.json()
            print(f"\n[결과] API 호출 성공!")
            print(f"    사용자: {data['username']}")
            print(f"    역할: {data['role']}")
            print(f"    부서: {data['department_kr']}")
            print(f"    메시지: {data['message']}")
        elif resp.status_code == 401:
            print(f"\n[오류] 인증 실패 — 토큰이 만료되었거나 유효하지 않습니다")
            print(f"    → 다시 SSO 로그인이 필요합니다")
        else:
            print(f"\n[오류] HTTP {resp.status_code}: {resp.text}")

    except requests.ConnectionError:
        print("\n[오류] 서버에 연결할 수 없습니다")
        print("    sso_mock_server.py와 sso_client.py가 실행 중인지 확인하세요")


# ============================================
# 3. requests 세션으로 토큰 자동 포함
# ============================================
def create_authenticated_session(access_token: str) -> requests.Session:
    """
    매번 헤더를 추가하는 대신, Session에 토큰을 설정하면
    이후 모든 요청에 자동으로 포함됩니다.

    실무 팁: 이렇게 세션을 만들어 재사용하세요.
    """
    session = requests.Session()
    session.headers.update({
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    })
    return session


# ============================================
# 4. SSO 연동 신청 절차 (이론)
# ============================================
SSO_INTEGRATION_GUIDE = """
=== SSO 연동 신청 절차 ===

1. SSO 관리 포털에서 서비스 등록 신청
   - 서비스명, 담당자, 콜백 URL 등록
   - client_id 발급 받음

2. 인증서 수령
   - SSO 서버의 공개키 인증서 (.cer 파일) 수령
   - id_token의 RS256 서명을 검증하는 데 사용

3. 콜백 URL 등록
   - SSO 서버가 form_post할 엔드포인트 URL
   - 예: https://your-service.company.net/callback

4. 개발 & 테스트
   - Mock SSO로 개발 (ENABLE_MOCK_SSO=true)
   - 실제 SSO로 전환 (ENABLE_MOCK_SSO=false)

5. 운영 배포
   - SSL 인증서 적용 필수
   - JWT 시크릿 키 변경
   - CORS 설정 확인

=== 주의사항 ===
- redirect_uri는 사전 등록된 것만 허용됨
- HTTPS 필수 (운영 환경)
- 토큰 만료 시 재로그인 (refresh token 없음)
"""


if __name__ == "__main__":
    print("=" * 50)
    print(" SSO 연동 API 사용법 데모")
    print("=" * 50)

    print("\n--- SSO 연동 신청 절차 ---")
    print(SSO_INTEGRATION_GUIDE)

    print("\n--- 토큰 획득 및 API 호출 테스트 ---")
    print("(sso_mock_server.py + sso_client.py 실행 필요)\n")

    try:
        token = get_access_token_from_sso()
        call_authenticated_api(token)

        print("\n\n--- Session 사용 예시 ---")
        session = create_authenticated_session(token)
        print(f"세션 생성 완료. 이후 session.get('/api/...') 으로 호출하면")
        print(f"Authorization 헤더가 자동으로 포함됩니다.")

    except Exception as e:
        print(f"\n서버가 실행 중이 아닙니다: {e}")
        print("먼저 다음 두 서버를 실행하세요:")
        print("  터미널 1: python sso_mock_server.py")
        print("  터미널 2: python sso_client.py")
