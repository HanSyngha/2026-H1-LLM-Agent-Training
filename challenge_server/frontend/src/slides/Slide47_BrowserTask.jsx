import { motion } from 'framer-motion';
import { Badge, SlideH2, Divider, Box, BoxTitle } from './SlideLayout';

export default function Slide47_BrowserTask() {
  return (
    <div className="slide-container">
      <div className="slide-inner">
        <Badge variant="day1">브라우저 실습</Badge>
        <SlideH2>바이브 코딩: JS 렌더링 페이지에서 비밀 키 추출</SlideH2>
        <Divider />

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}>
          <Box color="red" style={{ marginTop: 8, fontSize: '1em', padding: '18px 28px' }}>
            <strong>주의:</strong> 이 페이지는 <strong>JavaScript로 렌더링</strong>됩니다.<br />
            <code>requests.get()</code>이나 <code>curl</code>로는 "로딩 중..."만 보입니다!
          </Box>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4 }}>
          <Box color="blue" style={{ marginTop: 8, fontSize: '.95em', padding: '20px 28px' }}>
            <BoxTitle>과제</BoxTitle>
            아래 페이지에 숨겨진 <strong>비밀 키</strong>를 프로그래밍으로 추출하세요.<br />
            <code style={{ display: 'block', margin: '10px 0', padding: '8px 14px', background: 'rgba(0,0,0,.05)', borderRadius: 6, fontSize: '.95em' }}>
              http://a2g.samsungds.net:47777/browser-target
            </code>
            키는 DOM에 숨겨져 있습니다 — 눈에 보이지 않습니다!<br />
            <span style={{ fontSize: '.85em', color: '#64748b', marginTop: 4, display: 'block' }}>
              요소 ID: <code>#secret-key</code> | Playwright, Selenium, CDP 등 자유
            </span>
          </Box>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.5 }}>
          <Box color="yellow" style={{ marginTop: 8, fontSize: '.88em', padding: '14px 24px' }}>
            <strong>제출:</strong> <code>POST http://a2g.samsungds.net:47777/challenges/browser/submit</code><br />
            <code>{`{"token":"SSO토큰", "answer":{"secret_key":"추출한 비밀 키"}}`}</code>
          </Box>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.6 }}>
          <Box color="green" style={{ marginTop: 8, fontSize: '1em', textAlign: 'center' }}>
            <strong>성공 조건:</strong> 비밀 키가 정확히 일치하면 → <strong style={{ color: '#059669' }}>자동 통과!</strong>
          </Box>
        </motion.div>
      </div>
    </div>
  );
}
