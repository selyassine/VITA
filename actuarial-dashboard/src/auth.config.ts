import type { NextAuthConfig } from "next-auth";

export const authConfig = {
  pages: {
    signIn: "/login",
  },
  providers: [
    // Providers ajoutés dans auth.ts pour éviter les erreurs de type
  ],
  callbacks: {
    authorized({ auth, request: { nextUrl } }) {
      const isLoggedIn = !!auth?.user;
      const isOnDashboard = nextUrl.pathname.startsWith("/accueil") || 
                           nextUrl.pathname.startsWith("/modules") ||
                           nextUrl.pathname.startsWith("/methodologie") ||
                           nextUrl.pathname.startsWith("/demo");
      
      if (isOnDashboard) {
        if (isLoggedIn) return true;
        return false; // Rediriger vers la page de login
      } else if (isLoggedIn && nextUrl.pathname === "/login") {
        return Response.redirect(new URL("/accueil", nextUrl));
      }
      return true;
    },
  },
} satisfies NextAuthConfig;
