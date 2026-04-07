import { motion } from 'framer-motion';
import { Badge, SlideH2, Divider, Box, BoxTitle } from './SlideLayout';

export default function Slide21_PromptTask() {
  return (
    <div className="slide-container">
      <div className="slide-inner">
        <Badge variant="day1">프롬프트 실습</Badge>
        <SlideH2>과제: 바이오 데이터 JSON 추출</SlideH2>
        <Divider />

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
          <Box color="blue" style={{ fontSize: '1em', padding: '22px 28px' }}>
            <BoxTitle>문제</BoxTitle>
            <strong>하나의 System Prompt</strong>로 10개의 서로 다른 바이오 데이터(CBC, NGS, PK, Flow Cytometry 등)를<br />
            각각 정확한 JSON 스키마로 추출하세요. <strong>10개 전부 통과</strong>해야 성공입니다.
          </Box>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4 }}>
          <Box color="yellow" style={{ marginTop: 8, fontSize: '.95em', padding: '18px 28px' }}>
            <strong>핵심 난이도:</strong> 같은 프롬프트로 10가지 다른 데이터를 처리해야 합니다.<br />
            &bull; Boolean은 <code>true/false</code> (문자열 아님) &nbsp; &bull; 숫자는 단위 없이 &nbsp; &bull; 배열은 <code>[...]</code><br />
            &bull; <strong>타입을 정확히 지정하지 않으면 6~8개만 통과합니다</strong>
          </Box>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.6 }}>
          <Box color="green" style={{ marginTop: 8, fontSize: '1em', padding: '16px 28px', textAlign: 'center' }}>
            <strong>접속:</strong> <code>http://a2g.samsungds.net:47777/challenges/prompt</code> -> 프롬프트 입력 -> 테스트 -> 제출<br />
            <span role="img" aria-label="celebration">&#x1F389;</span> <strong>10/10 통과 시 대시보드에 이름 표시</strong>
          </Box>
        </motion.div>
      </div>
    </div>
  );
}
