import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar.jsx';
import Landing from './pages/Landing.jsx';
import Login from './pages/Login.jsx';
import PublisherDashboard from './pages/PublisherDashboard.jsx';
import AdvertiserDashboard from './pages/AdvertiserDashboard.jsx';
import CampaignCreate from './pages/CampaignCreate.jsx';
import CampaignEdit from './pages/CampaignEdit.jsx';
import Settings from './pages/Settings.jsx';
import NotFound from './pages/NotFound.jsx';

export default function App() {
  return (
    <BrowserRouter>
      <div style={{ minHeight: '100vh', background: 'var(--bg-main)' }}>
        <Routes>
          <Route path="/" element={<Landing />} />
          <Route path="/login" element={<Login />} />
          <Route path="/publisher/*" element={<PublisherDashboard />} />
          <Route path="/advertiser/*" element={<AdvertiserDashboard />} />
          <Route path="/advertiser/campaigns/new" element={<CampaignCreate />} />
          <Route path="/advertiser/campaigns/:id/edit" element={<CampaignEdit />} />
          <Route path="/settings" element={<Settings />} />
          <Route path="*" element={<NotFound />} />
        </Routes>
      </div>
    </BrowserRouter>
  );
}
