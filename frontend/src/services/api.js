// Frontend API helper module for upload and status endpoints.

// Constant declaration
// Constant declaration
const API_BASE = "/api";

// Exported async function
// Exported async function
export async function uploadDocument(file) {
  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch(`${API_BASE}/upload/`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || "Upload failed");
  }

  return response.json();
}

// Exported async function
// Exported async function
export async function getJobStatus(jobId) {
  const response = await fetch(`${API_BASE}/status/${jobId}`);
  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || "Could not fetch status.");
  }
  return response.json();
}
