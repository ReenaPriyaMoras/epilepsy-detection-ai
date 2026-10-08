import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Brain, Lock, Mail, User, ArrowRight, Activity, ShieldCheck } from 'lucide-react';

const Signup = () => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    password: '',
    confirmPassword: ''
  });
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const calculatePasswordStrength = (password) => {
    let strength = 0;
    if (password.length > 7) strength += 25;
    if (/[A-Z]/.test(password)) strength += 25;
    if (/[0-9]/.test(password)) strength += 25;
    if (/[^A-Za-z0-9]/.test(password)) strength += 25;
    return strength;
  };

  const strength = calculatePasswordStrength(formData.password);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (formData.password !== formData.confirmPassword) {
      setError("Passwords do not match");
      return;
    }
    setError('');
    setIsLoading(true);
    // Simulate API call
    setTimeout(() => {
      setIsLoading(false);
      navigate('/login');
    }, 1500);
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-50 relative overflow-hidden">
      {/* Premium Background Elements */}
      <div className="absolute top-0 right-0 -mr-20 -mt-20 w-96 h-96 rounded-full bg-gradient-to-br from-blue-100 to-indigo-100 blur-3xl opacity-60 pointer-events-none"></div>
      <div className="absolute bottom-0 left-0 -ml-20 -mb-20 w-[30rem] h-[30rem] rounded-full bg-gradient-to-tr from-emerald-50 to-cyan-50 blur-3xl opacity-60 pointer-events-none"></div>
      
      <div className="w-full max-w-5xl flex flex-col md:flex-row bg-white rounded-3xl shadow-xl overflow-hidden z-10 border border-slate-100 animate-in fade-in zoom-in-95 duration-700">
        
        {/* Left Side: Medical Branding & Illustration */}
        <div className="w-full md:w-5/12 bg-slate-900 p-12 text-white flex flex-col justify-between relative overflow-hidden">
          <div className="absolute inset-0 bg-gradient-to-br from-blue-600/20 to-indigo-900/40 mix-blend-multiply"></div>
          
          {/* Animated Medical Grid Background */}
          <div className="absolute inset-0 opacity-10" style={{ backgroundImage: 'radial-gradient(#ffffff 1px, transparent 1px)', backgroundSize: '24px 24px' }}></div>
          
          <div className="relative z-10 flex items-center gap-3 mb-12">
            <div className="w-10 h-10 rounded-xl bg-blue-500/20 flex items-center justify-center border border-blue-400/30">
              <Activity className="w-6 h-6 text-blue-400" />
            </div>
            <span className="text-xl font-bold tracking-wide">Epi<span className="text-blue-400">Detect</span> AI</span>
          </div>

          <div className="relative z-10 mb-12 space-y-6">
            <h2 className="text-3xl md:text-4xl font-light leading-tight">
              Join the future of <br/>
              <span className="font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-emerald-400">Clinical Neurology</span>
            </h2>
            <p className="text-slate-300 text-lg leading-relaxed">
              Create an account to access advanced AI-driven EEG analysis and comprehensive clinical decision support.
            </p>
          </div>

          <div className="relative z-10 space-y-4">
            <div className="flex items-center gap-3 text-sm text-slate-300">
              <ShieldCheck className="w-5 h-5 text-emerald-400" />
              <span>HIPAA Compliant Infrastructure</span>
            </div>
            <div className="flex items-center gap-3 text-sm text-slate-300">
              <Brain className="w-5 h-5 text-blue-400" />
              <span>State-of-the-art Neural Networks</span>
            </div>
          </div>
        </div>

        {/* Right Side: Signup Form */}
        <div className="w-full md:w-7/12 p-10 md:p-14 bg-white relative">
          
          <div className="max-w-md mx-auto">
            <div className="text-center md:text-left mb-10">
              <h2 className="text-3xl font-extrabold text-slate-900 tracking-tight">Create Account</h2>
              <p className="text-slate-500 mt-2">Enter your credentials to get started.</p>
            </div>

            {error && (
              <div className="mb-6 p-4 bg-red-50 border border-red-200 text-red-600 rounded-xl text-sm font-medium animate-in slide-in-from-top-2">
                {error}
              </div>
            )}

            <form onSubmit={handleSubmit} className="space-y-5">
              <div className="space-y-1.5">
                <label className="text-sm font-semibold text-slate-700">Full Name</label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                    <User className="h-5 w-5 text-slate-400" />
                  </div>
                  <input
                    type="text"
                    name="name"
                    value={formData.name}
                    onChange={handleChange}
                    className="w-full pl-11 pr-4 py-3.5 bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 outline-none transition-all text-slate-700 font-medium placeholder-slate-400"
                    placeholder="Dr. Jane Doe"
                    required
                  />
                </div>
              </div>

              <div className="space-y-1.5">
                <label className="text-sm font-semibold text-slate-700">Email Address</label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                    <Mail className="h-5 w-5 text-slate-400" />
                  </div>
                  <input
                    type="email"
                    name="email"
                    value={formData.email}
                    onChange={handleChange}
                    className="w-full pl-11 pr-4 py-3.5 bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 outline-none transition-all text-slate-700 font-medium placeholder-slate-400"
                    placeholder="doctor@hospital.org"
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
                    value={formData.password}
                    onChange={handleChange}
                    className="w-full pl-11 pr-4 py-3.5 bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 outline-none transition-all text-slate-700 font-medium placeholder-slate-400"
                    placeholder="••••••••"
                    required
                  />
                </div>
                {/* Password Strength Indicator */}
                {formData.password && (
                  <div className="pt-2 animate-in fade-in">
                    <div className="flex gap-1 h-1.5 w-full bg-slate-100 rounded-full overflow-hidden">
                      <div className={`h-full transition-all duration-300 ${strength > 0 ? 'bg-red-400' : ''}`} style={{ width: '25%' }}></div>
                      <div className={`h-full transition-all duration-300 ${strength > 25 ? 'bg-orange-400' : ''}`} style={{ width: '25%' }}></div>
                      <div className={`h-full transition-all duration-300 ${strength > 50 ? 'bg-emerald-400' : ''}`} style={{ width: '25%' }}></div>
                      <div className={`h-full transition-all duration-300 ${strength > 75 ? 'bg-emerald-600' : ''}`} style={{ width: '25%' }}></div>
                    </div>
                    <p className="text-xs text-slate-500 mt-1.5 font-medium">
                      {strength <= 25 && "Weak password"}
                      {strength === 50 && "Fair password"}
                      {strength === 75 && "Good password"}
                      {strength === 100 && "Strong password"}
                    </p>
                  </div>
                )}
              </div>

              <div className="space-y-1.5">
                <label className="text-sm font-semibold text-slate-700">Confirm Password</label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                    <Lock className="h-5 w-5 text-slate-400" />
                  </div>
                  <input
                    type="password"
                    name="confirmPassword"
                    value={formData.confirmPassword}
                    onChange={handleChange}
                    className="w-full pl-11 pr-4 py-3.5 bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 outline-none transition-all text-slate-700 font-medium placeholder-slate-400"
                    placeholder="••••••••"
                    required
                  />
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
                      Create Account
                      <ArrowRight className="w-5 h-5" />
                    </>
                  )}
                </button>
              </div>
            </form>

            <div className="mt-8 text-center text-sm font-medium text-slate-500">
              Already have an account?{' '}
              <Link to="/login" className="text-blue-600 hover:text-blue-700 font-bold hover:underline underline-offset-4">
                Sign in instead
              </Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Signup;
