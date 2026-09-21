import ModuleLayout, { Section, MetricGrid, MetricCard, LimitBox, ChartImage } from "@/components/ModuleLayout";
import { BarChart2, Clock, TrendingDown } from "lucide-react";

export const metadata = {
  title: "M11 — ORSA | Plateforme Actuarielle",
  description: "Own Risk and Solvency Assessment — projection pluriannuelle run-off du capital réglementaire",
};

export default function M11OrsaPage() {
  const orsa = [
    { year: 0, be: 44138580.18, scr: 4067046.06, ratio: 7.3764 },
    { year: 1, be: 45930196.06, scr: 4297980.07, ratio: 6.9800 },
    { year: 2, be: 47865923.17, scr: 4558332.56, ratio: 6.5814 },
  ];

  const ownFunds = 30000000;

  return (
    <ModuleLayout
      moduleId="m11-orsa"
      moduleNumber="Module 11"
      title="M11 — ORSA"
      subtitle="Own Risk and Solvency Assessment — projection pluriannuelle run-off du BE et du SCR"
      status="functional"
    >
      <Section title="Méthodologie" icon={<Clock size={18} />}>
        <p style={{ color: "#475569", lineHeight: 1.75, fontSize: 14.5 }}>
          L&apos;ORSA (Own Risk and Solvency Assessment) est l&apos;évaluation interne des risques et de la solvabilité
          d&apos;un assureur, requise par Solvabilité II article 45. M11 implémente une{" "}
          <strong>projection pluriannuelle run-off</strong> : à chaque pas annuel, le Best Estimate augmente
          (vieillissement du portefeuille, pas de nouvelles souscriptions), le SCR évolue en conséquence,
          et le ratio de couverture se dégrade progressivement. Les fonds propres sont supposés constants
          à <strong>30 M€</strong> (hypothèse simplificatrice).
        </p>
      </Section>

      <Section title="Trajectoire pluriannuelle" icon={<TrendingDown size={18} />}>
        <table className="data-table" style={{ marginBottom: 16 }}>
          <thead>
            <tr>
              <th>Année</th>
              <th>Best Estimate</th>
              <th>SCR Biométrique</th>
              <th>Fonds Propres</th>
              <th>Ratio SCR</th>
              <th>Évolution</th>
            </tr>
          </thead>
          <tbody>
            {orsa.map((row, i) => (
              <tr key={row.year}>
                <td><strong>Année {row.year}</strong>{i === 0 ? " (t₀)" : ""}</td>
                <td>{(row.be / 1e6).toFixed(2)} M€</td>
                <td>{(row.scr / 1e6).toFixed(2)} M€</td>
                <td>{(ownFunds / 1e6).toFixed(0)} M€</td>
                <td>
                  <span style={{
                    fontWeight: 700,
                    color: row.ratio > 2 ? "#166534" : row.ratio > 1.5 ? "#92400e" : "#991b1b",
                  }}>
                    {row.ratio.toFixed(2)}×
                  </span>
                </td>
                <td style={{ color: "#64748b", fontSize: 13 }}>
                  {i === 0 ? "— référence" : `−${((orsa[0].ratio - row.ratio) / orsa[0].ratio * 100).toFixed(1)}% vs t₀`}
                </td>
              </tr>
            ))}
          </tbody>
        </table>

        <MetricGrid>
          <MetricCard label="Ratio initial (t₀)" value={`${orsa[0].ratio.toFixed(2)}×`} color="green" />
          <MetricCard label="Ratio en année 2" value={`${orsa[2].ratio.toFixed(2)}×`} color="amber" />
          <MetricCard label="Baisse du ratio sur 2 ans" value={`−${((orsa[0].ratio - orsa[2].ratio) / orsa[0].ratio * 100).toFixed(1)}%`} color="amber" />
          <MetricCard label="Croissance du SCR/an" value="~5.7%" sub="due au vieillissement du portefeuille" />
        </MetricGrid>

        <div style={{ marginTop: 16, padding: "12px 16px", background: "#eff6ff", borderRadius: 8, border: "1px solid #bfdbfe" }}>
          <p style={{ fontSize: 13.5, color: "#1e40af", margin: 0 }}>
            <strong>Interprétation :</strong> Le ratio de couverture reste très confortable sur 2 ans (6.58×
            vs minimum réglementaire 1.0×). La dégradation est mécanique : en run-off sans nouvelles souscriptions,
            le portefeuille vieillit et la mortalité attendue augmente, augmentant le SCR biométrique.
            En pratique, un assureur compenserait par de nouvelles souscriptions ou une gestion du capital.
          </p>
        </div>
      </Section>

      <Section title="Trajectoire ORSA" icon={<BarChart2 size={18} />}>
        <ChartImage
          src="/figures/m11_orsa_trajectory.png"
          alt="Trajectoire ORSA pluriannuelle — Best Estimate et ratio SCR"
          caption="Évolution du Best Estimate (M€) et du ratio de couverture SCR sur 3 années en mode run-off. La dégradation progressive du ratio reflète le vieillissement du portefeuille sans nouvelles souscriptions."
        />
      </Section>

      <LimitBox items={[
        {
          title: "Fonds propres constants",
          text: "L'hypothèse de fonds propres fixes à 30 M€ sur toute la projection est simplificatrice. En réalité, les fonds propres évolueraient selon le résultat technique et les distributions.",
        },
        {
          title: "Run-off uniquement",
          text: "Le mode de projection est un run-off pur (pas de nouvelles souscriptions). Un ORSA réglementaire inclurait des scénarios avec croissance du portefeuille et stress tests.",
        },
        {
          title: "3 années seulement",
          text: "La projection couvre 3 ans. Solvabilité II recommande une projection sur la durée de vie du portefeuille ou au minimum 3-5 ans — l'extension à plus long terme est prévue.",
        },
      ]} />
    </ModuleLayout>
  );
}
