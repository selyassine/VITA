"use client";

import { CheckCircle2, AlertTriangle, ArrowRight } from "lucide-react";
import Link from "next/link";

export default function MethodologiePage() {
  const steps = [
    {
      title: "1. Génération du Portefeuille Synthétique",
      desc: "Loi de Gompertz pour l'âge et la maturité. Les données sont purement illustratives et ne proviennent d'aucun assureur.",
      modules: "Moteur de base",
      status: "info"
    },
    {
      title: "2. Projection de la Mortalité (Lee-Carter)",
      desc: "Ajustement sur les données HMD françaises (1950-2023). Bug corrigé : horizon étendu de 50 à 90 ans pour couvrir la Vie Entière.",
      modules: "M1",
      status: "success"
    },
    {
      title: "3. Calcul du Best Estimate et SCR",
      desc: "Évaluation du passif (prospective planchée à 0) et choc SCR Solvabilité II (+15%/-20% mortalité/longévité, chocs taux EIOPA).",
      modules: "M3, M4",
      status: "success"
    },
    {
      title: "4. Gestion Actif/Passif (ALM)",
      desc: "Bilan reconstitué avec portefeuille obligataire calibré. Analyse du duration gap et sensibilité du NAV aux variations de taux.",
      modules: "M8",
      status: "success"
    },
    {
      title: "5. Risques Comportementaux et Souscription",
      desc: "Label de rachat dérivé (M5) et classification de risque sur données Prudential par Random Forest (M6).",
      modules: "M5, M6",
      status: "warning"
    },
    {
      title: "6. Optimisation et Projection",
      desc: "Optimisation du chargement commercial (M9) et projection pluriannuelle ORSA en run-off (M11).",
      modules: "M9, M11",
      status: "success"
    }
  ];

  return (
    <div style={{ minHeight: "100vh", background: "#f8fafc" }}>
      <div style={{ background: "linear-gradient(135deg, #0a0f1e 0%, #111b33 100%)", padding: "48px 24px 64px" }}>
        <div style={{ maxWidth: 900, margin: "0 auto" }}>
          <h1 style={{ fontSize: 36, fontWeight: 800, color: "white", marginBottom: 16, letterSpacing: "-0.02em" }}>
            Méthodologie &amp; Limites
          </h1>
          <p style={{ fontSize: 16, color: "rgba(255,255,255,0.6)", lineHeight: 1.6 }}>
            Ce projet de fin d&apos;études en actuariat implémente un jumeau numérique d&apos;assurance-vie. 
            La transparence sur les données utilisées et les limites des modèles est primordiale.
          </p>
        </div>
      </div>

      <div style={{ maxWidth: 900, margin: "-32px auto 64px", padding: "0 24px" }}>
        
        {/* Warning card */}
        <div className="card animate-fade-in-up" style={{ padding: 24, marginBottom: 40, borderLeft: "4px solid #f59e0b" }}>
          <div style={{ display: "flex", gap: 16 }}>
            <AlertTriangle size={24} color="#d97706" style={{ flexShrink: 0 }} />
            <div>
              <h2 style={{ fontSize: 16, fontWeight: 700, color: "#92400e", marginBottom: 8 }}>Avertissement Global sur les Données</h2>
              <p style={{ fontSize: 14.5, color: "#475569", lineHeight: 1.6, margin: 0 }}>
                La plateforme utilise un mix de <strong>données réelles publiques</strong> (HMD, EIOPA, Kaggle Prudential) et de 
                <strong>données synthétiques</strong> (Gompertz, Kaggle Retention). Elle n&apos;utilise aucune donnée confidentielle d&apos;assureur. 
                Les résultats (primes, provisions, SCR) sont des démonstrations d&apos;architecture actuarielle et ne doivent pas être 
                interprétés comme des indicateurs réels de marché.
              </p>
            </div>
          </div>
        </div>

        {/* Timeline */}
        <div style={{ position: "relative" }}>
          <div style={{ position: "absolute", top: 24, bottom: 24, left: 24, width: 2, background: "#e2e8f0" }} />
          
          <div style={{ display: "flex", flexDirection: "column", gap: 24 }}>
            {steps.map((step, i) => (
              <div key={i} className="animate-fade-in-up" style={{ animationDelay: `${i * 0.1}s`, display: "flex", gap: 24, position: "relative" }}>
                <div style={{ 
                  width: 48, height: 48, borderRadius: "50%", background: "white", border: `2px solid ${step.status === 'success' ? '#22c55e' : step.status === 'warning' ? '#f59e0b' : '#3b82f6'}`, 
                  display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0, zIndex: 10,
                  boxShadow: "0 2px 4px rgba(0,0,0,0.05)"
                }}>
                  {step.status === 'success' ? <CheckCircle2 size={20} color="#16a34a" /> : <div style={{ fontSize: 16, fontWeight: 700, color: step.status === 'warning' ? '#d97706' : '#1d4ed8' }}>{i+1}</div>}
                </div>
                
                <div className="card" style={{ padding: 24, flex: 1 }}>
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 12 }}>
                    <h3 style={{ fontSize: 16, fontWeight: 700, color: "#0f172a", margin: 0 }}>{step.title}</h3>
                    <span className="badge badge-blue">{step.modules}</span>
                  </div>
                  <p style={{ fontSize: 14.5, color: "#475569", lineHeight: 1.6, margin: 0 }}>{step.desc}</p>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div style={{ marginTop: 40, textAlign: "center" }}>
          <Link href="/modules" className="btn-primary">
            Consulter les résultats détaillés <ArrowRight size={18} />
          </Link>
        </div>
      </div>
    </div>
  );
}
