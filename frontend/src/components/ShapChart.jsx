import Plot from "react-plotly.js";

export default function ShapChart({ drivers }) {
  if (!drivers || drivers.length === 0) return null;

  const sorted = [...drivers].sort((a, b) => Math.abs(b.value) - Math.abs(a.value)).slice(0, 8);
  const features = sorted.map(d => d.feature);
  const values = sorted.map(d => d.value);
  const colors = values.map(v => v > 0 ? "#FF6B6B" : "#4D9EFF");

  return (
    <div style={S.card}>
      <div style={S.header}>
        <div style={S.title}>SHAP Driver Analysis</div>
        <div style={S.sub}>Feature attribution for this prediction</div>
      </div>
      <Plot
        data={[{
          type: "bar", orientation: "h",
          x: values, y: features,
          marker: { color: colors },
          hovertemplate: "<b>%{y}</b><br>SHAP: %{x:.4f}<extra></extra>",
        }]}
        layout={{
          paper_bgcolor: "transparent", plot_bgcolor: "transparent",
          margin: { l: 160, r: 20, t: 10, b: 40 },
          height: 280,
          xaxis: {
            gridcolor: "#1A1A1A", tickfont: { color: "#555", size: 11 },
            zeroline: true, zerolinecolor: "#333", zerolinewidth: 1,
          },
          yaxis: { tickfont: { color: "#888", size: 11 }, automargin: true },
          showlegend: false,
        }}
        config={{ displayModeBar: false, responsive: true }}
        style={{ width: "100%" }}
      />
      <div style={S.legend}>
        <span style={{ ...S.dot, background: "#FF6B6B" }} /> Increases churn risk
        <span style={{ ...S.dot, background: "#4D9EFF", marginLeft: 16 }} /> Decreases churn risk
      </div>
    </div>
  );
}

const S = {
  card: { background: "#111", border: "1px solid #1A1A1A", borderRadius: 14, padding: "24px" },
  header: { marginBottom: 16 },
  title: { fontSize: 14, fontWeight: 600, marginBottom: 4, letterSpacing: "-0.01em" },
  sub: { fontSize: 12, color: "#444" },
  legend: { fontSize: 11, color: "#444", display: "flex", alignItems: "center", gap: 6, marginTop: 8 },
  dot: { display: "inline-block", width: 8, height: 8, borderRadius: "50%" },
};
