import React, { useState } from 'react';
import { Bell, Search, User, LogOut, Loader2 } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { healthcareAPI } from '../../services/api';
import toast, { Toaster } from 'react-hot-toast';

const Navbar = () => {
  const navigate = useNavigate();
  const [searchQuery, setSearchQuery] = useState('');
  const [isSearching, setIsSearching] = useState(false);
  const doctorName = localStorage.getItem("doctorName") || "Doctor";
  const avatarLetter = doctorName.charAt(0).toUpperCase();

  const handleLogout = () => {
    localStorage.clear();
    navigate('/login');
  };

  const handleSearch = async (e) => {
    if (e.key === 'Enter' || e.type === 'submit') {
      e.preventDefault();
      const query = searchQuery.trim();
      if (!query) return;

      setIsSearching(true);
      try {
        const response = await healthcareAPI.search(query);
        const results = response.data || [];

        if (results.length === 1) {
          // Navigate directly to the analysis report
          const item = results[0];
          navigate('/result', {
            state: {
              predictionData: item,
              fromSearch: true
            }
          });
          toast.success(`Found analysis for ${item.filename}`);
          setSearchQuery('');
        } else if (results.length > 1) {
          // Navigate to history with prefiltered search
          navigate(`/history?q=${encodeURIComponent(query)}`);
          toast.success(`Found ${results.length} matching analyses.`);
          setSearchQuery('');
        } else {
          toast.error(`No patient or analysis found for "${query}"`);
        }
      } catch (error) {
        console.error("Search error:", error);
        toast.error("Search query failed. Please try again.");
      } finally {
        setIsSearching(false);
      }
    }
  };

  return (
    <header className="bg-white border-b border-slate-200 h-16 flex items-center justify-between px-6 z-10 shrink-0 relative">
      <Toaster position="top-right" />
      
      <div className="flex items-center gap-4 flex-1">
        <h2 className="text-xl font-semibold text-slate-800 hidden sm:block">
          Clinical Decision Support
        </h2>
        <div className="hidden md:flex items-center gap-2 bg-blue-50 text-blue-700 px-3 py-1.5 rounded-full border border-blue-100">
          <span className="relative flex h-2 w-2">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-blue-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-2 w-2 bg-blue-500"></span>
          </span>
          <span className="text-xs font-semibold tracking-wide uppercase">AI Assistant Active</span>
        </div>
      </div>
      
      <div className="flex items-center gap-6">
        <form onSubmit={handleSearch} className="relative hidden lg:block">
          {isSearching ? (
            <Loader2 className="w-4 h-4 text-blue-500 animate-spin absolute left-3 top-1/2 -translate-y-1/2" />
          ) : (
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
          )}
          <input 
            type="text" 
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            onKeyDown={handleSearch}
            placeholder="Search patient, file, or analysis ID (Press Enter)..." 
            className="pl-9 pr-4 py-2 bg-slate-50 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all w-80"
          />
        </form>

        <button className="relative p-2 text-slate-400 hover:text-slate-600 transition-colors rounded-full hover:bg-slate-50">
          <Bell className="w-5 h-5" />
          <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-rose-500 rounded-full border-2 border-white"></span>
        </button>

        <div className="flex items-center gap-3 pl-6 border-l border-slate-200">
          <div className="text-right hidden sm:block">
            <p className="text-sm font-semibold text-slate-700 leading-none">{doctorName}</p>
            <p className="text-xs text-slate-500 mt-1">Neurology Dept</p>
          </div>
          <div className="w-9 h-9 rounded-full bg-gradient-to-br from-blue-600 to-indigo-600 flex items-center justify-center text-white shadow-sm ring-2 ring-white">
            <span className="font-bold text-sm">{avatarLetter}</span>
          </div>
          <button onClick={handleLogout} className="text-slate-400 hover:text-rose-500 transition-colors ml-2" title="Logout">
            <LogOut className="w-5 h-5" />
          </button>
        </div>
      </div>
    </header>
  );
};

export default Navbar;
