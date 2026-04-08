import { motion } from 'framer-motion';
import { Badge, SlideH2, Divider, Box, BoxTitle } from './SlideLayout';

export default function Slide35_StructuredTask() {
  return (
    <div className="slide-container">
      <div className="slide-inner">
        <Badge variant="day1">Tool Use 실습</Badge>
        <SlideH2>바이브 코딩: Function Calling 챗봇</SlideH2>
        <Divider />

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
          <Box color="blue">
            <BoxTitle>1단계: 코드 다운로드 & 실행</BoxTitle>
            <a href="/downloads/tool_use" download
              style={{ display: 'inline-block', padding: '8px 20px', borderRadius: 8, background: '#2563eb', color: '#fff',
                textDecoration: 'none', fontWeight: 600, fontSize: '.9em', marginBottom: 8 }}>
              📦 실습 코드 다운로드 (tool_use_code.zip)
            </a>
            <code style={{ display: 'block', fontSize: '1em', lineHeight: 1.8 }}>
              pip install streamlit requests PyJWT<br />
              streamlit run app.py --server.port 3000
            </code>
          </Box>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.35 }}>
          <Box color="yellow" style={{ marginTop: 8 }}>
            <BoxTitle color="#d97706">2단계: TODO 2개 채우기</BoxTitle>
            <div style={{ fontSize: '.9em', lineHeight: 1.8 }}>
              <strong>TODO 1</strong> — <code>tools = []</code> 에 tool 스키마 2개 정의<br />
              <strong>TODO 2</strong> — <code>execute_tool()</code> 함수 구현 (실제 API 호출)
            </div>
          </Box>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.5 }}>
          <Box color="purple" style={{ marginTop: 8, fontSize: '.85em', padding: '16px 24px' }}>
            <strong>제공되는 API 2개</strong>
            <code style={{ display: 'block', marginTop: 8, lineHeight: 2, background: 'rgba(0,0,0,.03)', padding: '10px 14px', borderRadius: 6 }}>
              GET /challenges/tool_use/secret?token=SSO토큰  → 시크릿 키 발급<br />
              POST /challenges/tool_use/submit  → 시크릿 키 제출
            </code>
          </Box>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.65 }}>
          <Box color="green" style={{ marginTop: 8, fontSize: '.95em' }}>
            <strong>성공 조건:</strong> LLM이 Tool 2개를 연속 호출 →{' '}
            <code>get_secret_key</code> → <code>submit_secret_key</code> → <strong style={{ color: '#059669' }}>자동 통과!</strong>
            <div style={{ marginTop: 8, fontSize: '.85em', color: '#64748b' }}>
              챗봇에 "과제 제출해줘"라고 입력하면 LLM이 알아서 Tool을 호출합니다.
            </div>
          </Box>
        </motion.div>
      </div>
    </div>
  );
}
