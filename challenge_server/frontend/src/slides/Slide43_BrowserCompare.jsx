import { motion } from 'framer-motion';
import { Badge, SlideH2 } from './SlideLayout';

export default function Slide43_BrowserCompare() {
  return (
    <div className="slide-container">
      <div className="slide-inner">
        <Badge variant="day1">브라우저 자동화</Badge>
        <SlideH2>브라우저 자동화 기술 비교</SlideH2>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
          <table style={{ marginTop: 12, fontSize: '.86em' }}>
            <thead>
              <tr>
                <th>기술</th>
                <th>방식</th>
                <th>장점</th>
                <th>단점</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td><strong style={{ color: '#2563eb' }}>CDP</strong></td>
                <td>Chrome DevTools Protocol<br />WebSocket 직접 통신</td>
                <td>저수준 제어<br />네트워크 감시 가능</td>
                <td>Chrome 전용<br />복잡한 API</td>
              </tr>
              <tr>
                <td><strong style={{ color: '#059669' }}>Playwright</strong></td>
                <td>브라우저 엔진 직접 제어<br />고수준 API</td>
                <td>멀티브라우저<br />자동 대기, 안정적</td>
                <td>별도 브라우저 설치</td>
              </tr>
              <tr>
                <td><strong style={{ color: '#7c3aed' }}>COM</strong></td>
                <td>Windows COM 자동화</td>
                <td>레거시 시스템 대응</td>
                <td>Windows 전용, 구식</td>
              </tr>
              <tr>
                <td><strong style={{ color: '#ea580c' }}>iframe</strong></td>
                <td>웹 내 임베디드 프레임</td>
                <td>기존 웹 앱 재사용</td>
                <td>CORS/보안 제약</td>
              </tr>
            </tbody>
          </table>
        </motion.div>
      </div>
    </div>
  );
}
