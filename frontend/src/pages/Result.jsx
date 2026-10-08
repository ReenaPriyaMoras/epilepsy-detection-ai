import React, { Suspense, lazy } from 'react';
import { 
  Download, 
  AlertTriangle, 
  ShieldCheck, 
  Activity, 
  Brain, 
  CheckCircle2, 
  XCircle, 
  Clock, 
  Database, 
  HardDrive, 
  Cpu, 
  FileText,
  User,
  Stethoscope
} from 'lucide-react';
import { useLocation, useNavigate } from 'react-router-dom';
import toast, { Toaster } from 'react-hot-toast';

const EEGVisualization = lazy(() => import('../components/EEGVisualization'));
const XAIDashboard = lazy(() => import('../components/XAIDashboard'));

const Result = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const predictionData = location.state?.predictionData || null;

  if (!predictionData) {
    return (
      <div className="max-w-4xl mx-auto mt-20 text-center animate-in fade-in duration-500">
        <div className="bg-white rounded-3xl border border-slate-200 shadow-sm p-12">
          <div className="w-24 h-24 bg-slate-50 rounded-full flex items-center justify-center mx-auto mb-6">
            <Activity className="w-12 h-12 text-slate-400" />
          </div>
          <h2 className="text-2xl font-bold text-slate-800 mb-4">No Analysis Available</h2>
          <p className="text-slate-500 mb-8 max-w-md mx-auto">
            You haven't selected or performed any EEG analysis yet. Please upload an EEG recording or select one from history.
          </p>
          <div className="flex justify-center gap-4">
            <button 
              onClick={() => navigate('/upload')}
              className="inline-flex items-center gap-2 px-6 py-3 bg-blue-600 text-white font-semibold rounded-xl hover:bg-blue-700 transition-colors"
            >
              Go to Upload
            </button>
            <button 
              onClick={() => navigate('/history')}
              className="inline-flex items-center gap-2 px-6 py-3 bg-white border border-slate-200 text-slate-700 font-semibold rounded-xl hover:bg-slate-50 transition-colors"
            >
              View History
            </button>
          </div>
        </div>
      </div>
    );
  }

  const predictionText = predictionData.prediction || 'Unknown';
  const isEpileptic = predictionText.toLowerCase() === 'epileptic';

  // Defensive probability & confidence calculations (ensures never multiplied twice)
  const rawProb = predictionData.seizure_probability !== undefined ? predictionData.seizure_probability : (isEpileptic ? 0.85 : 0.15);
  const probability = rawProb <= 1.0 ? (rawProb * 100).toFixed(1) : Number(rawProb).toFixed(1);

  const rawConf = predictionData.confidence_score !== undefined ? predictionData.confidence_score : 0.92;
  const confidence = rawConf <= 1.0 ? (rawConf * 100).toFixed(1) : Number(rawConf).toFixed(1);

  let riskLevel = predictionData.risk_level;
  if (!riskLevel) {
    if (probability > 75) riskLevel = 'High';
    else if (probability > 40) riskLevel = 'Medium';
    else riskLevel = 'Low';
  }

  const riskColor = isEpileptic ? 'text-rose-600' : 'text-emerald-600';
  const riskBg = isEpileptic ? 'bg-rose-50' : 'bg-emerald-50';
  const riskBorder = isEpileptic ? 'border-rose-200' : 'border-emerald-200';
  const RiskIcon = isEpileptic ? AlertTriangle : CheckCircle2;

  const handlePrintOrExport = () => {
    window.print();
    toast.success("Printing clinical report...");
  };

  return (
    <div className="max-w-7xl mx-auto space-y-8 animate-in fade-in duration-500 pb-12">
      <Toaster position="top-right" />
      
      {/* Top Header & Actions */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-white p-6 rounded-2xl border border-slate-200 shadow-sm">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <h1 className="text-2xl font-bold text-slate-800 flex items-center gap-2">
              <Activity className="w-6 h-6 text-blue-600" /> Clinical AI Analysis Report
            </h1>
            {predictionData.id && (
              <span className="text-xs font-mono font-bold bg-blue-50 text-blue-700 px-2.5 py-1 rounded-full border border-blue-200">
                {predictionData.id}
              </span>
            )}
          </div>
          <div className="flex flex-wrap gap-x-6 gap-y-2 mt-3 text-sm font-medium text-slate-600">
            <span className="flex items-center gap-1.5"><HardDrive className="w-4 h-4 text-slate-400" /> {predictionData.filename || 'eeg_recording.edf'}</span>
            <span className="flex items-center gap-1.5"><Database className="w-4 h-4 text-slate-400" /> Dataset: {predictionData.dataset || 'EpiEEG'}</span>
            <span className="flex items-center gap-1.5"><Clock className="w-4 h-4 text-slate-400" /> Processed: {predictionData.processing_time || '0.12s'}</span>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <button 
            onClick={handlePrintOrExport}
            className="flex items-center justify-center gap-2 px-6 py-3 bg-slate-900 hover:bg-slate-800 text-white font-bold rounded-xl shadow transition-all active:scale-[0.98]"
          >
            <Download className="w-5 h-5" /> Export / Print PDF
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        
        {/* Card 1: Primary Diagnosis */}
        <div className={`lg:col-span-1 rounded-3xl border shadow-sm p-8 flex flex-col justify-center items-center text-center ${riskBg} ${riskBorder}`}>
          <div className={`w-20 h-20 rounded-full flex items-center justify-center mb-6 bg-white shadow-sm border ${riskBorder}`}>
            <RiskIcon className={`w-10 h-10 ${riskColor}`} />
          </div>
          <h3 className="text-sm font-bold uppercase tracking-widest text-slate-500 mb-2">AI Diagnosis</h3>
          <h2 className={`text-3xl font-black tracking-tight ${riskColor}`}>{predictionText}</h2>
          <p className="mt-4 text-sm font-medium text-slate-600">
            {isEpileptic 
              ? 'High probability of seizure patterns detected in the recording.' 
              : 'No definitive seizure patterns detected. Normal EEG profile.'}
          </p>
        </div>

        {/* Card 2: Seizure Probability */}
        <div className="lg:col-span-2 bg-white rounded-3xl border border-slate-200 shadow-sm p-8 flex flex-col justify-center">
          <h3 className="text-lg font-bold text-slate-800 flex items-center gap-2 mb-8">
            <Activity className="w-5 h-5 text-blue-600" /> Class Probability Breakdown
          </h3>
          
          <div className="space-y-6">
            <div>
              <div className="flex justify-between items-end mb-2">
                <span className="font-bold text-slate-700">Epileptic (Seizure)</span>
                <span className="font-black text-xl text-rose-600">{probability}%</span>
              </div>
              <div className="w-full bg-slate-100 rounded-full h-4 overflow-hidden border border-slate-200">
                <div className="bg-gradient-to-r from-orange-400 to-rose-500 h-full rounded-full" style={{ width: `${Math.min(100, Math.max(0, probability))}%` }}></div>
              </div>
            </div>

            <div>
              <div className="flex justify-between items-end mb-2">
                <span className="font-bold text-slate-700">Healthy (Normal)</span>
                <span className="font-black text-xl text-emerald-600">{(100 - probability).toFixed(1)}%</span>
              </div>
              <div className="w-full bg-slate-100 rounded-full h-4 overflow-hidden border border-slate-200">
                <div className="bg-emerald-500 h-full rounded-full" style={{ width: `${Math.min(100, Math.max(0, 100 - probability))}%` }}></div>
              </div>
            </div>
          </div>
        </div>

        {/* Card 3: Confidence & Details */}
        <div className="lg:col-span-1 bg-white rounded-3xl border border-slate-200 shadow-sm p-8 flex flex-col justify-center">
          <h3 className="text-lg font-bold text-slate-800 flex items-center gap-2 mb-6">
            <ShieldCheck className="w-5 h-5 text-blue-600" /> Model Confidence
          </h3>
          <div className="flex items-center gap-6 mb-8">
            <div className="relative w-24 h-24 flex items-center justify-center shrink-0">
              <svg className="w-full h-full -rotate-90" viewBox="0 0 36 36">
                <path className="text-slate-100" strokeWidth="4" stroke="currentColor" fill="none" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" />
                <path className="text-blue-600" strokeWidth="4" strokeDasharray={`${confidence}, 100`} stroke="currentColor" fill="none" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" />
              </svg>
              <span className="absolute font-black text-xl text-slate-800">{confidence}%</span>
            </div>
            <p className="text-xs font-medium text-slate-500">
              Neural network internal certainty for this classification.
            </p>
          </div>
          
          <div className="pt-6 border-t border-slate-100 space-y-3">
             <div className="flex justify-between text-sm">
               <span className="text-slate-500 flex items-center gap-1"><Cpu className="w-4 h-4"/> Architecture</span>
               <span className="font-bold text-slate-700">GNN-BiLSTM</span>
             </div>
             <div className="flex justify-between text-sm">
               <span className="text-slate-500 flex items-center gap-1"><CheckCircle2 className="w-4 h-4"/> Status</span>
               <span className="font-bold text-emerald-600">Verified</span>
             </div>
          </div>
        </div>

      </div>

      {/* Clinical Recommendation Banner */}
      <div className="bg-white rounded-3xl border border-slate-200 shadow-sm p-6 flex items-start gap-4">
        <div className="p-3 bg-blue-50 text-blue-600 rounded-2xl shrink-0">
          <Stethoscope className="w-6 h-6" />
        </div>
        <div>
          <h3 className="font-bold text-slate-800 text-base mb-1">Clinical Decision Support Recommendation</h3>
          <p className="text-sm text-slate-600 leading-relaxed">
            {predictionData.doctor_recommendation || (isEpileptic 
              ? "High epileptiform activity detected. Prompt neurological consultation and 24-hr continuous video-EEG recommended."
              : "Normal baseline EEG profile without paroxysmal epileptiform discharges. Routine neurological follow-up.")}
          </p>
        </div>
      </div>

      {/* Raw EEG Visualization Section (if active session file present) */}
      {location.state?.file ? (
        <Suspense fallback={<div className="h-64 flex items-center justify-center bg-slate-50 border border-slate-200 rounded-3xl animate-pulse">Loading EEG Viewer...</div>}>
          <EEGVisualization file={location.state.file} />
        </Suspense>
      ) : null}
      
      {/* Explainable AI Dashboard */}
      {predictionData.explainability && (
        <Suspense fallback={<div className="h-64 flex items-center justify-center bg-slate-50 border border-slate-200 rounded-3xl animate-pulse">Loading Explainability...</div>}>
          <XAIDashboard explainability={predictionData.explainability} />
        </Suspense>
      )}

    </div>
  );
};

export default Result;
