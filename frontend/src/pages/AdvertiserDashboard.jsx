import React from 'react';
import { Link } from 'react-router-dom';
import Sidebar from '../components/Sidebar.jsx';
import KpiCard from '../components/KpiCard.jsx';
import StatusPill from '../components/StatusPill.jsx';
import { getCategoryLabel } from '../lib/categories.js';
import api from '../services/api.js';

export default function AdvertiserDashboard() {
  const [campaigns, setCampaigns] = React.useState([]);

  React.useEffect(() => {
    api.get('/advertiser/campaigns').then(r => setCampaigns(r.data)).catch(console.error);
  }, []);

  return (
    <div style={{ display: 'flex', minHeight: '100vh' }}>
      <Sidebar role="advertiser" />
      <main style={{ flex: 1, padding: '40px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '32px' }}>
          <h1 style={{ fontSize: '28px', fontWeight: 700 }}>Mes campagnes</h1>
          <Link to="/advertiser/campaigns/new"><button className="btn btn-primary">+ Nouvelle campagne</button></Link>
        </div>

        <div className="card">
          {campaigns.length === 0 ? (
            <p style={{ color: 'var(--text-muted)' }}>Aucune campagne. Créez votre première campagne pour commencer.</p>
          ) : (
            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
              <thead>
                <tr style={{ borderBottom: '1px solid var(--border)' }}>
                  <th style={{ textAlign: 'left', padding: '12px 0', fontSize: '11px', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.06em', color: 'var(--text-secondary)' }}>Nom</th>
                  <th style={{ textAlign: 'left', padding: '12px 0', fontSize: '11px', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.06em', color: 'var(--text-secondary)' }}>Catégorie</th>
                  <th style={{ textAlign: 'left', padding: '12px 0', fontSize: '11px', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.06em', color: 'var(--text-secondary)' }}>Statut</th>
                  <th style={{ textAlign: 'right', padding: '12px 0', fontSize: '11px', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.06em', color: 'var(--text-secondary)' }}>Budget</th>
                </tr>
              </thead>
              <tbody>
                {campaigns.map(c => (
                  <tr key={c.id} style={{ borderBottom: '1px solid var(--border)' }}>
                    <td style={{ padding: '16px 0' }}>
                      <Link to={`/advertiser/campaigns/${c.id}/edit`} style={{ fontWeight: 500 }}>{c.name}</Link>
                    </td>
                    <td style={{ padding: '16px 0', color: 'var(--text-secondary)' }}>{getCategoryLabel(c.category)}</td>
                    <td style={{ padding: '16px 0' }}><StatusPill status={c.status} /></td>
                    <td style={{ padding: '16px 0', textAlign: 'right' }}>{c.budget_spent} € / {c.budget_total} €</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </main>
    </div>
  );
}
