import React from 'react';
import Plot from 'react-plotly.js';
import { Brain, Activity, Info, BarChart3 } from 'lucide-react';

const XAIDashboard = ({ explainability }) => {
  if (!explainability) {
    return (
      <div className="bg-slate-50 border border-slate-200 rounded-3xl p-10 flex flex-col items-center justify-center text-center">
        <Info className="w-10 h-10 text-slate-400 mb-4" />
        <h3 className="font-bold text-slate-600 mb-2">Explainability Unavailable</h3>
        <p className="text-sm text-slate-500">The prediction was successful, but feature attribution could not be computed.</p>
      </div>
    );
  }

  const { top_channels, top_features, summary, time_ms } = explainability;

  // Prepare Plotly Chart Data for Channels
  const channelChartData = [
    {
      x: top_channels.map((c) => c.importance * 100),
      y: top_channels.map((c) => c.name),
      type: 'bar',
      orientation: 'h',
      marker: {
        color: 'rgba(59, 130, 246, 0.8)', // blue-500
        borderRadius: 4
      }
    }
  ];

  // Prepare Plotly Chart Data for Features
  const featureChartData = [
    {
      x: top_features.map((f) => f.importance * 100),
      y: top_features.map((f) => f.name),
      type: 'bar',
      orientation: 'h',
      marker: {
        color: 'rgba(16, 185, 129, 0.8)', // emerald-500
        borderRadius: 4
      }
    }
  ];

  const layoutConfig = {
    autosize: true,
    margin: { l: 100, r: 20, t: 20, b: 40 },
    xaxis: { title: 'Relative Importance (%)' },
    yaxis: { autorange: 'reversed' }
  };

  return (
    <div className="space-y-6 mt-8">
      <div className="flex items-center gap-3">
        <Brain className="w-6 h-6 text-blue-600" />
        <h2 className="text-xl font-bold text-slate-800">Explainable AI (XAI) Analysis</h2>
        <span className="text-xs font-semibold bg-blue-100 text-blue-700 px-2 py-1 rounded-full">
          Computed in {time_ms}ms
        </span>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Card 3: Clinical Summary */}
        <div className="lg:col-span-3 bg-white rounded-2xl border border-slate-200 shadow-sm p-6 bg-gradient-to-r from-blue-50 to-white">
          <h3 className="text-sm font-bold uppercase tracking-widest text-slate-500 mb-3 flex items-center gap-2">
            <Info className="w-4 h-4" /> Explanation Summary
          </h3>
          <p className="text-slate-700 font-medium leading-relaxed">
            {summary}
          </p>
        </div>

        {/* Card 1: Top Channels List */}
        <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-6">
          <h3 className="text-sm font-bold uppercase tracking-widest text-slate-500 mb-4 flex items-center gap-2">
            <Activity className="w-4 h-4" /> Influential Channels
          </h3>
          <div className="space-y-4">
            {top_channels.map((channel, idx) => (
              <div key={idx}>
                <div className="flex justify-between text-sm mb-1">
                  <span className="font-bold text-slate-700">{channel.name}</span>
                  <span className="text-slate-500">{(channel.importance * 100).toFixed(1)}%</span>
                </div>
                <div className="w-full bg-slate-100 rounded-full h-2">
                  <div className="bg-blue-500 h-2 rounded-full" style={{ width: `${Math.min(100, channel.importance * 100)}%` }}></div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Card 2: Top Features List */}
        <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-6">
          <h3 className="text-sm font-bold uppercase tracking-widest text-slate-500 mb-4 flex items-center gap-2">
            <BarChart3 className="w-4 h-4" /> Top Features
          </h3>
          <div className="space-y-4">
            {top_features.map((feature, idx) => (
              <div key={idx}>
                <div className="flex justify-between text-sm mb-1">
                  <span className="font-bold text-slate-700">{feature.name}</span>
                  <span className="text-slate-500">{(feature.importance * 100).toFixed(1)}%</span>
                </div>
                <div className="w-full bg-slate-100 rounded-full h-2">
                  <div className="bg-emerald-500 h-2 rounded-full" style={{ width: `${Math.min(100, feature.importance * 100)}%` }}></div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Card 4: Interactive Charts */}
        <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-6 overflow-hidden flex items-center justify-center min-h-[300px]">
           <Plot
              data={featureChartData}
              layout={{ ...layoutConfig, title: 'Feature Attribution (Global)' }}
              useResizeHandler={true}
              style={{ width: '100%', height: '100%' }}
              config={{ responsive: true, displayModeBar: false }}
            />
        </div>

      </div>
    </div>
  );
};

export default XAIDashboard;
