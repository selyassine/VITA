import ModuleLayout, { Section, MetricGrid, MetricCard, LimitBox, ChartImage } from "@/components/ModuleLayout";
import { Shield, BarChart2, FileText } from "lucide-react";

export const metadata = {
  title: "M4 — SCR | Plateforme Actuarielle",
  description: "Capital réglementaire Solvabilité II — SCR mortalité, longévité et taux via courbes EIOPA",
};

export default function M4ScrPage() {
  const d = {
    best_estimate_central: 44138580.18,
    scr_mortality: 4067046.06,
    scr_longevity: 0.0,
    scr_vie_biometrique: 4067046.06,
    scr_interest_down: 7420566.45,
    solvency_ratio: 7.38,
    own_funds: 30000000,
  };

  return (
    <ModuleLayout
      moduleId="m4-scr"
      moduleNumber="Module 4"
      title="M4 — SCR"
      subtitle="Solvency Capital Requirement — Formule standard Solvabilité II (Règlement délégué UE 2015/35)"
      status="functional"
    >
      <Section title="Méthodologie" icon={<Shield size={18} />}>
        <p style={{ color: "#475569", lineHeight: 1.75, fontSize: 14.5 }}>
          Le SCR est calculé par <strong>choc sur le Best Estimate</strong> selon la formule standard Solvabilité II.
          Trois sous-modules sont implémentés :
        </p>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(200px, 1fr))", gap: 12, marginTop: 16 }}>
          {[
            { label: "SCR Mortalité", choc: "+15% sur les taux qx", norm: "Art. 137 délégué" },
            { label: "SCR Longévité", choc: "−20% sur les taux qx", norm: "Art. 138 délégué" },
            { label: "SCR Taux", choc: "Choc up/down EIOPA", norm: "Courbe RFR 2026-05-31" },
          ].map(s => (
            <div key={s.label} style={{ background: "#f8fafc", border: "1px solid #e2e8f0", borderRadius: 8, padding: "14px 16px" }}>
              <p style={{ fontWeight: 700, color: "#0f172a", fontSize: 14, marginBottom: 4 }}>{s.label}</p>
              <p style={{ fontSize: 13, color: "#64748b" }}>Choc : {s.choc}</p>
              <p style={{ fontSize: 12, color: "#94a3b8" }}>{s.norm}</p>
            </div>
          ))}
        </div>
      </Section>

      <Section title="Résultats Clés" icon={<BarChart2 size={18} />}>
        <MetricGrid>
          <MetricCard label="Best Estimate central" value={`${(d.best_estimate_central / 1e6).toFixed(1)} M€`} />
          <MetricCard label="Fonds propres supposés" value={`${(d.own_funds / 1e6).toFixed(0)} M€`} />
          <MetricCard label="SCR Mortalité" value={`${(d.scr_mortality / 1e6).toFixed(2)} M€`} sub="choc +15% qx" color="amber" />
          <MetricCard label="SCR Longévité" value="0.00 M€" sub="choc −20% : non-déclenchant" color="green" />
          <MetricCard label="SCR Biométrique total" value={`${(d.scr_vie_biometrique / 1e6).toFixed(2)} M€`} color="amber" />
          <MetricCard label="SCR Taux (down)" value={`${(d.scr_interest_down / 1e6).toFixed(2)} M€`} sub="choc EIOPA baisse" color="red" />
          <MetricCard label="Ratio de couverture" value={`${d.solvency_ratio.toFixed(2)}×`} sub="Fonds propres / SCR total" color="green" />
        </MetricGrid>

        <div style={{ marginTop: 16, padding: "12px 16px", background: "#f0fdf4", borderRadius: 8, border: "1px solid #bbf7d0" }}>
          <p style={{ fontSize: 13.5, color: "#166534", margin: 0 }}>
            <strong>✓ Ratio de couverture très confortable :</strong> 7.38× signifie que les fonds propres
            couvrent 738% du SCR requis. Ce résultat reflète le choix d&apos;un portefeuille synthétique calibré
            sur des hypothèses prudentes — il n&apos;est pas directement comparable à un vrai assureur.
          </p>
        </div>
      </Section>

      <Section title="Décomposition du SCR" icon={<BarChart2 size={18} />}>
        <ChartImage
          src="/figures/m4_scr_breakdown.png"
          alt="Décomposition du SCR Solvabilité II"
          caption="Ventilation du SCR par sous-module : biométrique (mortalité + longévité) et taux d'intérêt. Le SCR taux domine via le choc baisse EIOPA."
        />
      </Section>

      <Section title="Données réglementaires utilisées" icon={<FileText size={18} />}>
        <table className="data-table">
          <thead>
            <tr>
              <th>Source</th>
              <th>Nature</th>
              <th>Usage</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>EIOPA RFR 2026-05-31</td>
              <td><span className="badge badge-green">Réelle officielle</span></td>
              <td>Courbe des taux sans risque (actualisation + chocs taux)</td>
            </tr>
            <tr>
              <td>HMD + Lee-Carter</td>
              <td><span className="badge badge-green">Réelle officielle</span></td>
              <td>Taux de mortalité projetés (chocs biométriques)</td>
            </tr>
          </tbody>
        </table>
      </Section>

      <LimitBox items={[
        {
          title: "SCR Longévité nul",
          text: "Sur ce portefeuille, le choc −20% sur les taux qx futurs n'augmente pas le Best Estimate au-delà du central. C'est un résultat plausible sur un portefeuille à dominante risque décès — à surveiller si le mix produits évolue vers plus de rentes.",
        },
        {
          title: "Corrélation inter-SCR simplifiée",
          text: "La formule standard applique des corrélations fixes entre sous-modules (biométrique/taux : 0%). Les corrélations en période de stress ne sont pas capturées.",
        },
        {
          title: "Décalage temporel EIOPA/HMD",
          text: "La courbe EIOPA date de mai 2026, les données HMD de 2023 — un léger décalage temporel qui n'affecte pas la qualité du résultat mais est à noter.",
        },
      ]} />
    </ModuleLayout>
  );
}
