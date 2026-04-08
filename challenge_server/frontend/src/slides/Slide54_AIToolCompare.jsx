import { motion } from 'framer-motion';
import { Badge, SlideH2, Divider, Box } from './SlideLayout';

const tools = [
  { name: 'Google Stitch', focus: '디자인 탐색 & 목업', strength: '무료, 음성, Figma 연동', limit: '프론트엔드만', color: '#7c3aed', best: '디자인 아이디어 → 프로토타입' },
  { name: 'v0 (Vercel)', focus: 'React 컴포넌트 생성', strength: '프로덕션급 코드, shadcn/ui', limit: 'React 전용', color: '#0f172a', best: '개발자가 컴포넌트 빠르게 생성' },
  { name: 'Bolt', focus: '풀스택 프로토타이핑', strength: '브라우저 샌드박스, NPM, DB', limit: '디자인 품질 낮음', color: '#3b82f6', best: '빠른 PoC, 전체 앱 프로토타입' },
  { name: 'Lovable', focus: '풀스택 앱 빌드', strength: '완성도 높은 제품', limit: '유료', color: '#dc2626', best: '스타트업 MVP, 완성형 앱' },
];

export default function Slide54_AIToolCompare() {
  return (
    <div className="slide-container">
      <div className="slide-inner">
        <Badge variant="day2">Frontend AI</Badge>
        <SlideH2>AI 디자인/개발 도구 비교</SlideH2>
        <Divider />

        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.2 }}>
          <table style={{ width: '100%', fontSize: '.85em', marginTop: 8 }}>
            <thead>
              <tr>
                <th style={{ width: '15%' }}>도구</th>
                <th style={{ width: '18%' }}>초점</th>
                <th style={{ width: '22%' }}>강점</th>
                <th style={{ width: '15%' }}>한계</th>
                <th>최적 용도</th>
              </tr>
            </thead>
            <tbody>
              {tools.map((t, i) => (
                <motion.tr key={t.name}
                  initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.3 + i * 0.1 }}>
                  <td><strong style={{ color: t.color }}>{t.name}</strong></td>
                  <td>{t.focus}</td>
                  <td>{t.strength}</td>
                  <td style={{ color: '#94a3b8' }}>{t.limit}</td>
                  <td style={{ fontSize: '.9em' }}>{t.best}</td>
                </motion.tr>
              ))}
            </tbody>
          </table>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.8 }}>
          <Box color="purple" style={{ marginTop: 16, fontSize: '.95em', lineHeight: 1.7 }}>
            <strong>우리 조직에서는?</strong> 디자인 탐색은 <strong>Stitch</strong>,
            컴포넌트 개발은 <strong>v0</strong>, PoC는 <strong>Bolt</strong> — 단계별로 조합하면 최고 효율
          </Box>
        </motion.div>
      </div>
    </div>
  );
}
