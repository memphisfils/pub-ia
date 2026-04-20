import React from 'react';
import { useNavigate } from 'react-router-dom';

export default function Login() {
  const navigate = useNavigate();

  const handleGoogleLogin = () => {
    window.location.href = '/auth/google';
  };

  return (
    <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
      <div className="card" style={{ width: '100%', maxWidth: '400px', textAlign: 'center' }}>
        <h1 style={{ fontSize: '28px', fontWeight: 700, marginBottom: '8px' }}>Connexion</h1>
        <p style={{ color: 'var(--text-secondary)', marginBottom: '32px' }}>Connectez-vous avec votre compte Google</p>
        <button onClick={handleGoogleLogin} className="btn btn-primary" style={{ width: '100%', padding: '14px', fontSize: '16px' }}>
          Se connecter avec Google
        </button>
      </div>
    </div>
  );
}
