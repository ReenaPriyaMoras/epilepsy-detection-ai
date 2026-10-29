import React, { useState, useEffect } from 'react';
import { X, Mail, Phone, Copy, Check, Users } from 'lucide-react';
import toast from 'react-hot-toast';

export const TEAM_MEMBERS = [
  {
    
  
    id: 1,
    name: "Ananya",
    email: "ananyashivaprasad18@gmail.com",
    phone: "9035438502"
  },
  {
    id: 2,
    name: "Lenn Shaun Sequeira",
    email: "sequeiralenn2005@gmail.com",
    phone: "9481955028"
  },
  {
    id: 3,
    name: "Phelicia Xavier Dsilva",
    email: "dsilvaphelicia@gmail.com",
    phone: "6360070463"
  },
  {
    id: 4,
    name: "Reena Priya Moras",
    email: "reenamoras2005@gmail.com",
    phone: "7349069103"
  },
];

const ContactModal = ({ isOpen, onClose }) => {
  const [copiedKey, setCopiedKey] = useState(null);

  useEffect(() => {
    if (!isOpen) return;

    const handleKeyDown = (e) => {
      if (e.key === 'Escape') {
        onClose();
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    const originalOverflow = document.body.style.overflow;
    document.body.style.overflow = 'hidden';

    return () => {
      window.removeEventListener('keydown', handleKeyDown);
      document.body.style.overflow = originalOverflow;
    };
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  const handleCopy = async (text, key, label) => {
    try {
      if (navigator?.clipboard?.writeText) {
        await navigator.clipboard.writeText(text);
      } else {
        const textArea = document.createElement('textarea');
        textArea.value = text;
        textArea.style.position = 'fixed';
        textArea.style.left = '-9999px';
        document.body.appendChild(textArea);
        textArea.select();
        document.execCommand('copy');
        document.body.removeChild(textArea);
      }
      setCopiedKey(key);
      toast.success(`Copied ${label} (${text}) to clipboard!`);
      setTimeout(() => {
        setCopiedKey((prev) => (prev === key ? null : prev));
      }, 2000);
    } catch (err) {
      console.error('Failed to copy: ', err);
      toast.error('Failed to copy to clipboard');
    }
  };

  return (
    <div 
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm animate-in fade-in duration-200"
      onClick={(e) => {
        if (e.target === e.currentTarget) onClose();
      }}
      role="dialog"
      aria-modal="true"
      aria-labelledby="contact-team-title"
    >
      <div className="relative w-full max-w-2xl bg-white rounded-3xl border border-slate-200 shadow-2xl overflow-hidden max-h-[90vh] flex flex-col animate-in zoom-in-95 duration-200">
        
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-5 border-b border-slate-200 bg-slate-50/70">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-blue-50 border border-blue-100 flex items-center justify-center text-blue-600">
              <Users className="w-5 h-5" />
            </div>
            <div>
              <h2 id="contact-team-title" className="text-xl font-bold text-slate-900">
                Team Members
              </h2>
              <p className="text-xs text-slate-500 font-medium">
                Department of Intelligent Computing and Business Systems • St Joseph Engineering College
              </p>
            </div>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="w-9 h-9 rounded-xl flex items-center justify-center text-slate-400 hover:text-slate-700 hover:bg-slate-100 transition-colors cursor-pointer"
            aria-label="Close dialog"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Members List */}
        <div className="p-6 overflow-y-auto space-y-4">
          {TEAM_MEMBERS.map((member, idx) => (
            <div
              key={member.id}
              className="bg-slate-50 border border-slate-200/80 rounded-2xl p-5 hover:border-blue-200 hover:shadow-xs transition-all"
            >
              {/* Member Name with Number */}
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center gap-3">
                  <span className="w-7 h-7 rounded-lg bg-blue-600 text-white font-bold text-xs flex items-center justify-center shadow-xs">
                    {idx + 1}
                  </span>
                  <h3 className="text-lg font-bold text-slate-900">
                    {member.name}
                  </h3>
                </div>
              </div>

              {/* Contact Actions Grid */}
              <div className="grid sm:grid-cols-2 gap-3 mt-2">
                {/* Email Box */}
                <div className="bg-white rounded-xl border border-slate-200/80 p-3 flex items-center justify-between gap-2 shadow-xs">
                  <div className="min-w-0 flex-1">
                    <div className="flex items-center gap-1.5 text-[11px] font-bold text-slate-400 uppercase tracking-wider mb-0.5">
                      <Mail className="w-3.5 h-3.5 text-blue-500" />
                      <span>Email</span>
                    </div>
                    <a
                      href={`mailto:${member.email}`}
                      className="text-sm font-semibold text-blue-600 hover:text-blue-800 hover:underline truncate block"
                      title={`Send email to ${member.email}`}
                    >
                      {member.email}
                    </a>
                  </div>
                  <button
                    type="button"
                    onClick={() => handleCopy(member.email, `email-${idx}`, `${member.name}'s Email`)}
                    className="p-2 rounded-lg text-slate-400 hover:text-blue-600 hover:bg-slate-50 active:bg-slate-100 transition-colors shrink-0 cursor-pointer"
                    title="Copy email to clipboard"
                    aria-label={`Copy ${member.name}'s email`}
                  >
                    {copiedKey === `email-${idx}` ? (
                      <span className="flex items-center gap-1 text-xs text-emerald-600 font-bold">
                        <Check className="w-4 h-4 text-emerald-600" />
                      </span>
                    ) : (
                      <Copy className="w-4 h-4" />
                    )}
                  </button>
                </div>

                {/* Phone Box */}
                <div className="bg-white rounded-xl border border-slate-200/80 p-3 flex items-center justify-between gap-2 shadow-xs">
                  <div className="min-w-0 flex-1">
                    <div className="flex items-center gap-1.5 text-[11px] font-bold text-slate-400 uppercase tracking-wider mb-0.5">
                      <Phone className="w-3.5 h-3.5 text-emerald-500" />
                      <span>Phone</span>
                    </div>
                    <a
                      href={`tel:${member.phone}`}
                      className="text-sm font-semibold text-slate-700 hover:text-blue-600 hover:underline block"
                      title={`Call ${member.phone}`}
                    >
                      {member.phone}
                    </a>
                  </div>
                  <button
                    type="button"
                    onClick={() => handleCopy(member.phone, `phone-${idx}`, `${member.name}'s Phone`)}
                    className="p-2 rounded-lg text-slate-400 hover:text-blue-600 hover:bg-slate-50 active:bg-slate-100 transition-colors shrink-0 cursor-pointer"
                    title="Copy phone to clipboard"
                    aria-label={`Copy ${member.name}'s phone`}
                  >
                    {copiedKey === `phone-${idx}` ? (
                      <span className="flex items-center gap-1 text-xs text-emerald-600 font-bold">
                        <Check className="w-4 h-4 text-emerald-600" />
                      </span>
                    ) : (
                      <Copy className="w-4 h-4" />
                    )}
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Footer */}
        <div className="px-6 py-4 border-t border-slate-200 bg-slate-50/70 flex justify-between items-center text-xs text-slate-500">
          <span>Artificial Intelligence & Machine Learning (Batch of 2027)</span>
          <button
            type="button"
            onClick={onClose}
            className="px-4 py-2 bg-slate-200 hover:bg-slate-300 text-slate-800 font-bold rounded-xl transition-colors cursor-pointer text-xs"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
};

export default ContactModal;
