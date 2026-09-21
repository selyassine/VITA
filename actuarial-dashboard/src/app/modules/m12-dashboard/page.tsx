import ModuleLayout, { Section, LimitBox, ChartImage } from "@/components/ModuleLayout";
import { LayoutDashboard, BarChart2 } from "lucide-react";
import Image from "next/image";

export const metadata = {
  title: "M12 — Dashboard | Plateforme Actuarielle",
  description: "Dashboard exécutif — 6 graphiques de synthèse exportés en PNG, robuste aux échecs partiels",
};

const figures = [
  {
    src: "/figures/m1_mortality_curve.png",
    title: "M1 — Courbe de Mortalité",
    desc: "Trajectoires Lee-Carter — historical et projetées",
  },
  {
    src: "/figures/m4_scr_breakdown.png",
    title: "M4 — Décomposition SCR",
    desc: "Ventilation du capital réglementaire par sous-module",
  },
  {
    src: "/figures/m8_alm_duration_gap.png",
    title: "M8 — Duration Gap ALM",
    desc: "Duration actif vs passif et sensibilité du NAV",
  },
  {
    src: "/figures/m9_margin_curve.png",
    title: "M9 — Courbe Marge/Chargement",
    desc: "Optimisation du chargement commercial — protection pure",
  },
  {
    src: "/figures/m10_emerging_risk_comparison.png",
    title: "M10 — Risques émergents",
    desc: "Comparaison thématique EIOPA vs ACPR",
  },
  {
    src: "/figures/m11_orsa_trajectory.png",
    title: "M11 — Trajectoire ORSA",
    desc: "Projection pluriannuelle run-off du ratio SCR",
  },
];

export default function M12DashboardPage() {
  return (
    <ModuleLayout
      moduleId="m12-dashboard"
      moduleNumber="Module 12"
      title="M12 — Dashboard Exécutif"
      subtitle="6 graphiques de synthèse — exports PNG générés automatiquement par la plateforme"
      status="functional"
    >
      <Section title="Méthodologie" icon={<LayoutDashboard size={18} />}>
        <p style={{ color: "#475569", lineHeight: 1.75, fontSize: 14.5 }}>
          M12 orchestre la génération des <strong>6 graphiques de synthèse</strong> de la plateforme.
          Chaque graphique est généré par le module source correspondant (M1, M4, M8, M9, M10, M11)
          et exporté en PNG dans <code style={{ fontFamily: "monospace", fontSize: 13, background: "#f1f5f9", padding: "1px 6px", borderRadius: 4 }}>outputs/figures/</code>.
          Le module est conçu pour être <strong>robuste aux échecs partiels</strong> : si un module
          sous-jacent échoue, le dashboard génère les graphiques disponibles et journalise l&apos;erreur
          sans interrompre l&apos;exécution des autres.
        </p>
        <div style={{ marginTop: 12, padding: "10px 14px", background: "#f0fdf4", borderRadius: 8, border: "1px solid #bbf7d0" }}>
          <p style={{ fontSize: 13.5, color: "#166534", margin: 0 }}>
            <strong>Robustesse :</strong> Tolérance aux pannes partielles par isolation des erreurs —
            pattern de développement typique d&apos;un système de production actuarielle.
          </p>
        </div>
      </Section>

      <Section title="Galerie des 6 Graphiques" icon={<BarChart2 size={18} />}>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(300px, 1fr))", gap: 20 }}>
          {figures.map((fig, i) => (
            <div key={i} className="card" style={{ overflow: "hidden" }}>
              <div style={{ background: "#f8fafc", padding: 8 }}>
                <Image
                  src={fig.src}
                  alt={fig.title}
                  width={600}
                  height={300}
                  style={{ width: "100%", height: "auto", borderRadius: 6 }}
                />
              </div>
              <div style={{ padding: "12px 14px" }}>
                <p style={{ fontWeight: 700, color: "#0f172a", fontSize: 14, margin: 0 }}>{fig.title}</p>
                <p style={{ fontSize: 12.5, color: "#64748b", marginTop: 4 }}>{fig.desc}</p>
              </div>
            </div>
          ))}
        </div>
      </Section>

      <LimitBox items={[
        {
          title: "Graphiques statiques",
          text: "Les figures sont des exports PNG statiques, pas des graphiques interactifs. Pour l'interactivité, les pages de modules utilisent Recharts ou reproduisent les résultats numériques.",
        },
        {
          title: "Dépendances en cascade",
          text: "La qualité des graphiques dépend de l'exécution préalable des modules correspondants (M1, M4, M8, M9, M10, M11). En mode run-off partiel, certains graphiques peuvent manquer.",
        },
      ]} />
    </ModuleLayout>
  );
}
