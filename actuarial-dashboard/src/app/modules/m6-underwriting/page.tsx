import ModuleLayout, { Section, MetricGrid, MetricCard, LimitBox } from "@/components/ModuleLayout";
import { Brain, Database, BarChart2 } from "lucide-react";

export const metadata = {
  title: "M6 — Underwriting | Plateforme Actuarielle",
  description: "Modèle baseline Random Forest de classification du risque assuré — données Prudential Kaggle",
};

export default function M6UnderwritingPage() {
  const d = {
    n_individus: 59381,
    n_colonnes: 128,
    dataset: "Prudential Life Insurance Assessment (Kaggle)",
    modele: "Random Forest (baseline)",
  };

  return (
    <ModuleLayout
      moduleId="m6-underwriting"
      moduleNumber="Module 6"
      title="M6 — Underwriting"
      subtitle="Classification du risque à la souscription — Random Forest baseline sur données Prudential"
      status="functional"
    >
      <Section title="Méthodologie" icon={<Brain size={18} />}>
        <p style={{ color: "#475569", lineHeight: 1.75, fontSize: 14.5 }}>
          Le module entraîne un modèle baseline de <strong>classification du risque assuré</strong> à la
          souscription. La variable cible est le niveau de risque (classe 1-8) défini par Prudential Financial.
          Le modèle utilisé est un <strong>Random Forest</strong> avec paramètres par défaut comme benchmark,
          entraîné sur le dataset Kaggle Prudential (données réelles anonymisées, 128 features incluant
          données médicales, habitudes de vie, antécédents familiaux).
        </p>
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12, marginTop: 16 }}>
          {[
            { label: "Objectif", value: "Prédire la classe de risque (1-8)" },
            { label: "Algorithme", value: "Random Forest (n=100, profondeur non limitée)" },
            { label: "Validation", value: "Train/test split, métriques classification" },
            { label: "Features", value: "128 variables (médicales, comportement, antécédents)" },
          ].map(item => (
            <div key={item.label} style={{ background: "#f8fafc", border: "1px solid #e2e8f0", borderRadius: 8, padding: "12px 14px" }}>
              <p style={{ fontSize: 12, fontWeight: 700, color: "#94a3b8", textTransform: "uppercase", letterSpacing: "0.08em", margin: 0 }}>{item.label}</p>
              <p style={{ fontSize: 14, fontWeight: 600, color: "#0f172a", marginTop: 4, margin: 0, marginTop: 4 }}>{item.value}</p>
            </div>
          ))}
        </div>
      </Section>

      <Section title="Résultats Clés" icon={<BarChart2 size={18} />}>
        <MetricGrid>
          <MetricCard label="Individus d'entraînement" value={d.n_individus.toLocaleString("fr-FR")} sub="données Prudential Kaggle" color="blue" />
          <MetricCard label="Features utilisées" value="128" sub="variables médicales et comportementales" />
          <MetricCard label="Classes de risque" value="8" sub="de 1 (faible risque) à 8 (haut risque)" />
          <MetricCard label="Modèle" value="Baseline" sub="Random Forest par défaut" color="amber" />
        </MetricGrid>

        <div style={{ marginTop: 16, padding: "14px 18px", background: "#eff6ff", border: "1px solid #bfdbfe", borderRadius: 8 }}>
          <p style={{ fontSize: 13.5, color: "#1e40af", margin: 0 }}>
            <strong>Mode rapide (quick=True) :</strong> Dans l&apos;orchestration M15 (Digital Twin), M6
            s&apos;exécute en mode rapide et retourne uniquement les statistiques du dataset sans entraîner
            le modèle complet, pour des raisons de performance. L&apos;entraînement complet est disponible
            via <code style={{ fontFamily: "monospace", fontSize: 12, background: "#dbeafe", padding: "1px 5px", borderRadius: 3 }}>quick=False</code>.
          </p>
        </div>
      </Section>

      <Section title="Source de données" icon={<Database size={18} />}>
        <table className="data-table">
          <thead>
            <tr>
              <th>Source</th>
              <th>Nature</th>
              <th>Licence</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td><strong>Prudential Life Insurance Assessment</strong></td>
              <td><span className="badge badge-green">Réelle tierce anonymisée</span></td>
              <td>Kaggle — usage éducatif</td>
            </tr>
          </tbody>
        </table>
      </Section>

      <LimitBox items={[
        {
          title: "Modèle baseline uniquement",
          text: "Le Random Forest est un point de départ, pas un modèle de production. Un modèle avancé (XGBoost, LightGBM, avec optimisation des hyperparamètres) pourrait améliorer significativement les performances.",
        },
        {
          title: "Données américaines",
          text: "Le dataset Prudential concerne le marché américain. Les classes de risque et les critères médicaux peuvent différer significativement du marché français.",
        },
        {
          title: "Mode rapide en M15",
          text: "L'exécution dans l'orchestrateur Digital Twin (M15) utilise quick=True : seules les statistiques du dataset sont retournées, sans entraînement du modèle.",
        },
      ]} />
    </ModuleLayout>
  );
}
