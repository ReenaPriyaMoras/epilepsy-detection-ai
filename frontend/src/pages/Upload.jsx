import React, { useState } from "react";
import { UploadCloud, File, AlertCircle, PlayCircle, XCircle } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { healthcareAPI } from "../services/api";
import toast, { Toaster } from "react-hot-toast";

const Upload = () => {
  const navigate = useNavigate();

  const [file, setFile] = useState(null);
  const [isPredicting, setIsPredicting] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [currentStage, setCurrentStage] = useState("");

  const handleFileSelect = (e) => {
    const selectedFile = e.target.files[0];
    if (!selectedFile) return;

    if (!selectedFile.name.toLowerCase().endsWith(".edf")) {
      toast.error("Security: Invalid file extension. Only EDF is allowed.");
      return;
    }

    if (selectedFile.size === 0) {
      toast.error("Security: Uploaded file is empty.");
      return;
    }

    const MAX_SIZE = 100 * 1024 * 1024; // 100MB
    if (selectedFile.size > MAX_SIZE) {
      toast.error("Security: File exceeds the 100 MB size limit.");
      return;
    }

    setFile(selectedFile);
    setUploadProgress(0);
    setCurrentStage("");
  };

  const handleCancel = () => {
    setFile(null);
    setUploadProgress(0);
    setCurrentStage("");
  };

  const formatBytes = (bytes, decimals = 2) => {
    if (!+bytes) return "0 Bytes";
    const k = 1024;
    const dm = decimals < 0 ? 0 : decimals;
    const sizes = ["Bytes", "KB", "MB", "GB"];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return `${parseFloat((bytes / Math.pow(k, i)).toFixed(dm))} ${sizes[i]}`;
  };

  const handlePredict = async () => {
    if (!file) {
      toast.error("Please select an EEG file first.");
      return;
    }

    setIsPredicting(true);
    setUploadProgress(0);
    setCurrentStage("Uploading EDF...");
    
    const startTime = performance.now();

    try {
      const formData = new FormData();
      formData.append("file", file);

      // Simulate multi-stage loading visually while the actual backend runs
      const stageInterval = setInterval(() => {
        setCurrentStage((prev) => {
          if (prev === "Uploading EDF..." && uploadProgress === 100) return "Reading EEG...";
          if (prev === "Reading EEG...") return "Extracting Features...";
          if (prev === "Extracting Features...") return "Scaling Features...";
          if (prev === "Scaling Features...") return "Running EpiEEG Model...";
          if (prev === "Running EpiEEG Model...") return "Generating Prediction...";
          return prev;
        });
      }, 2500);

      const result = await healthcareAPI.predictEEG(formData, (progressEvent) => {
        const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
        setUploadProgress(percentCompleted);
        if (percentCompleted === 100) setCurrentStage("Reading EEG...");
      });

      clearInterval(stageInterval);
      setCurrentStage("Done");

      const endTime = performance.now();
      const processingTime = ((endTime - startTime) / 1000).toFixed(2);

      const finalResult = {
        ...result,
        processing_time: `${processingTime}s`,
        filename: file.name,
        file_size: formatBytes(file.size)
      };

      toast.success("Prediction Completed!");

      navigate("/result", {
        state: {
          predictionData: finalResult,
          file: file,
        },
      });
    } catch (error) {
      console.error("Prediction Error:", error);
      if (error.response) {
        toast.error(error.response.data.detail || "Backend returned an error.");
      } else if (error.request) {
        toast.error("Cannot connect to backend.");
      } else {
        toast.error("Unexpected error occurred.");
      }
      setIsPredicting(false);
      setCurrentStage("");
    }
  };

  return (
    <div className="max-w-5xl mx-auto space-y-8 animate-in fade-in duration-500">
      <Toaster position="top-right" />

      <div>
        <h1 className="text-3xl font-bold text-slate-800">Upload Patient EEG</h1>
        <p className="text-slate-500 mt-2 text-lg">
          Upload standardized European Data Format (.edf) recordings for clinical AI analysis.
        </p>
      </div>

      <div className="bg-white rounded-3xl border border-slate-200 shadow-sm overflow-hidden">
        
        {/* Top Info Bar */}
        <div className="bg-slate-50 border-b border-slate-200 px-8 py-4 flex justify-between items-center text-sm font-medium text-slate-600">
          <span>Supported Format: EDF</span>
          <span>Max File Size: 100 MB</span>
        </div>

        <div className="p-10">
          {!file ? (
            <label className="border-2 border-dashed border-slate-300 bg-slate-50 hover:bg-blue-50/50 rounded-2xl p-16 flex flex-col items-center justify-center transition-all cursor-pointer group">
              <input
                type="file"
                accept=".edf"
                className="hidden"
                onChange={handleFileSelect}
              />
              <div className="w-24 h-24 bg-blue-100/50 group-hover:bg-blue-100 rounded-full flex items-center justify-center mb-6 transition-colors">
                <UploadCloud className="w-12 h-12 text-blue-600" />
              </div>
              <h3 className="text-2xl font-bold text-slate-800 mb-2">Drag & Drop EDF File</h3>
              <p className="text-slate-500 text-center mb-8">
                or click to browse your computer
              </p>
              <div className="px-8 py-3.5 bg-white border border-slate-200 shadow-sm rounded-xl font-bold text-slate-700 group-hover:border-blue-300 transition-colors">
                Browse Files
              </div>
            </label>
          ) : (
            <div className="animate-in zoom-in-95 duration-300">
              <div className="border border-slate-200 bg-white shadow-sm rounded-2xl p-6 mb-8 flex justify-between items-center">
                <div className="flex items-center gap-5">
                  <div className="bg-blue-50 p-4 rounded-xl border border-blue-100">
                    <File className="w-8 h-8 text-blue-600" />
                  </div>
                  <div>
                    <h4 className="text-lg font-bold text-slate-800">{file.name}</h4>
                    <p className="text-slate-500 font-medium">{formatBytes(file.size)}</p>
                  </div>
                </div>
                {!isPredicting && (
                  <button onClick={handleCancel} className="p-2 hover:bg-red-50 text-slate-400 hover:text-red-500 rounded-lg transition-colors" aria-label="Cancel">
                    <XCircle className="w-6 h-6" />
                  </button>
                )}
              </div>

              {isPredicting ? (
                <div className="bg-slate-50 border border-slate-200 rounded-2xl p-8 space-y-6">
                  <div className="flex justify-between items-end mb-2">
                    <span className="font-bold text-lg text-blue-800 animate-pulse">{currentStage}</span>
                    <span className="font-bold text-slate-500">{uploadProgress}%</span>
                  </div>
                  <div className="w-full bg-slate-200 rounded-full h-3 overflow-hidden">
                    <div 
                      className="bg-blue-600 h-3 transition-all duration-300 ease-out rounded-full" 
                      style={{ width: `${uploadProgress}%` }}
                    ></div>
                  </div>
                  <div className="flex items-center gap-3 text-sm font-medium text-slate-500">
                    <AlertCircle className="w-4 h-4 text-amber-500" />
                    Please do not close this tab. Analysis may take up to 15 seconds.
                  </div>
                </div>
              ) : (
                <div className="flex justify-end gap-4">
                  <button onClick={handleCancel} className="px-6 py-3.5 font-bold text-slate-600 bg-slate-100 hover:bg-slate-200 rounded-xl transition-colors">
                    Remove
                  </button>
                  <button onClick={handlePredict} className="px-8 py-3.5 font-bold text-white bg-blue-600 hover:bg-blue-700 shadow-md hover:shadow-lg rounded-xl flex items-center gap-2 transition-all">
                    <PlayCircle className="w-5 h-5" /> Analyze Recording
                  </button>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Upload;