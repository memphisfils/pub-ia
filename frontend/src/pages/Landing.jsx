import React from 'react';
import { Link } from 'react-router-dom';

export default function Landing() {
  return (
    <div style={{ minHeight: '100vh' }}>
      <nav style={{ padding: '20px 40px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px solid var(--border)', background: 'var(--bg-card)' }}>
        <div style={{ fontSize: '20px', fontWeight: 700, color: 'var(--accent)' }}>Pub-IA</div>
        <div style={{ display: 'flex', gap: '12px' }}>
          <Link to="/login"><button className="btn btn-secondary">Connexion</button></Link>
          <Link to="/advertiser/campaigns/new"><button className="btn btn-primary">Créer une campagne</button></Link>
        </div>
      </nav>

      <section style={{ textAlign: 'center', padding: '120px 40px' }}>
        <h1 style={{ fontSize: '48px', fontWeight: 700, marginBottom: '16px', color: 'var(--text-primary)' }}>
          Monétisez vos apps IA
        </h1>
        <p style={{ fontSize: '20px', color: 'var(--text-secondary)', maxWidth: '600px', margin: '0 auto 40px' }}>
          Pub-IA est l'infrastructure publicitaire native pour les chatbots conversationnels.
          Gagnez 70% du CPM sur chaque intention d'achat détectée.
        </p>
        <div style={{ display: 'flex', gap: '16px', justifyContent: 'center' }}>
          <Link to="/login"><button className="btn btn-primary" style={{ padding: '14px 32px', fontSize: '16px' }}>Démarrer gratuitement</button></Link>
        </div>
      </section>

      <section style={{ padding: '80px 40px', background: 'var(--bg-card)', borderTop: '1px solid var(--border)' }}>
        <h2 style={{ fontSize: '32px', fontWeight: 700, textAlign: 'center', marginBottom: '48px' }}>Comment ça marche</h2>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '40px', maxWidth: '1000px', margin: '0 auto' }}>
          {[
            { step: '01', title: 'Intégrez le SDK', desc: '15 minutes d\'intégration avec notre SDK JavaScript ou Python.' },
            { step: '02', title: 'Détection automatique', desc: 'Notre IA détecte les intentions d\'achat en temps réel.' },
            { step: '03', title: 'Gagnez de l\'argent', desc: 'Recevez 70% du CPM sur chaque annonce servie.' },
          ].map(item => (
            <div key={item.step} style={{ textAlign: 'center' }}>
              <div style={{ fontSize: '48px', fontWeight: 700, color: 'var(--accent)', marginBottom: '12px' }}>{item.step}</div>
              <h3 style={{ fontSize: '18px', fontWeight: 600, marginBottom: '8px' }}>{item.title}</h3>
              <p style={{ color: 'var(--text-secondary)', fontSize: '14px' }}>{item.desc}</p>
            </div>
          ))}
        </div>
      </section>

      <footer style={{ padding: '40px', textAlign: 'center', color: 'var(--text-muted)', fontSize: '14px' }}>
        © 2026 Pub-IA · Infrastructure publicitaire pour apps IA
      </footer>
    </div>
  );
}
