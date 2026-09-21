import ModuleLayout, { Section, MetricGrid, MetricCard, LimitBox } from "@/components/ModuleLayout";
import { DollarSign, FileText, BarChart2 } from "lucide-react";

export const metadata = {
  title: "M2 — Tarification | Plateforme Actuarielle",
  description: "Calcul des primes pures par équivalence actuarielle, utilisant les projections Lee-Carter de M1",
};

export default function M2TarificationPage() {
  const data = {
    n_contrats_tarifes: 4915,
    prime_pure_totale_eur: 9618282.93,
    prime_pure_moyenne: 9618282.93 / 4915,
  };

  return (
    <ModuleLayout
      moduleId="m2-tarification"
      moduleNumber="Module 2"
      title="M2 — Tarification"
      subtitle="Prime pure par équivalence actuarielle — données HMD + Lee-Carter"
      status="functional"
    >
      <Section title="Méthodologie" icon={<DollarSign size={18} />}>
        <p style={{ color: "#475569", lineHeight: 1.75, fontSize: 14.5 }}>
          La <strong>prime pure</strong> est calculée par <strong>équivalence actuarielle</strong> : la valeur
          actuarielle des primes payées égale la valeur actuarielle des prestations attendues. Pour chaque contrat
          du portefeuille synthétique (10 000 polices), le calcul utilise les taux de mortalité{" "}
          <strong>projetés par Lee-Carter (M1)</strong> sur la durée du contrat, actualisés au{" "}
          <strong>taux technique de 1%</strong>. Trois produits sont tarifés : Temporaire Décès,
          Prévoyance (arrêt de travail), et Vie Entière.
        </p>
        <div style={{ marginTop: 14, padding: "12px 16px", background: "#f8fafc", borderRadius: 8, border: "1px solid #e2e8f0", fontFamily: "monospace", fontSize: 13 }}>
          <span style={{ color: "#64748b" }}>Prime pure P = </span>
          <span style={{ color: "#1e40af" }}>∑(t) C · q(x+t) · v^(t+1) · tpx</span>
          <span style={{ color: "#64748b" }}> / </span>
          <span style={{ color: "#1e40af" }}>ä(x)</span>
        </div>
      </Section>

      <Section title="Résultats Clés" icon={<BarChart2 size={18} />}>
        <MetricGrid>
          <MetricCard label="Contrats tarifés" value={data.n_contrats_tarifes.toLocaleString("fr-FR")} sub="sur 10 000 (produits risque décès)" color="blue" />
          <MetricCard label="Prime pure totale" value={`${(data.prime_pure_totale_eur / 1e6).toFixed(2)} M€`} sub="portefeuille agrégé" color="green" />
          <MetricCard label="Prime pure moyenne" value={`${data.prime_pure_moyenne.toFixed(0)} €`} sub="par contrat tarifé" />
          <MetricCard label="Taux technique" value="1.0 %" sub="hypothèse prudente" color="amber" />
        </MetricGrid>

        <div style={{ marginTop: 20 }}>
          <h3 style={{ fontSize: 15, fontWeight: 700, color: "#0f172a", marginBottom: 12 }}>Produits couverts</h3>
          <table className="data-table">
            <thead>
              <tr>
                <th>Produit</th>
                <th>Méthode de tarification</th>
                <th>Données de mortalité</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td><strong>Temporaire Décès</strong></td>
                <td>Équivalence actuarielle sur durée fixe</td>
                <td>HMD + Lee-Carter (projeté)</td>
              </tr>
              <tr>
                <td><strong>Prévoyance</strong></td>
                <td>Équivalence actuarielle avec table invalidité proxy</td>
                <td>HMD + Lee-Carter</td>
              </tr>
              <tr>
                <td><strong>Vie Entière</strong></td>
                <td>Équivalence actuarielle à vie entière</td>
                <td>HMD + Lee-Carter (90 ans)</td>
              </tr>
            </tbody>
          </table>
        </div>
      </Section>

      <Section title="Note sur le chargement implicite" icon={<FileText size={18} />}>
        <div style={{ padding: "14px 18px", background: "#fff7ed", border: "1px solid #fed7aa", borderRadius: 8 }}>
          <p style={{ fontSize: 14, color: "#9a3412", lineHeight: 1.7, margin: 0 }}>
            <strong>Chargement implicite :</strong> La prime commerciale du portefeuille synthétique est calibrée
            via une courbe Gompertz approximative, volontairement indépendante de M1. La prime pure de M2 utilise,
            elle, les vraies données HMD via Lee-Carter. Le chargement implicite observé varie fortement :{" "}
            <strong>Temporaire Décès ~180%, Prévoyance ~185%, Vie Entière ~−4%</strong>. La dispersion jusqu&apos;à
            ~1900% en queue est un artefact synthétique, pas une prédiction de marge réelle.
          </p>
        </div>
      </Section>

      <LimitBox items={[
        {
          title: "Portefeuille synthétique",
          text: "Les 4 915 contrats tarifés proviennent du portefeuille synthétique généré par Gompertz, pas de données réelles de portefeuille assureur. Les primes obtenues sont illustratives.",
        },
        {
          title: "Horizon Lee-Carter",
          text: "Suite au bug corrigé en M1 (horizon passé de 50 à 90 ans), les primes pures recalculées sont plus élevées qu'en version initiale, notamment pour la Vie Entière.",
        },
        {
          title: "Taux technique unique",
          text: "Le taux d'actualisation de 1% est homogène pour tous les produits. En pratique, il devrait être aligné sur la courbe EIOPA et différencié par durée.",
        },
      ]} />
    </ModuleLayout>
  );
}
