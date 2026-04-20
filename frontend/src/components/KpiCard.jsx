import React from 'react';

export default function KpiCard({ label, value, trend }) {
  const trendColor = trend && trend.startsWith('+') ? 'var(--success)' : 'var(--danger)';
  return (
    <div className="card">
      <span className="label">{label}</span>
      <div style={{ fontSize: '32px', fontWeight: 700, marginTop: '8px', color: 'var(--text-primary)' }}>{value}</div>
      {trend && <div style={{ fontSize: '13px', fontWeight: 600, color: trendColor, marginTop: '4px' }}>{trend}</div>}
    </div>
  );
}
