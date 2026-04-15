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
          Model Context Protocol &mdash; 최근 많이 언급되지만 기본 선택지로 보기엔 제약이 많음
        </motion.p>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}>
          <Quote borderColor="#b42318">
            MCP를 먼저 쓰지 마세요. 대부분의 경우에는 <strong>REST API가 더 안정적이고 범용적</strong>입니다.
          </Quote>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4 }}>
          <Grid cols={2}>
            <Box color="green">
              <BoxTitle color="#027a48">더 나은 기본값: REST API</BoxTitle>
              <p style={{ fontSize: '.88em' }}>
                훨씬 안정적인 표준<br />
                대부분의 서비스와 인프라에 바로 연결 가능
              </p>
            </Box>
            <Box color="red">
              <BoxTitle color="#dc2626">MCP의 현실적 제약</BoxTitle>
              <p style={{ fontSize: '.88em' }}>
                생각보다 제약적이고 지원 범위가 좁음<br />
                어떤 AI 서비스에든 범용적으로 넣기 어렵습니다
              </p>
            </Box>
          </Grid>
        </motion.div>
      </div>
    </div>
  );
}
