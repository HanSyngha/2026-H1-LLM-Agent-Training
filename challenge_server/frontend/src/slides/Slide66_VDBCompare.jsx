import { motion } from 'framer-motion';
import { Badge, SlideH2, Box } from './SlideLayout';

function AnimatedBox({ x, y, w, h, fill, stroke, delay, children }) {
  return (
    <motion.g initial={{ opacity: 0, scale: 0.8 }} animate={{ opacity: 1, scale: 1 }} transition={{ delay, duration: 0.4 }}>
      <rect x={x} y={y} width={w} height={h} rx={12} fill={fill} stroke={stroke} strokeWidth={2} />
      {children}
    </motion.g>
  );
}

export default function Slide66_VDBCompare() {
  return (
    <div className="slide-container">
      <div className="slide-inner">
        <Badge variant="day2">검색 전략</Badge>
        <SlideH2 day2>비교: 언제 무엇을 쓸 것인가</SlideH2>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }} style={{ marginTop: 16 }}>
          <svg viewBox="0 0 950 270" width="950" height="270" className="diagram-svg">
            {/* Left: Vector DB */}
            <AnimatedBox x={20} y={10} w={420} h={250} fill="rgba(59,130,246,.1)" stroke="rgba(59,130,246,.5)" delay={0.3}>
              <text x={230} y={42} textAnchor="middle" fill="#1d4ed8" fontWeight={700} fontSize={16}>Vector DB (Semantic)</text>
            </AnimatedBox>

            {/* Dots cluster */}
            <motion.g initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.5 }}>
              <circle cx={85} cy={95} r={7} fill="rgba(59,130,246,.4)" />
              <circle cx={125} cy={84} r={7} fill="rgba(59,130,246,.5)" />
              <circle cx={105} cy={116} r={7} fill="rgba(59,130,246,.6)" />
              <circle cx={100} cy={100} r={22} fill="none" stroke="rgba(59,130,246,.3)" strokeWidth={1} strokeDasharray="4 3" />
              <text x={100} y={155} textAnchor="middle" fill="#475569" fontSize={13}>유사도 클러스터</text>
            </motion.g>

            {/* Pros */}
            <motion.g initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.6 }}>
              <text x={230} y={84} textAnchor="middle" fill="#10b981" fontSize={14} fontWeight={600}>장점</text>
              <text x={230} y={106} textAnchor="middle" fill="#334155" fontSize={13}>동의어/유사 표현 인식</text>
              <text x={230} y={126} textAnchor="middle" fill="#334155" fontSize={13}>자연어 질문 가능</text>
            </motion.g>

            {/* Cons */}
            <motion.g initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.7 }}>
              <text x={230} y={156} textAnchor="middle" fill="#dc2626" fontSize={14} fontWeight={600}>단점</text>
              <text x={230} y={178} textAnchor="middle" fill="#334155" fontSize={13}>임베딩 비용</text>
              <text x={230} y={198} textAnchor="middle" fill="#334155" fontSize={13}>정확도 불확실</text>
            </motion.g>

            {/* Use case */}
            <motion.g initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.8 }}>
              <rect x={55} y={220} width={320} height={30} rx={6} fill="rgba(59,130,246,.12)" stroke="rgba(59,130,246,.2)" strokeWidth={1} />
              <text x={215} y={240} textAnchor="middle" fill="#1d4ed8" fontSize={13} fontWeight={600}>문서 검색, FAQ, 지식베이스</text>
            </motion.g>

            {/* Right: Index Explore */}
            <AnimatedBox x={510} y={10} w={420} h={250} fill="rgba(16,185,129,.08)" stroke="rgba(16,185,129,.5)" delay={0.4}>
              <text x={720} y={42} textAnchor="middle" fill="#047857" fontWeight={700} fontSize={16}>Index Explore (Exact)</text>
            </AnimatedBox>

            {/* Tree structure */}
            <motion.g initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.55 }}>
              <line x1={590} y1={78} x2={568} y2={106} stroke="#10b981" strokeWidth={1.5} />
              <line x1={590} y1={78} x2={612} y2={106} stroke="#10b981" strokeWidth={1.5} />
              <circle cx={590} cy={75} r={6} fill="#10b981" />
              <circle cx={568} cy={109} r={5} fill="rgba(16,185,129,.5)" />
              <circle cx={612} cy={109} r={5} fill="rgba(16,185,129,.5)" />
              <text x={590} y={140} textAnchor="middle" fill="#475569" fontSize={13}>구조적 탐색</text>
            </motion.g>

            {/* Pros */}
            <motion.g initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.65 }}>
              <text x={720} y={84} textAnchor="middle" fill="#10b981" fontSize={14} fontWeight={600}>장점</text>
              <text x={720} y={106} textAnchor="middle" fill="#334155" fontSize={13}>정확한 결과</text>
              <text x={720} y={126} textAnchor="middle" fill="#334155" fontSize={13}>구조적 탐색, 빠름</text>
            </motion.g>

            {/* Cons */}
            <motion.g initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.75 }}>
              <text x={720} y={156} textAnchor="middle" fill="#dc2626" fontSize={14} fontWeight={600}>단점</text>
              <text x={720} y={178} textAnchor="middle" fill="#334155" fontSize={13}>의미적 연결 불가</text>
              <text x={720} y={198} textAnchor="middle" fill="#334155" fontSize={13}>패턴을 알아야 함</text>
            </motion.g>

            {/* Use case */}
            <motion.g initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.85 }}>
              <rect x={545} y={220} width={320} height={30} rx={6} fill="rgba(16,185,129,.12)" stroke="rgba(16,185,129,.2)" strokeWidth={1} />
              <text x={705} y={240} textAnchor="middle" fill="#047857" fontSize={13} fontWeight={600}>코드 탐색, 설정 파일, 로그</text>
            </motion.g>

            {/* VS divider */}
            <motion.text x={475} y={140} textAnchor="middle" fill="#64748b" fontSize={18} fontWeight={800}
              initial={{ opacity: 0, scale: 0.5 }} animate={{ opacity: 1, scale: 1 }} transition={{ delay: 0.9, type: 'spring' }}>
              VS
            </motion.text>
          </svg>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 1.0 }}>
          <Box color="blue" style={{ marginTop: '0.4em', fontSize: '.88em' }}>
            <strong>실전 팁:</strong> 두 방식을 <strong>혼합</strong>하면 최고 성능. 먼저 Vector로 후보를 찾고, grep으로 정확히 확인.
          </Box>
        </motion.div>
      </div>
    </div>
  );
}
