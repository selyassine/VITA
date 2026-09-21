import type { Metadata } from "next";
import "./globals.css";
import Navigation from "@/components/Navigation";

export const metadata: Metadata = {
  title: "Plateforme Actuarielle Vie — Mémoire d'Actuariat",
  description:
    "Dashboard professionnel présentant les résultats d'un mémoire d'actuariat : 15 modules simulant une compagnie d'assurance-vie (tarification, provisionnement, SCR, rachats, ALM, ORSA…)",
  keywords: "actuariat, assurance-vie, Solvabilité II, SCR, Lee-Carter, ORSA, ALM",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="fr">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
      </head>
      <body style={{ minHeight: "100vh", backgroundColor: "#f8fafc" }}>
        <Navigation />
        <main style={{ paddingTop: "64px" }}>
          {children}
        </main>
      </body>
    </html>
  );
}
