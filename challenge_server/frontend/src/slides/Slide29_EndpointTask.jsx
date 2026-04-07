import { motion } from 'framer-motion';
import { Badge, SlideH2, Divider, Box, BoxTitle } from './SlideLayout';

export default function Slide29_EndpointTask() {
  return (
    <div className="slide-container">
      <div className="slide-inner">
        <Badge variant="day1">Endpoint 실습</Badge>
        <SlideH2>바이브 코딩: LLM Gateway 연결</SlideH2>
        <Divider />

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}>
          <Box color="blue" style={{ marginTop: 12, fontSize: '1.05em', padding: '28px 32px' }}>
            <BoxTitle>문제</BoxTitle>
            사내 LLM Gateway에 연결하여 아래 질문의 응답을 받아오세요.<br />
            <strong style={{ marginTop: 8, display: 'inline-block' }}>
              "대한민국의 수도는 어디이며, 그 도시의 영문명을 알려주세요."
            </strong>
          </Box>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4 }}>
          <Box color="yellow" style={{ marginTop: 8, fontSize: '.92em', padding: '20px 28px' }}>
            <strong>성공 조건:</strong> 응답에 <code>"서울"</code>과 <code>"Seoul"</code>이 모두 포함되어야 합니다.
          </Box>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.5 }}>
          <Box color="green" style={{ marginTop: 8, fontSize: '.92em', padding: '20px 28px' }}>
            <strong>제출:</strong> <code>POST http://a2g.samsungds.net:47777/challenges/endpoint/submit</code><br />
            <code>{`{"token":"SSO토큰", "answer":{"response":"LLM이 응답한 전체 텍스트"}}`}</code><br />
            <strong style={{ color: '#059669' }}>→ 홍길동님, LLM Endpoint 연결 통과!</strong>
          </Box>
        </motion.div>
      </div>
    </div>
  );
}
