import ModuleLayout, { Section, MetricGrid, MetricCard, LimitBox, ChartImage } from "@/components/ModuleLayout";
import { TrendingDown, Database, BarChart2 } from "lucide-react";

export const metadata = {
  title: "M1 — Mortalité | Plateforme Actuarielle",
  description: "Modèle Lee-Carter ajusté sur données HMD réelles françaises — projection de la mortalité future",
};

export default function M1MortalitePage() {
  return (
    <ModuleLayout
      moduleId="m1-mortalite"
      moduleNumber="Module 1"
      title="M1 — Mortalité"
      subtitle="Modèle Lee-Carter ajusté sur données HMD réelles (France 1950-2023)"
      status="functional"
    >
      <Section title="Méthodologie" icon={<TrendingDown size={18} />}>
        <p style={{ color: "#475569", lineHeight: 1.75, fontSize: 14.5 }}>
          Le modèle <strong>Lee-Carter</strong> (Lee &amp; Carter, 1992) décompose la mortalité selon la formule{" "}
          <code style={{ background: "#f1f5f9", padding: "1px 6px", borderRadius: 4, fontFamily: "monospace", fontSize: 13 }}>
            log m(x,t) = a(x) + b(x) · k(t) + ε
          </code>
          . L&apos;ajustement est réalisé par <strong>SVD</strong> sur la matrice centrée des log-mortalités, et
          la projection de k(t) utilise une <strong>marche aléatoire avec dérive</strong>. Les données HMD
          (Human Mortality Database) françaises couvrent 74 années (1950–2023) et 101 âges (0–100 ans).
          L&apos;horizon de projection a été corrigé à <strong>90 ans</strong> (voir limites).
        </p>
      </Section>

      <Section title="Résultats Clés" icon={<BarChart2 size={18} />}>
        <MetricGrid>
          <MetricCard label="Dérive k(t)" value="−1.801" sub="par an (baisse tendancielle)" color="blue" />
          <MetricCard label="Âges couverts" value="101" sub="de 0 à 100 ans" />
          <MetricCard label="Années d'ajustement" value="74" sub="1950 – 2023" />
          <MetricCard label="Horizon projeté" value="90 ans" sub="avec marge de sécurité" color="green" />
        </MetricGrid>
        <div style={{ marginTop: 16, padding: "12px 16px", background: "#eff6ff", borderRadius: 8, border: "1px solid #bfdbfe" }}>
          <p style={{ fontSize: 13.5, color: "#1e40af", margin: 0 }}>
            <strong>Interprétation :</strong> La dérive k(t) = −1.801/an traduit une amélioration régulière
            de la survie : chaque année, l&apos;index k(t) baisse, réduisant les taux de mortalité à tous les âges
            selon leur sensibilité b(x). Ce résultat est cohérent avec les tendances longévité observées en France.
          </p>
        </div>
      </Section>

      <Section title="Courbe de mortalité Lee-Carter" icon={<BarChart2 size={18} />}>
        <ChartImage
          src="/figures/m1_mortality_curve.png"
          alt="Courbe de mortalité Lee-Carter — projection France"
          caption="Taux de mortalité log-linéaires par âge : historique (bleu) et trajectoires projetées (gris). La dérive k(t) = −1.801/an traduit l'amélioration tendancielle de la survie."
        />
      </Section>

      <Section title="Source de données" icon={<Database size={18} />}>
        <table className="data-table">
          <thead>
            <tr>
              <th>Source</th>
              <th>Nature</th>
              <th>Portée</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td><strong>HMD — Human Mortality Database</strong></td>
              <td><span className="badge badge-green">Réelle officielle</span></td>
              <td>France métropolitaine, 1950–2023</td>
            </tr>
          </tbody>
        </table>
        <p style={{ fontSize: 12.5, color: "#94a3b8", marginTop: 10 }}>
          Note : les fichiers HMD nécessitent un compte mortality.org pour le téléchargement.
        </p>
      </Section>

      <LimitBox items={[
        {
          title: "Horizon de projection — bug corrigé",
          text: "Initialement fixé à 50 ans, insuffisant pour couvrir un contrat Vie Entière souscrit à 18 ans (82 ans de projection nécessaires). La troncature silencieuse sous-estimait le BE de M2/M3/M4 (~87M€ au lieu de ~99M€, écart 2.6×). Corrigé à 90 ans ; une troncature résiduelle est désormais journalisée.",
        },
        {
          title: "Parallélisme des âges",
          text: "Le modèle Lee-Carter suppose que les trajectoires de mortalité par âge évoluent de manière proportionnelle (hypothèse b(x) fixe). Cette hypothèse peut ne pas tenir sur des horizons très longs ou en cas de choc épidémique.",
        },
        {
          title: "Périmètre géographique",
          text: "Les données HMD utilisées sont limitées à la France métropolitaine. Un assureur opérant à l'international devrait utiliser des tables de mortalité spécifiques à chaque marché.",
        },
      ]} />
    </ModuleLayout>
  );
}
