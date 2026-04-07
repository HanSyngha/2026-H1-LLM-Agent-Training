import { motion } from 'framer-motion';
import { Badge, SlideH2, Divider, Box, BoxTitle, Grid } from './SlideLayout';

export default function Slide18_Prompt1() {
  return (
    <div className="slide-container">
      <div className="slide-inner">
        <Badge variant="day1">프롬프트</Badge>
        <SlideH2>결국 프롬프트가 핵심</SlideH2>
        <Divider />
        <motion.p initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}
          style={{ fontSize: '1.1em', marginTop: '.6em' }}>
          같은 모델이라도 프롬프트에 따라 <strong style={{ color: '#2563eb' }}>성능이 극적으로</strong> 달라집니다
        </motion.p>

        <Grid cols={2} gap={20}>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4 }}>
            <Box color="red">
              <BoxTitle color="#dc2626">나쁜 프롬프트</BoxTitle>
              <p style={{ fontSize: '.9em', color: '#334155' }}>"이 코드 고쳐줘"</p>
              <p style={{ fontSize: '.8em', color: '#64748b', marginTop: '.3em' }}>-> 모호함, 맥락 부족, 기대 출력 불명확</p>
            </Box>
          </motion.div>

          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.6 }}>
            <Box color="green">
              <BoxTitle color="#10b981">좋은 프롬프트</BoxTitle>
              <p style={{ fontSize: '.9em', color: '#334155' }}>
                "아래 Python 함수에서 TypeError가 발생합니다.<br />
                입력 타입 검증을 추가하고, 수정된 코드만 반환하세요."
              </p>
              <p style={{ fontSize: '.8em', color: '#64748b', marginTop: '.3em' }}>-> 구체적, 맥락 포함, 출력 형태 명시</p>
            </Box>
          </motion.div>
        </Grid>
      </div>
    </div>
  );
}
