"use client";

import Link from "next/link";
import { ArrowLeft, CheckCircle, AlertTriangle } from "lucide-react";
import Image from "next/image";
import type { ReactNode } from "react";

interface ModuleLayoutProps {
  moduleId: string;
  moduleNumber: string;
  title: string;
  subtitle: string;
  status: "functional" | "partial";
  statusLabel?: string;
  children: ReactNode;
}

export default function ModuleLayout({
  moduleId,
  moduleNumber,
  title,
  subtitle,
  status,
  statusLabel,
  children,
}: ModuleLayoutProps) {
  const isPartial = status === "partial";

  return (
    <div style={{ minHeight: "100vh", background: "#f8fafc" }}>
      {/* Page header */}
      <div
        style={{
          background: "linear-gradient(135deg, #0a0f1e 0%, #111b33 100%)",
          padding: "28px 0 32px",
          borderBottom: "1px solid rgba(255,255,255,0.06)",
        }}
      >
        <div style={{ maxWidth: 1100, margin: "0 auto", padding: "0 24px" }}>
          <Link
            href="/modules"
            style={{
              display: "inline-flex",
              alignItems: "center",
              gap: 6,
              color: "rgba(255,255,255,0.5)",
              textDecoration: "none",
              fontSize: 13,
              marginBottom: 16,
              transition: "color 0.15s",
            }}
          >
            <ArrowLeft size={14} />
            Retour aux modules
          </Link>

          <div style={{ display: "flex", alignItems: "flex-start", justifyContent: "space-between", flexWrap: "wrap", gap: 16 }}>
            <div>
              <div style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: 8 }}>
                <span
                  style={{
                    fontSize: 11,
                    fontWeight: 700,
                    textTransform: "uppercase",
                    letterSpacing: "0.1em",
                    color: "#60a5fa",
                    background: "rgba(59,130,246,0.15)",
                    padding: "3px 10px",
                    borderRadius: 999,
                    border: "1px solid rgba(59,130,246,0.3)",
                  }}
                >
                  {moduleNumber}
                </span>
                <span
                  style={{
                    fontSize: 11,
                    fontWeight: 600,
                    textTransform: "uppercase",
                    letterSpacing: "0.06em",
                    padding: "3px 10px",
                    borderRadius: 999,
                    background: isPartial ? "rgba(251,191,36,0.15)" : "rgba(74,222,128,0.15)",
                    color: isPartial ? "#fbbf24" : "#4ade80",
                    border: `1px solid ${isPartial ? "rgba(251,191,36,0.3)" : "rgba(74,222,128,0.3)"}`,
                    display: "flex",
                    alignItems: "center",
                    gap: 4,
                  }}
                >
                  {isPartial ? <AlertTriangle size={11} /> : <CheckCircle size={11} />}
                  {statusLabel || (isPartial ? "Partiel" : "Fonctionnel")}
                </span>
              </div>
              <h1 style={{ color: "white", fontSize: 30, fontWeight: 800, margin: 0, letterSpacing: "-0.02em" }}>
                {title}
              </h1>
              <p style={{ color: "rgba(255,255,255,0.55)", fontSize: 15, marginTop: 6 }}>
                {subtitle}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Content */}
      <div style={{ maxWidth: 1100, margin: "0 auto", padding: "32px 24px" }}>
        {children}
      </div>
    </div>
  );
}

/* ---- Reusable sub-components ---- */

export function Section({ title, icon, children, style }: { title: string; icon?: ReactNode; children: ReactNode; style?: React.CSSProperties }) {
  return (
    <section
      style={{
        background: "white",
        border: "1px solid #e2e8f0",
        borderRadius: 12,
        padding: "24px 28px",
        marginBottom: 24,
        boxShadow: "0 1px 3px rgba(0,0,0,0.05)",
        ...style,
      }}
    >
      <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 20, paddingBottom: 14, borderBottom: "1px solid #f1f5f9" }}>
        {icon && (
          <div style={{ color: "#3b82f6" }}>
            {icon}
          </div>
        )}
        <h2 style={{ fontSize: 18, fontWeight: 700, color: "#0f172a", margin: 0 }}>{title}</h2>
      </div>
      {children}
    </section>
  );
}

export function MetricGrid({ children }: { children: ReactNode }) {
  return (
    <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(180px, 1fr))", gap: 14 }}>
      {children}
    </div>
  );
}

export function MetricCard({
  label,
  value,
  sub,
  color = "default",
}: {
  label: string;
  value: string;
  sub?: string;
  color?: "default" | "green" | "blue" | "amber" | "red";
}) {
  const colors = {
    default: { bg: "#f8fafc", accent: "#3b82f6", text: "#0f172a" },
    green:   { bg: "#f0fdf4", accent: "#22c55e", text: "#166534" },
    blue:    { bg: "#eff6ff", accent: "#3b82f6", text: "#1e40af" },
    amber:   { bg: "#fffbeb", accent: "#f59e0b", text: "#92400e" },
    red:     { bg: "#fff1f2", accent: "#ef4444", text: "#991b1b" },
  };
  const c = colors[color];

  return (
    <div
      style={{
        background: c.bg,
        border: `1px solid ${c.accent}22`,
        borderRadius: 10,
        padding: "16px 18px",
        position: "relative",
        overflow: "hidden",
      }}
    >
      <div style={{
        position: "absolute", top: 0, left: 0, right: 0, height: 3,
        background: c.accent,
      }} />
      <p style={{ fontSize: 11, fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.08em", color: c.text, opacity: 0.7, marginBottom: 6 }}>
        {label}
      </p>
      <p style={{ fontSize: 24, fontWeight: 800, color: c.text, letterSpacing: "-0.02em", lineHeight: 1 }}>
        {value}
      </p>
      {sub && (
        <p style={{ fontSize: 11.5, color: c.text, opacity: 0.65, marginTop: 4 }}>
          {sub}
        </p>
      )}
    </div>
  );
}

export function LimitBox({ items }: { items: { title: string; text: string }[] }) {
  return (
    <section
      style={{
        background: "#fffbeb",
        border: "1px solid #fde68a",
        borderLeft: "4px solid #f59e0b",
        borderRadius: 12,
        padding: "20px 24px",
        marginBottom: 24,
      }}
    >
      <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 14 }}>
        <AlertTriangle size={18} color="#d97706" />
        <h2 style={{ fontSize: 16, fontWeight: 700, color: "#92400e", margin: 0 }}>
          Limites Méthodologiques
        </h2>
      </div>
      <ul style={{ listStyle: "none", padding: 0, margin: 0, display: "flex", flexDirection: "column", gap: 10 }}>
        {items.map((item, i) => (
          <li key={i} style={{ display: "flex", alignItems: "flex-start", gap: 10, fontSize: 13.5, color: "#78350f" }}>
            <span style={{ flexShrink: 0, marginTop: 2, width: 6, height: 6, borderRadius: "50%", background: "#f59e0b", display: "inline-block" }} />
            <span>
              <strong>{item.title} : </strong>
              {item.text}
            </span>
          </li>
        ))}
      </ul>
    </section>
  );
}

export function ChartImage({ src, alt, caption }: { src: string; alt: string; caption?: string }) {
  return (
    <div>
      <div
        style={{
          background: "#f8fafc",
          border: "1px solid #e2e8f0",
          borderRadius: 10,
          padding: 12,
          overflow: "hidden",
        }}
      >
        <Image
          src={src}
          alt={alt}
          width={900}
          height={450}
          style={{ width: "100%", height: "auto", borderRadius: 6 }}
          priority
        />
      </div>
      {caption && (
        <p style={{ fontSize: 12.5, color: "#94a3b8", textAlign: "center", marginTop: 8 }}>
          {caption}
        </p>
      )}
    </div>
  );
}
