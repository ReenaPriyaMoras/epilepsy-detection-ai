import React from 'react';
import { useNavigate } from 'react-router-dom';
import { AlertOctagon, Home } from 'lucide-react';

const NotFound = () => {
  const navigate = useNavigate();
  
  return (
    <div className="flex flex-col items-center justify-center h-full min-h-[60vh] text-center px-4 animate-in fade-in duration-500">
      <div className="bg-red-50 p-6 rounded-full mb-6 text-red-500">
        <AlertOctagon className="w-16 h-16" />
      </div>
      <h1 className="text-4xl font-black text-slate-800 mb-2">404</h1>
      <h2 className="text-xl font-bold text-slate-600 mb-6">Page Not Found</h2>
      <p className="text-slate-500 max-w-md mb-8">
        The page you are looking for doesn't exist or has been moved. Please navigate back to the dashboard.
      </p>
      <button 
        onClick={() => navigate('/')}
        className="flex items-center gap-2 px-6 py-3 bg-blue-600 text-white font-bold rounded-xl shadow-lg shadow-blue-600/20 hover:bg-blue-700 transition-colors"
      >
        <Home className="w-5 h-5" /> Back to Dashboard
      </button>
    </div>
  );
};

export default NotFound;
