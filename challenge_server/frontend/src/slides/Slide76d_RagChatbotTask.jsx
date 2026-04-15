import { motion } from 'framer-motion';
import { Badge, SlideH2, Divider, Box, BoxTitle } from './SlideLayout';
import LabDownloadButton from './LabDownloadButton';

export default function Slide76d_RagChatbotTask({ slideRuntime }) {
  return (
    <div className="slide-container" style={{ padding: '20px 40px' }}>
      <div className="slide-inner">
        <Badge variant="day2">종합 응용 실습</Badge>
        <SlideH2>과제: RAG 챗봇 만들기 (Index Explore 방식)</SlideH2>
        <Divider />

        <div style={{ fontSize: '.82em', color: '#64748b', marginBottom: 8, lineHeight: 1.6 }}>
          지금까지 배운 <strong>모든 것</strong>을 총동원하는 종합 실습입니다.
          사내 위키를 검색하는 RAG 챗봇을 직접 설계·구현하세요.
          <strong style={{ color: '#dc2626' }}> 채점 없음 — 스스로 만들고, 스스로 검증합니다.</strong>
        </div>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
          <Box color="blue" style={{ fontSize: '.82em', padding: '12px 18px' }}>
            <BoxTitle>📦 문서 & 가이드 다운로드</BoxTitle>
            <LabDownloadButton
              href="/downloads/rag_chatbot"
              label="📥 rag_chatbot.zip (문서 25개 + README + 예시 질문)"
              slideRuntime={slideRuntime}
              style={{ marginTop: 4, fontSize: '.95em' }}
            />
            <div style={{ marginTop: 6, color: '#475569' }}>
              압축 풀면 <code>challenge/docs/</code> 폴더에 25개 markdown 문서,
              <code>README.md</code>에 상세 가이드, <code>questions.md</code>에 예시 질문 10개가 있습니다.
            </div>
          </Box>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.32 }}>
          <Box color="yellow" style={{ marginTop: 8, fontSize: '.82em', padding: '12px 18px' }}>
            <BoxTitle color="#d97706">🎯 과제 목표</BoxTitle>
            <div style={{ lineHeight: 1.7 }}>
              가상 회사 <strong>뉴럴웍스</strong>의 사내 위키(25개 문서)를 바탕으로 질문에 답하는 챗봇을 만드세요.
              문서에는 최신/outdated, 관련/무관, 파편화된 정보가 섞여 있습니다.
              챗봇이 <strong>어떤 문서를 읽을지 스스로 판단</strong>해야 정답에 도달합니다.
            </div>
          </Box>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.44 }}>
          <Box color="red" style={{ marginTop: 8, fontSize: '.82em', padding: '12px 18px' }}>
            <BoxTitle color="#dc2626">⚠️ 제약 — Index Explore 패턴 필수</BoxTitle>
            <div style={{ lineHeight: 1.7 }}>
              ❌ 모든 문서를 한꺼번에 프롬프트에 넣기 금지 (context overflow)<br />
              ❌ 벡터 DB (FAISS, Qdrant 등) 사용 금지<br />
              ✅ LLM에게 <strong>문서 목록(파일명 + 한 줄 요약)</strong>만 먼저 주고<br />
              ✅ LLM이 Tool Call로 <strong>읽을 문서를 스스로 선택</strong>하게 하고<br />
              ✅ 선택된 문서만 읽어서 다시 LLM에 피드백 → Agentic Loop 반복
            </div>
          </Box>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.56 }}>
          <Box color="purple" style={{ marginTop: 8, fontSize: '.8em', padding: '12px 18px' }}>
            <BoxTitle color="#7c3aed">🛠️ 구현 단계 (상세는 README.md 참조)</BoxTitle>
            <div style={{ lineHeight: 1.7 }}>
              <strong>1.</strong> <code>docs/</code> 스캔 → 파일명 + 한 줄 요약으로 <strong>인덱스</strong> 만들기<br />
              <strong>2.</strong> Tool 2개 정의: <code>list_documents()</code>, <code>read_document(filename)</code><br />
              <strong>3.</strong> System Prompt에 <strong>"최신 정보 우선 / 추측 금지 / 출처 제시"</strong> 규칙 명시<br />
              <strong>4.</strong> while loop로 Agentic Loop 구현 (LLM → tool 실행 → 결과 피드백)<br />
              <strong>5.</strong> <code>questions.md</code>의 10개 질문으로 테스트 → 틀리면 프롬프트 개선 반복
            </div>
          </Box>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.68 }}>
          <Box color="green" style={{ marginTop: 8, fontSize: '.8em', padding: '12px 18px' }}>
            <BoxTitle color="#059669">🧠 이 과제에서 써먹을 기존 학습</BoxTitle>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '4px 14px', lineHeight: 1.6 }}>
              <div>• <strong>#4 Endpoint</strong> — LLM Gateway 호출</div>
              <div>• <strong>#5 Tool Use</strong> — function calling 정의</div>
              <div>• <strong>#11 Agentic Loop</strong> — while 루프 반복 실행</div>
              <div>• <strong>#13 Index Explore</strong> — 목록→선택→읽기 패턴</div>
              <div>• <strong>Context Engineering</strong> — 필요한 정보만 주입</div>
              <div>• <strong>Prompt 방어/강화</strong> — 최신 우선, 추측 금지</div>
            </div>
          </Box>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.8 }}>
          <Box color="blue" style={{ marginTop: 8, fontSize: '.8em', padding: '12px 18px' }}>
            <BoxTitle>🏆 자가 완성 기준</BoxTitle>
            <div style={{ lineHeight: 1.7 }}>
              ✓ <code>questions.md</code> 10개 중 <strong>7개 이상</strong> 정답에 근접하게 답하는가?<br />
              ✓ 챗봇이 25개 전체가 아닌 <strong>5~10개 문서만 선택적으로</strong> 읽는가?<br />
              ✓ outdated 문서(v1, 2024년 버전)를 피하고 <strong>최신 문서를 우선</strong>하는가?<br />
              ✓ 노이즈 문서에 낚이지 않는가? (예: 트랜스포머 이론 블로그)<br />
              ✓ 답변에 <strong>출처 문서명</strong>이 포함되는가?
            </div>
          </Box>
        </motion.div>

        <div style={{
          marginTop: 10, padding: '10px 16px', borderRadius: 8,
          background: '#fffbeb', border: '1px solid #fde68a',
          fontSize: '.8em', color: '#92400e', lineHeight: 1.6,
        }}>
          💡 <strong>Q8번(육아휴직)이 가장 어렵습니다.</strong> 2024년 규정과 2025년 개정안이 별도 파일로 있고,
          챗봇이 "최신 문서 우선" 규칙을 제대로 지키지 않으면 12개월이라고 틀리게 답합니다.
          이 질문이 통과하면 프롬프트 설계가 성공한 것입니다.
        </div>
      </div>
    </div>
  );
}
