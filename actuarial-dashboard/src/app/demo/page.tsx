"use client";

import { useState } from "react";
import ModuleLayout, { Section } from "@/components/ModuleLayout";
import { SlidersHorizontal, BarChart2 } from "lucide-react";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ReferenceLine } from "recharts";

export default function DemoPage() {
  const [elasticity, setElasticity] = useState(2.0);

  // M9 formula: Optimal loading = 1 + 1/elasticity
  // Margin(x) approx curve for demo: Total Margin = Volume * Unit Margin
  // Volume(x) = BaseVolume * (1 - elasticity * (x - 1))
  // UnitMargin(x) = x - 1
  // Max is strictly at x = 1 + 1/(2*elasticity) if we use linear demand.
  // Wait, the formula in M9 says 1 + 1/ε. This implies exponential demand Volume(x) = BaseVolume * e^(-ε*x)
  // Let's use Volume(x) = 10000 * e^(-elasticity * (x - 1))
  // Margin(x) = Volume(x) * (x - 1) * 1000
  
  const generateData = (eps: number) => {
    const data = [];
    for (let x = 1.0; x <= 3.0; x += 0.05) {
      const volume = 10000 * Math.exp(-eps * (x - 1));
      const margin = volume * (x - 1) * 1000;
      data.push({
        loading: parseFloat(x.toFixed(2)),
        margin: parseFloat((margin / 1e6).toFixed(2)),
        volume: Math.round(volume),
      });
    }
    return data;
  };

  const data = generateData(elasticity);
  const optimalLoading = 1 + 1 / elasticity;
  
  // Find max margin point for reference line
  const maxPoint = data.reduce((prev, current) => (prev.margin > current.margin) ? prev : current, data[0]);

  return (
    <ModuleLayout
      moduleId="demo"
      moduleNumber="Démo"
      title="Tester en direct : Arbitrage M9"
      subtitle="Simulation interactive de l'optimisation du chargement commercial (Module 9)"
      status="functional"
    >
      <div style={{ display: "grid", gridTemplateColumns: "300px 1fr", gap: 24, alignItems: "start" }}>
        
        {/* Controls */}
        <div style={{ position: "sticky", top: 88 }}>
          <Section title="Paramètres" icon={<SlidersHorizontal size={18} />}>
            <div style={{ marginBottom: 20 }}>
              <label style={{ display: "block", fontSize: 13, fontWeight: 700, color: "#334155", marginBottom: 8 }}>
                Élasticité au rachat (ε)
              </label>
              <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
                <input
                  type="range"
                  min="0.5"
                  max="5.0"
                  step="0.1"
                  value={elasticity}
                  onChange={e => setElasticity(parseFloat(e.target.value))}
                  style={{ flex: 1, accentColor: "#3b82f6" }}
                />
                <span style={{ fontSize: 15, fontWeight: 700, color: "#0f172a", width: 36 }}>
                  {elasticity.toFixed(1)}
                </span>
              </div>
              <p style={{ fontSize: 12, color: "#64748b", marginTop: 8, lineHeight: 1.5 }}>
                Une forte élasticité signifie que les assurés résilient massivement si le chargement augmente.
              </p>
            </div>

            <div style={{ padding: "16px", background: "#f8fafc", borderRadius: 8, border: "1px solid #e2e8f0" }}>
              <h4 style={{ fontSize: 12, textTransform: "uppercase", letterSpacing: "0.08em", fontWeight: 700, color: "#64748b", margin: "0 0 12px" }}>
                Résultat Optimal (Formule)
              </h4>
              <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 8 }}>
                <span style={{ fontSize: 13, color: "#334155" }}>Chargement opt.</span>
                <span style={{ fontSize: 14, fontWeight: 700, color: "#166534" }}>{optimalLoading.toFixed(2)}×</span>
              </div>
              <div style={{ display: "flex", justifyContent: "space-between" }}>
                <span style={{ fontSize: 13, color: "#334155" }}>Marge max</span>
                <span style={{ fontSize: 14, fontWeight: 700, color: "#1d4ed8" }}>{maxPoint.margin.toFixed(2)} M€</span>
              </div>
            </div>
          </Section>
        </div>

        {/* Chart */}
        <Section title="Courbe de Marge Commerciale Interactive" icon={<BarChart2 size={18} />}>
          <p style={{ fontSize: 14, color: "#475569", marginBottom: 20 }}>
            Visualisation en temps réel de l&apos;impact du chargement sur la marge totale générée (en M€). 
            Le modèle suppose une demande exponentiellement décroissante <code style={{ fontSize: 12 }}>V(x) = V₀·e^(-ε(x-1))</code>.
          </p>
          
          <div style={{ height: 400, background: "#f8fafc", padding: "20px 20px 0 0", borderRadius: 12, border: "1px solid #e2e8f0" }}>
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={data}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#cbd5e1" />
                <XAxis 
                  dataKey="loading" 
                  type="number" 
                  domain={[1.0, 3.0]} 
                  tickCount={11}
                  stroke="#64748b" 
                  fontSize={12} 
                  tickFormatter={val => val.toFixed(1) + "×"}
                />
                <YAxis 
                  stroke="#64748b" 
                  fontSize={12} 
                  tickFormatter={val => val + " M€"}
                />
                <Tooltip 
                  formatter={(value: number, name: string) => {
                    if (name === "marge") return [value + " M€", "Marge totale"];
                    if (name === "volume") return [value + " contrats", "Volume restant"];
                    return [value, name];
                  }}
                  labelFormatter={label => `Chargement : ${label}×`}
                  contentStyle={{ borderRadius: 8, boxShadow: "0 4px 12px rgba(0,0,0,0.1)", border: "1px solid #e2e8f0" }}
                />
                <ReferenceLine 
                  x={optimalLoading} 
                  stroke="#166534" 
                  strokeDasharray="5 5" 
                  label={{ position: 'top', value: 'Optimal', fill: '#166534', fontSize: 12, fontWeight: 600 }} 
                />
                <Line 
                  type="monotone" 
                  dataKey="margin" 
                  name="marge" 
                  stroke="#3b82f6" 
                  strokeWidth={3} 
                  dot={false}
                  activeDot={{ r: 6, fill: "#3b82f6", strokeWidth: 0 }}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </Section>
      </div>
    </ModuleLayout>
  );
}
