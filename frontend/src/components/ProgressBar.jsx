// Component visualizing conversion progress.

// Exported React component
// Exported React component
export default function ProgressBar({ status }) {
  const label = status === "pending" ? "Waiting for worker..." : status === "processing" ? "Processing document..." : status === "done" ? "Ready to download" : "Failed";
  return (
    <div style={{ marginTop: 20, textAlign: "center" }}>
      <div style={{ marginBottom: 8, fontWeight: 600 }}>{label}</div>
      <div style={{ height: 12, width: "100%", background: "#e5e7eb", borderRadius: 8 }}>
        <div
          style={{
            height: "100%",
            width: status === "done" ? "100%" : status === "processing" ? "70%" : status === "pending" ? "40%" : "100%",
            background: status === "failed" ? "#ef4444" : "#2563eb",
            borderRadius: 8,
            transition: "width 0.3s ease",
          }}
        />
      </div>
    </div>
  );
}
