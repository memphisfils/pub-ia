import React from 'react';
import { Link, useLocation } from 'react-router-dom';

export default function Sidebar({ role }) {
  const location = useLocation();
  const isActive = (path) => location.pathname === path || location.pathname.startsWith(path + '/');

  const publisherLinks = [
    { path: '/publisher', label: 'Dashboard', icon: '📊' },
    { path: '/publisher/analytics', label: 'Analytics', icon: '📈' },
    { path: '/publisher/revenue', label: 'Revenus', icon: '💶' },
    { path: '/settings', label: 'Paramètres', icon: '⚙️' },
  ];

  const advertiserLinks = [
    { path: '/advertiser', label: 'Dashboard', icon: '📊' },
    { path: '/advertiser/budget', label: 'Budget', icon: '💰' },
    { path: '/settings', label: 'Paramètres', icon: '⚙️' },
  ];

  const links = role === 'publisher' ? publisherLinks : advertiserLinks;

  return (
    <aside style={{ width: '240px', background: 'var(--bg-card)', borderRight: '1px solid var(--border)', padding: '24px 0', flexShrink: 0 }}>
      <div style={{ padding: '0 20px', marginBottom: '24px' }}>
        <div style={{ fontSize: '18px', fontWeight: 700, color: 'var(--accent)' }}>Pub-IA</div>
      </div>
      <nav>
        {links.map(link => (
          <Link
            key={link.path}
            to={link.path}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '10px',
              padding: '12px 20px',
              color: isActive(link.path) ? 'var(--accent)' : 'var(--text-secondary)',
              background: isActive(link.path) ? 'var(--accent-l)' : 'transparent',
              textDecoration: 'none',
              fontSize: '14px',
              fontWeight: isActive(link.path) ? 600 : 400,
              borderLeft: isActive(link.path) ? '3px solid var(--accent)' : '3px solid transparent',
              transition: '150ms ease',
            }}
          >
            <span>{link.icon}</span>
            {link.label}
          </Link>
        ))}
      </nav>
    </aside>
  );
}
