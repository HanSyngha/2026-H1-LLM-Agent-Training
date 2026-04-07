import { motion } from 'framer-motion';
import { Badge, SlideH2, Divider, Box, BoxTitle, Grid } from './SlideLayout';

export default function Slide05_SSOChallenge() {
  return (
    <div className="slide-container">
      <div className="slide-inner">
        <Badge variant="day1">SSO 실습</Badge>
        <SlideH2>과제: Streamlit 앱에 SSO 연동하기</SlideH2>
        <Divider />

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
          <Box color="blue">
            <BoxTitle>1단계: 앱 실행</BoxTitle>
            <code style={{ display: 'block', fontSize: '1.05em', lineHeight: 1.8 }}>
              cd day1/00_sso/challenge<br />
              pip install streamlit requests PyJWT<br />
              streamlit run app.py --server.port 3000
            </code>
          </Box>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4 }}>
          <Box color="yellow" style={{ marginTop: 8 }}>
            <BoxTitle color="#d97706">2단계: 빈 화면 확인</BoxTitle>
            <div style={{ padding: '12px 16px', background: '#f8fafc', borderRadius: 8, fontSize: '.95em', lineHeight: 1.8, marginTop: 8 }}>
              🔐 <strong>SSO 로그인 실습</strong><br />
              ⚠️ 로그인이 필요합니다.<br />
              🔑 SSO 로그인 (OIDC) <span style={{ color: '#94a3b8' }}>(비활성)</span><br />
              이름: <span style={{ color: '#94a3b8' }}>__________</span> &nbsp; 부서: <span style={{ color: '#94a3b8' }}>__________</span><br />
              🎯 Challenge 서버에 제출 <span style={{ color: '#94a3b8' }}>(비활성)</span>
            </div>
          </Box>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.6 }}>
          <Box color="green" style={{ marginTop: 8, textAlign: 'center', fontSize: '1.05em' }}>
            <strong>3단계:</strong> 바이브 코딩으로 로그인 버튼에 OIDC를 연결하세요.<br />
            로그인 성공 → 정보 표시 → 제출 버튼 활성화!
          </Box>
        </motion.div>
      </div>
    </div>
  );
}
