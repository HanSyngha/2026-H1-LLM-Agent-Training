import { motion } from 'framer-motion';
import { Badge, SlideH2, Divider, Box, BoxTitle, CodeBlock } from './SlideLayout';

export default function Slide11b_PythonSetup() {
  return (
    <div className="slide-container">
      <div className="slide-inner">
        <Badge variant="day1">환경 설정</Badge>
        <SlideH2>Windows에서 Python 환경 확인</SlideH2>
        <Divider />

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
          <Box color="red" style={{ fontSize: '.9em', padding: '14px 24px' }}>
            <strong>streamlit이 안 됩니까?</strong> — Python Scripts 폴더가 PATH에 없을 가능성이 높습니다.
          </Box>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.35 }}>
          <Box color="blue" style={{ marginTop: 8, fontSize: '.85em', padding: '16px 24px' }}>
            <BoxTitle>1. Python 경로 확인 (PowerShell)</BoxTitle>
            <CodeBlock lang="powershell">{`# Python 위치 확인
where.exe python
# 또는
py --list-paths

# 예시 결과: C:\\Users\\홍길동\\AppData\\Local\\Programs\\Python\\Python312\\python.exe`}</CodeBlock>
          </Box>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.5 }}>
          <Box color="yellow" style={{ marginTop: 8, fontSize: '.85em', padding: '16px 24px' }}>
            <BoxTitle color="#d97706">2. 패키지 설치 (3가지 방법 중 되는 걸로)</BoxTitle>
            <CodeBlock lang="powershell">{`# 방법 1: pip이 PATH에 있을 때
pip install streamlit requests PyJWT

# 방법 2: python -m 사용 (가장 확실)
python -m pip install streamlit requests PyJWT

# 방법 3: py 런처 사용
py -m pip install streamlit requests PyJWT`}</CodeBlock>
          </Box>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.65 }}>
          <Box color="green" style={{ marginTop: 8, fontSize: '.85em', padding: '16px 24px' }}>
            <BoxTitle color="#059669">3. Streamlit 실행</BoxTitle>
            <CodeBlock lang="powershell">{`# streamlit이 PATH에 있으면
streamlit run app.py --server.port 3000

# 안 되면 python -m으로
python -m streamlit run app.py --server.port 3000`}</CodeBlock>
          </Box>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.8 }}>
          <Box color="purple" style={{ marginTop: 8, fontSize: '.82em', padding: '14px 24px' }}>
            <strong>PATH 등록 (영구):</strong> 시작 → "환경 변수" 검색 → 사용자 변수 Path 편집 →{' '}
            <code>C:\Users\홍길동\AppData\Local\Programs\Python\Python312\Scripts</code> 추가
          </Box>
        </motion.div>
      </div>
    </div>
  );
}
