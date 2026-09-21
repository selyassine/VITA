"use client";

import Link from "next/link";
import { ArrowRight, Activity, Shield, TrendingUp, ShieldCheck, Database, ServerCog, Sparkles } from "lucide-react";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";

// Simulated projection data for the hero chart
const projectionData = [
  { year: 2026, be: 44.1, scr: 4.1, funds: 30.0 },
  { year: 2027, be: 45.9, scr: 4.3, funds: 30.0 },
  { year: 2028, be: 47.9, scr: 4.6, funds: 30.0 },
  { year: 2029, be: 49.8, scr: 4.9, funds: 30.0 },
  { year: 2030, be: 51.5, scr: 5.2, funds: 30.0 },
];

export default function AccueilPage() {
  return (
    <div style={{ minHeight: "100vh", background: "#f8fafc", paddingBottom: 64 }}>
      {/* Hero Section */}
      <section className="hero-gradient" style={{ padding: "80px 24px 100px", color: "white" }}>
        <div style={{ maxWidth: 1200, margin: "0 auto", display: "grid", gridTemplateColumns: "1fr 1fr", gap: 64, alignItems: "center" }}>
          <div className="animate-fade-in-up">
            <div style={{ display: "inline-flex", alignItems: "center", gap: 8, padding: "6px 14px", background: "rgba(59,130,246,0.15)", border: "1px solid rgba(59,130,246,0.3)", borderRadius: 999, fontSize: 13, fontWeight: 600, color: "#93c5fd", marginBottom: 24 }}>
              <Sparkles size={14} />
              Soutenance Mémoire d&apos;Actuariat 2026
            </div>
            <h1 style={{ fontSize: 48, fontWeight: 800, lineHeight: 1.15, letterSpacing: "-0.02em", marginBottom: 24 }}>
              Plateforme Actuarielle Vie : <span style={{ color: "#60a5fa" }}>Digital Twin</span>
            </h1>
            <p style={{ fontSize: 18, color: "rgba(255,255,255,0.7)", lineHeight: 1.6, marginBottom: 32 }}>
              Simulation complète d&apos;une compagnie d&apos;assurance-vie. 15 modules couvrant l&apos;ensemble
              de la chaîne de valeur actuarielle : de la tarification au SCR, orchestrés par un jumeau numérique.
            </p>
            <div style={{ display: "flex", gap: 16 }}>
              <Link href="/modules" className="btn-primary" style={{ padding: "14px 24px", fontSize: 16 }}>
                Explorer les modules <ArrowRight size={18} />
              </Link>
              <Link href="/methodologie" style={{
                display: "inline-flex", alignItems: "center", padding: "14px 24px", fontSize: 16, fontWeight: 600,
                color: "white", textDecoration: "none", background: "rgba(255,255,255,0.1)", borderRadius: 8,
                transition: "background 0.2s"
              }}
              onMouseEnter={e => (e.currentTarget.style.background = "rgba(255,255,255,0.15)")}
              onMouseLeave={e => (e.currentTarget.style.background = "rgba(255,255,255,0.1)")}
              >
                Méthodologie
              </Link>
            </div>
          </div>
          
          <div className="animate-fade-in-up delay-200" style={{ position: "relative" }}>
            <div style={{ background: "rgba(15,23,42,0.6)", backdropFilter: "blur(12px)", border: "1px solid rgba(255,255,255,0.1)", borderRadius: 16, padding: 24, boxShadow: "0 24px 64px rgba(0,0,0,0.4)" }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 20 }}>
                <h3 style={{ fontSize: 15, fontWeight: 700, margin: 0, color: "white" }}>Projection ORSA (M€)</h3>
                <span className="badge badge-green">Live Preview</span>
              </div>
              <div style={{ height: 280 }}>
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={projectionData} margin={{ top: 5, right: 5, bottom: 5, left: -20 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" vertical={false} />
                    <XAxis dataKey="year" stroke="rgba(255,255,255,0.4)" fontSize={12} tickLine={false} axisLine={false} />
                    <YAxis stroke="rgba(255,255,255,0.4)" fontSize={12} tickLine={false} axisLine={false} />
                    <Tooltip 
                      contentStyle={{ background: "#0f172a", border: "1px solid #334155", borderRadius: 8, boxShadow: "0 8px 32px rgba(0,0,0,0.3)" }}
                      itemStyle={{ fontSize: 13 }}
                      labelStyle={{ color: "#94a3b8", fontSize: 12, marginBottom: 4 }}
                    />
                    <Line type="monotone" dataKey="be" name="Best Estimate" stroke="#3b82f6" strokeWidth={3} dot={{ r: 4, fill: "#3b82f6", strokeWidth: 0 }} />
                    <Line type="monotone" dataKey="funds" name="Fonds Propres" stroke="#10b981" strokeWidth={3} dot={false} strokeDasharray="5 5" />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* KPI Grid */}
      <section style={{ maxWidth: 1200, margin: "-40px auto 60px", padding: "0 24px", position: "relative", zIndex: 10 }}>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 20 }}>
          {[
            { label: "Portefeuille", value: "10 000", sub: "contrats synthétiques", icon: <Database size={20} color="#3b82f6" /> },
            { label: "Best Estimate", value: "44.1 M€", sub: "M3 Provisionnement", icon: <Shield size={20} color="#8b5cf6" /> },
            { label: "Ratio SCR", value: "7.38×", sub: "Solvabilité II", icon: <Activity size={20} color="#10b981" /> },
            { label: "Pipeline", value: "15", sub: "modules de bout en bout", icon: <ServerCog size={20} color="#f59e0b" /> },
          ].map((kpi, i) => (
            <div key={i} className={`card animate-fade-in-up delay-${(i+3)*100}`} style={{ padding: "24px", background: "white" }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 16 }}>
                <p style={{ fontSize: 13, fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.05em", color: "#64748b", margin: 0 }}>
                  {kpi.label}
                </p>
                <div style={{ background: "#f8fafc", padding: 8, borderRadius: 8 }}>
                  {kpi.icon}
                </div>
              </div>
              <p style={{ fontSize: 32, fontWeight: 800, color: "#0f172a", lineHeight: 1, margin: "0 0 8px" }}>
                {kpi.value}
              </p>
              <p style={{ fontSize: 13, color: "#94a3b8", margin: 0 }}>{kpi.sub}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Pillars */}
      <section style={{ maxWidth: 1200, margin: "0 auto", padding: "0 24px" }}>
        <div className="section-header">
          <h2 style={{ fontSize: 24 }}>Piliers du projet</h2>
        </div>
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 24 }}>
          {[
            {
              icon: <TrendingUp size={24} color="#2563eb" />,
              title: "Rigueur Méthodologique",
              desc: "Implémentation stricte des normes Solvabilité II (Best Estimate prospectif, chocs SCR réglementaires, courbes EIOPA).",
            },
            {
              icon: <ServerCog size={24} color="#059669" />,
              title: "Industrialisation",
              desc: "Pipeline de 15 modules orchestré par un jumeau numérique, export JSON centralisé, génération automatisée de reportings.",
            },
            {
              icon: <ShieldCheck size={24} color="#d97706" />,
              title: "Transparence",
              desc: "Toutes les limites (données synthétiques, simplifications) sont explicitement documentées dans chaque module.",
            },
          ].map((pillar, i) => (
            <div key={i} style={{ background: "white", borderRadius: 16, padding: 32, border: "1px solid #e2e8f0" }}>
              <div style={{ width: 48, height: 48, borderRadius: 12, background: "#f1f5f9", display: "flex", alignItems: "center", justifyContent: "center", marginBottom: 20 }}>
                {pillar.icon}
              </div>
              <h3 style={{ fontSize: 18, fontWeight: 700, color: "#0f172a", marginBottom: 12 }}>{pillar.title}</h3>
              <p style={{ fontSize: 14.5, color: "#475569", lineHeight: 1.6, margin: 0 }}>{pillar.desc}</p>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}
