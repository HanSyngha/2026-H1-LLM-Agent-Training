import { motion } from 'framer-motion';
import { Badge, SlideH2, Divider, Box, BoxTitle, Grid, Card } from './SlideLayout';

const fields = [
  { name: 'title', desc: '기사 제목', color: '#1d4ed8' },
  { name: 'category', desc: '기술/경제/정치/사회/스포츠', color: '#059669' },
  { name: 'sentiment', desc: '긍정/부정/중립', color: '#7c3aed' },
  { name: 'keywords', desc: '3~5개 배열', color: '#d97706' },
  { name: 'summary', desc: '2문장 요약', color: '#0891b2' },
];

export default function Slide35_StructuredTask() {
  return (
    <div className="slide-container">
      <div className="slide-inner">
        <Badge variant="day1">Structured Output 실습</Badge>
        <SlideH2>바이브 코딩: 뉴스 기사 분석</SlideH2>
        <Divider />

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}>
          <Box color="blue" style={{ marginTop: 8, fontSize: '.95em', padding: '20px 28px' }}>
            <BoxTitle>문제</BoxTitle>
            아래 뉴스 기사를 LLM의 <strong>Structured Output</strong>(response_format)으로 분석하세요.<br />
            <em style={{ color: '#64748b' }}>
              "[속보] 삼성전자, 차세대 AI 반도체 'Mach-1' 양산 개시 -- Mach-1은 기존 대비 전력 효율 2배..."
            </em>
          </Box>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4 }}>
          <Grid cols={5} gap={12}>
            {fields.map((f, i) => (
              <motion.div key={f.name} initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.5 + i * 0.08 }}>
                <Card borderColor={f.color} style={{ padding: 14 }}>
                  <h4 style={{ fontSize: '.9em', color: f.color, marginBottom: 4 }}>{f.name}</h4>
                  <p style={{ fontSize: '.8em', margin: 0 }}>{f.desc}</p>
                </Card>
              </motion.div>
            ))}
          </Grid>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.7 }}>
          <Box color="yellow" style={{ marginTop: 8, fontSize: '.88em', padding: '14px 24px' }}>
            <strong>제출:</strong> <code>POST http://a2g.samsungds.net:47777/challenges/structured/submit</code><br />
            <code>{`{"token":"SSO토큰", "answer":{"title":"...","category":"기술","sentiment":"긍정","keywords":[...],"summary":"..."}}`}</code>
          </Box>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.8 }}>
          <Box color="green" style={{ marginTop: 8, fontSize: '1em', textAlign: 'center' }}>
            <strong>성공:</strong> 홍길동님, Structured Output 통과! <strong>5/5 필드 검증 통과</strong>
          </Box>
        </motion.div>
      </div>
    </div>
  );
}
