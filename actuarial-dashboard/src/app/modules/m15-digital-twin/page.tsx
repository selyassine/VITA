import ModuleLayout, { Section, MetricGrid, MetricCard, LimitBox } from "@/components/ModuleLayout";
import { ServerCog, Activity, CheckCircle2 } from "lucide-react";

export const metadata = {
  title: "M15 — Digital Twin | Plateforme Actuarielle",
  description: "Orchestration complète du jumeau numérique — exécution de bout en bout de M1 à M14",
};

export default function M15DigitalTwinPage() {
  const dtResults = {
    generated_at: "2026-07-07T01:25:34Z",
    quick_mode: true,
    n_policies: 10000,
  };

  const evidences = [
    { module: "M1", name: "Mortalité", status: "Computed" },
    { module: "M2", name: "Tarification", status: "Computed" },
    { module: "M3", name: "Provisionnement", status: "Computed" },
    { module: "M4", name: "SCR", status: "Computed" },
    { module: "M5", name: "Rachats", status: "Computed" },
    { module: "M6", name: "Underwriting", status: "Computed" },
    { module: "M7", name: "Longévité", status: "Computed" },
    { module: "M8", name: "ALM", status: "Computed" },
    { module: "M9", name: "Optimizer", status: "Computed" },
    { module: "M10", name: "Risques émergents", status: "Computed" },
    { module: "M11", name: "ORSA", status: "Computed" },
  ];

  return (
    <ModuleLayout
      moduleId="m15-digital-twin"
      moduleNumber="Module 15"
      title="M15 — Digital Twin"
      subtitle="Orchestrateur maître — exécution de bout en bout et export centralisé"
      status="functional"
    >
      <Section title="Méthodologie" icon={<ServerCog size={18} />}>
        <p style={{ color: "#475569", lineHeight: 1.75, fontSize: 14.5 }}>
          M15 agit comme l&apos;<strong>orchestrateur maître</strong> de la plateforme. Son rôle est de lancer
          l&apos;exécution complète de l&apos;ensemble des modules métier (M1 à M14) dans le bon ordre de dépendance,
          de consolider tous les résultats chiffrés, et de générer un <strong>export JSON unique</strong> 
          (<code style={{ fontFamily: "monospace", fontSize: 13, background: "#f1f5f9", padding: "1px 6px", borderRadius: 4 }}>digital_twin_report.json</code>) 
          qui sert de source de vérité pour ce dashboard. 
        </p>
        <div style={{ marginTop: 14, padding: "12px 16px", background: "#f8fafc", borderRadius: 8, border: "1px solid #e2e8f0" }}>
          <p style={{ fontSize: 13.5, color: "#334155", margin: 0, display: "flex", alignItems: "center", gap: 8 }}>
            <Activity size={16} color="#3b82f6" />
            <strong>Génération du dernier rapport :</strong> {new Date(dtResults.generated_at).toLocaleString('fr-FR')}
          </p>
        </div>
      </Section>

      <Section title="Résultats de l'exécution" icon={<CheckCircle2 size={18} />}>
        <MetricGrid>
          <MetricCard label="Taille du portefeuille" value={dtResults.n_policies.toLocaleString("fr-FR")} sub="contrats générés" color="blue" />
          <MetricCard label="Mode d'exécution" value={dtResults.quick_mode ? "Rapide" : "Complet"} sub="quick_mode = True" color="amber" />
          <MetricCard label="Modules complétés" value={`${evidences.length} / 11`} sub="modules de calcul" color="green" />
        </MetricGrid>

        <div style={{ marginTop: 24 }}>
          <h3 style={{ fontSize: 15, fontWeight: 700, color: "#0f172a", marginBottom: 12 }}>Preuves d&apos;exécution (Module Evidence)</h3>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(200px, 1fr))", gap: 10 }}>
            {evidences.map((ev, i) => (
              <div key={i} style={{ background: "#f0fdf4", border: "1px solid #bbf7d0", borderRadius: 8, padding: "10px 14px", display: "flex", alignItems: "center", justifyContent: "space-between" }}>
                <div>
                  <span style={{ fontSize: 12, fontWeight: 700, color: "#166534" }}>{ev.module}</span>
                  <span style={{ fontSize: 13, color: "#14532d", marginLeft: 6 }}>{ev.name}</span>
                </div>
                <CheckCircle2 size={16} color="#22c55e" />
              </div>
            ))}
          </div>
        </div>
      </Section>

      <LimitBox items={[
        {
          title: "Mode rapide actif",
          text: "M15 a tourné en mode rapide (quick_mode=True), ce qui limite l'exécution de certains modules très lourds (par exemple, M6 extrait les statistiques du dataset au lieu d'entraîner le Random Forest complet).",
        },
        {
          title: "Temps d'exécution",
          text: "Même en mode rapide, l'orchestration complète prend plusieurs minutes en raison des simulations Monte-Carlo (M7) et de l'optimisation (M9).",
        }
      ]} />
    </ModuleLayout>
  );
}
