"use client";

import Link from "next/link";
import { ArrowRight, CheckCircle, AlertTriangle } from "lucide-react";

const moduleGroups = [
  {
    title: "Données & Biométrie",
    modules: [
      { id: "m1-mortalite", name: "M1 — Mortalité", desc: "Modèle Lee-Carter sur données HMD", status: "functional" },
      { id: "m5-rachats", name: "M5 — Rachats", desc: "Label de résiliation dérivé (Kaggle)", status: "functional" },
      { id: "m6-underwriting", name: "M6 — Underwriting", desc: "Classification de risque (Prudential)", status: "functional" },
    ]
  },
  {
    title: "Tarification & Provisionnement",
    modules: [
      { id: "m2-tarification", name: "M2 — Tarification", desc: "Prime pure par équivalence actuarielle", status: "functional" },
      { id: "m3-provisionnement", name: "M3 — Provisionnement", desc: "Best Estimate prospectif (plancher 0)", status: "functional" },
    ]
  },
  {
    title: "Solvabilité & ALM",
    modules: [
      { id: "m4-scr", name: "M4 — SCR", desc: "Capital réglementaire formule standard", status: "functional" },
      { id: "m7-longevite", name: "M7 — Longévité", desc: "VaR 99.5% par Monte-Carlo", status: "functional" },
      { id: "m8-alm", name: "M8 — ALM", desc: "Bilan actif/passif et Duration Gap", status: "functional" },
    ]
  },
  {
    title: "Stratégie & Gouvernance",
    modules: [
      { id: "m9-optimizer", name: "M9 — Optimizer", desc: "Arbitrage marge/rachat sur protection", status: "functional" },
      { id: "m10-risques-emergents", name: "M10 — Risques émergents", desc: "Comparaison EIOPA vs ACPR", status: "functional" },
      { id: "m11-orsa", name: "M11 — ORSA", desc: "Projection pluriannuelle du ratio SCR", status: "functional" },
      { id: "m14-compliance", name: "M14 — Conformité", desc: "Checklist documentaire ORSA", status: "functional" },
    ]
  },
  {
    title: "Restitution & IA",
    modules: [
      { id: "m12-dashboard", name: "M12 — Dashboard", desc: "Galerie des graphiques PNG exportés", status: "functional" },
      { id: "m13-copilot", name: "M13 — Copilot IA", desc: "Interrogation NLP des résultats", status: "partial" },
      { id: "m15-digital-twin", name: "M15 — Digital Twin", desc: "Orchestration complète bout-en-bout", status: "functional" },
    ]
  }
];

export default function ModulesIndexPage() {
  return (
    <div style={{ minHeight: "100vh", background: "#f8fafc" }}>
      <div style={{ background: "linear-gradient(135deg, #0a0f1e 0%, #111b33 100%)", padding: "48px 24px 64px" }}>
        <div style={{ maxWidth: 1100, margin: "0 auto", textAlign: "center" }}>
          <h1 style={{ fontSize: 36, fontWeight: 800, color: "white", marginBottom: 16, letterSpacing: "-0.02em" }}>
            Catalogue des 15 Modules
          </h1>
          <p style={{ fontSize: 16, color: "rgba(255,255,255,0.6)", maxWidth: 600, margin: "0 auto", lineHeight: 1.6 }}>
            L&apos;architecture de la plateforme reproduit les silos d&apos;une compagnie d&apos;assurance,
            connectés entre eux par le jumeau numérique.
          </p>
        </div>
      </div>

      <div style={{ maxWidth: 1100, margin: "-32px auto 64px", padding: "0 24px" }}>
        <div style={{ display: "flex", flexDirection: "column", gap: 32 }}>
          {moduleGroups.map((group, i) => (
            <div key={i} className="animate-fade-in-up" style={{ animationDelay: `${i * 0.1}s` }}>
              <h2 style={{ fontSize: 18, fontWeight: 700, color: "#0f172a", marginBottom: 16, paddingLeft: 8, borderLeft: "4px solid #3b82f6" }}>
                {group.title}
              </h2>
              <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(320px, 1fr))", gap: 16 }}>
                {group.modules.map(mod => (
                  <Link href={`/modules/${mod.id}`} key={mod.id} className="module-card">
                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 8 }}>
                      <h3 style={{ fontSize: 16, fontWeight: 700, color: "#0f172a", margin: 0 }}>{mod.name}</h3>
                      {mod.status === "functional" ? (
                        <span style={{ display: "flex", alignItems: "center", gap: 4, fontSize: 11, fontWeight: 600, color: "#166534", background: "#dcfce7", padding: "2px 8px", borderRadius: 999 }}>
                          <CheckCircle size={12} /> OK
                        </span>
                      ) : (
                        <span style={{ display: "flex", alignItems: "center", gap: 4, fontSize: 11, fontWeight: 600, color: "#92400e", background: "#fef3c7", padding: "2px 8px", borderRadius: 999 }}>
                          <AlertTriangle size={12} /> Partiel
                        </span>
                      )}
                    </div>
                    <p style={{ fontSize: 13.5, color: "#64748b", margin: "0 0 16px", lineHeight: 1.5 }}>
                      {mod.desc}
                    </p>
                    <div style={{ display: "flex", alignItems: "center", gap: 6, fontSize: 13, fontWeight: 600, color: "#3b82f6" }}>
                      Consulter le module <ArrowRight size={14} />
                    </div>
                  </Link>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
