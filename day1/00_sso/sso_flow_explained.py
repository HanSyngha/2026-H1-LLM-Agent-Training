"""
SSO (Single Sign-On) 동작 원리 설명

사내 SSO의 전체 흐름을 단계별로 설명합니다.
실제 A2A Agent Platform의 구현을 기반으로 합니다.

핵심 포인트:
- SSO 서버에 1회 요청 → 전체 인물정보가 JWT ID 토큰으로 반환
- 토큰 재요청(refresh) 로직 없음
- form_post 방식으로 안전하게 토큰 전달
"""

# ============================================
# SSO 전체 흐름도 (18단계)
# ============================================
#
#  [사용자]                    [프론트엔드]               [API Gateway]            [SSO 서버]
#     |                           |                          |                       |
#     |-- 1. 로그인 클릭 -------->|                          |                       |
#     |                           |-- 2. POST /api/auth/login -->                    |
#     |                           |                          |-- 3. SSO URL 생성     |
#     |                           |<-- 4. sso_login_url ----|                       |
#     |<-- 5. redirect ----------|                          |                       |
#     |                           |                          |                       |
#     |-- 6. 로그인 (ID/PW) ------------------------------------------------>     |
#     |                           |                          |                       |
#     |                           |                          |<-- 7. form_post ------|
#     |                           |                          |    (id_token JWT)     |
#     |                           |                          |                       |
#     |                           |<-- 8. redirect + id_token                       |
#     |                           |                          |                       |
#     |                           |-- 9. POST /api/auth/callback                    |
#     |                           |    { "id_token": "..." } |                       |
#     |                           |                          |                       |
#     |                           |<-- 10. access_token + user_info                 |
#     |                           |                          |                       |
#     |<-- 11. 로그인 완료! ------|                          |                       |
#
# 이후 모든 API 요청:
#   Authorization: Bearer <access_token>
#

# ============================================
# SSO의 핵심: "1회 요청 = 전체 정보"
# ============================================
#
# 우리 사내 SSO의 특징:
# 1. SSO 서버에서 돌아오는 id_token 안에 모든 정보가 들어있음
# 2. 별도의 /userinfo 엔드포인트 호출 불필요
# 3. token refresh 불필요 (12시간 후 재로그인)
#
# id_token JWT 페이로드 예시:
# {
#     "loginid": "hong.gildong",        ← 사번/로그인ID
#     "username": "홍길동",              ← 한글 이름
#     "mail": "hong.gildong@company.com",← 이메일
#     "deptid": "dev_team",             ← 부서 코드
#     "deptname": "개발팀",              ← 부서명 (한글)
#     "deptname_en": "Dev Team",         ← 부서명 (영문)
#     "iat": 1234567890,                 ← 발급 시각
#     "exp": 1234571490,                 ← 만료 시각
#     "iss": "sso-server",               ← 발급자
#     "aud": "our-platform"              ← 대상
# }
#
# ↑ 이 하나의 토큰만으로 사용자 인증 + 정보 획득이 완료됨!


# ============================================
# 비교: 일반 OAuth2 vs 우리 SSO
# ============================================
#
# [일반 OAuth2]
#   1. /authorize → code 받음
#   2. /token → access_token + refresh_token 받음
#   3. /userinfo → 사용자 정보 받음
#   4. refresh_token으로 주기적 갱신
#   → 최소 3번의 서버 통신 필요
#
# [우리 SSO]
#   1. /authorize → id_token (JWT) 받음 ← 여기에 모든 정보!
#   2. 끝. refresh 없음.
#   → 1번의 통신으로 완료
#
# 이것이 "서버에 한번 갔다오면 바로 전체 인물 정보를 다주는 방식"


print(__doc__)
print("이 파일은 SSO 흐름 설명용입니다.")
print("실제 동작하는 코드는 sso_mock_server.py와 sso_client.py를 참고하세요.")
