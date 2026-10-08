import React from 'react';
import { BookOpen } from 'lucide-react';

const Documentation = () => {
  const sections = [
    { title: "Project Overview", content: "EpiDetect AI is an advanced clinical AI system designed to detect epileptic seizure patterns from raw EEG recordings with high accuracy." },
    { title: "Architecture", content: "The system utilizes a modern FastAPI backend decoupled from a React/Vite frontend. Inference is powered by PyTorch." },
    { title: "Workflow", content: "1. Upload EDF -> 2. Vectorized Preprocessing -> 3. Graph Construction -> 4. GNN-BiLSTM Inference -> 5. Gradient Explainability -> 6. Dashboard Visualization." },
    { title: "Model Description", content: "The core engine is a Graph Neural Network (GNN) combined with a BiLSTM/BiGRU sequence modeling layer for spatial-temporal EEG feature extraction." },
    { title: "Datasets", content: "The model was trained on the Bonn University EEG database and evaluated on a diverse clinical test split." },
    { title: "Preprocessing", content: "Vectorized standard scaling across 43 EEG channels ensures normalized [0, 1] variance inputs without mutating raw signal geometry." },
    { title: "Feature Extraction", content: "Temporal and frequency domain features (mean, variance, skewness, kurtosis, bandpower) are extracted using MNE-Python." },
    { title: "Explainability", content: "Input*Gradient method is utilized to map model activations back to the original 43 EEG channels to trace decision rationales." },
    { title: "API Documentation", content: "A fully documented OpenAPI specification is available at /api/v1/docs on the backend." },
    { title: "Security Features", content: "Features include strict MIME type enforcement, 100MB upload limits, 15s inference timeouts, global exception masking, and robust rotating audit logs." },
    { title: "Future Work", content: "Integration with real-time continuous EEG streams, broader multi-center trials, and edge deployment via model quantization." }
  ];

  return (
    <div className="max-w-7xl mx-auto space-y-6 animate-in fade-in duration-500 pb-12">
      <div className="flex items-center gap-3 bg-white p-6 rounded-2xl border border-slate-200 shadow-sm">
        <BookOpen className="w-8 h-8 text-blue-600" />
        <h1 className="text-2xl font-bold text-slate-800">System Documentation</h1>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        {sections.map((sec, i) => (
          <div key={i} className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm">
            <h3 className="text-lg font-bold text-slate-800 mb-2">{sec.title}</h3>
            <p className="text-sm text-slate-600 leading-relaxed">{sec.content}</p>
          </div>
        ))}
      </div>
    </div>
  );
};

export default Documentation;
