const riskColors = {
  HIGH: { bg: "#1A0A0A", border: "#FF4444", text: "#FF6B6B", accent: "#FF4444" },
  MEDIUM: { bg: "#1A1400", border: "#FFB800", text: "#FFD166", accent: "#FFB800" },
  LOW: { bg: "#0A1A0E", border: "#00CC6A", text: "#00FF8C", accent: "#00CC6A" },
};

export default function RiskCard({ result }) {
  const c = riskColors[result.risk_level] || riskColors.MEDIUM;
  const pct = result.churn_percentage;

  return (
    <div style={{ ...S.card, background: c.bg, borderColor: c.border }}>
      <div style={S.left}>
        <div style={S.label}>Churn Risk Assessment</div>
        <div style={{ ...S.risk, color: c.text }}>{result.risk_level} RISK</div>
        <div style={S.sub}>
          {pct < 40
            ? "This customer is unlikely to churn in the near term."
            : pct < 70
            ? "This customer shows moderate churn signals — monitor closely."
            : "Immediate retention action required — high likelihood of churn."}
        </div>
        <div style={S.meta}>
          <span style={S.metaItem}>Tenure: <b>{result.tenure} months</b></span>
          <span style={S.metaDot} />
          <span style={S.metaItem}>Monthly: <b>${result.monthly_charges}/mo</b></span>
          {result.ragas_score !== null && (
            <>
              <span style={S.metaDot} />
              <span style={S.metaItem}>AI Quality: <b>{(result.ragas_score * 100).toFixed(0)}%</b></span>
            </>
          )}
        </div>
      </div>
      <div style={S.right}>
        <div style={{ ...S.gauge, borderColor: c.accent }}>
          <span style={{ ...S.gaugeNum, color: c.text }}>{pct}%</span>
          <span style={S.gaugeLabel}>Churn<br />Probability</span>
        </div>
      </div>
    </div>
  );
}

const S = {
  card: {
    border: "1px solid", borderRadius: 14, padding: "32px 36px",
    display: "flex", alignItems: "center", justifyContent: "space-between", gap: 32,
  },
  left: { flex: 1 },
  label: { fontSize: 11, letterSpacing: "0.1em", textTransform: "uppercase", color: "#555", marginBottom: 10 },
  risk: { fontSize: 32, fontWeight: 700, letterSpacing: "-0.01em", marginBottom: 10 },
  sub: { fontSize: 14, color: "#888", lineHeight: 1.6, marginBottom: 16, maxWidth: 400 },
  meta: { display: "flex", alignItems: "center", gap: 8 },
  metaItem: { fontSize: 13, color: "#555" },
  metaDot: { width: 3, height: 3, borderRadius: "50%", background: "#333" },
  right: { flexShrink: 0 },
  gauge: {
    width: 120, height: 120, borderRadius: "50%", border: "3px solid",
    display: "flex", flexDirection: "column", alignItems: "center",
    justifyContent: "center", gap: 4,
  },
  gaugeNum: { fontSize: 28, fontWeight: 700, letterSpacing: "-0.02em" },
  gaugeLabel: { fontSize: 10, color: "#555", letterSpacing: "0.06em", textAlign: "center", textTransform: "uppercase" },
};
