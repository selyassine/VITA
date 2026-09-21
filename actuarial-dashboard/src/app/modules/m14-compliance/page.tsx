import ModuleLayout, { Section, LimitBox } from "@/components/ModuleLayout";
import { ClipboardCheck, ShieldCheck } from "lucide-react";

export const metadata = {
  title: "M14 — Conformité | Plateforme Actuarielle",
  description: "Checklist documentaire ORSA et Solvabilité II",
};

const complianceItems = [
  {
    item: "Profil de risque biométrique",
    module: "M4",
    desc: "SCR mortalité/longévité calculé et décomposé par sous-module.",
    status: "OK"
  },
  {
    item: "Besoin global de solvabilité",
    module: "M4",
    desc: "Ratio de couverture SCR calculé (fonds propres / SCR).",
    status: "OK"
  },
  {
    item: "Évaluation prospective pluriannuelle",
    module: "M11",
    desc: "Projection du besoin de capital sur plusieurs années (run-off).",
    status: "OK"
  },
  {
    item: "Politique de gestion du capital / tarification",
    module: "M9",
    desc: "Analyse du chargement commercial et de son impact sur le SCR.",
    status: "OK"
  },
  {
    item: "Sensibilité au risque de taux",
    module: "M8",
    desc: "Duration actif/passif et sensibilité du NAV aux chocs de taux EIOPA.",
    status: "OK"
  },
  {
    item: "Sensibilité aux risques biométriques (approche stochastique)",
    module: "M7",
    desc: "VaR 99.5% par simulation Monte-Carlo des trajectoires de mortalité.",
    status: "OK"
  },
  {
    item: "Risque de rachat (lapse)",
    module: "M5",
    desc: "Modélisation du risque de résiliation (label dérivé).",
    status: "OK"
  },
  {
    item: "Risque de souscription / tarification",
    module: "M2",
    desc: "Prime pure calculée par équivalence actuarielle.",
    status: "OK"
  },
  {
    item: "Classification du risque à la souscription",
    module: "M6",
    desc: "Modèle de classification du risque assuré (Prudential).",
    status: "OK"
  },
  {
    item: "Veille des risques émergents",
    module: "M10",
    desc: "Comparaison thématique de rapports de supervision (EIOPA/ACPR).",
    status: "OK"
  }
];

export default function M14CompliancePage() {
  return (
    <ModuleLayout
      moduleId="m14-compliance"
      moduleNumber="Module 14"
      title="M14 — Conformité"
      subtitle="Checklist documentaire d'auto-vérification pour le rapport ORSA / SFCR"
      status="functional"
    >
      <Section title="Méthodologie" icon={<ClipboardCheck size={18} />}>
        <p style={{ color: "#475569", lineHeight: 1.75, fontSize: 14.5 }}>
          M14 est une <strong>checklist d&apos;auto-vérification documentaire</strong> : la plateforme vérifie-t-elle
          et produit-elle une preuve chiffrée pour chaque grande rubrique qu&apos;un rapport ORSA (Own Risk and Solvency Assessment)
          et SFCR (Solvency and Financial Condition Report) est censé couvrir ? Ce module scanne les résultats des
          autres modules pour confirmer la couverture de ces exigences réglementaires.
        </p>
      </Section>

      <Section title="Checklist Documentaire ORSA / Solvabilité II" icon={<ShieldCheck size={18} />}>
        <table className="data-table">
          <thead>
            <tr>
              <th>Rubrique Réglementaire</th>
              <th>Module Source</th>
              <th>Preuve Documentaire</th>
              <th>Statut</th>
            </tr>
          </thead>
          <tbody>
            {complianceItems.map((c, i) => (
              <tr key={i}>
                <td><strong>{c.item}</strong></td>
                <td><span className="badge badge-blue">{c.module}</span></td>
                <td style={{ color: "#64748b", fontSize: 13 }}>{c.desc}</td>
                <td><span className="badge badge-green">{c.status}</span></td>
              </tr>
            ))}
          </tbody>
        </table>
      </Section>

      <LimitBox items={[
        {
          title: "Ce n'est PAS un avis juridique",
          text: "M14 est une vérification interne de complétude technique (les modules ont-ils tourné ?). Ce n'est en aucun cas une certification de conformité réglementaire réelle ou un avis juridique. À rappeler explicitement si cette section est citée dans le mémoire.",
        },
        {
          title: "Périmètre partiel",
          text: "L'ORSA réel couvre de nombreux autres risques non modélisés ici (risque opérationnel, liquidité détaillée, gouvernance, risques climatiques approfondis).",
        }
      ]} />
    </ModuleLayout>
  );
}
