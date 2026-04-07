import { motion } from 'framer-motion';
import { Badge, SlideH2, Box, BoxTitle, Grid, CodeBlock } from './SlideLayout';

export default function Slide46_IframeCOM() {
  return (
    <div className="slide-container">
      <div className="slide-inner">
        <Badge variant="day1">브라우저 자동화</Badge>
        <SlideH2>iframe / COM 제어 개요</SlideH2>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
          <Grid cols={2}>
            <Box color="purple">
              <BoxTitle color="#8b5cf6">iframe 제어</BoxTitle>
              <pre style={{
                fontSize: '.78em', border: 'none', background: 'transparent',
                padding: '.3em 0', margin: 0, boxShadow: 'none', color: '#1e293b',
              }}>
                <code>{`# Playwright로 iframe 접근
frame = page.frame_locator(
    "iframe#app-frame"
)
frame.locator("button").click()`}</code>
              </pre>
            </Box>
            <Box color="yellow">
              <BoxTitle color="#d97706">COM 자동화 (Windows)</BoxTitle>
              <pre style={{
                fontSize: '.78em', border: 'none', background: 'transparent',
                padding: '.3em 0', margin: 0, boxShadow: 'none', color: '#1e293b',
              }}>
                <code>{`import win32com.client

# Excel COM 자동화
excel = win32com.client.Dispatch(
    "Excel.Application"
)
wb = excel.Workbooks.Open(path)`}</code>
              </pre>
            </Box>
          </Grid>
        </motion.div>
      </div>
    </div>
  );
}
