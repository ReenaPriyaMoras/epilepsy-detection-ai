import React, { useState } from 'react';
import { Activity, Lock, User, ArrowRight, Mail, ShieldCheck } from 'lucide-react';
import { useNavigate, Link } from 'react-router-dom';

const Login = () => {
  const navigate = useNavigate();
  const [credentials, setCredentials] = useState({ doctorId: '', password: '' });
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const handleLogin = (e) => {
    e.preventDefault();
    if (!credentials.doctorId || !credentials.password) {
      setError("Please fill in all fields");
      return;
    }
    
    setError('');
    setIsLoading(true);
    
    // Simulate backend validation & loading
    setTimeout(() => {
      setIsLoading(false);
      localStorage.setItem("doctorName", `Dr. ${credentials.doctorId}`);
      localStorage.setItem("doctorId", credentials.doctorId);
      navigate('/dashboard');
    }, 1500);
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setCredentials(prev => ({ ...prev, [name]: value }));
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-50 relative overflow-hidden">
      {/* Premium Background Elements */}
      <div className="absolute top-0 left-0 -ml-20 -mt-20 w-96 h-96 rounded-full bg-gradient-to-br from-blue-100 to-indigo-100 blur-3xl opacity-60 pointer-events-none"></div>
      <div className="absolute bottom-0 right-0 -mr-20 -mb-20 w-[30rem] h-[30rem] rounded-full bg-gradient-to-tr from-emerald-50 to-cyan-50 blur-3xl opacity-60 pointer-events-none"></div>
      
      <div className="w-full max-w-5xl flex flex-col md:flex-row bg-white rounded-3xl shadow-xl overflow-hidden z-10 border border-slate-100 animate-in fade-in zoom-in-95 duration-700">
        
        {/* Left Side: Medical Branding & Illustration */}
        <div className="w-full md:w-5/12 bg-slate-900 p-12 text-white flex flex-col justify-between relative overflow-hidden hidden md:flex">
          <div className="absolute inset-0 bg-gradient-to-br from-blue-600/20 to-indigo-900/40 mix-blend-multiply"></div>
          
          <div className="absolute inset-0 opacity-10" style={{ backgroundImage: 'radial-gradient(#ffffff 1px, transparent 1px)', backgroundSize: '24px 24px' }}></div>
          
          <div className="relative z-10 flex items-center gap-3 mb-12">
             <Link to="/" className="flex items-center gap-3 hover:opacity-80 transition-opacity">
               <div className="w-10 h-10 rounded-xl bg-blue-500/20 flex items-center justify-center border border-blue-400/30">
                 <Activity className="w-6 h-6 text-blue-400" />
               </div>
               <span className="text-xl font-bold tracking-wide">Epi<span className="text-blue-400">Detect</span> AI</span>
             </Link>
          </div>

          <div className="relative z-10 mb-12 space-y-6">
            <h2 className="text-3xl font-light leading-tight">
              Welcome back to <br/>
              <span className="font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-emerald-400">Clinical Dashboard</span>
            </h2>
            <p className="text-slate-300 text-lg leading-relaxed">
              Access patient EEG analyses, model insights, and AI-driven clinical reporting securely.
            </p>
          </div>

          <div className="relative z-10 space-y-4">
            <div className="flex items-center gap-3 text-sm text-slate-300">
              <ShieldCheck className="w-5 h-5 text-emerald-400" />
              <span>Secure Encrypted Session</span>
            </div>
          </div>
        </div>

        {/* Right Side: Login Form */}
        <div className="w-full md:w-7/12 p-10 md:p-14 bg-white relative flex flex-col justify-center">
          <div className="max-w-md mx-auto w-full">
            
            {/* Mobile Branding */}
            <div className="md:hidden flex items-center justify-center gap-2 mb-8">
              <Activity className="w-8 h-8 text-blue-600" />
              <span className="text-2xl font-bold tracking-tight text-slate-900">EpiDetect AI</span>
            </div>

            <div className="text-center md:text-left mb-10">
              <h2 className="text-3xl font-extrabold text-slate-900 tracking-tight">Sign In</h2>
              <p className="text-slate-500 mt-2">Enter your staff credentials to continue.</p>
            </div>

            {error && (
              <div className="mb-6 p-4 bg-red-50 border border-red-200 text-red-600 rounded-xl text-sm font-medium animate-in slide-in-from-top-2 flex items-center gap-2">
                <ShieldCheck className="w-5 h-5 text-red-500" /> {error}
              </div>
            )}

            <form onSubmit={handleLogin} className="space-y-6">
              <div className="space-y-1.5">
                <label className="text-sm font-semibold text-slate-700">Staff ID or Email</label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                    <User className="h-5 w-5 text-slate-400" />
                  </div>
                  <input
                    type="text"
                    name="doctorId"
                    value={credentials.doctorId}
                    onChange={handleChange}
                    className="w-full pl-11 pr-4 py-3.5 bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 outline-none transition-all text-slate-700 font-medium placeholder-slate-400"
                    placeholder="Enter Staff ID"
                    required
                  />
                </div>
              </div>
              
              <div className="space-y-1.5">
                <label className="text-sm font-semibold text-slate-700">Password</label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                    <Lock className="h-5 w-5 text-slate-400" />
                  </div>
                  <input
                    type="password"
                    name="password"
                    value={credentials.password}
                    onChange={handleChange}
                    className="w-full pl-11 pr-4 py-3.5 bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 outline-none transition-all text-slate-700 font-medium placeholder-slate-400"
                    placeholder="••••••••"
                    required
                  />
                </div>
              </div>

              <div className="flex items-center justify-between">
                <div className="flex items-center">
                  <input
                    id="remember-me"
                    name="remember-me"
                    type="checkbox"
                    className="h-4 w-4 rounded border-slate-300 text-blue-600 focus:ring-blue-600"
                  />
                  <label htmlFor="remember-me" className="ml-2 block text-sm text-slate-600 font-medium">
                    Remember me
                  </label>
                </div>
                <div className="text-sm">
                  <a href="#" className="font-semibold text-blue-600 hover:text-blue-500 hover:underline underline-offset-4 transition-all">
                    Forgot password?
                  </a>
                </div>
              </div>

              <div className="pt-2">
                <button
                  type="submit"
                  disabled={isLoading}
                  className="w-full flex items-center justify-center gap-2 bg-blue-600 hover:bg-blue-700 text-white font-bold py-3.5 px-4 rounded-xl shadow-lg shadow-blue-600/20 transition-all active:scale-[0.98] disabled:opacity-70 disabled:active:scale-100"
                >
                  {isLoading ? (
                    <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
                  ) : (
                    <>
                      Sign In
                      <ArrowRight className="w-5 h-5" />
                    </>
                  )}
                </button>
              </div>
            </form>

            <div className="mt-8 text-center text-sm font-medium text-slate-500">
              Don't have an account?{' '}
              <Link to="/signup" className="text-blue-600 hover:text-blue-700 font-bold hover:underline underline-offset-4">
                Request Access
              </Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Login;
