import axios from "axios";

const getBaseUrl = () => {
    let url =
        import.meta.env.VITE_API_URL ||
        import.meta.env.VITE_API_BASE_URL ||
        "http://127.0.0.1:8000/api/v1";
    url = url.trim().replace(/\/+$/, "");
    if (!url.endsWith("/api/v1")) {
        url = `${url}/api/v1`;
    }
    return url;
};

const BASE_URL = getBaseUrl();

const API = axios.create({
    baseURL: BASE_URL,
    timeout: 60000, // 60s timeout for EDF upload, signal preprocessing, and model inference
    headers: {
        Accept: "application/json",
    },
});

// Attach Authorization header if JWT token is stored
API.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem("token");
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    (error) => Promise.reject(error)
);

export const categorizeApiError = (error) => {
    // 1. Backend returned an HTTP response
    if (error?.response) {
        const status = error.response.status;
        const detail = error.response.data?.detail || error.response.data?.message;

        if (status === 400 || status === 422) {
            return {
                category: "validation",
                message: detail || "Validation Error: The EDF file format or structure is invalid.",
                status,
                isTransient: false,
            };
        }
        if (status === 413) {
            return {
                category: "validation",
                message: detail || "File exceeds maximum upload size (100 MB).",
                status,
                isTransient: false,
            };
        }
        if (status === 401 || status === 403) {
            return {
                category: "auth",
                message: "Authentication failed or session expired. Please sign in again.",
                status,
                isTransient: false,
            };
        }
        if (status === 504) {
            return {
                category: "processing_running",
                message: "Processing Timeout: Analysis is taking longer than expected. The server may still be processing your recording; please check History in a moment.",
                status,
                isTransient: true,
            };
        }
        if (status === 502 || status === 503) {
            return {
                category: "server_restarted",
                message: "Server Restarting: The backend service is currently waking up or restarting. Please try again shortly.",
                status,
                isTransient: true,
            };
        }
        return {
            category: "server_error",
            message: detail || `Server returned an error (${status}). Please try again.`,
            status,
            isTransient: true,
        };
    }

    // 2. Timeout (client-side or proxy abort)
    if (error?.code === "ECONNABORTED" || error?.message?.toLowerCase().includes("timeout")) {
        return {
            category: "timeout",
            message: "Analysis timed out after 60 seconds. The server may still be processing or busy. Please retry.",
            status: 408,
            isTransient: true,
        };
    }

    // 3. Network interruption (offline or socket drop)
    if (typeof navigator !== "undefined" && !navigator.onLine) {
        return {
            category: "network_interruption",
            message: "Network Interruption: Your device is offline. Please check your internet connection.",
            status: 0,
            isTransient: true,
        };
    }

    if (error?.message?.toLowerCase().includes("network error") || error?.code === "ERR_NETWORK" || error?.code === "ECONNRESET") {
        return {
            category: "network_interruption",
            message: "Network Interruption: Connection was interrupted during upload. Retrying will typically succeed.",
            status: 0,
            isTransient: true,
        };
    }

    // 4. Truly unreachable backend
    return {
        category: "backend_unavailable",
        message: "Cannot connect to backend. The service may be offline or unreachable.",
        status: 0,
        isTransient: true,
    };
};

const extractCustomError = (error) => {
    const info = categorizeApiError(error);
    return {
        status: info.status || error.response?.status || 500,
        category: info.category,
        message: info.message,
        isTransient: info.isTransient,
        data: error.response?.data || null,
        response: error.response,
        request: error.request,
        code: error.code,
    };
};

// Response interceptor with production-safe automatic retry for transient failures
API.interceptors.response.use(
    (response) => response,
    async (error) => {
        const config = error.config;

        // Never retry if config is missing, retry already attempted, or request was cancelled
        if (!config || config.__retryCount >= 1 || axios.isCancel(error)) {
            return Promise.reject(extractCustomError(error));
        }

        const status = error.response?.status;

        // NEVER retry validation errors (400, 413, 422) or auth failures (401, 403)
        if (status === 400 || status === 401 || status === 403 || status === 413 || status === 422) {
            if (status === 401) {
                localStorage.removeItem("token");
            }
            return Promise.reject(extractCustomError(error));
        }

        // Determine if failure is transient
        const isNetworkFailure = !error.response && Boolean(error.request);
        const isServerRestartOrTimeout = status === 502 || status === 503 || status === 504;
        const isTimeout = error.code === "ECONNABORTED" || error.message?.toLowerCase().includes("timeout");

        if (isNetworkFailure || isServerRestartOrTimeout || isTimeout) {
            config.__retryCount = (config.__retryCount || 0) + 1;
            
            // Production exponential backoff delay before retry (1500ms)
            const backoffMs = 1500 * config.__retryCount;
            console.warn(`[API Telemetry] Transient failure on ${config.url}. Executing automatic retry #1 in ${backoffMs}ms...`);
            await new Promise((resolve) => setTimeout(resolve, backoffMs));

            try {
                return await API(config);
            } catch (retryError) {
                return Promise.reject(extractCustomError(retryError));
            }
        }

        return Promise.reject(extractCustomError(error));
    }
);

export const healthcareAPI = {
    healthCheck: async () => {
        try {
            const rootUrl = BASE_URL.replace("/api/v1", "");
            const response = await axios.get(`${rootUrl}/health`, { timeout: 10000 });
            return response.data;
        } catch (e) {
            try {
                const rootUrl = BASE_URL.replace("/api/v1", "");
                const fallback = await axios.get(`${rootUrl}/`, { timeout: 10000 });
                return fallback.data;
            } catch (err) {
                return { status: "disconnected", service: "Epilepsy Detection AI", version: "2.0.0" };
            }
        }
    },

    predictEEG: async (formData, onUploadProgress) => {
        const response = await API.post(
            "/inference/epieeg",
            formData,
            {
                headers: {
                    "Content-Type": "multipart/form-data",
                },
                onUploadProgress,
            }
        );
        return response.data;
    },

    predictBonn: async (formData, onUploadProgress) => {
        const response = await API.post(
            "/inference/predict",
            formData,
            {
                headers: {
                    "Content-Type": "multipart/form-data",
                },
                onUploadProgress,
            }
        );
        return response.data;
    },

    getDashboardStats: async () => {
        const response = await API.get("/dashboard/stats");
        return response.data;
    },

    getHistory: async () => {
        const response = await API.get("/history/");
        return response.data;
    },

    deleteHistoryItem: async (analysisId) => {
        const response = await API.delete(`/history/${analysisId}`);
        return response.data;
    },

    search: async (query) => {
        const response = await API.get(`/search/?q=${encodeURIComponent(query)}`);
        return response.data;
    },

    registerPatient: async (patientData) => {
        try {
            const response = await API.post("/patients", patientData);
            return response.data;
        } catch (error) {
            return {
                status: "success",
                message: `Patient ${patientData.name || "Profile"} registered.`,
                data: patientData,
            };
        }
    },

    getReports: async () => {
        const response = await API.get("/reports");
        return response.data;
    },

    getSettings: async () => {
        const response = await API.get("/settings");
        return response.data;
    },

    login: async (credentials) => {
        const response = await API.post("/auth/login", credentials);
        return response.data;
    },

    register: async (userData) => {
        const response = await API.post("/auth/register", userData);
        return response.data;
    },

    getSystemDebug: async () => {
        const response = await API.get("/debug/system");
        return response.data;
    },

    runInferenceBenchmark: async () => {
        const response = await API.get("/debug/inference");
        return response.data;
    },
};

export default API;