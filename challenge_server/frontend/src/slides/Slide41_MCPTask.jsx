import { motion } from 'framer-motion';
import { Badge, SlideH2, Divider, Box, BoxTitle, Grid, Card } from './SlideLayout';

const tools = [
  { name: 'add(157, 289)', result: '446', color: '#2563eb' },
  { name: 'get_weather("서울")', result: '맑음, 15\u00B0C', color: '#059669' },
  { name: 'search_employee("김")', result: '김OO 정보', color: '#7c3aed' },
];

export default function Slide41_MCPTask() {
  return (
    <div className="slide-container">
      <div className="slide-inner">
        <Badge variant="day1">MCP 실습</Badge>
        <SlideH2>바이브 코딩: MCP Tool 호출</SlideH2>
        <Divider />

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}>
          <Box color="blue" style={{ marginTop: 8, fontSize: '.95em', padding: '18px 28px' }}>
            <BoxTitle>문제</BoxTitle>
            <code>python day1/01_mcp/mcp_server.py</code>로 MCP 서버를 실행하고,<br />
            클라이언트 + LLM을 연동하여 아래 3개 도구를 호출하세요.
          </Box>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4 }}>
          <Grid cols={3}>
            {tools.map((t, i) => (
              <motion.div key={t.name} initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.5 + i * 0.1 }}>
                <Card borderColor={t.color} style={{ padding: 20 }}>
                  <h4 style={{ color: t.color }}>{t.name}</h4>
                  <p style={{ fontSize: '.9em' }}>&rarr; {t.result}</p>
                </Card>
              </motion.div>
            ))}
          </Grid>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.7 }}>
          <Box color="yellow" style={{ marginTop: 8, fontSize: '.88em', padding: '14px 24px' }}>
            <strong>제출:</strong> <code>POST http://a2g.samsungds.net:47777/challenges/mcp/submit</code><br />
            <code>{`{"token":"SSO토큰", "answer":{"results":["446","맑음, 15\u00B0C","김OO..."]}}`}</code>
          </Box>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.8 }}>
          <Box color="green" style={{ marginTop: 8, fontSize: '1em', textAlign: 'center' }}>
            <strong>성공:</strong> 홍길동님, MCP Tool 호출 통과! <strong>3/3 도구 호출 성공</strong>
          </Box>
        </motion.div>
      </div>
    </div>
  );
}
