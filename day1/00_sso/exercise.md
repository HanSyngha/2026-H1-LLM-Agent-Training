# 실습: SSO 인증 체험하기

## 목표

Mock SSO 서버와 클라이언트를 실행하여 SSO 인증 흐름을 직접 체험하고,
JWT 토큰의 구조를 이해합니다.

---

## 요구사항

### 1. Mock SSO 서버 실행 및 로그인 테스트

1. **터미널 1**에서 Mock SSO 서버를 실행하세요:
   ```bash
   python sso_mock_server.py
   ```
   - 서버가 `http://localhost:9999`에서 실행되는지 확인하세요.

2. **터미널 2**에서 SSO 클라이언트를 실행하세요:
   ```bash
   python sso_client.py
   ```
   - 클라이언트가 `http://localhost:8000`에서 실행되는지 확인하세요.

3. 브라우저에서 `http://localhost:8000`에 접속하여 SSO 로그인 흐름을 체험하세요:
   - "SSO 로그인" 버튼 클릭
   - SSO 로그인 페이지에서 사용자 선택
   - 로그인 성공 페이지에서 사용자 정보 확인

### 2. JWT 토큰 디코딩하여 인물정보 확인

로그인 성공 후 표시되는 `id_token`을 직접 디코딩하여 인물 정보를 확인하세요.

**방법 1: jwt.io 사용**
- https://jwt.io에 접속하여 토큰을 붙여넣기

**방법 2: Python 코드로 디코딩**
```python
import jwt
import json

id_token = "여기에_토큰_붙여넣기"

# 서명 검증 없이 디코딩 (학습용)
payload = jwt.decode(id_token, options={"verify_signature": False})
print(json.dumps(payload, ensure_ascii=False, indent=2))
```

**확인할 항목:**
- [ ] `loginid`: 사번/로그인 ID
- [ ] `username`: 한글 이름
- [ ] `mail`: 이메일 주소
- [ ] `deptid`: 부서 코드
- [ ] `deptname`: 부서명
- [ ] `role`: 역할 (ADMIN/USER)
- [ ] `exp`: 토큰 만료 시간 (Unix timestamp)

### 3. sso_client.py 수정하여 커스텀 콜백 페이지 만들기

`sso_client.py`의 `/callback` 엔드포인트를 수정하여 나만의 콜백 페이지를 만드세요.

**요구사항:**
- [ ] 사용자 정보를 카드 형태로 표시
- [ ] 부서별 배경 색상 다르게 적용
- [ ] 토큰 만료 시간을 사람이 읽을 수 있는 형식으로 표시
- [ ] "API 테스트" 버튼 추가 (access_token으로 `/api/me` 호출)

---

## 체크리스트

- [ ] Mock SSO 서버가 정상 실행됨
- [ ] SSO 클라이언트가 정상 실행됨
- [ ] 브라우저에서 SSO 로그인 흐름이 정상 동작함
- [ ] JWT 토큰에서 인물 정보를 추출할 수 있음
- [ ] 각 필드의 의미를 설명할 수 있음
- [ ] 커스텀 콜백 페이지가 정상 동작함

---

## 힌트

### JWT 토큰의 구조
```
xxxxx.yyyyy.zzzzz
  │       │       │
  │       │       └─ 서명 (Signature)
  │       └─ 페이로드 (Payload) = 사용자 정보
  └─ 헤더 (Header) = 알고리즘, 타입
```

### Python에서 Unix timestamp 변환
```python
from datetime import datetime
exp = payload["exp"]
exp_time = datetime.fromtimestamp(exp)
print(f"만료 시간: {exp_time.strftime('%Y-%m-%d %H:%M:%S')}")
```

### SSO 흐름 요약
```
사용자 브라우저 → 우리 서비스(/login)
    → SSO 서버(/mock-sso/login) 리다이렉트
    → 사용자 인증 (ID/PW 또는 선택)
    → 우리 서비스(/callback)로 id_token POST (form_post)
    → id_token 검증 → 자체 access_token 발급
    → 사용자에게 응답
```

---

## 참고 파일

| 파일 | 내용 |
|-----|------|
| `sso_mock_server.py` | Mock SSO 서버 (JWT 토큰 생성, 로그인 페이지) |
| `sso_client.py` | SSO 클라이언트 (콜백 처리, 자체 토큰 발급) |
| `sso_flow_explained.py` | SSO 흐름 상세 설명 |
| `sso_api_usage.py` | 토큰을 사용한 API 호출 예시 |
