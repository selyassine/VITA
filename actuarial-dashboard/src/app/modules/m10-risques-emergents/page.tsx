import ModuleLayout, { Section, MetricGrid, MetricCard, LimitBox, ChartImage } from "@/components/ModuleLayout";
import { Globe, BarChart2, FileSearch } from "lucide-react";

export const metadata = {
  title: "M10 — Risques émergents | Plateforme Actuarielle",
  description: "Comparaison thématique EIOPA vs ACPR — analyse de contenu des rapports de supervision",
};

export default function M10EmergingRiskPage() {
  const themes = [
    { id: "immobilier_liquidite", label: "Immobilier & Liquidité", score: 3.163 },
    { id: "ia_digitalisation",   label: "IA & Digitalisation",    score: 2.474 },
    { id: "cyber",               label: "Cyber",                   score: 1.563 },
    { id: "macro_taux",          label: "Macro & Taux",            score: 1.065 },
    { id: "geopolitique",        label: "Géopolitique",            score: 0.533 },
    { id: "climat_transition",   label: "Climat & Transition",     score: 0.065 },
  ];

  const maxScore = themes[0].score;

  const docs = [
    { name: "EIOPA Financial Stability Report", dominant: "Immobilier & Liquidité", coverage: "Cyber, IA, Immobilier (7-8 occ./1000 mots)" },
    { name: "ACPR — Assurance Vie 2025",        dominant: "Macro & Taux",           coverage: "Centré sur solvabilité/flux, peu de cyber/IA" },
    { name: "ACPR — Situation Assureurs S1-2025",dominant: "Immobilier & Liquidité", coverage: "Proche EIOPA sur ce thème" },
  ];

  return (
    <ModuleLayout
      moduleId="m10-risques-emergents"
      moduleNumber="Module 10"
      title="M10 — Risques Émergents"
      subtitle="Comparaison thématique EIOPA vs ACPR — analyse de contenu des rapports de supervision"
      status="functional"
    >
      <Section title="Méthodologie" icon={<FileSearch size={18} />}>
        <p style={{ color: "#475569", lineHeight: 1.75, fontSize: 14.5 }}>
          <strong>Recadrage assumé :</strong> l&apos;ambition initiale (détecteur de tendance temporelle) nécessitait
          des éditions successives d&apos;un même rapport. Les 3 documents disponibles (EIOPA + 2 ACPR) ne
          permettent pas d&apos;analyse temporelle. M10 a été recadré en{" "}
          <strong>comparaison thématique inter-rapports</strong> : fréquence normalisée de 6 familles
          de mots-clés dans chaque document, produisant un{" "}
          <strong>score thématique par-1000-mots</strong>.
        </p>
        <div style={{ marginTop: 14, padding: "12px 16px", background: "#eff6ff", border: "1px solid #bfdbfe", borderRadius: 8 }}>
          <p style={{ fontSize: 13.5, color: "#1e40af", margin: 0 }}>
            <strong>Résultat défendable :</strong> Le contraste observé entre le niveau de supervision
            européen (EIOPA, très actif sur cyber/IA/immobilier) et les publications ACPR analysées (davantage
            centrées sur flux/solvabilité) est un résultat citable en soi, indépendamment de la tendance temporelle.
          </p>
        </div>
      </Section>

      <Section title="Thèmes dominants par document" icon={<Globe size={18} />}>
        <table className="data-table">
          <thead>
            <tr>
              <th>Document</th>
              <th>Thème dominant</th>
              <th>Couverture observée</th>
            </tr>
          </thead>
          <tbody>
            {docs.map((doc, i) => (
              <tr key={i}>
                <td><strong>{doc.name}</strong></td>
                <td><span className="badge badge-blue">{doc.dominant}</span></td>
                <td style={{ color: "#64748b", fontSize: 13 }}>{doc.coverage}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </Section>

      <Section title="Classement global des thèmes" icon={<BarChart2 size={18} />}>
        <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
          {themes.map((t, i) => (
            <div key={t.id}>
              <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 4 }}>
                <span style={{ fontSize: 13.5, fontWeight: 600, color: "#334155" }}>
                  {i + 1}. {t.label}
                </span>
                <span style={{ fontSize: 13, fontWeight: 700, color: "#0f172a" }}>
                  {t.score.toFixed(3)} / 1000 mots
                </span>
              </div>
              <div style={{ height: 10, background: "#f1f5f9", borderRadius: 5, overflow: "hidden" }}>
                <div style={{
                  height: "100%",
                  width: `${(t.score / maxScore) * 100}%`,
                  background: i === 0 ? "#3b82f6" : i === 1 ? "#8b5cf6" : i === 2 ? "#06b6d4" : "#94a3b8",
                  borderRadius: 5,
                  transition: "width 0.5s ease",
                }} />
              </div>
            </div>
          ))}
        </div>
      </Section>

      <Section title="Visualisation comparative" icon={<BarChart2 size={18} />}>
        <ChartImage
          src="/figures/m10_emerging_risk_comparison.png"
          alt="Comparaison thématique EIOPA vs ACPR"
          caption="Scores thématiques normalisés (occurrences pour 1000 mots) par document et par famille de risques émergents."
        />
      </Section>

      <LimitBox items={[
        {
          title: "Limite de reproductibilité stricte",
          text: "Les comptages de mots-clés ont été extraits avec l'aide d'un autre modèle de langage sur le texte des PDF sources (l'environnement de développement ne pouvait pas télécharger les PDF). Un script déterministe (extract_from_pdfs.py, regex + pdfplumber) est fourni mais n'a pas été exécuté.",
        },
        {
          title: "Pas de tendance temporelle",
          text: "Le recadrage en comparaison thématique est défendable mais différent de l'objectif initial. Une vraie analyse de tendance nécessiterait des éditions successives d'un même rapport (ex. EIOPA 2023, 2024, 2025).",
        },
        {
          title: "Analyse lexicale uniquement",
          text: "Les scores reflètent la fréquence des mots-clés, pas la profondeur de l'analyse des régulateurs. Un document peut mentionner peu 'cyber' tout en ayant une politique cyber très développée.",
        },
      ]} />
    </ModuleLayout>
  );
}
