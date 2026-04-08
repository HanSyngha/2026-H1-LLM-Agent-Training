import { motion } from 'framer-motion';
import { Badge, SlideH2, Divider, Box, BoxTitle } from './SlideLayout';

export default function Slide73_IndexExploreTask() {
  return (
    <div className="slide-container">
      <div className="slide-inner">
        <Badge variant="day2">Index Explore 실습</Badge>
        <SlideH2>과제: .md 계층 인덱스 만들기</SlideH2>
        <Divider />

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
          <Box color="blue">
            <BoxTitle>1단계: 코드 다운로드 & 실행</BoxTitle>
            <a href="/downloads/index_explore" download
              style={{ display: 'inline-block', padding: '8px 20px', borderRadius: 8, background: '#2563eb', color: '#fff',
                textDecoration: 'none', fontWeight: 600, fontSize: '.9em', marginBottom: 8 }}>
              📦 실습 코드 다운로드
            </a>
            <code style={{ display: 'block', fontSize: '1em', lineHeight: 1.8 }}>
              pip install streamlit requests<br />
              streamlit run app.py --server.port 3000
            </code>
          </Box>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.35 }}>
          <Box color="purple" style={{ marginTop: 8 }}>
            <BoxTitle color="#7c3aed">핵심 개념</BoxTitle>
            <div style={{ fontSize: '.9em', lineHeight: 1.8 }}>
              정리 안 된 <strong>raw 문서 10개</strong>가 주어집니다.<br />
              이것을 <strong>MEMORY.md</strong> (최상위 인덱스) + 하위 .md 파일로 계층화하세요.<br />
              <code>MEMORY.md → products.md, meetings.md, ...</code>
            </div>
          </Box>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.5 }}>
          <Box color="yellow" style={{ marginTop: 8 }}>
            <BoxTitle color="#d97706">AI 테스트</BoxTitle>
            <div style={{ fontSize: '.88em', lineHeight: 1.8 }}>
              AI 에이전트가 <strong>MEMORY.md만 먼저 읽고</strong> → 관련 파일을 찾아 → 질문에 답변<br />
              인덱스가 잘 정리되어 있으면 AI가 정답을 찾고, 아니면 헤맵니다!<br />
              <strong>3개 질문 전부 통과</strong> → 자동 제출!
            </div>
          </Box>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.65 }}>
          <Box color="green" style={{ marginTop: 8, textAlign: 'center', fontSize: '1em' }}>
            <strong>배우는 것:</strong> AI에게 일 잘 시키려면 → <strong style={{ color: '#059669' }}>문서를 잘 정리해야 한다</strong>
          </Box>
        </motion.div>
      </div>
    </div>
  );
}
