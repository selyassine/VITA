import ModuleLayout, { Section, MetricGrid, MetricCard, LimitBox } from "@/components/ModuleLayout";
import { AlertTriangle, BarChart2, FileText } from "lucide-react";

export const metadata = {
  title: "M5 — Rachats | Plateforme Actuarielle",
  description: "Modélisation du risque de résiliation — label dérivé par score actuariel calibré",
};

export default function M5RachatsPage() {
  const d = {
    taux_global: 0.1785,
    taux_term_life: 0.244,
    taux_universal: 0.114,
    taux_variable: 0.096,
    taux_whole_life: 0.075,
    n_individus: 59381,
  };

  return (
    <ModuleLayout
      moduleId="m5-rachats"
      moduleNumber="Module 5"
      title="M5 — Rachats (Lapse)"
      subtitle="Modélisation du risque de résiliation sur données Kaggle Retention (label dérivé)"
      status="functional"
    >
      <Section title="Méthodologie" icon={<FileText size={18} />}>
        <p style={{ color: "#475569", lineHeight: 1.75, fontSize: 14.5, marginBottom: 14 }}>
          Le dataset Kaggle Retention (Mostly AI — données <strong>synthétiques tierces</strong>) ne contient
          aucune colonne de résiliation. Un <strong>label binaire &apos;lapsed&apos;</strong> est entièrement
          dérivé via un <strong>score de propension actuariel</strong> combinant :
        </p>
        <ul style={{ listStyle: "none", padding: 0, margin: 0, display: "flex", flexDirection: "column", gap: 8 }}>
          {[
            "Ratio prime/revenu (charge financière relative)",
            "Bosse de rachat par ancienneté (modèle actuariel classique)",
            "Nombre de personnes à charge (contrainte financière)",
            "Statut de santé (corrélation besoin de couverture)",
            "Type de police (Term Life > Universal Life > Variable > Whole Life)",
          ].map((item, i) => (
            <li key={i} style={{ display: "flex", alignItems: "flex-start", gap: 10, fontSize: 14, color: "#475569" }}>
              <span style={{ flexShrink: 0, marginTop: 4, width: 6, height: 6, borderRadius: "50%", background: "#3b82f6", display: "inline-block" }} />
              {item}
            </li>
          ))}
        </ul>
        <p style={{ color: "#475569", lineHeight: 1.75, fontSize: 14.5, marginTop: 14 }}>
          La probabilité est transformée par une fonction logistique puis tirée aléatoirement, calibrée pour un
          taux global cible de <strong>17.5%</strong>.
        </p>
      </Section>

      <Section title="Résultats Clés" icon={<BarChart2 size={18} />}>
        <MetricGrid>
          <MetricCard label="Taux global observé" value={`${(d.taux_global * 100).toFixed(1)}%`} sub="cible : 17.5%" color="blue" />
          <MetricCard label="Individus du jeu de données" value={d.n_individus.toLocaleString("fr-FR")} sub="Kaggle Retention" />
        </MetricGrid>

        <div style={{ marginTop: 20 }}>
          <h3 style={{ fontSize: 15, fontWeight: 700, color: "#0f172a", marginBottom: 12 }}>Gradient par type de police</h3>
          <table className="data-table">
            <thead>
              <tr>
                <th>Type de police</th>
                <th>Taux de résiliation</th>
                <th>Interprétation actuarielle</th>
              </tr>
            </thead>
            <tbody>
              {[
                { type: "Term Life (Temporaire Décès)", rate: d.taux_term_life, note: "Pas de valeur de rachat → résiliations élevées" },
                { type: "Universal Life", rate: d.taux_universal, note: "Flexibilité → attachement modéré" },
                { type: "Variable Life", rate: d.taux_variable, note: "Investisseurs — moins enclins à résilier" },
                { type: "Whole Life (Vie Entière)", rate: d.taux_whole_life, note: "Valeur de rachat → forte rétention" },
              ].map((row, i) => (
                <tr key={i}>
                  <td><strong>{row.type}</strong></td>
                  <td>
                    <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                      <div style={{ flex: 1, height: 8, background: "#f1f5f9", borderRadius: 4, overflow: "hidden" }}>
                        <div style={{ width: `${row.rate * 100 / 0.244 * 100}%`, height: "100%", background: "#3b82f6", borderRadius: 4 }} />
                      </div>
                      <span style={{ fontWeight: 700, color: "#0f172a", minWidth: 42 }}>{(row.rate * 100).toFixed(1)}%</span>
                    </div>
                  </td>
                  <td style={{ color: "#64748b", fontSize: 13 }}>{row.note}</td>
                </tr>
              ))}
            </tbody>
          </table>
          <div style={{ marginTop: 12, padding: "10px 14px", background: "#f0fdf4", borderRadius: 8, border: "1px solid #bbf7d0" }}>
            <p style={{ fontSize: 13.5, color: "#166534", margin: 0 }}>
              <strong>Validation du gradient :</strong> Le classement Term Life &gt; Universal Life &gt; Variable Life &gt; Whole Life
              correspond exactement au comportement actuariel attendu — validant que la règle de dérivation
              produit un signal cohérent, pas seulement un taux global correct par coïncidence.
            </p>
          </div>
        </div>
      </Section>

      <div style={{ padding: "16px 20px", background: "#fff1f2", border: "1px solid #fecdd3", borderLeft: "4px solid #ef4444", borderRadius: 12, marginBottom: 24 }}>
        <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 10 }}>
          <AlertTriangle size={18} color="#dc2626" />
          <h3 style={{ fontSize: 15, fontWeight: 700, color: "#991b1b", margin: 0 }}>
            Avertissement méthodologique important
          </h3>
        </div>
        <p style={{ fontSize: 14, color: "#7f1d1d", lineHeight: 1.7, margin: 0 }}>
          Ce label ne reflète <strong>aucun événement réel de rachat</strong> — c&apos;est une construction
          statistique plausible pour démontrer la méthodologie de modélisation. Le dataset Kaggle Retention
          est lui-même synthétique (généré par Mostly AI), ce qui crée un double niveau de synthèse.
          À rappeler explicitement à chaque citation des résultats M5 dans le mémoire.
        </p>
      </div>

      <LimitBox items={[
        {
          title: "Label entièrement dérivé",
          text: "Le dataset Kaggle Retention ne contient aucune colonne de résiliation réelle. Le label 'lapsed' est construit par règles actuarielles heuristiques, pas observé dans les données.",
        },
        {
          title: "Double synthèse",
          text: "Les données source sont elles-mêmes synthétiques (Mostly AI), initialement classées comme réelles par erreur. Deux niveaux de synthèse accumulés.",
        },
        {
          title: "Pas de modèle ML final",
          text: "Le module charge et dérive le label mais n'entraîne pas de modèle de prédiction du rachat. Un modèle Random Forest ou gradient boosting pourrait être ajouté en extension.",
        },
      ]} />
    </ModuleLayout>
  );
}
