import ModuleLayout, { Section, MetricGrid, MetricCard, LimitBox, ChartImage } from "@/components/ModuleLayout";
import { BarChart2, TrendingUp, Scale } from "lucide-react";

export const metadata = {
  title: "M8 — ALM | Plateforme Actuarielle",
  description: "Asset-Liability Management — bilan actif/passif, duration gap et sensibilité NAV aux taux",
};

export default function M8AlmPage() {
  const d = {
    liability_value_central: 11074400.73,
    liability_duration: 21.22,
    bond_value_central: 8527288.54,
    bond_duration: 8.71,
    equities_value: 2436368.16,
    real_estate_value: 1218184.08,
    total_asset_value: 12181840.78,
    blended_asset_duration: 6.10,
    dollar_duration_gap: -160673940.23,
    nav_central: 1107440.05,
    nav_shock_up: 4619349.89,
    nav_shock_down: -5557208.16,
    nav_sensitivity_up: 3511909.84,
    nav_sensitivity_down: -6664648.22,
  };

  return (
    <ModuleLayout
      moduleId="m8-alm"
      moduleNumber="Module 8"
      title="M8 — ALM"
      subtitle="Asset-Liability Management — bilan synthétique, duration gap et sensibilité du NAV"
      status="functional"
    >
      <Section title="Méthodologie" icon={<Scale size={18} />}>
        <p style={{ color: "#475569", lineHeight: 1.75, fontSize: 14.5 }}>
          Le module ALM construit un <strong>bilan synthétique actif/passif</strong> :
          le passif est valorisé par la fonction M4 (Best Estimate avec plancher 0 par contrat) ;
          l&apos;actif est un portefeuille obligataire calibré pour couvrir le passif à un{" "}
          <strong>ratio de couverture cible de 110%</strong>, complété par des actions (20%) et de
          l&apos;immobilier (10%). La <strong>duration de Macaulay</strong> est calculée sur les
          flux de prestations (passif) et sur les flux obligataires (actif). Le{" "}
          <strong>dollar duration gap</strong> mesure la sensibilité du NAV aux variations de taux.
        </p>
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 10, marginTop: 14 }}>
          {[
            { label: "Obligations", pct: "70%", color: "#3b82f6" },
            { label: "Actions", pct: "20%", color: "#8b5cf6" },
            { label: "Immobilier", pct: "10%", color: "#06b6d4" },
          ].map(item => (
            <div key={item.label} style={{ background: "#f8fafc", border: "1px solid #e2e8f0", borderRadius: 8, padding: "12px 14px", textAlign: "center" }}>
              <div style={{ width: 40, height: 40, borderRadius: "50%", background: item.color + "22", border: `3px solid ${item.color}`, margin: "0 auto 8px", display: "flex", alignItems: "center", justifyContent: "center" }}>
                <span style={{ fontSize: 13, fontWeight: 800, color: item.color }}>{item.pct}</span>
              </div>
              <p style={{ fontSize: 13, fontWeight: 600, color: "#334155", margin: 0 }}>{item.label}</p>
            </div>
          ))}
        </div>
      </Section>

      <Section title="Bilan ALM — Résultats" icon={<BarChart2 size={18} />}>
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16, marginBottom: 20 }}>
          <div style={{ background: "#eff6ff", border: "1px solid #bfdbfe", borderRadius: 10, padding: "20px" }}>
            <h3 style={{ fontSize: 15, fontWeight: 700, color: "#1e40af", marginBottom: 12 }}>Passif</h3>
            <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
              <Row label="Best Estimate" value={`${(d.liability_value_central / 1e6).toFixed(2)} M€`} />
              <Row label="Duration (Macaulay)" value={`${d.liability_duration.toFixed(1)} ans`} />
            </div>
          </div>
          <div style={{ background: "#f0fdf4", border: "1px solid #bbf7d0", borderRadius: 10, padding: "20px" }}>
            <h3 style={{ fontSize: 15, fontWeight: 700, color: "#166534", marginBottom: 12 }}>Actif</h3>
            <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
              <Row label="Obligations" value={`${(d.bond_value_central / 1e6).toFixed(2)} M€`} />
              <Row label="Duration obligations" value={`${d.bond_duration.toFixed(1)} ans`} />
              <Row label="Actions" value={`${(d.equities_value / 1e6).toFixed(2)} M€`} />
              <Row label="Immobilier" value={`${(d.real_estate_value / 1e6).toFixed(2)} M€`} />
              <Row label="Total actif" value={`${(d.total_asset_value / 1e6).toFixed(2)} M€`} bold />
              <Row label="Duration actif blended" value={`${d.blended_asset_duration.toFixed(1)} ans`} />
            </div>
          </div>
        </div>

        <MetricGrid>
          <MetricCard label="NAV central" value={`${(d.nav_central / 1e6).toFixed(2)} M€`} sub="Actif − Passif" color="blue" />
          <MetricCard label="Dollar Duration Gap" value={`${(d.dollar_duration_gap / 1e6).toFixed(0)} M€`} sub="Actif sous-duré vs passif" color="amber" />
          <MetricCard label="NAV si taux +" value={`+${(d.nav_sensitivity_up / 1e6).toFixed(2)} M€`} sub="choc taux hausse EIOPA" color="green" />
          <MetricCard label="NAV si taux −" value={`${(d.nav_sensitivity_down / 1e6).toFixed(2)} M€`} sub="choc taux baisse EIOPA" color="red" />
        </MetricGrid>

        <div style={{ marginTop: 12, padding: "12px 16px", background: "#fffbeb", borderRadius: 8, border: "1px solid #fde68a" }}>
          <p style={{ fontSize: 13.5, color: "#92400e", margin: 0 }}>
            <strong>Interprétation :</strong> La duration du passif (21.2 ans) dépasse largement celle de l&apos;actif
            obligataire (8.7 ans). Ce <strong>duration gap négatif</strong> signifie que le NAV baisse si les taux
            baissent (passif s&apos;apprécie plus que l&apos;actif) et monte si les taux montent — comportement
            normal pour un assureur-vie non immunisé.
          </p>
        </div>
      </Section>

      <Section title="Duration Gap Actif/Passif" icon={<TrendingUp size={18} />}>
        <ChartImage
          src="/figures/m8_alm_duration_gap.png"
          alt="Duration Gap ALM — Actif vs Passif"
          caption="Duration de Macaulay comparée actif (bleu) / passif (orange). Le gap de ~12.5 ans traduit un risque de taux significatif sur le NAV."
        />
      </Section>

      <LimitBox items={[
        {
          title: "Correction n°1 — Duration négative (bug corrigé)",
          text: "La duration était initialement calculée sur le flux NET (prestations − primes), produisant −2.9 ans. Corrigé : calculée sur les prestations seules (toujours positive), conforme à la pratique ALM standard.",
        },
        {
          title: "Correction n°2 — Passif négatif (bug corrigé)",
          text: "La valeur du passif était calculée sans plancher 0 par contrat, générant un bilan entièrement négatif. Corrigé : réutilisation de la fonction M4 déjà testée avec plafonnement par contrat.",
        },
        {
          title: "Actif entièrement synthétique",
          text: "L'allocation (70% obligations, 20% actions, 10% immobilier) est illustrative. Aucune donnée réelle de bilan assureur n'est disponible.",
        },
        {
          title: "Actions et immobilier — duration zéro",
          text: "Ces actifs sont traités sans sensibilité aux taux modélisée. Leur risque relève d'autres sous-modules SCR hors périmètre.",
        },
      ]} />
    </ModuleLayout>
  );
}

function Row({ label, value, bold }: { label: string; value: string; bold?: boolean }) {
  return (
    <div style={{ display: "flex", justifyContent: "space-between", fontSize: 13.5 }}>
      <span style={{ color: "#64748b" }}>{label}</span>
      <span style={{ fontWeight: bold ? 700 : 600, color: "#0f172a" }}>{value}</span>
    </div>
  );
}
