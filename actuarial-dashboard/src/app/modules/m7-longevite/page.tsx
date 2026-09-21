import ModuleLayout, { Section, MetricGrid, MetricCard, LimitBox } from "@/components/ModuleLayout";
import { TrendingDown, BarChart2, Activity } from "lucide-react";

export const metadata = {
  title: "M7 — Longévité | Plateforme Actuarielle",
  description: "VaR 99.5% du risque de longévité par simulation Monte-Carlo des trajectoires Lee-Carter",
};

export default function M7LongevitePage() {
  const d = {
    be_mean_simulated: 43134165.90,
    var_longevity: 3801448.56,
    var_pct: (3801448.56 / 43134165.90 * 100),
    n_simulations: 200,
    n_profils: "< 10 000",
  };

  return (
    <ModuleLayout
      moduleId="m7-longevite"
      moduleNumber="Module 7"
      title="M7 — Longévité (Stochastique)"
      subtitle="VaR 99.5% par simulation Monte-Carlo des trajectoires de mortalité Lee-Carter"
      status="functional"
    >
      <Section title="Méthodologie" icon={<Activity size={18} />}>
        <p style={{ color: "#475569", lineHeight: 1.75, fontSize: 14.5 }}>
          M7 est le <strong>complément stochastique</strong> du choc déterministe de M4. Plutôt qu&apos;appliquer
          un choc forfaitaire −20% sur les qx, M7 simule{" "}
          <strong>{d.n_simulations} trajectoires Monte-Carlo</strong> du paramètre k(t) de Lee-Carter
          (incluant l&apos;incertitude autour de la dérive et de la volatilité), calcule le Best Estimate
          pour chaque trajectoire, et dérive la <strong>VaR 99.5%</strong> comme le quantile 99.5e de
          la distribution simulée du BE.
        </p>
        <div style={{ marginTop: 14, padding: "12px 16px", background: "#f8fafc", borderRadius: 8, border: "1px solid #e2e8f0", fontFamily: "monospace", fontSize: 13 }}>
          <span style={{ color: "#64748b" }}>VaR 99.5% = </span>
          <span style={{ color: "#1e40af" }}>Quantile(BE_simulés, 0.995)</span>
          <span style={{ color: "#64748b" }}> − </span>
          <span style={{ color: "#1e40af" }}>BE_moyen</span>
        </div>
        <div style={{ marginTop: 12, padding: "12px 16px", background: "#eff6ff", border: "1px solid #bfdbfe", borderRadius: 8 }}>
          <p style={{ fontSize: 13.5, color: "#1e40af", margin: 0 }}>
            <strong>Optimisation :</strong> Le portefeuille est <strong>regroupé par profil</strong> (produit,
            genre, âge) avant simulation — réduisant les milliers de contrats à quelques centaines de groupes
            homogènes pour un temps de calcul raisonnable.
          </p>
        </div>
      </Section>

      <Section title="Résultats Clés" icon={<BarChart2 size={18} />}>
        <MetricGrid>
          <MetricCard label="BE moyen simulé" value={`${(d.be_mean_simulated / 1e6).toFixed(2)} M€`} sub="moyenne des 200 trajectoires" color="blue" />
          <MetricCard label="VaR 99.5% longévité" value={`${(d.var_longevity / 1e6).toFixed(2)} M€`} sub="risque de longévité stochastique" color="amber" />
          <MetricCard label="VaR en % du BE" value={`${d.var_pct.toFixed(1)} %`} sub="intensité du risque longévité" color="amber" />
          <MetricCard label="Simulations" value={`${d.n_simulations}`} sub="trajectoires Monte-Carlo" />
        </MetricGrid>

        <div style={{ marginTop: 16, padding: "12px 16px", background: "#eff6ff", borderRadius: 8, border: "1px solid #bfdbfe" }}>
          <p style={{ fontSize: 13.5, color: "#1e40af", margin: 0 }}>
            <strong>Écart BE simulé vs M3 :</strong> Le BE moyen simulé de M7 (43.1 M€) diffère légèrement
            du BE déterministe de M3 (44.1 M€). Cet écart de ~1 M€ est <strong>normal en modélisation stochastique</strong> :
            il reflète l&apos;effet de convexité (la moyenne des taux de mortalité simulés ≠ taux central)
            et non une erreur. La comparaison entre les deux approches est en soi un résultat de validation croisée.
          </p>
        </div>

        <div style={{ marginTop: 12 }}>
          <h3 style={{ fontSize: 15, fontWeight: 700, color: "#0f172a", marginBottom: 10 }}>Comparaison M4 (choc déterministe) vs M7 (Monte-Carlo)</h3>
          <table className="data-table">
            <thead>
              <tr>
                <th>Approche</th>
                <th>Méthode</th>
                <th>Résultat longévité</th>
                <th>Niveau de confiance</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td><strong>M4 — SCR formule standard</strong></td>
                <td>Choc forfaitaire −20% sur qx</td>
                <td>0 M€ (non-déclenchant)</td>
                <td>99.5% (réglementaire)</td>
              </tr>
              <tr>
                <td><strong>M7 — Monte-Carlo Lee-Carter</strong></td>
                <td>200 trajectoires stochastiques k(t)</td>
                <td>3.80 M€</td>
                <td>99.5% (empirique)</td>
              </tr>
            </tbody>
          </table>
        </div>
      </Section>

      <LimitBox items={[
        {
          title: "Nombre de simulations réduit",
          text: "200 simulations (vs 1000 dans M1/M4) pour un temps de calcul raisonnable. Un intervalle de confiance sur la VaR elle-même nécessiterait davantage de simulations (bootstrap).",
        },
        {
          title: "Regroupement par profil",
          text: "Pour des raisons de performance, les contrats sont agrégés par (produit, genre, âge). Les hétérogénéités intra-groupe ne sont pas capturées.",
        },
        {
          title: "Incertitude paramétrique uniquement",
          text: "Le modèle simule l'incertitude autour des paramètres k(t) mais pas l'incertitude sur les paramètres a(x) et b(x) du modèle Lee-Carter lui-même.",
        },
      ]} />
    </ModuleLayout>
  );
}
