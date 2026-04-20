import React from 'react';
import { Link } from 'react-router-dom';

export default function Navbar({ user }) {
  return (
    <nav style={{ padding: '16px 40px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', background: 'var(--bg-card)', borderBottom: '1px solid var(--border)' }}>
      <Link to="/" style={{ fontSize: '18px', fontWeight: 700, color: 'var(--accent)', textDecoration: 'none' }}>Pub-IA</Link>
      <div style={{ display: 'flex', alignItems: 'center', gap: '20px' }}>
        {user ? (
          <>
            {user.role === 'publisher' && <Link to="/publisher" style={{ color: 'var(--text-secondary)', textDecoration: 'none', fontSize: '14px' }}>Dashboard</Link>}
            {user.role === 'advertiser' && <Link to="/advertiser" style={{ color: 'var(--text-secondary)', textDecoration: 'none', fontSize: '14px' }}>Dashboard</Link>}
            <Link to="/settings"><img src={user.avatar_url || 'https://via.placeholder.com/32'} alt="" style={{ width: 32, height: 32, borderRadius: '50%' }} /></Link>
          </>
        ) : (
          <Link to="/login"><button className="btn btn-primary" style={{ padding: '8px 16px' }}>Connexion</button></Link>
        )}
      </div>
    </nav>
  );
}
