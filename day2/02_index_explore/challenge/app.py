"""
Index Explore 실습 — .md 계층 인덱스 만들기

실행: pip install streamlit requests
     streamlit run app.py --server.port 3000
접속: http://localhost:3000

과제: 정리되지 않은 10개의 raw 문서를 계층적 .md 파일로 정리하세요.
      AI 에이전트가 당신의 인덱스만 보고 3개 질문에 답변합니다.
      잘 정리하면 AI가 정답을 찾고, 못 정리하면 AI가 헤맵니다!
"""

import json
import requests
import streamlit as st

st.set_page_config(page_title="Index Explore 실습", page_icon="📂", layout="wide")

# ============================================
# 서버 정보
# ============================================
CHALLENGE_SERVER = "http://a2g.samsungds.net:47777"
LLM_GATEWAY = "http://a2g.samsungds.net:8090/v1"
SERVICE_ID = "test-service"
USER_ID = "student"

# ============================================
# Raw 문서 10개 (정리 안 된 원본)
# ============================================
RAW_DOCS = {
    "raw_01_제품스펙.txt": """HBM3E 메모리 사양서 (비공식 메모)
적층: 12단 TSV, 용량 36GB, 대역폭 1.18TB/s
전력소비: 8.4W (경쟁사 대비 15% 절감)
양산 시작: 2025년 3월, 첫 고객 납품: 2025년 5월
주요 고객: N사 AI 가속기, M사 GPU
가격: 개당 $120 (예상 ASP)

DDR5-6400 DRAM
용량: 16GB/32GB, 속도: 6400MT/s
적용: 서버, PC, 워크스테이션
양산: 2024년 Q4부터 대량 출하 중

LPDDR5X (모바일용)
용량: 12GB/16GB, 속도: 8533MT/s
특징: 온디바이스 AI 최적화, 전력 20% 절감
주요 고객: S전자 갤럭시, A사 아이폰""",

    "raw_02_회의록.txt": """[2분기 실적 검토 회의]
일시: 2025-06-15 14:00
장소: 본관 19층 대회의실
참석: 박영수 상무, 김태호 팀장, 이수진 과장, 정민호 대리, 한지원 사원
안건: Q2 매출 리뷰, 하반기 투자 계획
주요 내용:
- Q2 매출 14.2조원 (전분기 대비 +8%)
- HBM 매출 비중 35%로 확대
- 하반기 EUV 라인 1개 추가 증설 결정
- 투자액: 3.5조원 (설비 2.8조 + 인프라 0.7조)
결정사항: HBM 라인 증설 승인, Q3 착공 목표

[AI 반도체 전략 워크숍]
일시: 2025-07-03 09:00
장소: R&D센터 세미나실
참석: 최현우 부사장, 박영수 상무, 기술기획팀 전원
안건: AI 반도체 로드맵 2026-2028
주요 내용:
- CXL 메모리 개발 가속화
- PIM(Processing-in-Memory) 1세대 2027년 출시 목표
- AI 가속기 자체 개발 여부 검토 (결론: 메모리 중심 전략 유지)""",

    "raw_03_공정현황.txt": """[EUV 공정 현황 리포트 - 2025년 6월]
현재 수율: 92.3%
목표 수율: 95% (Q4 달성 목표)
주요 불량 유형:
1. 오버레이 오차: 38% (마스크 정밀도 이슈)
2. 파티클 오염: 27% (클린룸 관리)
3. 에칭 깊이 편차: 19%
4. 기타: 16%
개선 활동:
- 마스크 교체 주기: 30일 → 21일로 단축
- 클린룸 등급: Class 10 → Class 1 업그레이드 진행 중
- AI 기반 불량 예측 시스템 시범 운영 (정확도 87%)

[DRAM 1b 공정]
수율: 88.7%
목표: 92% (연말)
웨이퍼 처리량: 월 45,000장
가동률: 94.2%""",

    "raw_04_조직도.txt": """반도체 사업부 조직도 (2025년 기준)

사업부장: 이재용 부회장 (겸임)
├── 메모리사업부: 최현우 부사장
│   ├── DRAM설계팀: 박영수 상무
│   │   ├── 1팀: 김태호 팀장 (DDR5 담당)
│   │   ├── 2팀: 오정훈 팀장 (HBM 담당)
│   │   └── 3팀: 최민석 팀장 (LPDDR 담당)
│   ├── NAND설계팀: 이동현 상무
│   └── 신제품기획팀: 정수빈 상무
├── 파운드리사업부: 한승완 부사장
│   ├── 공정개발팀: 류지혜 상무
│   └── 고객기술팀: 김현수 상무
└── 기술기획실: 장원영 전무
    ├── 선행기술팀: 손예진 상무
    └── IP/특허팀: 김지수 팀장""",

    "raw_05_예산.txt": """2025년 반도체 사업부 예산 현황

[설비 투자]
- EUV 장비: 8,500억원 (ASML NXE:3800 2대)
- 클린룸 증설: 3,200억원
- 검사장비: 1,800억원
- 패키징 장비: 2,100억원
합계: 1조 5,600억원

[R&D 예산]
- HBM 차세대: 2,800억원
- CXL 메모리: 1,500억원
- PIM 연구: 800억원
- AI 공정최적화: 600억원
합계: 5,700억원

[인건비]
- 정규직 12,500명: 1조 8,750억원
- 계약직/파견: 3,200명: 2,880억원

총 예산: 4조 2,930억원""",

    "raw_06_일정.txt": """2025년 하반기 주요 일정

7월:
- 7/1~7/5: 상반기 성과 발표회
- 7/10: CXL 1.0 샘플 테이프아웃
- 7/15: DRAM 1c 공정 개발 킥오프

8월:
- 8/5~8/9: 여름 휴가 (공장 정기 보수)
- 8/20: HBM4 설계 리뷰
- 8/25: 반도체학회 논문 제출 마감

9월:
- 9/1: 하반기 조직개편 시행
- 9/15: Q3 중간 실적 리뷰
- 9/22~9/24: 글로벌 고객사 기술 세미나 (미국)

10월:
- 10/8: 창립기념일
- 10/15: EUV 신규 라인 가동 시작
- 10/30: Q3 실적 발표

11월:
- 11/5: 2026년 사업 계획 확정
- 11/20: HBM3E 2세대 양산 시작

12월:
- 12/10: 연말 성과 평가
- 12/20: 송년 행사""",

    "raw_07_특허.txt": """주요 특허 현황

[등록 완료]
1. US-2025-001234: "고효율 TSV 적층 방법" (HBM 관련)
   발명자: 오정훈, 김민재 / 등록: 2025-02
2. US-2025-002345: "온칩 AI 추론 가속 아키텍처" (PIM 관련)
   발명자: 손예진, 박동현 / 등록: 2025-04
3. KR-2025-003456: "EUV 마스크 결함 검출 알고리즘"
   발명자: 류지혜, 정승환 / 등록: 2025-03

[출원 중]
4. PCT-2025-004567: "CXL 기반 메모리 풀링 프로토콜"
   발명자: 정수빈, 한지원 / 출원: 2025-05
5. US-2025-005678: "3D NAND 256단 적층 기술"
   발명자: 이동현, 최은비 / 출원: 2025-06

특허 포트폴리오: 총 2,847건 (국내 1,203건, 해외 1,644건)""",

    "raw_08_경쟁사.txt": """경쟁사 동향 분석 (2025 Q2)

[SK하이닉스]
- HBM3E 12단 양산 중 (당사와 동일 스펙)
- 점유율: HBM 시장 약 50% (당사 40%, 마이크론 10%)
- 강점: N사와의 밀접한 파트너십
- 약점: DRAM 범용 제품 수익성 낮음

[마이크론]
- HBM3E 8단 양산 (12단은 2025 Q4 예정)
- 미국 정부 보조금 확보 ($6.1B)
- NAND 시장에서 공격적 가격 전략

[TSMC (파운드리)]
- 2nm 공정 2025년 하반기 양산
- CoWoS 패키징 캐파 2배 증설
- 당사 파운드리 대비 기술 격차: 약 1~1.5세대

시장 전망:
- 2025년 메모리 반도체 시장: $180B (전년 대비 +25%)
- AI 관련 메모리 비중: 40% → 55% (2026년 예상)""",

    "raw_09_품질이슈.txt": """[품질 이슈 트래커 - 2025년 6월]

ISSUE-2025-042: HBM3E 열 관리 문제
- 심각도: High
- 상태: 대응 중
- 내용: 12단 적층 시 상위 다이 온도가 105°C 초과
- 원인: 마이크로범프 열전도 계수 부족
- 대응: 열계면재(TIM) 변경 테스트 중
- 담당: 오정훈 팀장

ISSUE-2025-051: DDR5 신호 무결성 이슈
- 심각도: Medium
- 상태: 해결 완료
- 내용: 6400MT/s에서 간헐적 비트 에러
- 원인: PCB 임피던스 매칭 오차
- 해결: 패키지 기판 재설계 (Rev B)
- 담당: 김태호 팀장

ISSUE-2025-063: EUV 포토레지스트 불량
- 심각도: Medium
- 상태: 모니터링
- 내용: 특정 로트에서 패턴 붕괴 현상
- 원인: 레지스트 공급사 배치 편차
- 대응: 입고 검사 기준 강화
- 담당: 류지혜 상무""",

    "raw_10_교육.txt": """[사내 교육 프로그램 2025]

AI/ML 교육:
- "LLM Agent 개발 실습" (2일, 한승하 강사) — 7월 예정
- "MLOps 파이프라인 구축" (3일, 외부 강사)
- "AI 반도체를 위한 딥러닝 기초" (5일, 온라인)

반도체 공정 교육:
- "EUV 리소그래피 원리와 실습" (2일, 류지혜 상무)
- "패키징 기술 트렌드" (1일, 기술기획실)
- "수율 분석 방법론" (3일, 품질팀)

리더십/소프트스킬:
- "시니어 엔지니어 리더십" (2일, 임원 대상)
- "기술 보고서 작성법" (1일, 전 직원)
- "글로벌 커뮤니케이션" (4주, 온라인)

인증/자격:
- 반도체설계기사 대비반 (3개월 과정)
- ISTQB 테스팅 자격증 (2개월 과정)

교육 예산: 인당 연 150만원, 총 187.5억원""",
}

# ============================================
# 3개 테스트 질문
# ============================================
QUESTIONS = [
    {
        "id": 1,
        "question": "HBM3E의 적층 단수와 대역폭은?",
        "keywords": ["12단", "1.18"],
        "hint": "제품 스펙 관련 문서를 찾아보세요",
    },
    {
        "id": 2,
        "question": "2분기 실적 회의에서 결정된 투자액은 얼마인가?",
        "keywords": ["3.5"],
        "hint": "회의록 관련 문서를 찾아보세요",
    },
    {
        "id": 3,
        "question": "EUV 공정의 주요 불량 원인 1위와 그 비율은?",
        "keywords": ["오버레이", "38"],
        "hint": "공정 관련 문서를 찾아보세요",
    },
]

# ============================================
# 세션 초기화
# ============================================
if "files" not in st.session_state:
    st.session_state.files = {
        "MEMORY.md": "# 문서 인덱스\n\n여기에 계층적 인덱스를 작성하세요.\n\n- [파일명.md](파일명.md) — 설명\n",
    }
if "test_results" not in st.session_state:
    st.session_state.test_results = None
if "current_file" not in st.session_state:
    st.session_state.current_file = "MEMORY.md"

# ============================================
# AI 계층적 검색 함수
# ============================================
def ai_hierarchical_search(question, files):
    """AI가 MEMORY.md + 하위 파일을 읽고 질문에 답변합니다."""
    memory_md = files.get("MEMORY.md", "")
    if not memory_md.strip():
        return "MEMORY.md가 비어있습니다.", []

    sub_files = [f for f in files.keys() if f != "MEMORY.md"]

    # 검증: 하위 파일이 2개 이상 있어야 함
    if len(sub_files) < 2:
        return f"하위 .md 파일이 {len(sub_files)}개뿐입니다. 최소 2개 이상의 하위 파일로 정리하세요.", []

    # 검증: MEMORY.md가 500자 이내여야 함 (인덱스니까)
    if len(memory_md) > 500:
        return f"MEMORY.md가 {len(memory_md)}자입니다. 인덱스는 500자 이내로 작성하세요. (raw 데이터를 넣지 마세요!)", []

    trace = []
    trace.append({"step": "MEMORY.md 읽기", "content": memory_md[:200]})

    # 전체 문서 context 구성 (MEMORY.md 기반 계층 구조)
    ctx = f"## MEMORY.md (인덱스)\n{memory_md}\n"
    for fname in sub_files:
        content = files[fname]
        if content.strip():
            ctx += f"\n## {fname}\n{content}\n"
            trace.append({"step": f"{fname} 로드", "content": content[:100]})

    prompt = f"""{ctx}

위 문서를 참고하여 질문에 답하세요.
문서에 있는 수치와 용어를 그대로 사용하여 간결하게 답하세요.

질문: {question}"""

    try:
        resp = requests.post(
            f"{LLM_GATEWAY}/chat/completions",
            headers={"Content-Type": "application/json", "x-service-id": SERVICE_ID, "x-user-id": USER_ID},
            json={"model": "testmodel", "messages": [{"role": "user", "content": prompt}], "max_tokens": 200},
            timeout=120,
        )
        if resp.status_code != 200:
            return f"LLM 오류: {resp.status_code}", trace

        answer = resp.json()["choices"][0]["message"]["content"].strip()
        trace.append({"step": "AI 답변", "content": answer})
        return answer, trace
    except Exception as e:
        return f"LLM 연결 실패: {e}", trace


def _norm(s):
    """공백/대소문자/유니코드/특수문자 모두 무시하는 정규화"""
    import re, unicodedata
    # 유니코드 정규화 (NFC vs NFD, fullwidth 숫자/슬래시 등을 halfwidth로)
    s = unicodedata.normalize('NFKC', s)
    # 모든 whitespace + zero-width space 제거
    s = re.sub(r'[\s\u200b\u200c\u200d\ufeff]+', '', s)
    return s.lower()


def check_answer(answer, keywords):
    """답변에 필수 키워드가 포함되어 있는지 확인"""
    normalized = _norm(answer)
    # 디버그: 못 찾은 키워드가 있으면 터미널에 출력
    missing = [kw for kw in keywords if _norm(kw) not in normalized]
    if missing:
        print(f"[check_answer] FAIL — missing: {missing}")
        print(f"[check_answer] normalized answer: {repr(normalized)}")
    return not missing


# ============================================
# UI
# ============================================
st.title("📂 Index Explore — .md 계층 인덱스 만들기")
st.markdown("---")

left, right = st.columns([1, 1])

# ── 왼쪽: Raw 문서 ──
with left:
    st.markdown("### 📄 Raw 문서 (정리 안 됨)")
    raw_tab = st.selectbox("문서 선택", list(RAW_DOCS.keys()), key="raw_select")
    st.code(RAW_DOCS[raw_tab], language="text")

# ── 오른쪽: 인덱스 에디터 ──
with right:
    st.markdown("### ✏️ 인덱스 에디터")

    # 파일 탭
    col1, col2, col3 = st.columns([3, 2, 1])
    with col1:
        st.session_state.current_file = st.selectbox(
            "파일", list(st.session_state.files.keys()), key="file_select"
        )
    with col2:
        new_name = st.text_input("새 파일", placeholder="products.md", key="new_file")
    with col3:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("➕ 추가") and new_name:
            if not new_name.endswith(".md"):
                new_name += ".md"
            if new_name not in st.session_state.files:
                st.session_state.files[new_name] = f"# {new_name.replace('.md', '')}\n\n"
                st.session_state.current_file = new_name
                st.rerun()

    # 에디터
    current = st.session_state.current_file
    content = st.text_area(
        f"편집: {current}",
        value=st.session_state.files.get(current, ""),
        height=300,
        key=f"editor_{current}",
    )
    st.session_state.files[current] = content

    # 파일 목록
    st.caption(f"📁 파일 {len(st.session_state.files)}개: {', '.join(st.session_state.files.keys())}")

# ── 하단: AI 테스트 ──
st.markdown("---")
st.markdown("### 🧪 AI 테스트 — 인덱스로 질문에 답할 수 있는지 확인")

if st.button("🚀 AI 테스트 실행", type="primary"):
    results = []
    for q in QUESTIONS:
        with st.spinner(f"Q{q['id']}: {q['question']}"):
            answer, trace = ai_hierarchical_search(q["question"], st.session_state.files)
            passed = check_answer(answer, q["keywords"])
            results.append({"question": q, "answer": answer, "trace": trace, "passed": passed})
    st.session_state.test_results = results

if st.session_state.test_results:
    results = st.session_state.test_results
    passed_count = sum(1 for r in results if r["passed"])

    # 결과 표시
    for r in results:
        q = r["question"]
        icon = "✅" if r["passed"] else "❌"
        with st.expander(f"{icon} Q{q['id']}: {q['question']}", expanded=not r["passed"]):
            st.markdown(f"**AI 답변:** {r['answer']}")
            st.markdown(f"**필수 키워드:** {', '.join(q['keywords'])}")
            if r["trace"]:
                st.markdown("**탐색 경로:**")
                for t in r["trace"]:
                    st.caption(f"→ {t['step']}")
            if not r["passed"]:
                st.info(f"💡 힌트: {q['hint']}")

    # 전체 통과 시 자동 제출
    if passed_count == len(QUESTIONS):
        st.balloons()
        st.success(f"🎉 {passed_count}/{len(QUESTIONS)} 전체 통과! 인덱스가 잘 정리되어 있습니다!")

        # 과제 서버에 제출
        try:
            answers = {f"q{r['question']['id']}": r["answer"] for r in results}
            resp = requests.post(
                f"{CHALLENGE_SERVER}/challenges/index_explore/submit",
                json={"answer": answers},
                headers={"Content-Type": "application/json"},
                timeout=10,
            )
        except Exception:
            pass
    else:
        st.warning(f"📝 {passed_count}/{len(QUESTIONS)} 통과 — 인덱스를 개선해보세요!")
