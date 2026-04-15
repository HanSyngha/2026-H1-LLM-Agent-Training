const buttonStyle = {
  display: 'inline-block',
  padding: '8px 20px',
  borderRadius: 10,
  background: '#2563eb',
  color: '#fff',
  textDecoration: 'none',
  fontWeight: 700,
  fontSize: '.9em',
  flexShrink: 0,
  boxShadow: '0 10px 24px rgba(37,99,235,.18)',
};

const noticeStyle = {
  display: 'inline-flex',
  alignItems: 'center',
  minHeight: 38,
  padding: '8px 14px',
  borderRadius: 10,
  background: 'rgba(15,23,42,.05)',
  color: '#475569',
  fontSize: '.82em',
  fontWeight: 600,
};

export default function LabDownloadButton({
  href,
  label = '📦 다운로드',
  slideRuntime,
  style,
}) {
  const downloadsEnabled = slideRuntime ? slideRuntime.downloadsEnabled : true;
  const offlineArchive = slideRuntime?.offlineArchive ?? false;

  if (offlineArchive) {
    return (
      <div style={noticeStyle}>
        오프라인 보관본에서는 실습 코드 다운로드가 비활성화됩니다.
      </div>
    );
  }

  if (!downloadsEnabled) {
    return (
      <div style={noticeStyle}>
        강사가 자유 탐색을 열면 다운로드 버튼이 표시됩니다.
      </div>
    );
  }

  return (
    <a href={href} download style={{ ...buttonStyle, ...style }}>
      {label}
    </a>
  );
}
