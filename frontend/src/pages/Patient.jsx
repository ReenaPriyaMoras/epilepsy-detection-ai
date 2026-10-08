import React, { useState } from 'react';
import { UserPlus, Save, Calendar, FileText, Loader2 } from 'lucide-react';
import { healthcareAPI } from '../services/api';
import toast, { Toaster } from 'react-hot-toast';

const Patient = () => {
  const [isSaving, setIsSaving] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    age: '',
    gender: '',
    notes: ''
  });

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleSave = async (e) => {
    e.preventDefault();
    if (!formData.name || !formData.age || !formData.gender) {
      toast.error('Please fill out all required fields.');
      return;
    }

    setIsSaving(true);
    try {
      const response = await healthcareAPI.registerPatient(formData);
      toast.success(response.message || 'Patient registered successfully.');
      // Reset form
      setFormData({ name: '', age: '', gender: '', notes: '' });
    } catch (error) {
      toast.error('Failed to register patient. Please try again.');
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <Toaster position="top-right" />
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-800">Patient Registration</h1>
          <p className="text-slate-500">Enter patient details to link with EEG records.</p>
        </div>
      </div>

      <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
        <div className="p-8">
          <form onSubmit={handleSave} className="space-y-6">
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Patient ID */}
              <div>
                <label className="block text-sm font-semibold text-slate-700 mb-1">Patient ID (Auto-generated)</label>
                <input 
                  type="text" 
                  value="PT-2026-0942"
                  disabled
                  className="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl text-slate-500 cursor-not-allowed"
                />
              </div>

              {/* Full Name */}
              <div>
                <label className="block text-sm font-semibold text-slate-700 mb-1">Full Name *</label>
                <input 
                  type="text" 
                  name="name"
                  value={formData.name}
                  onChange={handleChange}
                  className="w-full px-4 py-3 bg-white border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 transition-colors"
                  placeholder="e.g. John Doe"
                />
              </div>

              {/* Age */}
              <div>
                <label className="block text-sm font-semibold text-slate-700 mb-1">Age *</label>
                <div className="relative">
                  <Calendar className="w-5 h-5 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
                  <input 
                    type="number" 
                    name="age"
                    value={formData.age}
                    onChange={handleChange}
                    className="w-full pl-10 pr-4 py-3 bg-white border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 transition-colors"
                    placeholder="e.g. 45"
                  />
                </div>
              </div>

              {/* Gender */}
              <div>
                <label className="block text-sm font-semibold text-slate-700 mb-1">Gender *</label>
                <select 
                  name="gender"
                  value={formData.gender}
                  onChange={handleChange}
                  className="w-full px-4 py-3 bg-white border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 transition-colors appearance-none"
                >
                  <option value="" disabled>Select gender</option>
                  <option value="Male">Male</option>
                  <option value="Female">Female</option>
                  <option value="Other">Other</option>
                </select>
              </div>
            </div>

            {/* Clinical Notes */}
            <div>
              <label className="block text-sm font-semibold text-slate-700 mb-1">Clinical Notes & History</label>
              <div className="relative">
                <FileText className="w-5 h-5 text-slate-400 absolute left-3 top-4" />
                <textarea 
                  name="notes"
                  value={formData.notes}
                  onChange={handleChange}
                  rows="5"
                  className="w-full pl-10 pr-4 py-3 bg-white border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 transition-colors resize-none"
                  placeholder="Enter previous medical history, known conditions, medications..."
                ></textarea>
              </div>
            </div>

            <div className="flex justify-end gap-4 pt-4 border-t border-slate-100">
              <button 
                type="button" 
                onClick={() => setFormData({ name: '', age: '', gender: '', notes: '' })}
                className="px-6 py-3 bg-white border border-slate-300 text-slate-700 font-semibold rounded-xl hover:bg-slate-50 transition-colors"
              >
                Clear
              </button>
              <button 
                type="submit" 
                disabled={isSaving}
                className="flex items-center gap-2 px-8 py-3 bg-blue-600 text-white font-bold rounded-xl shadow-sm hover:bg-blue-700 transition-colors disabled:bg-blue-400"
              >
                {isSaving ? <Loader2 className="w-5 h-5 animate-spin" /> : <Save className="w-5 h-5" />}
                {isSaving ? 'Saving...' : 'Save Patient Profile'}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default Patient;
