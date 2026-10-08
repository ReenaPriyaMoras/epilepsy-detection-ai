import React, { useState, useEffect } from "react";
import Plot from "react-plotly.js";
import { blobSource, openEdf, readWindow, toPhysical } from "edfcore";
import { Loader2 } from "lucide-react";

const EEGVisualization = ({ file }) => {
  const [eegData, setEegData] = useState({});
  const [selectedChannels, setSelectedChannels] = useState([]);
  const [allChannels, setAllChannels] = useState([]);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    if (!file) return;

    const parseEDF = async () => {
      setIsLoading(true);

      try {
        const source = blobSource(file);
        const edf = await openEdf(source);

        const channels = edf.header.signals;
        const channelNames = channels.map((c) => c.label);

        setAllChannels(channelNames);

        const defaultSelected = channelNames.slice(
          0,
          Math.min(4, channelNames.length)
        );

        setSelectedChannels(defaultSelected);

        const duration = Math.min(10, edf.index.durationSeconds || 10);

        const chunks = await readWindow(edf, {
          startSeconds: 0,
          durationSeconds: duration,
          signalIndices: Array.from(channels.keys()),
        });

        const parsedData = {};

        if (chunks.length > 0) {
          const chunk = chunks[0];

          channels.forEach((ch, i) => {
            const rawSignal = chunk.signals[i];

            const physicalSignal = toPhysical(ch, rawSignal);

            const sampleRate =
              physicalSignal.length / chunk.durationSeconds;

            parsedData[ch.label] = {
              x: Array.from(
                { length: physicalSignal.length },
                (_, idx) => idx / sampleRate
              ),
              y: Array.from(physicalSignal),
            };
          });
        }

        setEegData(parsedData);
      } catch (err) {
        console.warn("EDF Visualization skipped:", err);

        // Hide visualization gracefully
        setEegData({});
        setSelectedChannels([]);
        setAllChannels([]);
      } finally {
        setIsLoading(false);
      }
    };

    parseEDF();
  }, [file]);

  if (isLoading) {
    return (
      <div className="flex justify-center items-center py-10">
        <Loader2 className="w-6 h-6 animate-spin text-blue-600" />
      </div>
    );
  }

  // Nothing to show
  if (
    allChannels.length === 0 ||
    selectedChannels.length === 0
  ) {
    return null;
  }

  const toggleChannel = (channel) => {
    if (selectedChannels.includes(channel)) {
      setSelectedChannels(
        selectedChannels.filter((c) => c !== channel)
      );
    } else {
      setSelectedChannels([...selectedChannels, channel]);
    }
  };

  const plotData = selectedChannels
    .filter((c) => eegData[c])
    .map((channel) => ({
      x: eegData[channel].x,
      y: eegData[channel].y,
      type: "scatter",
      mode: "lines",
      name: channel,
      line: { width: 1.5 },
    }));

  if (plotData.length === 0) return null;

  return (
    <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-6 mt-6">
      <h2 className="text-lg font-bold text-slate-800 mb-4">
        Raw EEG Visualization
      </h2>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="md:col-span-1 border-r border-slate-200 pr-4">
          <div className="flex justify-between mb-3">
            <button
              onClick={() => setSelectedChannels(allChannels)}
              className="text-xs text-blue-600"
            >
              All
            </button>

            <button
              onClick={() => setSelectedChannels([])}
              className="text-xs text-gray-600"
            >
              Clear
            </button>
          </div>

          <div className="max-h-96 overflow-y-auto space-y-1">
            {allChannels.map((channel) => (
              <label
                key={channel}
                className="flex items-center gap-2 text-sm"
              >
                <input
                  type="checkbox"
                  checked={selectedChannels.includes(channel)}
                  onChange={() => toggleChannel(channel)}
                />

                {channel}
              </label>
            ))}
          </div>
        </div>

        <div className="md:col-span-3">
          <Plot
            data={plotData}
            layout={{
              autosize: true,
              margin: {
                l: 45,
                r: 20,
                t: 20,
                b: 45,
              },
              showlegend: true,
              hovermode: "closest",
              xaxis: {
                title: "Time (s)",
              },
              yaxis: {
                title: "Amplitude (μV)",
              },
            }}
            config={{
              responsive: true,
              displayModeBar: true,
              scrollZoom: true,
            }}
            style={{
              width: "100%",
              height: "500px",
            }}
            useResizeHandler
          />
        </div>
      </div>

      <div className="mt-6 rounded-lg bg-blue-50 border border-blue-100 p-4 text-sm text-blue-800">
        <strong>Note:</strong> EEG visualization is displayed only if the uploaded EDF
        file can be decoded in the browser. Prediction results are independent
        of this visualization.
      </div>
    </div>
  );
};

export default EEGVisualization;