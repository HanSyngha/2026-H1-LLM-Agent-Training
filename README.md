# LLM Agent 2-Day Training Workshop

> 2-Day Intensive · 실습 중심 · 원리 이해
> 엔지니어를 위한 LLM Agent 개발 강의의 슬라이드 + 실습 코드 + 채점 서버 풀세트

이 레포는 **2일짜리 기업용 LLM Agent 교육 과정**의 전체 콘텐츠입니다.
슬라이드(React SPA), 과제 스켈레톤 코드, OIDC 로그인 + 자동 채점 서버를 포함하며
누구나 받아서 자기 조직에 맞게 변형해 사용할 수 있게 공개합니다.

---

## 🗺️ 구성 요소

```
.
├── day1/                    # Day 1 실습 코드 (SSO, Prompt, Endpoint, Tool Use, MCP, Browser)
├── day2/                    # Day 2 실습 코드 (Agentic Loop, Bash Tool, Index Explore, RAG 등)
├── challenge_server/        # FastAPI + React 슬라이드/채점 서버
│   ├── server.py            # 메인 서버 (OIDC 인증 + 채점 + 대시보드)
│   ├── challenges.py        # 과제 정의 + 검증 로직
│   ├── frontend/            # React 슬라이드 SPA
│   ├── docker-compose.yml
│   └── Dockerfile
├── extras/                  # 참고 자료, 추가 문서
└── setup/                   # 환경 셋업 문서
```

---

## 🧑‍🏫 커리큘럼 요약

### Day 1 — 원리 이해
| # | 주제 | 실습 |
|---|-----|------|
| 0 | SSO / OIDC | 바이브 코딩으로 OIDC 로그인 붙이기 |
| 1 | AI 학습 기초 | 문제 정의가 솔루션을 결정한다 |
| 2 | 프롬프팅 | 시스템/유저/어시스턴트 메시지 분류/요약/추출 |
| 3 | API & Gateway | OpenAI 호환 API 직접 호출 |
| 4 | Tool Use / Function Calling | 다중 tool 체인 |
| 5 | MCP (참고) | FastMCP 개요 |
| 6 | 브라우저 자동화 | Playwright/CDP로 JS 렌더링 페이지 크롤링 |

### Day 2 — 종합 응용
| # | 주제 | 실습 |
|---|-----|------|
| 9 | Context Engineering | 압축 프롬프트, Few-shot, Prompt Defense |
| 10 | 프레임워크 둘러보기 | ADK, LangGraph 개념만 |
| 11 | Agentic Loop | 미로(maze) 과제로 while-loop 에이전트 만들기 |
| 12 | Bash Tool | subprocess로 파일 해독하는 CLI 에이전트 |
| 13 | Vector DB vs Index Explore | 벡터 검색 없이 계층 인덱스로 답 찾기 |
| 14 | Harness | CLAUDE.md, 보안, 구성 파일 베스트 프랙티스 |
| 15 | React 대시보드 | 제공 API 5개를 시각화, VL 모델이 자동 채점 |
| 16 | RAG 챗봇 | Index Explore로 난잡한 25개 문서에서 답 찾기 |

---

## 🚀 Quick Start

### Docker (권장)

```bash
git clone https://github.com/HanSyngha/2026-H1-LLM-Agent-Training.git
cd 2026-H1-LLM-Agent-Training/challenge_server

cp .env.example .env
# .env 편집: 본인 OIDC provider, LLM Gateway, 강사 계정 sub 등

./deploy.sh          # Docker 빌드 + 시작
./deploy.sh logs     # 로그 확인
./deploy.sh restart  # 코드 변경 후 재배포
./deploy.sh stop     # 중지
```

브라우저에서 `http://localhost:47777` 접속.

### 직접 실행 (Docker 없이)

```bash
cd challenge_server

# 프론트엔드 빌드
cd frontend && npm install && npm run build && cd ..

# 백엔드 실행
pip install -r requirements.txt
python server.py
```

### 로컬 개발 (SSO 우회)

```bash
cd challenge_server
DEV_MODE=true python server.py
```
DEV_MODE에서는 모든 요청이 `admin` 유저로 취급되어 OIDC 없이 바로 테스트 가능.

---

## ⚙️ 설정 (.env)

핵심 환경변수:

| 변수 | 설명 | 기본값 |
|-----|-----|-------|
| `AUTH_SERVER` | OIDC provider (서버→서버 호출) | `https://auth.example.com` |
| `AUTH_PUBLIC` | OIDC provider (브라우저 리다이렉트용) | `$AUTH_SERVER` |
| `CHALLENGE_HOST` | Challenge 서버 공개 주소 (callback URL 생성) | `http://localhost:47777` |
| `CHALLENGE_PORT` | 리스닝 포트 | `47777` |
| `LLM_GATEWAY_URL` | 채점용 LLM (OpenAI 호환) | `https://llm-gateway.example.com/v1` |
| `LLM_GATEWAY_API_KEY` | 위 LLM의 API 키 | *(비움)* |
| `LLM_MODEL` | 모델 이름 | `gpt-4o-mini` |
| `PRESENTER_SUB` | 강사 계정 OIDC sub | `admin` |
| `DEV_MODE` | SSO 우회 (개발용) | `false` |

전체 목록은 [`challenge_server/.env.example`](challenge_server/.env.example) 참고.

### 사내망 배포 (프록시 + 사내 미러)

Docker 빌드 시 인자로 주입:
```bash
docker compose build \
  --build-arg NPM_REGISTRY=https://<your-npm-mirror>/ \
  --build-arg PIP_INDEX_URL=https://<your-pypi-mirror>/simple
```
`.env`에 `HTTP_PROXY`, `HTTPS_PROXY`, `NO_PROXY`도 함께 설정.

---

## 🏫 커스터마이징

### 본인 조직의 OIDC provider 연결
`.env`에서 `AUTH_SERVER`, `AUTH_PUBLIC` 수정. OIDC endpoint는 다음을 따라야 합니다:
- `GET /oidc/authorize` — 인증 시작
- `POST /oidc/token` — 토큰 교환
- `GET /oidc/userinfo` — 유저 정보 (`sub`, `name`, `dept`, `email`)

### 채점 LLM 교체
OpenAI 호환 API면 모두 동작:
- OpenAI: `https://api.openai.com/v1`
- Anthropic (API 변환기 사용): `https://api.anthropic.com/v1`
- 로컬 Ollama: `http://localhost:11434/v1`
- 사내 Gateway: 조직 내부 URL

### 강사 권한 부여
`.env`에서 `PRESENTER_SUB`에 OIDC sub 값 입력. 이 유저만 다음 기능 접근 가능:
- 슬라이드 넘기기 (수강생은 자동 추종)
- 수강생 자유 탐색 잠금/해제
- 대시보드 리셋
- 답안 공개/잠금 토글

### 과제 추가/수정
- `challenge_server/challenges.py`에 validate 함수 등록
- `challenge_server/frontend/src/slides/`에 슬라이드 컴포넌트 추가
- `day1/` 또는 `day2/`에 스켈레톤 코드 저장 (`/downloads/<id>`로 zip 배포됨)

---

## 🧪 강의 진행 플로우

1. 강사가 Challenge 서버를 사내망에 띄움
2. 수강생들이 브라우저로 접속 → OIDC 로그인
3. 강사가 슬라이드 넘기면 수강생 화면도 자동 동기화
4. 과제 슬라이드에서 ZIP 다운로드 → 로컬에서 바이브 코딩
5. 완성된 결과 제출 → 실시간으로 대시보드에 표시 (이름, 부서, 통과 시간)
6. 강사가 필요 시 "자유 탐색 잠금 해제" → 수강생 개별 진도 허용

---

## 📦 주요 기능

- **OIDC 기반 자동 로그인**: 모든 수강생 신원 자동 확인
- **실시간 슬라이드 동기화**: 강사 화면을 수강생이 자동 추종 (잠금/해제 가능)
- **자동 채점**: 과제 제출 시 LLM + 규칙 기반 검증
- **리더보드**: 통과한 과제 수 · 속도 기준 실시간 순위
- **질문 / 반응 / 피드백**: 슬라이드별 상호작용 기능
- **오프라인 아카이브**: 강의 종료 후 정적 HTML로 열람 가능
- **Persistent State**: 서버 재시작해도 기록 보존 (`data/state.json`)

---

## 🛡️ 보안 주의사항

- **`.env` 파일은 절대 commit 금지** (이미 `.gitignore`에 등록됨)
- 배포 시 `DEV_MODE=false` 확인
- `PRESENTER_SUB`을 본인만 아는 값으로 바꿔주세요 (기본 `admin`은 쉽게 추측됨)
- OIDC provider의 client_secret은 필요하면 별도 관리

---

## 📝 License

MIT License. 자유롭게 fork / 수정 / 재배포 가능합니다.
본인 조직에 맞게 커스터마이징해서 사용하셔도 좋습니다.

---

## 🙋 도움 & 기여

- 이슈 / PR 환영합니다
- 새 과제 기여, 번역, 커리큘럼 개선 제안 특히 환영
- 오리지널 저자가 아닌 여러분의 조직에 맞는 fork가 더 가치 있다고 생각합니다

Happy Agent Building! 🤖
