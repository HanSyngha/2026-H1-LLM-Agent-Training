import { motion } from 'framer-motion';
import { Badge, SlideH2, Divider, Box, BoxTitle } from './SlideLayout';
import AnswerButton from './AnswerButton';
import Slide30_EndpointAnswer from './Slide30_EndpointAnswer';

export default function Slide29_EndpointTask() {
  return (
    <div className="slide-container">
      <div className="slide-inner">
        <Badge variant="day1">Endpoint 실습</Badge>
        <SlideH2>바이브 코딩: LLM Gateway 연결</SlideH2>
        <Divider />

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
          <Box color="blue">
            <BoxTitle>1단계: 코드 다운로드 & 실행</BoxTitle>
            <a href="/downloads/endpoint" download
              style={{ display: 'inline-block', padding: '8px 20px', borderRadius: 8, background: '#2563eb', color: '#fff',
                textDecoration: 'none', fontWeight: 600, fontSize: '.9em', marginBottom: 8 }}>
              📦 실습 코드 다운로드 (endpoint_code.zip)
            </a>
            <code style={{ display: 'block', fontSize: '1em', lineHeight: 1.8 }}>
              pip install streamlit requests PyJWT<br />
              streamlit run app.py --server.port 3000
            </code>
          </Box>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.35 }}>
          <Box color="yellow" style={{ marginTop: 8 }}>
            <BoxTitle color="#d97706">2단계: TODO 채우기</BoxTitle>
            <div style={{ fontSize: '.92em', lineHeight: 1.7 }}>
              앱을 열면 <strong>SSO 로그인은 자동</strong>으로 됩니다.<br />
              <code>app.py</code>의 <code style={{ color: '#dc2626' }}>resp = None</code> 부분을<br />
              <code style={{ color: '#059669' }}>requests.post(...)</code>로 채워서 LLM Gateway에 연결하세요.
            </div>
          </Box>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.5 }}>
          <Box color="purple" style={{ marginTop: 8, fontSize: '.85em', padding: '16px 24px' }}>
            <strong>사내 LLM Gateway 연결 정보</strong>
            <code style={{ display: 'block', marginTop: 8, lineHeight: 1.9, background: 'rgba(0,0,0,.03)', padding: '10px 14px', borderRadius: 6 }}>
              URL: http://a2g.samsungds.net:8090/v1/chat/completions<br />
              Header: x-service-id: test-service  (세팅됨)<br />
              Header: x-user-id: {'<'}user_id 변수{'>'}  (SSO에서 자동 세팅됨)
            </code>
          </Box>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.65 }}>
          <Box color="green" style={{ marginTop: 8, textAlign: 'center', fontSize: '1.05em' }}>
            <strong>3단계:</strong> 챗봇에서 아무 메시지나 보내면 → LLM 응답 → <strong style={{ color: '#059669' }}>자동 제출 & 통과!</strong>
          </Box>
        </motion.div>

        <AnswerButton answerId="endpoint"><Slide30_EndpointAnswer /></AnswerButton>
      </div>
    </div>
  );
}
