import { motion } from 'framer-motion';
import { Badge, SlideH2, Divider, Grid, Box, BoxTitle } from './SlideLayout';

export default function Slide69_ContextEng2() {
  return (
    <div className="slide-container">
      <div className="slide-inner">
        <Badge variant="day2">하네스 엔지니어링</Badge>
        <SlideH2 day2>컨텍스트 엔지니어링</SlideH2>
        <p>Anthropic 연구: 컨텍스트 최적화만으로 <strong style={{ color: '#3b82f6' }}>54% 성능 향상</strong></p>
        <Divider />

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4 }}>
          <Grid cols={2} gap={20}>
            <Box color="blue">
              <BoxTitle>넣어야 할 것</BoxTitle>
              <ul style={{ fontSize: '.88em' }}>
                <li>명확한 역할 정의</li>
                <li>관련 문서/코드 (RAG 결과)</li>
                <li>이전 Tool 실행 결과</li>
                <li>출력 형식 예시 (few-shot)</li>
                <li>제약 조건과 경계</li>
              </ul>
            </Box>
            <Box color="red">
              <BoxTitle color="#dc2626">빼야 할 것</BoxTitle>
              <ul style={{ fontSize: '.88em' }}>
                <li>무관한 문서 (노이즈)</li>
                <li>오래된/부정확한 정보</li>
                <li>과도한 히스토리 (요약 필요)</li>
                <li>중복 내용</li>
                <li>민감 정보 (개인정보 등)</li>
              </ul>
            </Box>
          </Grid>
        </motion.div>
      </div>
    </div>
  );
}
