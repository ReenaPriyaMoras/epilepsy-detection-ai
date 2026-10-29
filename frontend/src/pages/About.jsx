import React, { useState } from 'react';
import { ShieldCheck, Brain, Server, Zap, GitBranch, Mail, Building, Users, Activity, GraduationCap } from 'lucide-react';
import { Link } from 'react-router-dom';
import ContactModal from '../components/ContactModal';

const About = () => {
  const [isContactModalOpen, setIsContactModalOpen] = useState(false);

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
            <Users className="w-4 h-4" /> Academic Major Project
          </div>
          <h1 className="text-4xl md:text-6xl font-extrabold tracking-tight mb-6">
            EpiDetect AI
          </h1>
          <div className="space-y-4 text-base md:text-lg text-slate-300 leading-relaxed max-w-3xl mx-auto">
            <p>
              EpiDetect AI is an academic major project developed by the Department of Intelligent Computing and Business Systems (ICBS), St Joseph Engineering College, Mangaluru.
            </p>
            <p>
              The project presents an intelligent web-based framework for automated epileptic seizure detection using EEG signals through a hybrid Graph Neural Network (GNN), BiLSTM, and BiGRU architecture.
            </p>
            <p>
              The platform enables EEG upload, preprocessing, seizure prediction, explainable AI visualization, report generation, and clinical decision support while providing a modern and user-friendly interface.
            </p>
          </div>
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
              { 
                icon: Zap, 
                title: "Objective 1", 
                desc: "To design a hybrid GNN–BiLSTM–BiGRU model for automated epileptic seizure detection using multi-channel EEG signals." 
              },
              { 
                icon: ShieldCheck, 
                title: "Objective 2", 
                desc: "To develop a web-based platform for EEG upload, preprocessing, seizure prediction, visualization, and report generation." 
              },
              { 
                icon: Brain, 
                title: "Objective 3", 
                desc: "To improve prediction performance using standardized preprocessing, statistical feature extraction, and Explainable AI techniques." 
              },
              { 
                icon: Server, 
                title: "Objective 4", 
                desc: "To evaluate the proposed framework using standard performance metrics and compare it with existing methods." 
              }
            ].map((obj, i) => {
              const Icon = obj.icon;
              return (
                <div 
                  key={i} 
                  className="bg-white p-8 rounded-3xl border border-slate-200 shadow-sm hover:shadow-md transition-shadow"
                >
                  <div className="w-14 h-14 bg-blue-50 rounded-2xl flex items-center justify-center mb-6">
                    <Icon className="w-7 h-7 text-blue-600" />
                  </div>
                  <h3 className="text-xl font-bold text-slate-800 mb-3">{obj.title}</h3>
                  <p className="text-slate-500 leading-relaxed">
                    <span className="font-semibold text-slate-700">{i + 1}. </span>
                    {obj.desc}
                  </p>
                </div>
              );
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
                  { name: "GNN + BiLSTM + BiGRU", role: "Architecture" },
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

        {/* Academic Details */}
        <section>
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-slate-900">Academic Information</h2>
            <div className="w-20 h-1.5 bg-blue-600 mx-auto mt-6 rounded-full"></div>
          </div>
          <div className="bg-white rounded-3xl border border-slate-200 shadow-sm p-8 md:p-12">
            <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-8">
              <div className="flex flex-col items-center text-center p-6 rounded-2xl bg-slate-50 border border-slate-100 hover:border-blue-100 transition-colors">
                <div className="w-14 h-14 bg-blue-50 rounded-2xl flex items-center justify-center mb-4 text-blue-600">
                  <Building className="w-7 h-7" />
                </div>
                <span className="text-xs font-semibold tracking-wider text-slate-400 uppercase">Institution & Location</span>
                <h3 className="text-lg font-bold text-slate-800 mt-2">St Joseph Engineering College</h3>
                <p className="text-sm font-semibold text-blue-600 mt-1">Mangaluru</p>
              </div>

              <div className="flex flex-col items-center text-center p-6 rounded-2xl bg-slate-50 border border-slate-100 hover:border-indigo-100 transition-colors">
                <div className="w-14 h-14 bg-indigo-50 rounded-2xl flex items-center justify-center mb-4 text-indigo-600">
                  <Activity className="w-7 h-7" />
                </div>
                <span className="text-xs font-semibold tracking-wider text-slate-400 uppercase">Department</span>
                <h3 className="text-base font-bold text-slate-800 mt-2">Department of Intelligent Computing and Business Systems (ICBS)</h3>
              </div>

              <div className="flex flex-col items-center text-center p-6 rounded-2xl bg-slate-50 border border-slate-100 hover:border-emerald-100 transition-colors">
                <div className="w-14 h-14 bg-emerald-50 rounded-2xl flex items-center justify-center mb-4 text-emerald-600">
                  <Brain className="w-7 h-7" />
                </div>
                <span className="text-xs font-semibold tracking-wider text-slate-400 uppercase">Programme</span>
                <h3 className="text-base font-bold text-slate-800 mt-2">Artificial Intelligence and Machine Learning</h3>
              </div>

              <div className="flex flex-col items-center text-center p-6 rounded-2xl bg-slate-50 border border-slate-100 hover:border-amber-100 transition-colors">
                <div className="w-14 h-14 bg-amber-50 rounded-2xl flex items-center justify-center mb-4 text-amber-600">
                  <GraduationCap className="w-7 h-7" />
                </div>
                <span className="text-xs font-semibold tracking-wider text-slate-400 uppercase">Batch</span>
                <h3 className="text-lg font-bold text-slate-800 mt-2">Batch of 2027</h3>
                <p className="text-sm font-medium text-slate-500 mt-1">Academic Year 2023–2027</p>
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
               <div className="flex flex-wrap justify-center gap-4">
                 <a 
                   href="https://github.com/ReenaPriyaMoras/epilepsy-detection-ai"
                   target="_blank"
                   rel="noopener noreferrer"
                   className="inline-flex items-center gap-2 px-6 py-3 bg-white text-slate-900 font-bold rounded-xl hover:bg-slate-100 transition-colors cursor-pointer"
                 >
                   <GitBranch className="w-5 h-5" /> View Repository
                 </a>
                 <button 
                   type="button"
                   onClick={() => setIsContactModalOpen(true)}
                   className="inline-flex items-center gap-2 px-6 py-3 bg-blue-600 text-white font-bold rounded-xl hover:bg-blue-700 transition-colors cursor-pointer"
                 >
                   <Mail className="w-5 h-5" /> Contact Team
                 </button>
               </div>
             </div>
          </div>
        </section>

      </div>

      {/* Contact Team Modal */}
      <ContactModal 
        isOpen={isContactModalOpen} 
        onClose={() => setIsContactModalOpen(false)} 
      />
    </div>
  );
};

export default About;
