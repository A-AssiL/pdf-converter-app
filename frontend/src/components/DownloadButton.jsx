export default function DownloadButton({ url }) {
  if (!url) {
    return null;
  }

  return (
    <div style={{ marginTop: 20, textAlign: "center" }}>
      <a
        href={url}
        download
        style={{ display: "inline-block", padding: "10px 20px", background: "#10b981", color: "#fff", borderRadius: 8, textDecoration: "none" }}
      >
        Download PDF
      </a>
    </div>
  );
}
