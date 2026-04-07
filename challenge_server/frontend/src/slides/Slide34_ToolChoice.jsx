import { motion } from 'framer-motion';
import { Badge, SlideH2, Divider } from './SlideLayout';

export default function Slide34_ToolChoice() {
  return (
    <div className="slide-container">
      <div className="slide-inner">
        <Badge variant="day1">Structured Output</Badge>
        <SlideH2>tool_choice 옵션</SlideH2>
        <Divider />

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}>
          <table style={{ marginTop: 16 }}>
            <thead>
              <tr>
                <th>옵션</th>
                <th>동작</th>
                <th>사용 시기</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td><code style={{ color: '#2563eb' }}>"auto"</code></td>
                <td>LLM이 알아서 판단<br />Tool 호출 or 텍스트 응답</td>
                <td>일반적인 대화형 Agent</td>
              </tr>
              <tr>
                <td><code style={{ color: '#059669' }}>"required"</code></td>
                <td>반드시 하나 이상의 Tool 호출<br />텍스트만 응답 불가</td>
                <td>무조건 액션이 필요한 경우</td>
              </tr>
              <tr>
                <td><code style={{ color: '#dc2626' }}>"none"</code></td>
                <td>Tool 호출 금지<br />텍스트 응답만 가능</td>
                <td>최종 답변 생성 단계</td>
              </tr>
              <tr>
                <td>
                  <code style={{ color: '#7c3aed', fontSize: '.85em' }}>
                    {`{"type":"function",`}<br />{`"function":{"name":"X"}}`}
                  </code>
                </td>
                <td>특정 Tool만 호출 강제</td>
                <td>확정된 워크플로우</td>
              </tr>
            </tbody>
          </table>
        </motion.div>
      </div>
    </div>
  );
}
