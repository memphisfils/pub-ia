import React from 'react';
import { Link } from 'react-router-dom';
import Sidebar from '../components/Sidebar.jsx';
import KpiCard from '../components/KpiCard.jsx';
import TrendChart from '../components/TrendChart.jsx';
import ApiKeyCard from '../components/ApiKeyCard.jsx';
import api from '../services/api.js';

export default function PublisherDashboard() {
  const [apps, setApps] = React.useState([]);
  const [analytics, setAnalytics] = React.useState({ impressions: 0, revenue: 0, ecpm: 0 });
  const [showCreate, setShowCreate] = React.useState(false);
  const [newAppName, setNewAppName] = React.useState('');

  React.useEffect(() => {
    loadData();
  }, []);

  async function loadData() {
    try {
      const [appsRes, analyticsRes] = await Promise.all([
        api.get('/publisher/apps'),
        api.get('/publisher/analytics'),
      ]);
      setApps(appsRes.data);
      setAnalytics(analyticsRes.data);
    } catch (e) {
      console.error(e);
    }
  }

  async function createApp(e) {
    e.preventDefault();
    try {
      await api.post('/publisher/apps', { name: newAppName });
      setNewAppName('');
      setShowCreate(false);
      loadData();
    } catch (e) {
      console.error(e);
    }
  }

  return (
    <div style={{ display: 'flex', minHeight: '100vh' }}>
      <Sidebar role="publisher" />
      <main style={{ flex: 1, padding: '40px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '32px' }}>
          <h1 style={{ fontSize: '28px', fontWeight: 700 }}>Publisher Dashboard</h1>
          <button className="btn btn-primary" onClick={() => setShowCreate(true)}>+ Nouvelle app</button>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '20px', marginBottom: '40px' }}>
          <KpiCard label="Revenus" value={`${analytics.revenue.toFixed(2)} €`} trend="+12%" />
          <KpiCard label="Impressions" value={analytics.impressions.toLocaleString()} trend="+8%" />
          <KpiCard label="eCPM" value={`${analytics.ecpm.toFixed(2)} €`} trend="+3%" />
        </div>

        {showCreate && (
          <div className="card" style={{ marginBottom: '24px' }}>
            <h3 style={{ fontSize: '16px', fontWeight: 600, marginBottom: '16px' }}>Créer une app</h3>
            <form onSubmit={createApp} style={{ display: 'flex', gap: '12px' }}>
              <input
                placeholder="Nom de l'application"
                value={newAppName}
                onChange={e => setNewAppName(e.target.value)}
                required
                style={{ flex: 1 }}
              />
              <button type="submit" className="btn btn-primary">Créer</button>
              <button type="button" className="btn btn-secondary" onClick={() => setShowCreate(false)}>Annuler</button>
            </form>
          </div>
        )}

        <div className="card">
          <h3 style={{ fontSize: '16px', fontWeight: 600, marginBottom: '20px' }}>Vos applications</h3>
          {apps.length === 0 ? (
            <p style={{ color: 'var(--text-muted)' }}>Aucune application. Créez votre première app pour commencer.</p>
          ) : (
            <div style={{ display: 'grid', gap: '16px' }}>
              {apps.map(app => (
                <div key={app.id} style={{ padding: '16px', border: '1px solid var(--border)', borderRadius: 'var(--radius)' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <div>
                      <div style={{ fontWeight: 600 }}>{app.name}</div>
                      <div style={{ fontSize: '12px', color: 'var(--text-muted)' }}>{app.description || 'Aucune description'}</div>
                    </div>
                    <ApiKeyCard apiKey={app.api_key} />
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
