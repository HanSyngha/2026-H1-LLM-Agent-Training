import { motion } from 'framer-motion';
import { Badge, SlideH2, Divider, Box, Quote } from './SlideLayout';

export default function Slide11_SSOLabIntro() {
  return (
    <div className="slide-container">
      <div className="slide-inner">
        <Badge variant="day1">SSO</Badge>
        <SlideH2>실습 안내</SlideH2>
        <Divider />

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}>
          <Box color="blue" style={{ fontSize: '1.1em', lineHeight: 1.8, textAlign: 'center' }}>
            Agent Dashboard에 <strong>OAuth2 / OIDC 인증 서버</strong>를 준비해 두었습니다.<br />
            LLM은 이 표준 흐름을 이미 잘 알고 있으니, 여러분은 <strong>사내 조건</strong>을 알려주고 <strong>클라이언트</strong>를 붙이면 됩니다.
          </Box>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.5 }}>
          <Quote borderColor="#059669">
            <span style={{ fontStyle: 'normal' }}>
              이 실습의 목표는 OAuth2/OIDC를 완벽히 암기하는 것이 아니라,<br />
              <strong>바이브코딩으로 SSO를 실제로 붙여보며 "생각보다 쉽게 도입할 수 있다"</strong>는 자신감을 얻는 것입니다.<br />
              단, 사내 SSO의 <strong>3가지 주의사항</strong>은 AI에게 정확히 전달해야 합니다.
            </span>
          </Quote>
        </motion.div>
      </div>
    </div>
  );
}
