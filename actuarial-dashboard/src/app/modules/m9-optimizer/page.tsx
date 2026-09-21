import ModuleLayout, { Section, MetricGrid, MetricCard, LimitBox, ChartImage } from "@/components/ModuleLayout";
import { TrendingUp, BarChart2, Zap } from "lucide-react";

export const metadata = {
  title: "M9 — Optimizer | Plateforme Actuarielle",
  description: "Chargement commercial optimal — arbitrage marge/rachat pour produits de protection pure",
};

export default function M9OptimizerPage() {
  const d = {
    optimal_loading: 1.5,
    lapse_elasticity: 2.0,
    total_margin_optimal: 2543716.58,
    total_margin_reference: 2276867.53,
    n_policies_priced: 2350,
    scr_biometrique_baseline: 4067046.06,
    scr_biometrique_optimal: 3973142.28,
    solvency_ratio_baseline: 7.3764,
    solvency_ratio_optimal: 7.5507,
    own_funds: 30000000,
    gain_marge_pct: ((2543716.58 - 2276867.53) / 2276867.53 * 100),
  };

  return (
    <ModuleLayout
      moduleId="m9-optimizer"
      moduleNumber="Module 9"
      title="M9 — Optimizer"
      subtitle="Chargement commercial optimal — arbitrage marge / rachat (protection pure uniquement)"
      status="functional"
    >
      <Section title="Méthodologie" icon={<Zap size={18} />}>
        <p style={{ color: "#475569", lineHeight: 1.75, fontSize: 14.5 }}>
          Le modèle d&apos;arbitrage suppose que le <strong>taux de rachat augmente avec le chargement</strong>{" "}
          commercial selon une élasticité constante ε. La marge totale (prime commerciale − prime pure) est
          maximisée analytiquement — le chargement optimal est donné par la <strong>formule fermée</strong> :
        </p>
        <div style={{ marginTop: 14, padding: "14px 18px", background: "#f8fafc", borderRadius: 8, border: "1px solid #e2e8f0", fontFamily: "monospace", fontSize: 15, textAlign: "center" }}>
          <span style={{ color: "#64748b" }}>Chargement optimal = </span>
          <span style={{ color: "#1e40af", fontWeight: 700 }}>1 + 1 / ε</span>
          <span style={{ color: "#64748b" }}>  où ε = élasticité au rachat</span>
        </div>
        <p style={{ color: "#475569", lineHeight: 1.75, fontSize: 14.5, marginTop: 14 }}>
          Périmètre : <strong>produits de protection pure uniquement</strong> (Temporaire Décès et Prévoyance).
          La Vie Entière est <strong>explicitement exclue</strong> (bug corrigé — voir limites).
        </p>
      </Section>

      <Section title="Résultats Clés" icon={<BarChart2 size={18} />}>
        <MetricGrid>
          <MetricCard label="Chargement optimal" value={`${d.optimal_loading.toFixed(1)}×`} sub={`= 1 + 1/${d.lapse_elasticity} (ε=${d.lapse_elasticity})`} color="green" />
          <MetricCard label="Marge à l'optimal" value={`${(d.total_margin_optimal / 1e6).toFixed(2)} M€`} sub="sur 2 350 contrats" color="green" />
          <MetricCard label="Marge référence (×1.3)" value={`${(d.total_margin_reference / 1e6).toFixed(2)} M€`} sub="chargement commercial initial" />
          <MetricCard label="Gain de marge" value={`+${d.gain_marge_pct.toFixed(1)}%`} sub="vs chargement de référence" color="blue" />
          <MetricCard label="SCR biométrique optimal" value={`${(d.scr_biometrique_optimal / 1e6).toFixed(2)} M€`} sub="vs baseline 4.07 M€" color="green" />
          <MetricCard label="Ratio de couverture optimal" value={`${d.solvency_ratio_optimal.toFixed(2)}×`} sub="vs baseline 7.38×" color="green" />
        </MetricGrid>

        <div style={{ marginTop: 16, padding: "12px 16px", background: "#f0fdf4", borderRadius: 8, border: "1px solid #bbf7d0" }}>
          <p style={{ fontSize: 13.5, color: "#166534", margin: 0 }}>
            <strong>Double bénéfice de l&apos;optimisation :</strong> Le chargement optimal de 1.5× améliore
            à la fois la <strong>marge commerciale (+11.7%)</strong> et le{" "}
            <strong>ratio de couverture SCR (+2.4%)</strong>, car un chargement plus élevé réduit le volume
            des sinistres (via l&apos;élasticité au rachat) et donc le SCR biométrique.
          </p>
        </div>
      </Section>

      <Section title="Courbe Marge vs Chargement" icon={<TrendingUp size={18} />}>
        <ChartImage
          src="/figures/m9_margin_curve.png"
          alt="Courbe de marge commerciale en fonction du chargement"
          caption="Marge totale (€) en fonction du taux de chargement. Le maximum à 1.5× est obtenu par arbitrage entre prime unitaire (croissante) et volume (décroissant via l'élasticité)."
        />
      </Section>

      <LimitBox items={[
        {
          title: "Bug corrigé — Vie Entière",
          text: "L'application du chargement commercial uniforme à la Vie Entière écrasait sa provision mathématique à 0 (incompatibilité avec la fonction d'épargne implicite). La Vie Entière est désormais explicitement exclue du périmètre de M9.",
        },
        {
          title: "Élasticité homogène",
          text: "L'hypothèse d'élasticité au rachat uniforme (ε=2) sur tout le périmètre est une simplification. Une version plus fine ferait varier ε par segment (âge, ancienneté, prime).",
        },
        {
          title: "Chargement indépendant du contrat",
          text: "Le chargement optimal 1 + 1/ε est indépendant de la prime pure et de la rente de survie individuelle — conséquence directe de l'hypothèse d'élasticité uniforme.",
        },
      ]} />
    </ModuleLayout>
  );
}
