import { motion } from 'framer-motion';
import { Badge, SlideH2, Divider, Box, BoxTitle, Grid } from './SlideLayout';

export default function Slide49_Day1Lab() {
  return (
    <div className="slide-container">
      <div className="slide-inner">
        <Badge variant="day1">DAY 1 실습</Badge>
        <SlideH2>바이브 코딩 실습</SlideH2>
        <Divider />

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}>
          <Grid cols={2}>
            <Box color="blue" style={{ padding: '24px 28px' }}>
              <BoxTitle>진행 방법</BoxTitle>
              <ol style={{ fontSize: '1em', lineHeight: 1.8, paddingLeft: 20, textAlign: 'left' }}>
                <li>슬라이드의 <strong>문제와 성공 조건</strong> 확인</li>
                <li>AI를 활용하여 <strong>바이브 코딩</strong></li>
                <li>SSO 토큰 + 정답을 <strong>서버에 제출</strong></li>
                <li>대시보드에 <strong>본인 이름</strong> 뜨면 성공!</li>
              </ol>
            </Box>
            <Box color="green" style={{ padding: '24px 28px' }}>
              <BoxTitle color="#059669">서버 정보</BoxTitle>
              <div style={{ fontSize: '.95em', lineHeight: 2, textAlign: 'left' }}>
                <div><strong>Challenge:</strong> <code style={{ color: '#2563eb' }}>challenge.example.com:47777</code></div>
                <div><strong>인증(SSO):</strong> <code style={{ color: '#2563eb' }}>auth.example.com</code></div>
                <div><strong>대시보드:</strong> <code style={{ color: '#2563eb' }}>challenge.example.com:47777</code></div>
                <div><strong>정답 제출:</strong> <code>POST /challenges/{'{id}'}/submit</code></div>
              </div>
            </Box>
          </Grid>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.5 }}>
          <Box color="yellow" style={{ marginTop: 12, fontSize: '1em', textAlign: 'center' }}>
            <strong>제출 형식:</strong> <code>{`{"token": "<SSO 토큰>", "answer": { ... }}`}</code> &nbsp;&rarr;&nbsp; <strong>홍길동님 통과!</strong>
          </Box>
        </motion.div>
      </div>
    </div>
  );
}
