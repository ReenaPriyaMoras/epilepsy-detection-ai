import React, { useState, useEffect } from 'react';
import { Settings as SettingsIcon, Server, Cpu, Link, Palette, Info, CheckCircle2, XCircle } from 'lucide-react';
import axios from 'axios';

const Settings = () => {
  const [status, setStatus] = useState('Checking...');
  
  useEffect(() => {
    const checkHealth = async () => {
      try {
        const API_URL =
          import.meta.env.VITE_API_URL?.replace("/api/v1","")
          || "http://localhost:8000";

        await axios.get(`${API_URL}/health`);
        setStatus('Online');
      } catch (e) {
        setStatus('Offline');
      }
    };
    checkHealth();
  }, []);

  const cards = [
    { title: "Application Version", value: "v2.0.0-stable", icon: Info },
    { title: "Model Version", value: "EpiEEG GNN-BiLSTM (Release 1)", icon: Cpu },
    { title: "Backend Status", value: status, icon: Server, highlight: status === 'Online' },
    { title: "Frontend Status", value: "Online", icon: CheckCircle2, highlight: true },
    { title: "API URL", value: "http://localhost:8000/api/v1", icon: Link },
    { title: "Theme", value: "Light (Default)", icon: Palette },
    { title: "About Project", value: "Epilepsy Detection AI", icon: Info }
  ];

  return (
    <div className="max-w-7xl mx-auto space-y-6 animate-in fade-in duration-500 pb-12">
      <div className="flex items-center gap-3 bg-white p-6 rounded-2xl border border-slate-200 shadow-sm">
        <SettingsIcon className="w-8 h-8 text-blue-600" />
        <h1 className="text-2xl font-bold text-slate-800">System Settings</h1>
      </div>

      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        {cards.map((card, i) => {
          const Icon = card.icon;
          return (
            <div key={i} className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm flex items-start gap-4">
              <div className={`p-3 rounded-xl ${card.highlight ? 'bg-emerald-100 text-emerald-600' : card.highlight === false ? 'bg-red-100 text-red-600' : 'bg-slate-100 text-slate-600'}`}>
                <Icon className="w-6 h-6" />
              </div>
              <div>
                <h3 className="text-sm font-bold text-slate-500 uppercase tracking-wider">{card.title}</h3>
                <p className={`mt-1 font-semibold ${card.highlight ? 'text-emerald-600' : card.highlight === false ? 'text-red-600' : 'text-slate-800'}`}>
                  {card.value}
                </p>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default Settings;
