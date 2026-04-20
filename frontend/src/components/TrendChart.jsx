import React from 'react';
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';

// Données par défaut si aucune data n'est fournie
const defaultData = [
  { day: 'Jan', value: 120 },
  { day: 'Fév', value: 180 },
  { day: 'Mar', value: 240 },
  { day: 'Avr', value: 300 },
];

/**
 * TrendChart - Graphique de tendance avec Recharts
 * 
 * @param {Object} props
 * @param {string} props.title - Titre du graphique
 * @param {Array} props.data - Données dynamiques [{day: string, value: number, ...}]
 * @param {string} props.dataKey - Clé des données à afficher (par défaut: "value")
 * @param {string} props.strokeColor - Couleur de la ligne (par défaut: "#0077CC")
 * @param {number} props.height - Hauteur du graphique (par défaut: 200)
 */
export default function TrendChart({ 
  title, 
  data = defaultData, 
  dataKey = "value",
  strokeColor = "#0077CC",
  height = 200 
}) {
  const chartData = data && data.length > 0 ? data : defaultData;

  return (
    <div className="card">
      <span className="label" style={{ marginBottom: '16px', display: 'block' }}>{title || 'Tendance'}</span>
      <ResponsiveContainer width="100%" height={height}>
        <LineChart data={chartData}>
          <XAxis 
            dataKey="day" 
            tick={{ fontSize: 12, fill: '#64748B' }} 
            axisLine={false} 
            tickLine={false} 
          />
          <YAxis 
            tick={{ fontSize: 12, fill: '#64748B' }} 
            axisLine={false} 
            tickLine={false} 
          />
          <Tooltip 
            contentStyle={{ 
              background: '#FFFFFF', 
              border: '1px solid #E1E8F0', 
              borderRadius: '8px',
              boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.05)'
            }} 
          />
          <Line 
            type="monotone" 
            dataKey={dataKey} 
            stroke={strokeColor} 
            strokeWidth={2} 
            dot={false} 
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
