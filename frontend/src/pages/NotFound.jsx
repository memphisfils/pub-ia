import React from 'react';
import { Link } from 'react-router-dom';

export default function NotFound() {
  return (
    <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', textAlign: 'center' }}>
      <div>
        <h1 style={{ fontSize: '64px', fontWeight: 700, color: 'var(--accent)', marginBottom: '16px' }}>404</h1>
        <h2 style={{ fontSize: '24px', fontWeight: 600, marginBottom: '8px' }}>Page non trouvée</h2>
        <p style={{ color: 'var(--text-secondary)', marginBottom: '24px' }}>Cette page n'existe pas.</p>
        <Link to="/"><button className="btn btn-primary">Retour à l'accueil</button></Link>
      </div>
    </div>
  );
}
