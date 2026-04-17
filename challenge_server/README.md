# Challenge 서버 배포 가이드

## 개요

강사가 `challenge.example.com:47777`에 띄워두면, 수강생이 SSO 토큰 + 정답을 제출하여 과제를 통과합니다.

| 구성요소 | 주소 | 역할 |
|---------|------|------|
| 인증 서버 | `auth.example.com` | SSO/OIDC 토큰 발급, 사용자 정보 |
| Challenge 서버 | `challenge.example.com:47777` | 과제 미션 제공, 정답 검증, 성공자 대시보드 |

## 1. Docker 배포 (권장)

```bash
git clone https://github.com/HanSyngha/2026-H1-LLM-Agent-Training.git
cd 2026-H1-LLM-Agent-Training/challenge_server

# 설정
cp .env.example .env
# .env 편집: LLM_GATEWAY_URL, LLM_GATEWAY_API_KEY (선택)

# 배포
./deploy.sh              # 빌드 + 시작
./deploy.sh status       # 상태 확인
./deploy.sh test         # 전체 테스트
./deploy.sh logs         # 실시간 로그
./deploy.sh restart      # 재빌드 + 재시작
./deploy.sh stop         # 중지
```

## 2. 직접 실행 (Docker 없이)

```bash
git clone https://github.com/HanSyngha/2026-H1-LLM-Agent-Training.git
cd 2026-H1-LLM-Agent-Training
```

## 2. 패키지 설치

```bash
pip install fastapi uvicorn requests PyJWT python-multipart urllib3
```

## 3. 서버 실행

```bash
cd challenge_server
python server.py
```

정상 실행 시:
```
============================================================
  LLM Agent 교육 Challenge 서버
  http://0.0.0.0:47777
  인증 서버: https://auth.example.com
  과제 수: 7개
============================================================
```

백그라운드 실행 (강의 당일):
```bash
nohup python server.py > challenge.log 2>&1 &
echo $! > challenge.pid

# 로그 확인
tail -f challenge.log

# 종료
kill $(cat challenge.pid)
```

## 4. 테스트 순서

### 4-1. 헬스체크

```bash
curl http://localhost:47777/health
```

### 4-2. 대시보드

```
브라우저에서 http://challenge.example.com:47777
```

### 4-3. LLM 채점 설정

```
브라우저에서 http://challenge.example.com:47777/settings
→ LLM Base URL, API Key, Model 입력 → 저장 및 테스트
```

미설정 시 하드코딩 검증으로 동작합니다.

### 4-4. 미션 조회

```bash
curl http://localhost:47777/challenges/endpoint/mission
```

### 4-5. 정답 제출 테스트

```bash
TOKEN="access_token_여기에"

curl -X POST http://localhost:47777/challenges/endpoint/submit \
  -H "Content-Type: application/json" \
  -d "{
    \"token\": \"$TOKEN\",
    \"answer\": {
      \"response\": \"대한민국의 수도는 서울이며, 영문명은 Seoul입니다.\"
    }
  }"
```

성공 시:
```json
{
  "status": "SUCCESS",
  "user": "Admin",
  "message": "🎉 Admin님, LLM Endpoint 연결 통과!"
}
```

### 4-6. 브라우저 wiki 페이지

```bash
# requests로 접근 → "데이터 로드 중..."만 보임 (정상)
curl http://localhost:47777/browser-target | grep "로드 중"

# 데이터 API 직접 확인
curl http://localhost:47777/api/wiki-data
```

### 4-7. 대시보드에서 성공자 확인

```
브라우저에서 http://challenge.example.com:47777
→ 제출 성공 시 이름/부서가 실시간 표시됩니다
```

## 5. 과제 목록

| ID | 과제명 | 미션 | 제출 스키마 |
|----|--------|------|-----------|
| `prompt` | 프롬프트 엔지니어링 | 감정 분류 + 요약 + 정보 추출 | `{classify, summarize, extract}` |
| `endpoint` | LLM Endpoint 연결 | Gateway 연결 + 질문 응답 | `{response}` |
| `structured` | Structured Output | 뉴스 기사 JSON 분석 | `{title, category, sentiment, keywords, summary}` |
| `mcp` | MCP Tool 호출 | 3개 도구 호출 결과 | `{results: [...]}` |
| `browser` | 브라우저 자동화 | JS 렌더링 wiki에서 데이터 추출 (CDP) | `{products: [{name, price}]}` |
| `agent_loop` | Agentic Loop | 복합 질문 Agent Loop 해결 | `{response}` |
| `final` | 종합 실습 | 검색→추출 파이프라인 | `{items: [{title, link}]}` |

## 6. 엔드포인트

| Method | Path | 설명 |
|--------|------|------|
| GET | `/` | 성공자 대시보드 |
| GET | `/challenges` | 과제 목록 |
| GET | `/challenges/{id}/mission` | 미션 데이터 |
| POST | `/challenges/{id}/submit` | 정답 제출 `{token, answer}` |
| GET | `/completions` | 성공자 현황 JSON |
| GET | `/browser-target` | 브라우저 과제 타겟 페이지 (JS 렌더링) |
| GET | `/api/wiki-data` | 브라우저 과제 데이터 API |
| GET | `/settings` | LLM 설정 페이지 |
| POST | `/settings/update` | LLM 설정 저장 |
| GET | `/health` | 헬스체크 |

## 7. 강의 당일 체크리스트

- [ ] 인증 서버(`:8090`) 정상 동작
- [ ] Challenge 서버(`:47777`) 실행
- [ ] `curl :47777/health` 응답 확인
- [ ] `/settings`에서 LLM 연결 설정 완료
- [ ] 본인 토큰으로 endpoint 과제 제출 테스트
- [ ] 대시보드에 이름 표시 확인
- [ ] `/browser-target` 브라우저에서 데이터 표시 확인
