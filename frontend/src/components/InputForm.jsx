import { useState } from "react";

const S = {
  form: { display: "flex", flexDirection: "column", gap: 16 },
  group: { display: "flex", flexDirection: "column", gap: 6 },
  label: { fontSize: 11, color: "#555", letterSpacing: "0.08em", textTransform: "uppercase" },
  input: {
    background: "#111", border: "1px solid #222", borderRadius: 8,
    color: "#F0F0F0", fontSize: 13, padding: "10px 14px", outline: "none",
    fontFamily: "inherit", transition: "border-color 0.2s",
  },
  select: {
    background: "#111", border: "1px solid #222", borderRadius: 8,
    color: "#F0F0F0", fontSize: 13, padding: "10px 14px", outline: "none",
    fontFamily: "inherit", width: "100%",
  },
  toggle: {
    display: "flex", alignItems: "center", justifyContent: "space-between",
    background: "#111", border: "1px solid #222", borderRadius: 8,
    padding: "10px 14px", cursor: "pointer",
  },
  toggleLabel: { fontSize: 13, color: "#F0F0F0" },
  toggleDot: (active) => ({
    width: 36, height: 20, background: active ? "#00FF8C22" : "#222",
    border: `1px solid ${active ? "#00FF8C" : "#333"}`,
    borderRadius: 20, position: "relative", transition: "all 0.2s",
  }),
  toggleKnob: (active) => ({
    width: 14, height: 14, borderRadius: "50%",
    background: active ? "#00FF8C" : "#444",
    position: "absolute", top: 2,
    left: active ? 18 : 2, transition: "all 0.2s",
  }),
  divider: { borderTop: "1px solid #1A1A1A", margin: "4px 0" },
  sectionLabel: { fontSize: 10, color: "#333", letterSpacing: "0.12em", textTransform: "uppercase" },
  btn: {
    background: "#00FF8C", color: "#000", border: "none", borderRadius: 8,
    padding: "14px", fontSize: 14, fontWeight: 700, cursor: "pointer",
    letterSpacing: "0.04em", marginTop: 8, fontFamily: "inherit",
    transition: "opacity 0.2s",
  },
  btnDisabled: { opacity: 0.5, cursor: "not-allowed" },
  rangeWrap: { display: "flex", flexDirection: "column", gap: 4 },
  rangeVal: { fontSize: 20, fontWeight: 700, color: "#00FF8C", letterSpacing: "-0.02em" },
  range: { width: "100%", accentColor: "#00FF8C" },
};

const Toggle = ({ label, value, onChange }) => (
  <div style={S.toggle} onClick={() => onChange(!value)}>
    <span style={S.toggleLabel}>{label}</span>
    <div style={S.toggleDot(value)}>
      <div style={S.toggleKnob(value)} />
    </div>
  </div>
);

const Select = ({ label, value, onChange, options }) => (
  <div style={S.group}>
    <label style={S.label}>{label}</label>
    <select style={S.select} value={value} onChange={e => onChange(e.target.value)}>
      {options.map(o => <option key={o} value={o}>{o}</option>)}
    </select>
  </div>
);

export default function InputForm({ onSubmit, loading }) {
  const [form, setForm] = useState({
    gender: "Male", senior_citizen: false, partner: false,
    dependents: false, tenure: 12, phone_service: true,
    multiple_lines: "No", internet_service: "DSL",
    online_security: "No", online_backup: "No",
    device_protection: "No", tech_support: "No",
    streaming_tv: "No", streaming_movies: "No",
    contract: "Month-to-month", paperless_billing: true,
    payment_method: "Electronic check", monthly_charges: 65,
  });

  const set = (key) => (val) => setForm(f => ({ ...f, [key]: val }));

  return (
    <form style={S.form} onSubmit={e => { e.preventDefault(); onSubmit(form); }}>

      <span style={S.sectionLabel}>Personal</span>
      <Select label="Gender" value={form.gender} onChange={set("gender")} options={["Male", "Female"]} />
      <Toggle label="Senior Citizen" value={form.senior_citizen} onChange={set("senior_citizen")} />
      <Toggle label="Has Partner" value={form.partner} onChange={set("partner")} />
      <Toggle label="Has Dependents" value={form.dependents} onChange={set("dependents")} />

      <div style={S.divider} />
      <span style={S.sectionLabel}>Service</span>

      <div style={S.rangeWrap}>
        <label style={S.label}>Tenure (months)</label>
        <span style={S.rangeVal}>{form.tenure} mo</span>
        <input type="range" min={0} max={72} value={form.tenure}
          onChange={e => set("tenure")(+e.target.value)} style={S.range} />
      </div>

      <div style={S.rangeWrap}>
        <label style={S.label}>Monthly Charges ($)</label>
        <span style={S.rangeVal}>${form.monthly_charges}</span>
        <input type="range" min={18} max={120} value={form.monthly_charges}
          onChange={e => set("monthly_charges")(+e.target.value)} style={S.range} />
      </div>

      <Toggle label="Phone Service" value={form.phone_service} onChange={set("phone_service")} />
      <Select label="Internet Service" value={form.internet_service}
        onChange={set("internet_service")} options={["DSL", "Fiber optic", "No"]} />
      <Select label="Multiple Lines" value={form.multiple_lines}
        onChange={set("multiple_lines")} options={["No", "Yes", "No phone service"]} />

      <div style={S.divider} />
      <span style={S.sectionLabel}>Add-ons</span>

      {[["Online Security", "online_security"],
        ["Online Backup", "online_backup"],
        ["Device Protection", "device_protection"],
        ["Tech Support", "tech_support"],
        ["Streaming TV", "streaming_tv"],
        ["Streaming Movies", "streaming_movies"]
      ].map(([label, key]) => (
        <Select key={key} label={label} value={form[key]}
          onChange={set(key)} options={["No", "Yes", "No internet service"]} />
      ))}

      <div style={S.divider} />
      <span style={S.sectionLabel}>Billing</span>

      <Select label="Contract" value={form.contract} onChange={set("contract")}
        options={["Month-to-month", "One year", "Two year"]} />
      <Toggle label="Paperless Billing" value={form.paperless_billing} onChange={set("paperless_billing")} />
      <Select label="Payment Method" value={form.payment_method} onChange={set("payment_method")}
        options={["Electronic check", "Mailed check", "Bank transfer (automatic)", "Credit card (automatic)"]} />

      <button type="submit" style={{ ...S.btn, ...(loading ? S.btnDisabled : {}) }} disabled={loading}>
        {loading ? "Analysing..." : "Run Churn Analysis"}
      </button>
    </form>
  );
}
