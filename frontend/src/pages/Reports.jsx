import React, { useState, useEffect } from 'react';
import { Download, FileDown, Search, Filter, FileText, ExternalLink, Activity } from 'lucide-react';
import { healthcareAPI } from '../services/api';
import { useNavigate } from 'react-router-dom';
import toast, { Toaster } from 'react-hot-toast';

const Reports = () => {
  const navigate = useNavigate();
  const [reports, setReports] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');

  const fetchReports = async () => {
    try {
      setLoading(true);
      const res = await healthcareAPI.getHistory();
      setReports(res.data || []);
    } catch (e) {
      console.error("Error loading reports:", e);
      toast.error("Failed to load reports from database.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchReports();
  }, []);

  const handleOpenReport = (record) => {
    navigate('/result', {
      state: {
        predictionData: record,
        fromReports: true
      }
    });
  };

  const handleExportCSV = () => {
    if (reports.length === 0) {
      toast.error("No reports available to export.");
      return;
    }
    const headers = ["Analysis ID", "Patient ID", "Filename", "Prediction", "Confidence Score", "Risk Level", "Timestamp"];
    const rows = reports.map(r => [
      r.id,
      r.patient_id,
      `"${r.filename}"`,
      r.prediction,
      r.confidence_score,
      r.risk_level,
      `"${r.timestamp}"`
    ]);
    const csvContent = "data:text/csv;charset=utf-8," + [headers.join(","), ...rows.map(e => e.join(","))].join("\n");
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", `EEG_Clinical_Reports_${new Date().toISOString().slice(0, 10)}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    toast.success("Reports exported to CSV.");
  };

  const filteredReports = reports.filter(r => 
    (r.id && r.id.toLowerCase().includes(searchQuery.toLowerCase())) ||
    (r.patient_id && r.patient_id.toLowerCase().includes(searchQuery.toLowerCase())) ||
    (r.filename && r.filename.toLowerCase().includes(searchQuery.toLowerCase())) ||
    (r.prediction && r.prediction.toLowerCase().includes(searchQuery.toLowerCase()))
  );

  return (
    <div className="space-y-6 animate-in fade-in duration-500">
      <Toaster position="top-right" />
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-800">Clinical Reports</h1>
          <p className="text-slate-500">Verified diagnostic reports generated from EEG analyses.</p>
        </div>
        <div className="flex items-center gap-3">
          <button 
            onClick={handleExportCSV}
            className="flex items-center gap-2 px-4 py-2.5 bg-white border border-slate-200 text-slate-700 font-semibold rounded-xl shadow-sm hover:bg-slate-50 transition-colors text-sm"
          >
            <FileDown className="w-4 h-4" />
            Export CSV
          </button>
        </div>
      </div>

      <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
        {/* Toolbar */}
        <div className="p-4 border-b border-slate-200 bg-slate-50/50 flex flex-col sm:flex-row gap-4 justify-between items-center">
          <div className="relative w-full sm:w-80">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
            <input 
              type="text" 
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search by ID, Patient, or Filename..." 
              className="w-full pl-9 pr-4 py-2 bg-white border border-slate-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <span className="text-xs font-semibold text-slate-500">
            {filteredReports.length} {filteredReports.length === 1 ? 'Report' : 'Reports'} Found
          </span>
        </div>

        {/* Loading State */}
        {loading && (
          <div className="flex flex-col items-center justify-center p-16">
            <div className="w-8 h-8 border-4 border-blue-600 border-t-transparent rounded-full animate-spin mb-3"></div>
            <p className="text-sm text-slate-500">Loading clinical reports...</p>
          </div>
        )}

        {/* Empty State */}
        {!loading && filteredReports.length === 0 && (
          <div className="flex flex-col items-center justify-center p-16 text-center">
            <div className="w-16 h-16 bg-slate-50 rounded-full flex items-center justify-center mb-4 text-slate-400">
              <FileText className="w-8 h-8" />
            </div>
            <h3 className="text-base font-bold text-slate-700">No clinical reports found</h3>
            <p className="text-sm text-slate-500 mt-1 max-w-sm">
              {searchQuery ? "No reports match your search query." : "No EEG recordings have been analyzed yet. Upload an EDF file to generate clinical reports."}
            </p>
            <button
              onClick={() => navigate('/upload')}
              className="mt-6 px-6 py-2.5 bg-blue-600 text-white font-semibold rounded-xl hover:bg-blue-700 transition-colors text-sm"
            >
              Analyze EDF Recording
            </button>
          </div>
        )}

        {/* Table */}
        {!loading && filteredReports.length > 0 && (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm text-slate-600">
              <thead className="bg-slate-50 text-slate-500 font-semibold uppercase text-xs tracking-wider border-b border-slate-200">
                <tr>
                  <th className="px-6 py-4">Report ID</th>
                  <th className="px-6 py-4">Filename</th>
                  <th className="px-6 py-4">Patient ID</th>
                  <th className="px-6 py-4">Date & Time</th>
                  <th className="px-6 py-4">Prediction</th>
                  <th className="px-6 py-4">Risk</th>
                  <th className="px-6 py-4 text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {filteredReports.map((report) => {
                  const isEpileptic = report.prediction?.toLowerCase() === 'epileptic';
                  return (
                    <tr key={report.id} className="hover:bg-slate-50 transition-colors">
                      <td className="px-6 py-4 font-mono font-medium text-slate-800">{report.id}</td>
                      <td className="px-6 py-4 font-semibold text-slate-700">{report.filename}</td>
                      <td className="px-6 py-4">{report.patient_id}</td>
                      <td className="px-6 py-4 text-slate-500">{report.timestamp}</td>
                      <td className="px-6 py-4">
                        <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-bold ${
                          isEpileptic ? 'bg-rose-50 text-rose-700 border border-rose-200' : 'bg-emerald-50 text-emerald-700 border border-emerald-200'
                        }`}>
                          {report.prediction} ({((report.confidence_score || 0) * 100).toFixed(1)}%)
                        </span>
                      </td>
                      <td className="px-6 py-4 font-semibold">{report.risk_level || (isEpileptic ? 'High' : 'Low')}</td>
                      <td className="px-6 py-4 text-right">
                        <button 
                          onClick={() => handleOpenReport(report)}
                          className="inline-flex items-center gap-1 text-blue-600 hover:text-blue-800 font-semibold p-2 rounded-lg hover:bg-blue-50 transition-colors text-xs" 
                          title="View Full Report"
                        >
                          <ExternalLink className="w-4 h-4" /> View Report
                        </button>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};

export default Reports;
