import { motion } from 'framer-motion';
import { Badge, SlideH2, Quote, Box, BoxTitle, Grid } from './SlideLayout';

export default function Slide37_MCP1() {
  return (
    <div className="slide-container">
      <div className="slide-inner">
        <Badge variant="day1">MCP</Badge>
        <SlideH2>MCP란?</SlideH2>
        <motion.p
          initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}
          style={{ color: '#475569' }}
        >
          Model Context Protocol &mdash; 2026 업계 표준
        </motion.p>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}>
          <Quote borderColor="#059669">
            "USB-C for AI" &mdash; AI 도구 연결의 표준 인터페이스
          </Quote>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4 }}>
          <Grid cols={2}>
            <Box color="red">
              <BoxTitle color="#dc2626">Before MCP</BoxTitle>
              <p style={{ fontSize: '.88em' }}>
                각 AI 앱마다 별도 Tool 구현<br />
                N개 앱 x M개 도구 = <strong>N*M</strong> 통합 필요
              </p>
            </Box>
            <Box color="green">
              <BoxTitle color="#10b981">After MCP</BoxTitle>
              <p style={{ fontSize: '.88em' }}>
                MCP 서버 1개 만들면 모든 AI 앱에서 사용<br />
                <strong>N + M</strong> 통합으로 충분
              </p>
            </Box>
          </Grid>
        </motion.div>
      </div>
    </div>
  );
}
