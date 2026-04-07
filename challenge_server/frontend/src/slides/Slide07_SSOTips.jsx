import { motion } from 'framer-motion';
import { Badge, SlideH2, Box, BoxTitle, Grid } from './SlideLayout';

export default function Slide07_SSOTips() {
  return (
    <div className="slide-container">
      <div className="slide-inner">
        <Badge variant="day1">SSO</Badge>
        <SlideH2>SSO 연동 신청 & 팁</SlideH2>

        <Grid cols={2} gap={20}>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
            <Box color="blue">
              <BoxTitle>연동 신청 절차</BoxTitle>
              <ul style={{ fontSize: '.9em', textAlign: 'left', paddingLeft: '1.2em', lineHeight: 1.8 }}>
                <li>사내 포털에서 API 사용 신청</li>
                <li>서비스 등록 및 Callback URL 설정</li>
                <li>Client ID / 인증서 발급</li>
                <li>토큰 만료 시 재로그인 처리</li>
              </ul>
            </Box>
          </motion.div>

          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4 }}>
            <Box color="green">
              <BoxTitle color="#10b981">실전 팁</BoxTitle>
              <ul style={{ fontSize: '.9em', textAlign: 'left', paddingLeft: '1.2em', lineHeight: 1.8 }}>
                <li>SSO 응답에서 인물정보 즉시 파싱 (별도 API 불필요)</li>
                <li>토큰 만료(12시간) 시 재로그인 안내</li>
                <li>에러 시 자동 재시도 로직 필수</li>
                <li>환경변수로 Credential 관리</li>
              </ul>
            </Box>
          </motion.div>
        </Grid>
      </div>
    </div>
  );
}
