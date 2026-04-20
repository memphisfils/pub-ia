import React from 'react';

export default function AdPreview({ creative }) {
  if (!creative || !creative.headline) return null;
  return (
    <div className="card">
      <span className="label" style={{ marginBottom: '16px', display: 'block' }}>Aperçu de l'annonce</span>
      <div style={{ background: 'var(--bg-main)', padding: '16px', borderRadius: 'var(--radius)', border: '1px solid var(--border)' }}>
        <div style={{ fontSize: '12px', color: 'var(--text-muted)', marginBottom: '8px' }}>💡 Sponsorisé</div>
        <div style={{ fontWeight: 600, marginBottom: '4px' }}>{creative.headline}</div>
        <div style={{ fontSize: '14px', color: 'var(--text-secondary)', marginBottom: '12px' }}>{creative.body}</div>
        <a href={creative.cta_url || '#'} style={{ display: 'inline-block', padding: '8px 16px', background: 'var(--accent)', color: 'white', borderRadius: 'var(--radius)', fontSize: '13px', fontWeight: 500, textDecoration: 'none' }}>
          {creative.cta_text || 'En savoir plus'}
        </a>
      </div>
    </div>
  );
}
