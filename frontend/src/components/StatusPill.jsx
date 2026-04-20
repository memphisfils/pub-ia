import React from 'react';

export default function StatusPill({ status }) {
  const colors = {
    active: { bg: 'var(--success-l)', color: 'var(--success)' },
    draft: { bg: 'var(--warning-l)', color: 'var(--warning)' },
    paused: { bg: 'var(--accent-l)', color: 'var(--accent)' },
    completed: { bg: 'var(--bg-main)', color: 'var(--text-muted)' },
  };
  const { bg, color } = colors[status] || colors.draft;
  return (
    <span style={{ display: 'inline-block', padding: '4px 12px', borderRadius: '100px', fontSize: '12px', fontWeight: 600, background: bg, color, textTransform: 'capitalize' }}>
      {status}
    </span>
  );
}
