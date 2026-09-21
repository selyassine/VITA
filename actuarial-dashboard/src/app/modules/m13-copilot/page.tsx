import ModuleLayout, { Section, LimitBox } from "@/components/ModuleLayout";
import { Bot, AlertTriangle, Code2 } from "lucide-react";

export const metadata = {
  title: "M13 — Copilot IA | Plateforme Actuarielle",
  description: "Copilote IA Anthropic Claude — outils de requête en langage naturel sur les résultats actuariels",
};

const tools = [
  { name: "get_mortality_results()", desc: "Retourne les paramètres Lee-Carter (a, b, k) et la dérive k(t)" },
  { name: "get_pricing_results()", desc: "Retourne les primes pures par produit et les statistiques du portefeuille" },
  { name: "get_scr_results()", desc: "Retourne le SCR par sous-module et le ratio de couverture" },
  { name: "get_alm_results()", desc: "Retourne le bilan ALM, les durations et la sensibilité NAV" },
  { name: "get_orsa_projection()", desc: "Retourne la trajectoire ORSA pluriannuelle" },
  { name: "get_compliance_status()", desc: "Retourne l'état de la checklist documentaire ORSA" },
];

export default function M13CopilotPage() {
  return (
    <ModuleLayout
      moduleId="m13-copilot"
      moduleNumber="Module 13"
      title="M13 — Copilot IA"
      subtitle="Outils de requête en langage naturel sur les résultats — API Anthropic Claude"
      status="partial"
      statusLabel="Partiel (API key requise)"
    >
      <Section title="Architecture" icon={<Bot size={18} />}>
        <p style={{ color: "#475569", lineHeight: 1.75, fontSize: 14.5, marginBottom: 14 }}>
          M13 implémente un <strong>copilote IA</strong> permettant d&apos;interroger la plateforme en langage
          naturel via Anthropic Claude (claude-3-5-sonnet). L&apos;architecture sépare volontairement :
        </p>
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
          <div style={{ background: "#f0fdf4", border: "1px solid #bbf7d0", borderRadius: 8, padding: "14px 16px" }}>
            <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 8 }}>
              <Code2 size={16} color="#166534" />
              <span style={{ fontWeight: 700, color: "#166534", fontSize: 14 }}>tools.py — Testé ✓</span>
            </div>
            <p style={{ fontSize: 13.5, color: "#14532d", margin: 0 }}>
              Définitions des outils et leur dispatch — entièrement testés sans réseau. Toutes les fonctions
              de requête sur les résultats actuariels sont opérationnelles.
            </p>
          </div>
          <div style={{ background: "#fff7ed", border: "1px solid #fed7aa", borderRadius: 8, padding: "14px 16px" }}>
            <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 8 }}>
              <AlertTriangle size={16} color="#c2410c" />
              <span style={{ fontWeight: 700, color: "#c2410c", fontSize: 14 }}>copilot.py — Non testé E2E</span>
            </div>
            <p style={{ fontSize: 13.5, color: "#9a3412", margin: 0 }}>
              Boucle d&apos;appel à l&apos;API Anthropic — nécessite <code style={{ fontFamily: "monospace", fontSize: 12, background: "#fed7aa", padding: "1px 4px", borderRadius: 3 }}>ANTHROPIC_API_KEY</code> non configurée
              dans cet environnement.
            </p>
          </div>
        </div>
      </Section>

      <Section title="Outils disponibles" icon={<Code2 size={18} />}>
        <p style={{ fontSize: 14, color: "#64748b", marginBottom: 14 }}>
          6 outils actuariels exposés à Claude pour l&apos;appel de fonction :
        </p>
        <table className="data-table">
          <thead>
            <tr>
              <th>Outil</th>
              <th>Description</th>
              <th>Statut</th>
            </tr>
          </thead>
          <tbody>
            {tools.map((tool, i) => (
              <tr key={i}>
                <td>
                  <code style={{ fontFamily: "monospace", fontSize: 13, color: "#1e40af" }}>
                    {tool.name}
                  </code>
                </td>
                <td style={{ fontSize: 13.5, color: "#475569" }}>{tool.desc}</td>
                <td><span className="badge badge-green">Testé</span></td>
              </tr>
            ))}
          </tbody>
        </table>
      </Section>

      <Section title="Pour activer le copilote" icon={<Bot size={18} />}>
        <div style={{ background: "#0f172a", borderRadius: 10, padding: "16px 20px" }}>
          <pre style={{ fontFamily: "monospace", fontSize: 13, color: "#e2e8f0", margin: 0, whiteSpace: "pre-wrap" }}>
{`# Configurer la clé API
set ANTHROPIC_API_KEY=sk-ant-...

# Lancer le copilote
python -m src.m13_copilot.copilot`}
          </pre>
        </div>
        <p style={{ fontSize: 13, color: "#64748b", marginTop: 10 }}>
          Une fois la clé configurée, le copilote peut répondre à des questions en langage naturel comme
          &quot;Quel est le SCR de mortalité ?&quot; ou &quot;Explique la duration gap ALM.&quot;
        </p>
      </Section>

      <LimitBox items={[
        {
          title: "API Anthropic non testée de bout en bout",
          text: "La clé ANTHROPIC_API_KEY n'était pas disponible pendant le développement. La boucle d'appel API copilot.py n'a pas pu être testée en intégration complète.",
        },
        {
          title: "Outils entièrement testés sans réseau",
          text: "Les fonctions de dispatch des outils (tools.py) sont couvertes par des tests unitaires indépendants de l'API — la logique actuarielle est validée.",
        },
      ]} />
    </ModuleLayout>
  );
}
