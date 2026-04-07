import { motion } from 'framer-motion';
import { Badge, SlideH2, Divider, Box, BoxTitle } from './SlideLayout';

export default function Slide47_BrowserTask() {
  return (
    <div className="slide-container">
      <div className="slide-inner">
        <Badge variant="day1">브라우저 실습</Badge>
        <SlideH2>바이브 코딩: CDP로 데이터 추출</SlideH2>
        <Divider />

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}>
          <Box color="red" style={{ marginTop: 8, fontSize: '1em', padding: '18px 28px' }}>
            <strong>주의:</strong> 이 페이지는 <strong>JavaScript로 렌더링</strong>됩니다. <code>requests.get()</code>으로는 "데이터 로드 중..."만 보입니다.<br />
            Chrome을 <code>--remote-debugging-port=9222</code>로 실행하고 CDP로 접근해야 합니다.
          </Box>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4 }}>
          <Box color="blue" style={{ marginTop: 8, fontSize: '.95em', padding: '18px 28px' }}>
            <BoxTitle>문제</BoxTitle>
            <code>http://a2g.samsungds.net:47777/browser-target</code> 페이지에서<br />
            상품 5개의 <strong>이름과 가격</strong>을 추출하세요.
          </Box>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.5 }}>
          <Box color="yellow" style={{ marginTop: 8, fontSize: '.88em', padding: '14px 24px' }}>
            <strong>제출:</strong> <code>POST http://a2g.samsungds.net:47777/challenges/browser/submit</code><br />
            <code>{`{"token":"SSO토큰", "answer":{"products":[{"name":"AI 가속기 Mach-1","price":1250000},...]}}`}</code>
          </Box>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.6 }}>
          <Box color="green" style={{ marginTop: 8, fontSize: '1em', textAlign: 'center' }}>
            <strong>성공:</strong> 홍길동님, 브라우저 자동화 통과! <strong>5/5 상품 데이터 일치</strong>
          </Box>
        </motion.div>
      </div>
    </div>
  );
}
