import React from 'react';
import { useNavigate } from 'react-router-dom';

import { CATEGORY_OPTIONS } from '../lib/categories.js';
import api from '../services/api.js';

export default function CampaignCreate() {
  const navigate = useNavigate();
  const [form, setForm] = React.useState({
    name: '',
    category: '',
    budget_total: '',
    bid_cpm: '',
  });

  async function handleSubmit(e) {
    e.preventDefault();
    try {
      const res = await api.post('/advertiser/campaigns', form);
      navigate(`/advertiser/campaigns/${res.data.id}/edit`);
    } catch (error) {
      console.error(error);
    }
  }

  return (
    <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '40px' }}>
      <div className="card" style={{ width: '100%', maxWidth: '600px' }}>
        <h1 style={{ fontSize: '24px', fontWeight: 700, marginBottom: '24px' }}>Nouvelle campagne</h1>
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <span className="label">Nom de la campagne</span>
            <input
              value={form.name}
              onChange={(e) => setForm({ ...form, name: e.target.value })}
              required
              placeholder="Ma campagne beauté"
            />
          </div>
          <div className="form-group">
            <span className="label">Catégorie</span>
            <select
              value={form.category}
              onChange={(e) => setForm({ ...form, category: e.target.value })}
              required
            >
              <option value="">Sélectionner une catégorie</option>
              {CATEGORY_OPTIONS.map(({ value, label }) => (
                <option key={value} value={value}>{label}</option>
              ))}
            </select>
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
            <div className="form-group">
              <span className="label">Budget total (EUR)</span>
              <input
                type="number"
                value={form.budget_total}
                onChange={(e) => setForm({ ...form, budget_total: e.target.value })}
                required
                min="0"
                step="0.01"
              />
            </div>
            <div className="form-group">
              <span className="label">Bid CPM (EUR)</span>
              <input
                type="number"
                value={form.bid_cpm}
                onChange={(e) => setForm({ ...form, bid_cpm: e.target.value })}
                min="0"
                step="0.01"
              />
            </div>
          </div>
          <div style={{ display: 'flex', gap: '12px', justifyContent: 'flex-end' }}>
            <button type="button" className="btn btn-secondary" onClick={() => navigate(-1)}>Annuler</button>
            <button type="submit" className="btn btn-primary">Créer</button>
          </div>
        </form>
      </div>
    </div>
  );
}
