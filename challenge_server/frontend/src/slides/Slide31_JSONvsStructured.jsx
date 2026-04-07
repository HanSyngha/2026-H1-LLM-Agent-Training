import { motion } from 'framer-motion';
import { Badge, SlideH2, Divider } from './SlideLayout';

export default function Slide31_JSONvsStructured() {
  return (
    <div className="slide-container">
      <div className="slide-inner">
        <Badge variant="day1">Structured Output</Badge>
        <SlideH2>JSON mode vs Structured Output</SlideH2>
        <Divider />

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}>
          <table style={{ marginTop: 16 }}>
            <thead>
              <tr>
                <th></th>
                <th>JSON Mode</th>
                <th>Structured Output</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td><strong>보장 수준</strong></td>
                <td>JSON 형태만 보장<br />스키마 준수 X</td>
                <td>JSON Schema 완전 준수<br />100% 보장</td>
              </tr>
              <tr>
                <td><strong>설정 방법</strong></td>
                <td style={{ fontFamily: 'monospace', fontSize: '.85em' }}>
                  response_format=<br />{`{"type":"json_object"}`}
                </td>
                <td style={{ fontFamily: 'monospace', fontSize: '.85em' }}>
                  response_format=<br />{`{"type":"json_schema",...}`}
                </td>
              </tr>
              <tr>
                <td><strong>활용</strong></td>
                <td>간단한 JSON 응답</td>
                <td>복잡한 구조화 데이터 추출</td>
              </tr>
              <tr>
                <td><strong>신뢰도</strong></td>
                <td style={{ color: '#d97706' }}>중간</td>
                <td style={{ color: '#059669' }}>높음</td>
              </tr>
            </tbody>
          </table>
        </motion.div>
      </div>
    </div>
  );
}
