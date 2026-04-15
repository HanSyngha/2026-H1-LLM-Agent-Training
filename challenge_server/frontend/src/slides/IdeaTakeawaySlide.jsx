import { motion } from 'framer-motion';
import { Badge, SlideH2, Divider, Grid, Box, BoxTitle, Quote } from './SlideLayout';

function BulletList({ items }) {
  return (
    <ul style={{ margin: 0, paddingLeft: '1.1em', lineHeight: 1.8, fontSize: '.9em', color: '#334155' }}>
      {items.map((item) => (
        <li key={item} style={{ marginBottom: 4 }}>{item}</li>
      ))}
    </ul>
  );
}

function IdeaTakeawaySlide({
  badge = '실습 회고',
  title,
  lead,
  ideaTitle = '가져갈 아이디어',
  ideaPoints = [],
  antiTitle = '버려야 할 오해',
  antiPoints = [],
  applyTitle = '실무 전환 포인트',
  applyPoints = [],
  closing,
  accent = '#2563eb',
  day2 = false,
}) {
  return (
    <div className="slide-container">
      <div className="slide-inner">
        <Badge variant={day2 ? 'day2' : 'day1'}>{badge}</Badge>
        <SlideH2 day2={day2}>{title}</SlideH2>
        <Divider />

        {lead && (
          <motion.p
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.15 }}
            style={{ fontSize: '1em', color: '#334155', marginBottom: 8 }}
          >
            {lead}
          </motion.p>
        )}

        <Grid cols={3} gap={16}>
          <motion.div initial={{ opacity: 0, y: 18 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.22 }}>
            <Box color="blue" style={{ height: '100%' }}>
              <BoxTitle color={accent}>{ideaTitle}</BoxTitle>
              <BulletList items={ideaPoints} />
            </Box>
          </motion.div>

          <motion.div initial={{ opacity: 0, y: 18 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.32 }}>
            <Box color="red" style={{ height: '100%' }}>
              <BoxTitle color="#dc2626">{antiTitle}</BoxTitle>
              <BulletList items={antiPoints} />
            </Box>
          </motion.div>

          <motion.div initial={{ opacity: 0, y: 18 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.42 }}>
            <Box color="green" style={{ height: '100%' }}>
              <BoxTitle color="#059669">{applyTitle}</BoxTitle>
              <BulletList items={applyPoints} />
            </Box>
          </motion.div>
        </Grid>

        {closing && (
          <motion.div initial={{ opacity: 0, y: 18 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.5 }}>
            <Quote borderColor={accent}>
              <span style={{ fontStyle: 'normal' }}>{closing}</span>
            </Quote>
          </motion.div>
        )}
      </div>
    </div>
  );
}

export function createIdeaTakeawaySlide(config) {
  function GeneratedIdeaTakeawaySlide() {
    return <IdeaTakeawaySlide {...config} />;
  }

  GeneratedIdeaTakeawaySlide.displayName = `IdeaTakeaway_${config.title || 'Slide'}`;
  return GeneratedIdeaTakeawaySlide;
}

export default IdeaTakeawaySlide;
