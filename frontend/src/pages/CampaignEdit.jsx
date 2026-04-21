import React from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import Sidebar from '../components/Sidebar.jsx';
import AdPreview from '../components/AdPreview.jsx';
import { getCategoryLabel } from '../lib/categories.js';
import api from '../services/api.js';

export default function CampaignEdit() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [campaign, setCampaign] = React.useState(null);
  const [creatives, setCreatives] = React.useState([]);
  const [newCreative, setNewCreative] = React.useState({ headline: '', body: '', cta_text: '', cta_url: '' });

  React.useEffect(() => {
    load();
  }, [id]);

  async function load() {
    try {
      const [cRes, crRes] = await Promise.all([
        api.get(`/advertiser/campaigns/${id}`),
        api.get(`/advertiser/campaigns/${id}/creatives`),
      ]);
      setCampaign(cRes.data);
      setCreatives(crRes.data);
    } catch (e) { console.error(e); }
  }

  async function createCreative(e) {
    e.preventDefault();
    try {
      await api.post(`/advertiser/campaigns/${id}/creatives`, newCreative);
      setNewCreative({ headline: '', body: '', cta_text: '', cta_url: '' });
      load();
    } catch (e) { console.error(e); }
  }

  async function pauseCampaign() {
    await api.post(`/advertiser/campaigns/${id}/pause`);
    load();
  }

  async function resumeCampaign() {
    await api.post(`/advertiser/campaigns/${id}/resume`);
    load();
  }

  if (!campaign) return <div style={{ padding: '40px', textAlign: 'center' }}>Chargement...</div>;

  return (
    <div style={{ display: 'flex', minHeight: '100vh' }}>
      <Sidebar role="advertiser" />
      <main style={{ flex: 1, padding: '40px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '32px' }}>
          <div>
            <h1 style={{ fontSize: '24px', fontWeight: 700 }}>{campaign.name}</h1>
            <span style={{ color: 'var(--text-secondary)' }}>{getCategoryLabel(campaign.category)}</span>
          </div>
          <div style={{ display: 'flex', gap: '12px' }}>
            {campaign.status === 'active'
              ? <button className="btn btn-secondary" onClick={pauseCampaign}>Pause</button>
              : <button className="btn btn-primary" onClick={resumeCampaign}>Reprendre</button>
            }
          </div>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '24px' }}>
          <div>
            <div className="card" style={{ marginBottom: '24px' }}>
              <h3 style={{ fontSize: '16px', fontWeight: 600, marginBottom: '20px' }}>Créatives</h3>
              <form onSubmit={createCreative} style={{ marginBottom: '20px' }}>
                <div className="form-group"><input placeholder="Headline" value={newCreative.headline} onChange={e => setNewCreative({ ...newCreative, headline: e.target.value })} required /></div>
                <div className="form-group"><input placeholder="Body" value={newCreative.body} onChange={e => setNewCreative({ ...newCreative, body: e.target.value })} required /></div>
                <div className="form-group"><input placeholder="CTA text" value={newCreative.cta_text} onChange={e => setNewCreative({ ...newCreative, cta_text: e.target.value })} /></div>
                <div className="form-group"><input placeholder="CTA URL" value={newCreative.cta_url} onChange={e => setNewCreative({ ...newCreative, cta_url: e.target.value })} required /></div>
                <button type="submit" className="btn btn-primary" style={{ width: '100%' }}>+ Ajouter créative</button>
              </form>
              {creatives.map(cr => (
                <div key={cr.id} style={{ padding: '12px', border: '1px solid var(--border)', borderRadius: 'var(--radius)', marginBottom: '8px' }}>
                  <div style={{ fontWeight: 600, fontSize: '14px' }}>{cr.headline}</div>
                  <div style={{ fontSize: '13px', color: 'var(--text-secondary)' }}>{cr.body}</div>
                </div>
              ))}
            </div>
          </div>
          <div>
            <AdPreview creative={creatives[0] || newCreative} />
          </div>
        </div>
      </main>
    </div>
  );
}
