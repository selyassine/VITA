"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useState } from "react";
import {
  Menu,
  X,
  Shield,
  FileText,
  Beaker,
  BookOpen,
  LogOut,
  Home,
  ChevronDown,
  ChevronRight,
} from "lucide-react";

const moduleLinks = [
  { href: "/modules/m1-mortalite",          label: "M1 — Mortalité" },
  { href: "/modules/m2-tarification",        label: "M2 — Tarification" },
  { href: "/modules/m3-provisionnement",     label: "M3 — Provisionnement" },
  { href: "/modules/m4-scr",                 label: "M4 — SCR" },
  { href: "/modules/m5-rachats",             label: "M5 — Rachats" },
  { href: "/modules/m6-underwriting",        label: "M6 — Underwriting" },
  { href: "/modules/m7-longevite",           label: "M7 — Longévité" },
  { href: "/modules/m8-alm",                 label: "M8 — ALM" },
  { href: "/modules/m9-optimizer",           label: "M9 — Optimizer" },
  { href: "/modules/m10-risques-emergents",  label: "M10 — Risques émergents" },
  { href: "/modules/m11-orsa",               label: "M11 — ORSA" },
  { href: "/modules/m12-dashboard",          label: "M12 — Dashboard" },
  { href: "/modules/m13-copilot",            label: "M13 — Copilot IA" },
  { href: "/modules/m14-compliance",         label: "M14 — Conformité" },
  { href: "/modules/m15-digital-twin",       label: "M15 — Digital Twin" },
];

export default function Navigation() {
  const pathname = usePathname();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [modulesOpen, setModulesOpen] = useState(false);

  const isActive = (path: string) => pathname === path || pathname.startsWith(path + "/");
  const isModulesSection = pathname.startsWith("/modules");

  const handleLogout = async () => {
    window.location.href = "/api/auth/signout";
  };

  return (
    <nav
      style={{
        position: "fixed",
        top: 0, left: 0, right: 0,
        height: 64,
        background: "linear-gradient(135deg, #0a0f1e 0%, #111b33 100%)",
        borderBottom: "1px solid rgba(255,255,255,0.07)",
        zIndex: 50,
        display: "flex",
        alignItems: "center",
        boxShadow: "0 2px 16px rgba(0,0,0,0.3)",
      }}
    >
      <div
        style={{
          maxWidth: 1280,
          margin: "0 auto",
          width: "100%",
          padding: "0 24px",
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
        }}
      >
        {/* Logo */}
        <Link
          href="/accueil"
          style={{
            display: "flex",
            alignItems: "center",
            gap: 10,
            textDecoration: "none",
            color: "white",
          }}
        >
          <div
            style={{
              width: 34,
              height: 34,
              borderRadius: 8,
              background: "linear-gradient(135deg, #3b82f6, #1d4ed8)",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
            }}
          >
            <Shield size={18} color="white" />
          </div>
          <div>
            <div style={{ fontSize: 15, fontWeight: 700, lineHeight: 1 }}>
              VitaAI Actuariat
            </div>
            <div style={{ fontSize: 11, color: "rgba(255,255,255,0.5)", lineHeight: 1, marginTop: 2 }}>
              Mémoire · 15 Modules
            </div>
          </div>
        </Link>

        {/* Desktop Navigation */}
        <div style={{ display: "flex", alignItems: "center", gap: 4 }} className="hide-mobile">
          <NavItem href="/accueil" icon={<Home size={15} />} label="Accueil" active={isActive("/accueil")} />

          {/* Modules dropdown */}
          <div style={{ position: "relative" }}>
            <button
              onClick={() => setModulesOpen(!modulesOpen)}
              style={{
                display: "flex",
                alignItems: "center",
                gap: 6,
                padding: "7px 12px",
                borderRadius: 8,
                border: "none",
                cursor: "pointer",
                fontSize: 14,
                fontWeight: 500,
                fontFamily: "inherit",
                background: isModulesSection ? "rgba(59,130,246,0.18)" : "transparent",
                color: isModulesSection ? "#93c5fd" : "rgba(255,255,255,0.7)",
                transition: "all 0.15s",
              }}
              onMouseEnter={e => {
                if (!isModulesSection) (e.currentTarget as HTMLButtonElement).style.background = "rgba(255,255,255,0.07)";
                (e.currentTarget as HTMLButtonElement).style.color = "white";
              }}
              onMouseLeave={e => {
                if (!isModulesSection) (e.currentTarget as HTMLButtonElement).style.background = "transparent";
                (e.currentTarget as HTMLButtonElement).style.color = isModulesSection ? "#93c5fd" : "rgba(255,255,255,0.7)";
              }}
            >
              <FileText size={15} />
              <span>Modules</span>
              {modulesOpen ? <ChevronDown size={13} /> : <ChevronRight size={13} />}
            </button>

            {modulesOpen && (
              <>
                <div
                  style={{
                    position: "fixed",
                    inset: 0,
                    zIndex: 40,
                  }}
                  onClick={() => setModulesOpen(false)}
                />
                <div
                  style={{
                    position: "absolute",
                    top: "calc(100% + 8px)",
                    left: 0,
                    width: 240,
                    background: "white",
                    border: "1px solid #e2e8f0",
                    borderRadius: 12,
                    boxShadow: "0 8px 32px rgba(0,0,0,0.15)",
                    padding: "8px 0",
                    zIndex: 50,
                    maxHeight: "80vh",
                    overflowY: "auto",
                  }}
                >
                  <div style={{ padding: "8px 16px 4px", fontSize: 11, fontWeight: 700, color: "#94a3b8", textTransform: "uppercase", letterSpacing: "0.08em" }}>
                    15 Modules
                  </div>
                  {moduleLinks.map(m => (
                    <Link
                      key={m.href}
                      href={m.href}
                      onClick={() => setModulesOpen(false)}
                      style={{
                        display: "block",
                        padding: "8px 16px",
                        fontSize: 13.5,
                        fontWeight: 500,
                        textDecoration: "none",
                        color: pathname === m.href ? "#1d4ed8" : "#334155",
                        background: pathname === m.href ? "#dbeafe" : "transparent",
                        transition: "all 0.1s",
                      }}
                      onMouseEnter={e => {
                        if (pathname !== m.href) {
                          (e.currentTarget as HTMLAnchorElement).style.background = "#f1f5f9";
                        }
                      }}
                      onMouseLeave={e => {
                        if (pathname !== m.href) {
                          (e.currentTarget as HTMLAnchorElement).style.background = "transparent";
                        }
                      }}
                    >
                      {m.label}
                    </Link>
                  ))}
                </div>
              </>
            )}
          </div>

          <NavItem href="/demo" icon={<Beaker size={15} />} label="Tester en direct" active={isActive("/demo")} />
          <NavItem href="/methodologie" icon={<BookOpen size={15} />} label="Méthodologie" active={isActive("/methodologie")} />

          <div style={{ width: 1, height: 24, background: "rgba(255,255,255,0.12)", margin: "0 8px" }} />

          <button
            onClick={handleLogout}
            style={{
              display: "flex",
              alignItems: "center",
              gap: 6,
              padding: "7px 12px",
              borderRadius: 8,
              border: "none",
              cursor: "pointer",
              fontSize: 14,
              fontWeight: 500,
              fontFamily: "inherit",
              background: "transparent",
              color: "rgba(255,255,255,0.55)",
              transition: "all 0.15s",
            }}
            onMouseEnter={e => {
              (e.currentTarget as HTMLButtonElement).style.background = "rgba(239,68,68,0.15)";
              (e.currentTarget as HTMLButtonElement).style.color = "#fca5a5";
            }}
            onMouseLeave={e => {
              (e.currentTarget as HTMLButtonElement).style.background = "transparent";
              (e.currentTarget as HTMLButtonElement).style.color = "rgba(255,255,255,0.55)";
            }}
          >
            <LogOut size={15} />
            <span>Déconnexion</span>
          </button>
        </div>

        {/* Mobile burger */}
        <button
          onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
          style={{
            background: "transparent",
            border: "none",
            color: "rgba(255,255,255,0.8)",
            cursor: "pointer",
            padding: 8,
            borderRadius: 8,
          }}
          className="show-mobile"
        >
          {mobileMenuOpen ? <X size={22} /> : <Menu size={22} />}
        </button>
      </div>

      {/* Mobile menu */}
      {mobileMenuOpen && (
        <div
          style={{
            position: "absolute",
            top: 64,
            left: 0,
            right: 0,
            background: "#0d1426",
            borderBottom: "1px solid rgba(255,255,255,0.08)",
            padding: "12px 16px",
            maxHeight: "80vh",
            overflowY: "auto",
          }}
        >
          {[
            { href: "/accueil", label: "Accueil" },
            { href: "/modules", label: "Tous les modules" },
            ...moduleLinks.slice(0, 5),
            { href: "/demo", label: "Tester en direct" },
            { href: "/methodologie", label: "Méthodologie" },
          ].map(item => (
            <Link
              key={item.href}
              href={item.href}
              onClick={() => setMobileMenuOpen(false)}
              style={{
                display: "block",
                padding: "10px 12px",
                color: pathname === item.href ? "#93c5fd" : "rgba(255,255,255,0.7)",
                textDecoration: "none",
                fontSize: 15,
                borderRadius: 8,
              }}
            >
              {item.label}
            </Link>
          ))}
        </div>
      )}

      <style>{`
        @media (max-width: 768px) { .hide-mobile { display: none !important; } }
        @media (min-width: 769px) { .show-mobile { display: none !important; } }
      `}</style>
    </nav>
  );
}

function NavItem({ href, icon, label, active }: { href: string; icon: React.ReactNode; label: string; active: boolean }) {
  return (
    <Link
      href={href}
      style={{
        display: "flex",
        alignItems: "center",
        gap: 6,
        padding: "7px 12px",
        borderRadius: 8,
        textDecoration: "none",
        fontSize: 14,
        fontWeight: 500,
        background: active ? "rgba(59,130,246,0.18)" : "transparent",
        color: active ? "#93c5fd" : "rgba(255,255,255,0.7)",
        transition: "all 0.15s",
      }}
      onMouseEnter={e => {
        if (!active) (e.currentTarget as HTMLAnchorElement).style.background = "rgba(255,255,255,0.07)";
        (e.currentTarget as HTMLAnchorElement).style.color = "white";
      }}
      onMouseLeave={e => {
        if (!active) (e.currentTarget as HTMLAnchorElement).style.background = "transparent";
        (e.currentTarget as HTMLAnchorElement).style.color = active ? "#93c5fd" : "rgba(255,255,255,0.7)";
      }}
    >
      {icon}
      <span>{label}</span>
    </Link>
  );
}
