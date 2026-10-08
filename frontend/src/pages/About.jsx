import React from 'react';
import { ShieldCheck, Brain, Server, Zap, GitBranch, Mail, Building, Users, Activity } from 'lucide-react';
import { Link } from 'react-router-dom';

const About = () => {
  return (
    <div className="min-h-screen bg-slate-50 font-sans text-slate-900 selection:bg-blue-100">
      {/* Public Header */}
      <header className="bg-white border-b border-slate-200 sticky top-0 z-50">
        <div className="max-w-6xl mx-auto px-6 h-20 flex items-center justify-between">
          <Link to="/" className="flex items-center gap-2">
            <Activity className="w-8 h-8 text-blue-600" />
            <span className="text-2xl font-bold tracking-tight text-slate-900">Epi<span className="text-blue-600">Detect</span> AI</span>
          </Link>
          <div className="flex gap-4">
            <Link to="/login" className="px-5 py-2.5 text-sm font-semibold text-slate-600 hover:text-slate-900 transition-colors">Sign In</Link>
            <Link to="/signup" className="px-5 py-2.5 text-sm font-bold bg-blue-600 text-white rounded-xl shadow-md hover:bg-blue-700 transition-colors">Get Started</Link>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <div className="relative overflow-hidden bg-slate-900 text-white py-24">
        <div className="absolute inset-0 bg-gradient-to-br from-blue-900/50 to-emerald-900/30"></div>
        <div className="absolute top-0 right-0 w-[40rem] h-[40rem] bg-blue-500/10 rounded-full blur-3xl -mr-40 -mt-40 pointer-events-none"></div>
        <div className="max-w-4xl mx-auto px-6 relative z-10 text-center animate-in fade-in slide-in-from-bottom-4 duration-700">
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-blue-500/20 border border-blue-400/30 text-blue-300 font-medium text-sm mb-8">
            <Users className="w-4 h-4" /> Student Research Project
          </div>
          <h1 className="text-4xl md:text-6xl font-extrabold tracking-tight mb-6">
            Pioneering Clinical AI for <br/> <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-emerald-400">Epilepsy Detection</span>
          </h1>
          <p className="text-lg md:text-xl text-slate-300 leading-relaxed max-w-3xl mx-auto">
            We are students developing an AI-powered Epilepsy Detection and Clinical Decision Support System using EEG signals. Our mission is to bridge the gap between advanced deep learning and practical clinical neurology.
          </p>
        </div>
      </div>

      {/* Content Section */}
      <div className="max-w-4xl mx-auto px-6 py-20 space-y-24">
        
        {/* Objectives */}
        <section className="animate-in fade-in duration-700 delay-100">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-slate-900">Project Objectives</h2>
            <div className="w-20 h-1.5 bg-blue-600 mx-auto mt-6 rounded-full"></div>
          </div>
          <div className="grid md:grid-cols-2 gap-8">
            {[
              { icon: Zap, title: "Automated Analysis", desc: "Reduce neurologist workload by automatically screening hours of EEG recordings in seconds." },
              { icon: ShieldCheck, title: "Clinical Reliability", desc: "Achieve high sensitivity and specificity using hybrid neural architectures (GNN-BiLSTM)." },
              { icon: Brain, title: "Explainable AI (XAI)", desc: "Provide transparent reasoning for model predictions so clinicians can trust the results." },
              { icon: Server, title: "Secure Infrastructure", desc: "Maintain patient privacy with HIPAA-inspired data handling and secure backend systems." }
            ].map((obj, i) => {
              const Icon = obj.icon;
              return (
                <div key={i} className="bg-white p-8 rounded-3xl border border-slate-200 shadow-sm hover:shadow-md transition-shadow">
                  <div className="w-14 h-14 bg-blue-50 rounded-2xl flex items-center justify-center mb-6">
                    <Icon className="w-7 h-7 text-blue-600" />
                  </div>
                  <h3 className="text-xl font-bold text-slate-800 mb-3">{obj.title}</h3>
                  <p className="text-slate-500 leading-relaxed">{obj.desc}</p>
                </div>
              )
            })}
          </div>
        </section>

        {/* Tech Stack */}
        <section>
          <div className="bg-white rounded-3xl border border-slate-200 shadow-sm p-12 relative overflow-hidden">
            <div className="absolute top-0 right-0 w-64 h-64 bg-slate-50 rounded-full blur-3xl -mr-20 -mt-20"></div>
            <div className="relative z-10">
              <h2 className="text-2xl font-bold text-slate-900 mb-8">Technology Stack</h2>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
                {[
                  { name: "React 19", role: "Frontend" },
                  { name: "Tailwind CSS", role: "Styling" },
                  { name: "FastAPI", role: "Backend API" },
                  { name: "PyTorch", role: "Deep Learning" },
                  { name: "GNN + BiLSTM", role: "Architecture" },
                  { name: "EDF Core", role: "Signal Processing" },
                  { name: "Plotly", role: "Visualization" },
                  { name: "Docker", role: "Deployment" },
                ].map((tech, i) => (
                  <div key={i} className="border border-slate-200 rounded-2xl p-4 text-center hover:bg-slate-50 transition-colors">
                    <h4 className="font-bold text-slate-800">{tech.name}</h4>
                    <p className="text-xs font-medium text-slate-500 mt-1 uppercase tracking-wider">{tech.role}</p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </section>

        {/* Team */}
        <section>
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-slate-900">Academic Context</h2>
            <div className="w-20 h-1.5 bg-blue-600 mx-auto mt-6 rounded-full"></div>
          </div>
          <div className="bg-white rounded-3xl border border-slate-200 shadow-sm overflow-hidden">
            <div className="grid md:grid-cols-2 divide-y md:divide-y-0 md:divide-x divide-slate-200">
              <div className="p-10 flex flex-col items-center text-center">
                <div className="w-16 h-16 bg-blue-50 rounded-full flex items-center justify-center mb-4">
                  <Building className="w-8 h-8 text-blue-600" />
                </div>
                <h3 className="text-lg font-bold text-slate-800">University / Institution</h3>
                <p className="text-slate-500 mt-2">Department of Computer Science & Engineering</p>
                <div className="mt-4 px-4 py-2 bg-slate-100 rounded-lg text-sm font-medium text-slate-600">
                  [University Name Placeholder]
                </div>
              </div>
              <div className="p-10 flex flex-col items-center text-center">
                <div className="w-16 h-16 bg-emerald-50 rounded-full flex items-center justify-center mb-4">
                  <Users className="w-8 h-8 text-emerald-600" />
                </div>
                <h3 className="text-lg font-bold text-slate-800">Project Supervision</h3>
                <p className="text-slate-500 mt-2">Guided by experienced faculty members in AI and Healthcare.</p>
                <div className="mt-4 px-4 py-2 bg-slate-100 rounded-lg text-sm font-medium text-slate-600">
                  [Supervisor Name Placeholder]
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Contact CTA */}
        <section className="pb-20">
          <div className="bg-slate-900 rounded-3xl p-12 text-center text-white relative overflow-hidden">
             <div className="absolute inset-0 bg-gradient-to-b from-transparent to-blue-900/50"></div>
             <div className="relative z-10">
               <h2 className="text-3xl font-bold mb-6">Open Source Contribution</h2>
               <p className="text-slate-300 max-w-2xl mx-auto mb-10">
                 This project represents a significant step forward in our academic journey. The source code and documentation will be available for peer review and further research.
               </p>
               <div className="flex justify-center gap-4">
                 <button className="flex items-center gap-2 px-6 py-3 bg-white text-slate-900 font-bold rounded-xl hover:bg-slate-100 transition-colors">
                   <GitBranch className="w-5 h-5" /> View Repository
                 </button>
                 <button className="flex items-center gap-2 px-6 py-3 bg-blue-600 text-white font-bold rounded-xl hover:bg-blue-700 transition-colors">
                   <Mail className="w-5 h-5" /> Contact Team
                 </button>
               </div>
             </div>
          </div>
        </section>

      </div>
    </div>
  );
};

export default About;
