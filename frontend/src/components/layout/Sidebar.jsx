import React from 'react';
import { NavLink } from 'react-router-dom';
import { 
  LayoutDashboard, 
  UploadCloud, 
  Activity, 
  History, 
  BookOpen, 
  Settings as SettingsIcon,
  FileSpreadsheet
} from 'lucide-react';

const Sidebar = () => {
  const navItems = [
    { name: 'Dashboard', path: '/dashboard', icon: LayoutDashboard },
    { name: 'Upload EEG', path: '/upload', icon: UploadCloud },
    { name: 'Analysis Results', path: '/result', icon: Activity },
    { name: 'History', path: '/history', icon: History },
    { name: 'Clinical Reports', path: '/reports', icon: FileSpreadsheet },
    { name: 'Documentation', path: '/docs', icon: BookOpen },
    { name: 'Settings', path: '/settings', icon: SettingsIcon }
  ];

  return (
    <aside className="w-64 bg-slate-900 text-slate-300 flex flex-col shadow-2xl z-20 shrink-0 h-full">
      {/* Brand Header */}
      <div className="h-16 flex items-center px-6 border-b border-slate-800 bg-slate-900/50">
        <Activity className="w-6 h-6 text-blue-500 mr-3" />
        <h1 className="text-xl font-bold text-white tracking-wide">
          Epi<span className="text-blue-500">Detect</span> AI
        </h1>
      </div>
      
      {/* Navigation */}
      <nav className="flex-1 overflow-y-auto py-6">
        <ul className="space-y-1.5 px-3">
          {navItems.map((item) => {
            const Icon = item.icon;
            return (
              <li key={item.name}>
                <NavLink
                  to={item.path}
                  className={({ isActive }) =>
                    `flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-200 font-medium text-sm ${
                      isActive 
                        ? 'bg-blue-600 text-white shadow-lg shadow-blue-900/20' 
                        : 'hover:bg-slate-800 hover:text-white text-slate-400'
                    }`
                  }
                >
                  <Icon className="w-5 h-5" />
                  {item.name}
                </NavLink>
              </li>
            );
          })}
        </ul>
      </nav>
      
      {/* Footer System Status */}
      <div className="p-4 border-t border-slate-800 bg-slate-900/50">
        <div className="bg-slate-800/50 rounded-xl p-4 text-xs">
          <p className="font-semibold text-slate-300 mb-2 uppercase tracking-wider text-[10px]">Inference Engine</p>
          <div className="flex items-center justify-between">
            <span className="text-slate-400 font-medium">GNN-BiLSTM</span>
            <div className="flex items-center gap-1.5">
              <span className="relative flex h-2.5 w-2.5">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-emerald-500"></span>
              </span>
              <span className="text-emerald-500 font-medium">Online</span>
            </div>
          </div>
        </div>
      </div>
    </aside>
  );
};

export default Sidebar;
