import React from 'react';
import { AlertTriangle, RefreshCw, Home, ShieldAlert } from 'lucide-react';

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null, errorInfo: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    this.setState({ errorInfo });
    console.error('ErrorBoundary caught a runtime exception:', error, errorInfo);
  }

  handleReload = () => {
    window.location.reload();
  };

  handleReset = () => {
    this.setState({ hasError: false, error: null, errorInfo: null });
    window.location.href = '/dashboard';
  };

  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen bg-slate-50 flex items-center justify-center p-6 font-sans">
          <div className="max-w-xl w-full bg-white rounded-3xl border border-slate-200 shadow-xl p-8 md:p-10 text-center animate-in fade-in zoom-in-95 duration-300">
            <div className="w-20 h-20 bg-rose-50 border border-rose-100 rounded-2xl flex items-center justify-center mx-auto mb-6">
              <ShieldAlert className="w-10 h-10 text-rose-600" />
            </div>
            
            <h1 className="text-2xl font-black text-slate-900 mb-2">
              Application Notice
            </h1>
            <p className="text-slate-500 mb-6 text-sm leading-relaxed">
              An unexpected runtime state occurred in the clinical interface. The system has prevented a crash to protect data integrity.
            </p>

            {this.state.error && (
              <div className="bg-slate-50 border border-slate-200 rounded-xl p-4 mb-6 text-left overflow-hidden">
                <p className="text-xs font-mono text-rose-600 font-semibold truncate">
                  {this.state.error.toString()}
                </p>
              </div>
            )}

            <div className="flex flex-col sm:flex-row gap-3 justify-center">
              <button
                onClick={this.handleReload}
                className="inline-flex items-center justify-center gap-2 px-6 py-3 bg-blue-600 text-white font-bold rounded-xl shadow-md hover:bg-blue-700 transition-all active:scale-[0.98] text-sm"
              >
                <RefreshCw className="w-4 h-4" /> Reload View
              </button>
              <button
                onClick={this.handleReset}
                className="inline-flex items-center justify-center gap-2 px-6 py-3 bg-white border border-slate-200 text-slate-700 font-bold rounded-xl shadow-sm hover:bg-slate-50 transition-all active:scale-[0.98] text-sm"
              >
                <Home className="w-4 h-4" /> Return to Dashboard
              </button>
            </div>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;
