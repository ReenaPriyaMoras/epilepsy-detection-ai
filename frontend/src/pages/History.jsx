import React, { useState, useEffect } from 'react';
import { 
  History as HistoryIcon, 
  Download, 
  AlertCircle, 
  FileText, 
  Trash2, 
  ExternalLink, 
  Search, 
  Filter, 
  Activity, 
  CheckCircle2, 
  AlertTriangle 
} from 'lucide-react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { healthcareAPI } from '../services/api';
import toast, { Toaster } from 'react-hot-toast';

const History = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const initialQuery = searchParams.get('q') || '';

  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchTerm, setSearchTerm] = useState(initialQuery);
  const [filterType, setFilterType] = useState('ALL');
  const [sortBy, setSortBy] = useState('NEWEST');

  const fetchHistory = async () => {
    try {
      setLoading(true);
      const response = await healthcareAPI.getHistory();
      setHistory(response.data || []);
      setError(null);
    } catch (err) {
      console.error("Failed to load history:", err);
      setError('Failed to fetch analysis history from server.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchHistory();
  }, []);

  const handleDelete = async (id, e) => {
    e.stopPropagation();
    if (!window.confirm("Are you sure you want to delete this analysis record?")) return;

    try {
      await healthcareAPI.deleteHistoryItem(id);
      setHistory(prev => prev.filter(item => item.id !== id));
      toast.success("Analysis record deleted.");
    } catch (err) {
      console.error("Delete error:", err);
      toast.error("Failed to delete record.");
    }
  };

  const handleOpenReport = (record) => {
    navigate('/result', {
      state: {
        predictionData: record,
        fromHistory: true
      }
    });
  };

  const filteredHistory = history.filter(item => {
    const matchesSearch = 
      (item.filename && item.filename.toLowerCase().includes(searchTerm.toLowerCase())) ||
      (item.patient_id && item.patient_id.toLowerCase().includes(searchTerm.toLowerCase())) ||
      (item.id && item.id.toLowerCase().includes(searchTerm.toLowerCase())) ||
      (item.prediction && item.prediction.toLowerCase().includes(searchTerm.toLowerCase()));

    if (filterType === 'EPILEPTIC') {
      return matchesSearch && item.prediction?.toLowerCase() === 'epileptic';
    }
    if (filterType === 'HEALTHY') {
      return matchesSearch && item.prediction?.toLowerCase() !== 'epileptic';
    }
    return matchesSearch;
  }).sort((a, b) => {
    if (sortBy === 'NEWEST') {
      return new Date(b.created_at || b.timestamp) - new Date(a.created_at || a.timestamp);
    }
    if (sortBy === 'OLDEST') {
      return new Date(a.created_at || a.timestamp) - new Date(b.created_at || b.timestamp);
    }
    if (sortBy === 'CONFIDENCE') {
      return (b.confidence_score || 0) - (a.confidence_score || 0);
    }
    return 0;
  });

  return (
    <div className="max-w-7xl mx-auto space-y-6 animate-in fade-in duration-500 pb-12">
      <Toaster position="top-right" />

      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-white p-6 rounded-2xl border border-slate-200 shadow-sm">
        <div className="flex items-center gap-3">
          <div className="p-3 bg-blue-50 text-blue-600 rounded-xl">
            <HistoryIcon className="w-7 h-7" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-slate-800">Analysis History</h1>
            <p className="text-sm text-slate-500">Permanent diagnostic database of all processed EEG recordings.</p>
          </div>
        </div>
        <button
          onClick={() => navigate('/upload')}
          className="px-5 py-2.5 bg-blue-600 hover:bg-blue-700 text-white font-bold rounded-xl shadow transition-colors text-sm"
        >
          New Analysis
        </button>
      </div>

      {/* Search & Filter Bar */}
      <div className="bg-white p-4 rounded-2xl border border-slate-200 shadow-sm flex flex-col md:flex-row gap-4 justify-between items-center">
        <div className="relative w-full md:w-96">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="Filter by filename, patient ID, or ID..."
            className="w-full pl-9 pr-4 py-2 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500"
          />
        </div>

        <div className="flex items-center gap-3 w-full md:w-auto">
          <select
            value={filterType}
            onChange={(e) => setFilterType(e.target.value)}
            className="px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-sm font-medium text-slate-700 focus:outline-none focus:ring-2 focus:ring-blue-500/20"
          >
            <option value="ALL">All Predictions</option>
            <option value="EPILEPTIC">Epileptic Only</option>
            <option value="HEALTHY">Non-Epileptic Only</option>
          </select>

          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value)}
            className="px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-sm font-medium text-slate-700 focus:outline-none focus:ring-2 focus:ring-blue-500/20"
          >
            <option value="NEWEST">Sort: Newest First</option>
            <option value="OLDEST">Sort: Oldest First</option>
            <option value="CONFIDENCE">Sort: Highest Confidence</option>
          </select>
        </div>
      </div>

      {/* States: Loading, Error, Empty, List */}
      {loading && (
        <div className="flex flex-col items-center justify-center p-16 bg-white rounded-2xl border shadow-sm">
          <div className="w-10 h-10 border-4 border-blue-600 border-t-transparent rounded-full animate-spin mb-3"></div>
          <span className="text-slate-500 font-medium">Loading database records...</span>
        </div>
      )}

      {error && !loading && (
        <div className="flex items-center justify-center gap-2 p-12 bg-red-50 text-red-600 rounded-2xl border border-red-200 shadow-sm font-medium">
          <AlertCircle className="w-5 h-5" /> {error}
        </div>
      )}

      {!loading && !error && filteredHistory.length === 0 && (
        <div className="flex flex-col items-center justify-center p-16 bg-white rounded-2xl border border-slate-200 shadow-sm text-center">
          <div className="w-16 h-16 bg-slate-50 rounded-full flex items-center justify-center mb-4 text-slate-400">
            <FileText className="w-8 h-8" />
          </div>
          <h3 className="text-lg font-bold text-slate-700">No analyses found</h3>
          <p className="text-sm text-slate-500 mt-1 max-w-sm">
            {searchTerm ? "No records match your search criteria. Try a different query." : "No EEG recordings have been analyzed yet. Upload an EDF file to generate clinical reports."}
          </p>
          <button
            onClick={() => navigate('/upload')}
            className="mt-6 px-6 py-2.5 bg-blue-600 text-white font-semibold rounded-xl hover:bg-blue-700 transition-colors text-sm"
          >
            Upload EDF File
          </button>
        </div>
      )}

      {!loading && !error && filteredHistory.length > 0 && (
        <div className="grid gap-4">
          {filteredHistory.map((record) => {
            const isEpileptic = record.prediction?.toLowerCase() === 'epileptic';
            const confPct = (record.confidence_score ? record.confidence_score * 100 : 0).toFixed(1);
            
            return (
              <div 
                key={record.id} 
                onClick={() => handleOpenReport(record)}
                className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm hover:shadow-md transition-all cursor-pointer flex flex-col md:flex-row md:items-center justify-between gap-4 group"
              >
                <div className="flex items-start gap-4">
                  <div className={`p-3 rounded-xl shrink-0 mt-1 ${isEpileptic ? 'bg-rose-50 text-rose-600' : 'bg-emerald-50 text-emerald-600'}`}>
                    {isEpileptic ? <AlertTriangle className="w-6 h-6" /> : <CheckCircle2 className="w-6 h-6" />}
                  </div>
                  <div>
                    <div className="flex items-center gap-2">
                      <h4 className="font-bold text-slate-800 text-base group-hover:text-blue-600 transition-colors">
                        {record.filename}
                      </h4>
                      <span className="text-xs font-mono bg-slate-100 text-slate-600 px-2 py-0.5 rounded">
                        {record.id}
                      </span>
                    </div>
                    <p className="text-xs text-slate-400 mt-1">
                      Patient: <span className="font-medium text-slate-600">{record.patient_id}</span> • Analyzed on: <span className="text-slate-600">{record.timestamp}</span> • Time: {record.processing_time || 'N/A'}
                    </p>
                    <div className="mt-3 flex items-center gap-2">
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-bold ${
                        isEpileptic ? 'bg-rose-100 text-rose-800' : 'bg-emerald-100 text-emerald-800'
                      }`}>
                        {record.prediction} ({confPct}%)
                      </span>
                      <span className="text-xs font-semibold px-2 py-0.5 bg-slate-100 text-slate-600 rounded-full">
                        Risk: {record.risk_level || (isEpileptic ? 'High' : 'Low')}
                      </span>
                    </div>
                  </div>
                </div>

                <div className="flex items-center gap-2 self-end md:self-center">
                  <button 
                    onClick={(e) => {
                      e.stopPropagation();
                      handleOpenReport(record);
                    }}
                    className="flex items-center gap-1.5 px-3.5 py-2 bg-blue-50 text-blue-600 hover:bg-blue-100 font-semibold rounded-xl text-sm transition-colors"
                  >
                    <ExternalLink className="w-4 h-4" /> Open Report
                  </button>
                  <button 
                    onClick={(e) => handleDelete(record.id, e)}
                    className="p-2 text-slate-400 hover:text-rose-600 hover:bg-rose-50 rounded-xl transition-colors"
                    title="Delete Record"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};

export default History;
