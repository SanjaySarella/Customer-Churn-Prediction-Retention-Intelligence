export default function SimilarCustomers({ customers }) {
  if (!customers || customers.length === 0) return (
    <div style={S.card}>
      <div style={S.title}>Similar At-Risk Customers</div>
      <div style={S.empty}>No similar churned customers found in this segment.</div>
    </div>
  );

  return (
    <div style={S.card}>
      <div style={S.header}>
        <div style={S.title}>Similar At-Risk Customers</div>
        <div style={S.sub}>Historical churned customers in this segment</div>
      </div>
      <table style={S.table}>
        <thead>
          <tr>
            {["Tenure", "Monthly", "Contract", "Internet"].map(h => (
              <th key={h} style={S.th}>{h}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {customers.map((c, i) => (
            <tr key={i} style={S.tr}>
              <td style={S.td}>{c.tenure} mo</td>
              <td style={S.td}>${c.MonthlyCharges?.toFixed(0)}</td>
              <td style={S.td}>{c.Contract?.replace("-", "\n")}</td>
              <td style={S.td}>{c.InternetService}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

const S = {
  card: { background: "#111", border: "1px solid #1A1A1A", borderRadius: 14, padding: "24px" },
  header: { marginBottom: 16 },
  title: { fontSize: 14, fontWeight: 600, marginBottom: 4, letterSpacing: "-0.01em" },
  sub: { fontSize: 12, color: "#444" },
  empty: { fontSize: 13, color: "#444", padding: "20px 0" },
  table: { width: "100%", borderCollapse: "collapse" },
  th: {
    fontSize: 10, letterSpacing: "0.1em", textTransform: "uppercase",
    color: "#333", padding: "8px 12px", textAlign: "left",
    borderBottom: "1px solid #1A1A1A",
  },
  td: { fontSize: 13, color: "#888", padding: "10px 12px", borderBottom: "1px solid #111" },
  tr: {},
};
