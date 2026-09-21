import ModuleLayout, { Section, MetricGrid, MetricCard, LimitBox } from "@/components/ModuleLayout";
import { BookOpen, BarChart2 } from "lucide-react";

export const metadata = {
  title: "M3 — Provisionnement | Plateforme Actuarielle",
  description: "Provisions mathématiques par méthode prospective — Best Estimate du portefeuille",
};

export default function M3ProvissionnementPage() {
  const be = 44138580.18;

  return (
    <ModuleLayout
      moduleId="m3-provisionnement"
      moduleNumber="Module 3"
      title="M3 — Provisionnement"
      subtitle="Provision mathématique par méthode prospective — Best Estimate Solvabilité II"
      status="functional"
    >
      <Section title="Méthodologie" icon={<BookOpen size={18} />}>
        <p style={{ color: "#475569", lineHeight: 1.75, fontSize: 14.5 }}>
          La <strong>provision mathématique</strong> est calculée par la <strong>méthode prospective</strong> :
          Best Estimate = valeur actuarielle des flux de prestations futurs − valeur actuarielle des primes
          futures, pour chaque contrat individuellement, avec plancher à 0 par contrat (conforme à Solvabilité II).
          Le calcul utilise les projections Lee-Carter (M1) pour les taux de mortalité futurs et la courbe
          des taux sans risque EIOPA pour l&apos;actualisation.
        </p>
        <div style={{ marginTop: 14, padding: "12px 16px", background: "#f8fafc", borderRadius: 8, border: "1px solid #e2e8f0", fontFamily: "monospace", fontSize: 13 }}>
          <span style={{ color: "#64748b" }}>BE = max(0, </span>
          <span style={{ color: "#1e40af" }}>∑(t) Prestations(t) · v^t</span>
          <span style={{ color: "#64748b" }}> − </span>
          <span style={{ color: "#1e40af" }}>∑(t) Primes(t) · v^t</span>
          <span style={{ color: "#64748b" }}>)</span>
          <span style={{ color: "#64748b" }}> par contrat</span>
        </div>
      </Section>

      <Section title="Résultats Clés" icon={<BarChart2 size={18} />}>
        <MetricGrid>
          <MetricCard label="Best Estimate total" value={`${(be / 1e6).toFixed(1)} M€`} sub="provision mathématique agrégée" color="blue" />
          <MetricCard label="BE moyen par contrat" value={`${(be / 10000).toFixed(0)} €`} sub="sur 10 000 contrats" />
          <MetricCard label="Méthode" value="Prospective" sub="plancher 0 par contrat" color="green" />
          <MetricCard label="Cohérence M4" value="✓ Aligné" sub="réutilisé directement en SCR" color="green" />
        </MetricGrid>

        <div style={{ marginTop: 16, padding: "12px 16px", background: "#eff6ff", borderRadius: 8, border: "1px solid #bfdbfe" }}>
          <p style={{ fontSize: 13.5, color: "#1e40af", margin: 0 }}>
            <strong>Cohérence inter-modules :</strong> Le Best Estimate de M3 (44.1 M€) est réutilisé directement
            par M4 (SCR), M7 (longévité stochastique) et M8 (ALM) — garantissant la cohérence de la plateforme.
            La fonction M3 applique le plafonnement à 0 <em>par contrat</em>, ce qui était le bug de M8 corrigé.
          </p>
        </div>
      </Section>

      <Section title="Décomposition par produit" icon={<BarChart2 size={18} />}>
        <table className="data-table">
          <thead>
            <tr>
              <th>Produit</th>
              <th>Caractéristique</th>
              <th>Contribution au BE</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td><strong>Vie Entière</strong></td>
              <td>Produit d&apos;épargne à vie — provision croissante</td>
              <td>Dominante (durée + capital)</td>
            </tr>
            <tr>
              <td><strong>Temporaire Décès</strong></td>
              <td>Risque pur court terme — provision faible</td>
              <td>Faible (durée limitée)</td>
            </tr>
            <tr>
              <td><strong>Prévoyance</strong></td>
              <td>Risque d&apos;invalidité — provision intermédiaire</td>
              <td>Intermédiaire</td>
            </tr>
          </tbody>
        </table>
      </Section>

      <LimitBox items={[
        {
          title: "Dépendance à M1",
          text: "Le Best Estimate dépend des projections Lee-Carter. Toute correction de M1 (comme le bug d'horizon passé de 50 à 90 ans) modifie les valeurs de M3 — les chiffres présentés correspondent à la version corrigée.",
        },
        {
          title: "Marge de risque non calculée",
          text: "La provision technique au sens de Solvabilité II inclut Best Estimate + Marge de risque (Cost-of-Capital). Seul le Best Estimate est calculé ici — la marge de risque nécessiterait un calcul de SCR projeté sur la durée.",
        },
        {
          title: "Hypothèses de rachats",
          text: "Le modèle ne tient pas compte du risque de rachat dans les flux du passif. Un modèle complet intègrerait les probabilités de résiliation par ancienneté.",
        },
      ]} />
    </ModuleLayout>
  );
}
