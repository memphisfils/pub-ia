import React from 'react';

export default function Settings() {
  const [user, setUser] = React.useState(null);

  React.useEffect(() => {
    fetch('/auth/me', { credentials: 'include' })
      .then((response) => (response.ok ? response.json() : null))
      .then((data) => setUser(data))
      .catch(() => {});
  }, []);

  if (!user) return <div style={{ padding: '40px', textAlign: 'center' }}>Chargement...</div>;

  return (
    <div style={{ padding: '40px', maxWidth: '600px' }}>
      <h1 style={{ fontSize: '28px', fontWeight: 700, marginBottom: '32px' }}>Paramètres</h1>
      <div className="card" style={{ marginBottom: '24px' }}>
        <h2 style={{ fontSize: '18px', fontWeight: 600, marginBottom: '16px' }}>Profil</h2>
        <div className="form-group">
          <span className="label">Nom</span>
          <div style={{ fontSize: '16px' }}>{user.name}</div>
        </div>
        <div className="form-group">
          <span className="label">Email</span>
          <div style={{ fontSize: '16px' }}>{user.email}</div>
        </div>
        <div className="form-group">
          <span className="label">Rôle</span>
          <div style={{ fontSize: '16px', textTransform: 'capitalize' }}>{user.role}</div>
        </div>
        <div className="form-group">
          <span className="label">Plan</span>
          <div style={{ fontSize: '16px', textTransform: 'capitalize' }}>{user.plan}</div>
        </div>
      </div>
    </div>
  );
}
