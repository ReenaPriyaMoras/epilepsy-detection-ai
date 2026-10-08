import React from 'react';
import { Link } from 'react-router-dom';
import {
  Brain,
  Activity,
  ArrowRight,
  ShieldCheck,
  Zap,
  UploadCloud,
  Database,
  CheckCircle2,
  Mail
} from "lucide-react";

const Home = () => {
  return (
    <div className="min-h-screen bg-slate-50 font-sans selection:bg-blue-100">
      
      {/* Public Header */}
      <header className="bg-white/80 backdrop-blur-lg border-b border-slate-200 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6 h-20 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-10 h-10 rounded-xl bg-blue-600 flex items-center justify-center shadow-lg shadow-blue-600/20">
              <Activity className="w-6 h-6 text-white" />
            </div>
            <span className="text-2xl font-bold tracking-tight text-slate-900">Epi<span className="text-blue-600">Detect</span> AI</span>
          </div>
          <nav className="hidden md:flex gap-8 text-sm font-semibold text-slate-600">
            <a href="#features" className="hover:text-blue-600 transition-colors">Features</a>
            <a href="#how-it-works" className="hover:text-blue-600 transition-colors">How it Works</a>
            <Link to="/about" className="hover:text-blue-600 transition-colors">About Us</Link>
          </nav>
          <div className="flex gap-4">
            <Link to="/login" className="px-5 py-2.5 text-sm font-semibold text-slate-600 hover:text-slate-900 transition-colors hidden md:block">Sign In</Link>
            <Link to="/signup" className="px-5 py-2.5 text-sm font-bold bg-slate-900 text-white rounded-xl shadow-md hover:bg-slate-800 transition-colors">Get Started</Link>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <div className="relative overflow-hidden bg-white">
        <div className="absolute top-0 right-0 w-[40rem] h-[40rem] bg-gradient-to-br from-blue-50 to-indigo-50 rounded-full blur-3xl -mr-40 -mt-40 pointer-events-none opacity-60"></div>
        <div className="absolute bottom-0 left-0 w-[30rem] h-[30rem] bg-gradient-to-tr from-emerald-50 to-cyan-50 rounded-full blur-3xl -ml-20 -mb-20 pointer-events-none opacity-60"></div>
        
        <div className="max-w-7xl mx-auto px-6 py-24 md:py-32 relative z-10 grid lg:grid-cols-2 gap-16 items-center">
          <div className="animate-in fade-in slide-in-from-bottom-8 duration-700">
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-blue-50 text-blue-600 font-medium text-sm mb-6 border border-blue-100 shadow-sm">
              <Activity className="w-4 h-4" /> v2.0 Clinical Engine Live
            </div>
            <h1 className="text-5xl md:text-6xl font-extrabold text-slate-900 tracking-tight leading-tight mb-6">
              Next-Generation <br/>
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-emerald-600">Neurological AI</span>
            </h1>
            <p className="text-xl text-slate-500 mb-10 leading-relaxed">
              Empower your clinical decision-making with state-of-the-art deep learning. Upload EEG recordings for rapid, explainable, and highly accurate epilepsy detection.
            </p>
            <div className="flex flex-col sm:flex-row gap-4">
              <Link 
                to="/dashboard" 
                className="inline-flex items-center justify-center gap-2 px-8 py-4 bg-blue-600 text-white font-bold rounded-xl shadow-lg shadow-blue-600/20 hover:bg-blue-700 transition-all active:scale-[0.98]"
              >
                Analyze EEG
                <ArrowRight className="w-5 h-5" />
              </Link>
              <Link 
                to="/about" 
                className="inline-flex items-center justify-center gap-2 px-8 py-4 bg-white text-slate-700 border border-slate-200 font-bold rounded-xl shadow-sm hover:bg-slate-50 transition-all active:scale-[0.98]"
              >
                Learn More
              </Link>
            </div>
          </div>
          
          <div className="relative animate-in fade-in zoom-in-95 duration-1000 delay-200 hidden lg:block">
            {/* Abstract Medical Illustration */}
            <div className="w-full aspect-square relative flex items-center justify-center">
              <div className="absolute inset-0 bg-gradient-to-tr from-blue-100 to-emerald-50 rounded-full blur-2xl opacity-50"></div>
              <div className="relative w-4/5 h-4/5 bg-white rounded-3xl shadow-2xl border border-slate-100 p-6 flex flex-col">
                <div className="flex justify-between items-center mb-6 border-b border-slate-100 pb-4">
                  <div className="flex items-center gap-2">
                    <Brain className="w-6 h-6 text-blue-600" />
                    <span className="font-bold text-slate-700">Clinical EEG</span>
                  </div>
                  <span className="px-3 py-1 bg-emerald-100 text-emerald-700 text-xs font-bold rounded-full">Processing</span>
                </div>
                {/* Simulated EEG Waveform */}
                <div className="flex-1 flex flex-col justify-center gap-4">
                  {[1, 2, 3].map((i) => (
                    <div key={i} className="h-12 w-full overflow-hidden relative opacity-60">
                      <svg viewBox="0 0 400 40" preserveAspectRatio="none" className={`w-full h-full stroke-blue-500 fill-none stroke-[2] delay-${i*100}`}>
                        <path d="M0,20 Q10,10 20,20 T40,20 T60,10 T80,30 T100,20 T120,5 T140,20 T160,35 T180,20 T200,20 T220,10 T240,20 T260,30 T280,20 T300,5 T320,20 T340,35 T360,20 T380,20 T400,20" className="animate-pulse" />
                      </svg>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Features Grid */}
      <section id="features" className="py-24 bg-slate-50">
        <div className="max-w-7xl mx-auto px-6">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-extrabold text-slate-900 mb-4">Enterprise-Grade Clinical Tools</h2>
            <p className="text-lg text-slate-500 max-w-2xl mx-auto">Designed specifically for neurological diagnostics, combining speed with unparalleled accuracy.</p>
          </div>
          
          <div className="grid md:grid-cols-3 gap-8">
            {[
              { 
                title: 'AI-Powered Detection', 
                desc: 'Utilizes a state-of-the-art hybrid GNN-BiLSTM architecture to identify epileptic signatures in raw EEG data.',
                icon: Brain,
                color: 'text-blue-600',
                bg: 'bg-blue-50',
                border: 'border-blue-100'
              },
              { 
                title: 'Clinical Explainability', 
                desc: 'Black-box models are not enough for healthcare. We provide channel-level feature importance and confidence scores.',
                icon: ShieldCheck,
                color: 'text-emerald-600',
                bg: 'bg-emerald-50',
                border: 'border-emerald-100'
              },
              { 
                title: 'Lightning Fast Inference', 
                desc: 'Process standard 10-20 system EDF files in seconds, drastically reducing the time needed for initial screening.',
                icon: Zap,
                color: 'text-amber-600',
                bg: 'bg-amber-50',
                border: 'border-amber-100'
              }
            ].map((feature, idx) => {
              const Icon = feature.icon;
              return (
                <div key={idx} className="bg-white p-8 rounded-3xl border border-slate-200 shadow-sm hover:shadow-lg transition-shadow duration-300">
                  <div className={`w-14 h-14 rounded-2xl flex items-center justify-center mb-6 ${feature.bg} border ${feature.border}`}>
                    <Icon className={`w-7 h-7 ${feature.color}`} />
                  </div>
                  <h3 className="text-xl font-bold text-slate-900 mb-3">{feature.title}</h3>
                  <p className="text-slate-500 leading-relaxed">{feature.desc}</p>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* How it Works Pipeline */}
      <section id="how-it-works" className="py-24 bg-white border-y border-slate-200 overflow-hidden relative">
         <div className="max-w-7xl mx-auto px-6 relative z-10">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-extrabold text-slate-900 mb-4">Seamless Diagnostic Workflow</h2>
            <p className="text-lg text-slate-500 max-w-2xl mx-auto">From raw data to actionable clinical insights in five simple steps.</p>
          </div>

          <div className="flex flex-col md:flex-row justify-between items-center md:items-start gap-8 relative">
             {/* Connecting Line */}
             <div className="hidden md:block absolute top-12 left-10 right-10 h-0.5 bg-gradient-to-r from-blue-100 via-blue-400 to-emerald-100 -z-10"></div>
             
             {[
               { step: "01", title: "Upload EDF", icon: UploadCloud },
               { step: "02", title: "Preprocessing", icon: Activity },
               { step: "03", title: "Feature Extraction", icon: Database },
               { step: "04", title: "AI Prediction", icon: Brain },
               { step: "05", title: "Clinical Report", icon: CheckCircle2 }
             ].map((item, idx) => {
               const Icon = item.icon;
               return (
                 <div key={idx} className="flex flex-col items-center w-48 text-center bg-white">
                   <div className="w-24 h-24 rounded-full bg-slate-50 border-4 border-white shadow-xl flex items-center justify-center mb-6 relative group hover:scale-105 transition-transform duration-300">
                     <Icon className="w-10 h-10 text-blue-600 group-hover:text-emerald-500 transition-colors" />
                     <div className="absolute -top-3 -right-3 w-8 h-8 rounded-full bg-slate-900 text-white font-bold flex items-center justify-center text-sm shadow-sm">
                       {item.step}
                     </div>
                   </div>
                   <h4 className="font-bold text-slate-800">{item.title}</h4>
                 </div>
               )
             })}
          </div>
         </div>
      </section>

      {/* Footer */}
      <footer className="bg-slate-900 text-slate-400 py-16">
        <div className="max-w-7xl mx-auto px-6 grid md:grid-cols-4 gap-12">
          <div className="col-span-1 md:col-span-2">
             <div className="flex items-center gap-2 mb-6">
               <Activity className="w-6 h-6 text-blue-500" />
               <span className="text-xl font-bold text-white">EpiDetect AI</span>
             </div>
             <p className="max-w-sm mb-6 leading-relaxed">
               An advanced clinical decision support system utilizing deep learning to provide reliable, explainable epilepsy detection from EEG signals.
             </p>
             <div className="flex gap-4">
               {/* Placeholders for social/contact */}
               <div className="w-10 h-10 rounded-full bg-slate-800 hover:bg-slate-700 flex items-center justify-center cursor-pointer transition-colors"><Mail className="w-5 h-5 text-slate-300"/></div>
             </div>
          </div>
          <div>
            <h4 className="text-white font-bold mb-6">Platform</h4>
            <ul className="space-y-4">
              <li><Link to="/upload" className="hover:text-blue-400 transition-colors">Analyze EEG</Link></li>
              <li><Link to="/dashboard" className="hover:text-blue-400 transition-colors">Dashboard</Link></li>
              <li><Link to="/history" className="hover:text-blue-400 transition-colors">History</Link></li>
            </ul>
          </div>
          <div>
            <h4 className="text-white font-bold mb-6">Institution</h4>
            <ul className="space-y-4">
              <li><span className="hover:text-white transition-colors cursor-default">Department of Computer Science</span></li>
              <li><span className="hover:text-white transition-colors cursor-default">[University Name]</span></li>
              <li><Link to="/about" className="hover:text-blue-400 transition-colors">About the Project</Link></li>
            </ul>
          </div>
        </div>
        <div className="max-w-7xl mx-auto px-6 mt-16 pt-8 border-t border-slate-800 text-sm text-center md:text-left flex flex-col md:flex-row justify-between items-center">
          <p>© 2024 EpiDetect AI Research Project. All rights reserved.</p>
          <p className="mt-2 md:mt-0">Not for actual medical diagnosis without physician supervision.</p>
        </div>
      </footer>

    </div>
  );
};

export default Home;
