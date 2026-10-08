import React, { useEffect, useState } from 'react';
import { 
  Download, 
  Users, 
  Clock, 
  Activity, 
  BrainCircuit, 
  AlertTriangle,
  LineChart,
  Loader2,
  ShieldAlert,
  CheckCircle2,
  FileText
} from 'lucide-react';
import { healthcareAPI } from '../services/api';
import toast, { Toaster } from 'react-hot-toast';
import { useNavigate } from 'react-router-dom';

const Dashboard = () => {
  const navigate = useNavigate();
  const [stats, setStats] = useState({
    total_analyses: 0,
    epileptic_cases: 0,
    healthy_cases: 0,
    average_confidence: '--',
    today_analyses: 0,
    total_reports_generated: 0,
    backend_status: 'Checking...',
    last_analysis_time: 'None'
  });
  const [isLoading, setIsLoading] = useState(true);
  const doctorName = localStorage.getItem("doctorName") || "Doctor";

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        const data = await healthcareAPI.getDashboardStats();
        if (data && data.status === 'success') {
          setStats(data);
        } else {
          setStats(prev => ({ ...prev, backend_status: 'Connected' }));
        }
      } catch (error) {
        console.error("Dashboard Stats Fetch Error:", error);
        setStats(prev => ({ ...prev, backend_status: 'Offline' }));
        toast.error("Unable to connect to AI Backend");
      } finally {
        setIsLoading(false);
      }
    };

    fetchDashboardData();
  }, []);

  const isConnected = stats.backend_status === 'Connected';
  const isOffline = stats.backend_status === 'Offline';

  return (
    <div className="space-y-6 animate-in fade-in duration-500">
      <Toaster position="top-right" />
      
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Welcome, {doctorName}</h1>
          <p className="text-sm text-slate-500 mt-1">Real-time overview of clinical EEG analyses and inference metrics.</p>
        </div>
        <div className="flex gap-3">
          <button 
            onClick={() => navigate('/upload')}
            className="inline-flex items-center justify-center gap-2 px-5 py-2.5 bg-blue-600 text-white rounded-xl shadow-sm hover:bg-blue-700 font-bold text-sm transition-all active:scale-[0.98]"
          >
            <Activity className="w-4 h-4" />
            Analyze New EEG
          </button>
          <button 
            onClick={() => navigate('/history')}
            className="inline-flex items-center justify-center gap-2 px-5 py-2.5 bg-white border border-slate-200 text-slate-700 rounded-xl shadow-sm hover:bg-slate-50 hover:border-slate-300 font-medium text-sm transition-all active:scale-[0.98]"
          >
            <FileText className="w-4 h-4 text-slate-500" />
            View Records
          </button>
        </div>
      </div>

      {/* Top Metrics Row */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {[
          { 
            label: 'Total Analyses', 
            value: isLoading ? '--' : stats.total_analyses, 
            trend: `${stats.today_analyses} analyzed today`, 
            icon: Activity, 
            color: 'text-blue-600', 
            bg: 'bg-blue-50' 
          },
          { 
            label: 'Epileptic Detections', 
            value: isLoading ? '--' : stats.epileptic_cases, 
            trend: `${stats.healthy_cases} normal profile`, 
            icon: AlertTriangle, 
            color: 'text-rose-600', 
            bg: 'bg-rose-50' 
          },
          { 
            label: 'Backend Status', 
            value: isLoading ? <Loader2 className="w-6 h-6 animate-spin text-slate-400" /> : stats.backend_status, 
            trend: isOffline ? 'Backend unreachable' : 'GNN-BiLSTM Core Active', 
            icon: BrainCircuit, 
            color: isOffline ? 'text-rose-600' : 'text-emerald-600', 
            bg: isOffline ? 'bg-rose-50' : 'bg-emerald-50' 
          },
          { 
            label: 'Avg Model Confidence', 
            value: isLoading ? '--' : stats.average_confidence, 
            trend: stats.total_analyses > 0 ? 'Computed across database' : 'Awaiting analyses', 
            icon: CheckCircle2, 
            color: 'text-indigo-600', 
            bg: 'bg-indigo-50' 
          },
        ].map((stat, i) => {
          const Icon = stat.icon;
          return (
            <div key={i} className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm relative overflow-hidden group hover:shadow-md transition-shadow">
              <div className="flex justify-between items-start mb-4">
                <div className={`p-2.5 rounded-xl ${stat.bg}`}>
                  <Icon className={`w-5 h-5 ${stat.color}`} />
                </div>
              </div>
              <div className={`text-3xl font-bold tracking-tight mb-1 ${isOffline && i === 2 ? 'text-rose-600' : 'text-slate-900'}`}>
                {stat.value}
              </div>
              <div className="flex items-center justify-between">
                <p className="text-sm font-medium text-slate-600">{stat.label}</p>
                <p className="text-xs text-slate-400">{stat.trend}</p>
              </div>
            </div>
          );
        })}
      </div>

      {/* Main Content Area */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Left Column (Charts/EEG placeholder) */}
        <div className="lg:col-span-2 bg-white border border-slate-200 rounded-2xl shadow-sm p-6 min-h-[450px] flex flex-col relative overflow-hidden">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-lg font-bold text-slate-800 flex items-center gap-2">
              <LineChart className="w-5 h-5 text-slate-400" />
              EEG Multichannel Visualizer
            </h3>
            <span className="text-xs font-semibold px-2.5 py-1 bg-slate-100 text-slate-600 rounded-full">
              43 Channels Standardized
            </span>
          </div>
          
          <div className="flex-1 flex flex-col items-center justify-center bg-slate-50/50 rounded-xl border border-dashed border-slate-200 p-8 text-center">
            <div className="w-16 h-16 bg-white rounded-full flex items-center justify-center shadow-sm mb-4">
              <Activity className="w-8 h-8 text-blue-600" />
            </div>
            <h4 className="text-base font-semibold text-slate-700">Ready for EEG Analysis</h4>
            <p className="text-sm text-slate-500 max-w-sm mt-2 mb-6">
              Upload standardized European Data Format (.edf) recordings to visualize multichannel signals and trigger deep learning inference.
            </p>
            <button
              onClick={() => navigate('/upload')}
              className="px-6 py-2.5 bg-blue-600 text-white font-bold text-sm rounded-xl shadow hover:bg-blue-700 transition-colors"
            >
              Upload EDF File
            </button>
          </div>
        </div>

        {/* Right Column (AI Insights & Diagnostics) */}
        <div className="bg-white border border-slate-200 rounded-2xl shadow-sm flex flex-col">
          <div className="p-6 border-b border-slate-100">
            <h3 className="font-bold text-slate-800 flex items-center gap-2">
              <BrainCircuit className="w-5 h-5 text-blue-500" />
              Clinical System Health
            </h3>
          </div>
          
          <div className="p-6 flex-1 bg-slate-50/30 space-y-6">
            {isOffline && (
              <div className="bg-rose-50 border border-rose-200 rounded-xl p-4 shadow-sm">
                <div className="flex items-start gap-3">
                  <AlertTriangle className="w-5 h-5 text-rose-500 shrink-0 mt-0.5" />
                  <div>
                    <h4 className="text-sm font-bold text-rose-900 mb-1">Backend Disconnected</h4>
                    <p className="text-xs text-rose-700 leading-relaxed">
                      Cannot connect to the FastAPI inference server. Verify server is running on port 8000.
                    </p>
                  </div>
                </div>
              </div>
            )}
            
            <div>
              <div className="flex justify-between items-end mb-2">
                <span className="text-sm font-semibold text-slate-700">Inference Engine Readiness</span>
                <span className="text-lg font-bold text-slate-600">{isConnected ? '100%' : '--%'}</span>
              </div>
              <div className="w-full bg-slate-200 rounded-full h-2.5">
                <div className={`h-2.5 rounded-full ${isConnected ? 'bg-emerald-500' : 'bg-slate-400'}`} style={{ width: isConnected ? '100%' : '0%' }}></div>
              </div>
            </div>

            <div className="pt-4 border-t border-slate-200 space-y-3 text-sm">
              <div className="flex justify-between text-slate-600">
                <span>Model Architecture</span>
                <span className="font-bold text-slate-800">GNN-BiLSTM-BiGRU</span>
              </div>
              <div className="flex justify-between text-slate-600">
                <span>Total Analyses Stored</span>
                <span className="font-bold text-slate-800">{stats.total_analyses}</span>
              </div>
              <div className="flex justify-between text-slate-600">
                <span>Last Analysis Processed</span>
                <span className="font-bold text-slate-800">{stats.last_analysis_time}</span>
              </div>
            </div>
          </div>
        </div>

      </div>
    </div>
  );
};

export default Dashboard;
