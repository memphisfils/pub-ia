import React from 'react';

export default function ApiKeyCard({ apiKey }) {
  const [copied, setCopied] = React.useState(false);

  async function copy() {
    await navigator.clipboard.writeText(apiKey);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  }

  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
      <code style={{ fontSize: '12px', background: 'var(--bg-main)', padding: '4px 8px', borderRadius: '4px', fontFamily: 'monospace' }}>
        {apiKey ? apiKey.slice(0, 12) + '...' : 'Pas de clé'}
      </code>
      <button onClick={copy} className="btn btn-secondary" style={{ padding: '4px 12px', fontSize: '12px' }}>
        {copied ? 'Copié!' : 'Copier'}
      </button>
    </div>
  );
}
