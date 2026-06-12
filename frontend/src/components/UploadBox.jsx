// Component for selecting and uploading DOCX files.

import { useState } from "react";

// Exported React component
// Exported React component
export default function UploadBox({ onUpload }) {
  const [selectedFile, setSelectedFile] = useState(null);

  return (
    <div style={{ padding: 16, border: "1px solid #ddd", borderRadius: 12, maxWidth: 520, margin: "0 auto" }}>
      <label style={{ display: "block", marginBottom: 8, fontWeight: 600 }}>
        Upload DOCX file
      </label>
      <input
        type="file"
        accept=".doc,.docx"
        onChange={(e) => setSelectedFile(e.target.files?.[0] ?? null)}
        style={{ marginBottom: 12 }}
      />
      <button
        disabled={!selectedFile}
        onClick={() => onUpload(selectedFile)}
        style={{ padding: "10px 20px", borderRadius: 8, border: "none", background: "#2563eb", color: "#fff", cursor: "pointer" }}
      >
        Upload and Convert
      </button>
    </div>
  );
}
