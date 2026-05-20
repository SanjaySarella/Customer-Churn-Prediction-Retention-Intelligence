import { useState } from "react";
import { predictChurn } from "./api";
import InputForm from "./components/InputForm";
import RiskCard from "./components/RiskCard";
import ShapChart from "./components/ShapChart";
import AiBrief from "./components/AiBrief";
import SimilarCustomers from "./components/SimilarCustomers";

export default function App() {
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async (formData) => {
    setLoading(true);
    setError(null);
    try {
      const data = await predictChurn(formData);
      setResult(data);
    } catch (err) {
      setError(err.response?.data?.detail || "Analysis failed. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={styles.root}>
      {/* NAV */}
      <nav style={styles.nav}>
        <span style={styles.navLogo}>CHURN INTELLIGENCE</span>
        <span style={styles.navSub}>Customer Retention System · Financial Services</span>
      </nav>

      <div style={styles.layout}>
        {/* SIDEBAR */}
        <aside style={styles.sidebar}>
          <div style={styles.sidebarHeader}>
            <h2 style={styles.sidebarTitle}>Customer Profile</h2>
            <p style={styles.sidebarSub}>Configure customer attributes and run analysis</p>
          </div>
          <InputForm onSubmit={handleSubmit} loading={loading} />
        </aside>

        {/* MAIN CONTENT */}
        <main style={styles.main}>
          {!result && !loading && (
            <div style={styles.empty}>
              <div style={styles.emptyIcon}>◎</div>
              <h3 style={styles.emptyTitle}>Configure a customer profile</h3>
              <p style={styles.emptySub}>
                Set the customer attributes in the sidebar and click
                Run Analysis to generate churn prediction, SHAP attribution,
                and AI retention strategy.
              </p>
              <div style={styles.emptyStats}>
                <div style={styles.emptyStat}>
                  <span style={styles.emptyStatNum}>7,043</span>
                  <span style={styles.emptyStatLabel}>Training Records</span>
                </div>
                <div style={styles.emptyStatDiv} />
                <div style={styles.emptyStat}>
                  <span style={styles.emptyStatNum}>$500K+</span>
                  <span style={styles.emptyStatLabel}>Recoverable Revenue</span>
                </div>
                <div style={styles.emptyStatDiv} />
                <div style={styles.emptyStat}>
                  <span style={styles.emptyStatNum}>XGBoost</span>
                  <span style={styles.emptyStatLabel}>Production Model</span>
                </div>
              </div>
            </div>
          )}

          {loading && (
            <div style={styles.loading}>
              <div style={styles.loadingSpinner} />
              <p style={styles.loadingText}>
                Running prediction pipeline...<br />
                <span style={styles.loadingSubText}>
                  XGBoost inference → SHAP attribution → LlamaIndex RAG → LangGraph agent
                </span>
              </p>
            </div>
          )}

          {error && (
            <div style={styles.error}>
              <span style={styles.errorIcon}>⚠</span>
              <span>{error}</span>
            </div>
          )}

          {result && !loading && (
            <div style={styles.results}>
              <RiskCard result={result} />
              <div style={styles.twoCol}>
                <ShapChart drivers={result.shap_drivers} />
                <SimilarCustomers customers={result.similar_customers} />
              </div>
              <AiBrief brief={result.retention_brief} score={result.ragas_score} />
            </div>
          )}
        </main>
      </div>
    </div>
  );
}

const styles = {
  root: {
    background: "#0D0D0D",
    color: "#F0F0F0",
    minHeight: "100vh",
    fontFamily: "'DM Sans', 'Helvetica Neue', sans-serif",
  },
  nav: {
    display: "flex",
    alignItems: "center",
    justifyContent: "space-between",
    padding: "18px 40px",
    borderBottom: "1px solid #1A1A1A",
    position: "sticky",
    top: 0,
    background: "rgba(13,13,13,0.95)",
    backdropFilter: "blur(12px)",
    zIndex: 100,
  },
  navLogo: {
    fontSize: 13,
    fontWeight: 700,
    letterSpacing: "0.12em",
    color: "#00FF8C",
  },
  navSub: {
    fontSize: 12,
    color: "#444",
    letterSpacing: "0.06em",
  },
  layout: {
    display: "grid",
    gridTemplateColumns: "360px 1fr",
    minHeight: "calc(100vh - 57px)",
  },
  sidebar: {
    borderRight: "1px solid #1A1A1A",
    padding: "32px 24px",
    overflowY: "auto",
  },
  sidebarHeader: {
    marginBottom: 28,
  },
  sidebarTitle: {
    fontSize: 18,
    fontWeight: 600,
    margin: "0 0 6px 0",
    letterSpacing: "-0.01em",
  },
  sidebarSub: {
    fontSize: 13,
    color: "#555",
    margin: 0,
  },
  main: {
    padding: "40px",
    overflowY: "auto",
  },
  empty: {
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    justifyContent: "center",
    minHeight: "60vh",
    textAlign: "center",
    maxWidth: 480,
    margin: "0 auto",
  },
  emptyIcon: {
    fontSize: 48,
    color: "#222",
    marginBottom: 24,
  },
  emptyTitle: {
    fontSize: 22,
    fontWeight: 400,
    margin: "0 0 12px 0",
    color: "#888",
  },
  emptySub: {
    fontSize: 14,
    color: "#444",
    lineHeight: 1.7,
    margin: "0 0 40px 0",
  },
  emptyStats: {
    display: "flex",
    alignItems: "center",
    gap: 0,
  },
  emptyStat: {
    display: "flex",
    flexDirection: "column",
    gap: 4,
    padding: "0 28px",
  },
  emptyStatNum: {
    fontSize: 22,
    fontWeight: 700,
    color: "#00FF8C",
    letterSpacing: "-0.02em",
  },
  emptyStatLabel: {
    fontSize: 11,
    color: "#333",
    letterSpacing: "0.06em",
    textTransform: "uppercase",
  },
  emptyStatDiv: {
    width: 1,
    height: 32,
    background: "#1E1E1E",
  },
  loading: {
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    justifyContent: "center",
    minHeight: "60vh",
    gap: 24,
  },
  loadingSpinner: {
    width: 40,
    height: 40,
    border: "2px solid #1E1E1E",
    borderTop: "2px solid #00FF8C",
    borderRadius: "50%",
    animation: "spin 1s linear infinite",
  },
  loadingText: {
    fontSize: 16,
    color: "#666",
    textAlign: "center",
    lineHeight: 1.8,
  },
  loadingSubText: {
    fontSize: 12,
    color: "#333",
    letterSpacing: "0.04em",
  },
  error: {
    display: "flex",
    alignItems: "center",
    gap: 12,
    background: "#1A0A0A",
    border: "1px solid #3D1515",
    borderRadius: 10,
    padding: "16px 20px",
    color: "#FF6B6B",
    fontSize: 14,
  },
  errorIcon: {
    fontSize: 18,
  },
  results: {
    display: "flex",
    flexDirection: "column",
    gap: 24,
  },
  twoCol: {
    display: "grid",
    gridTemplateColumns: "1fr 1fr",
    gap: 24,
  },
};
