import { useEffect, useState } from "react";
import UploadBox from "../components/UploadBox";
import ProgressBar from "../components/ProgressBar";
import DownloadButton from "../components/DownloadButton";
import { getJobStatus, uploadDocument } from "../services/api";

export default function Home() {
  const [jobId, setJobId] = useState(null);
  const [status, setStatus] = useState(null);
  const [downloadUrl, setDownloadUrl] = useState(null);
  const [message, setMessage] = useState("");
  const [error, setError] = useState(null);

  useEffect(() => {
    let interval = null;

    if (jobId && status && status !== "done" && status !== "failed") {
      interval = setInterval(async () => {
        const response = await getJobStatus(jobId);
        setStatus(response.status);
        setDownloadUrl(response.download_url);
        setError(response.error);
      }, 2000);
    }

    return () => {
      if (interval) {
        clearInterval(interval);
      }
    };
  }, [jobId, status]);

  async function handleUpload(file) {
    setError(null);
    setMessage("Uploading file...");
    setStatus("pending");
    setDownloadUrl(null);

    try {
      const result = await uploadDocument(file);
      setJobId(result.job_id);
      setStatus(result.status);
      setMessage(result.message);
    } catch (err) {
      setError(err.message || "Upload failed.");
      setStatus("failed");
    }
  }

  return (
    <div style={{ fontFamily: "Inter, sans-serif", minHeight: "100vh", background: "#f8fafc", padding: 24 }}>
      <div style={{ maxWidth: 760, margin: "0 auto", background: "#fff", padding: 32, borderRadius: 24, boxShadow: "0 20px 60px rgba(0,0,0,.08)" }}>
        <h1 style={{ marginBottom: 16 }}>Word to PDF Converter</h1>
        <p style={{ lineHeight: 1.8, color: "#374151" }}>
          Upload a DOCX document and let the worker pipeline convert it into a downloadable PDF file.
        </p>

        <UploadBox onUpload={handleUpload} />

        {message && <p style={{ marginTop: 20 }}>{message}</p>}
        {status && <ProgressBar status={status} />}
        {error && <p style={{ marginTop: 12, color: "#dc2626" }}>{error}</p>}
        {downloadUrl && <DownloadButton url={downloadUrl} />}
      </div>
    </div>
  );
}
