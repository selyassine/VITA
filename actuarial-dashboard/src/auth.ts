import NextAuth from "next-auth";
import Credentials from "next-auth/providers/credentials";
import { authConfig } from "./auth.config";

export const { handlers, signIn, signOut, auth } = NextAuth({
  ...authConfig,
  providers: [
    Credentials({
      credentials: {
        username: { label: "Username", type: "text" },
        password: { label: "Password", type: "password" }
      },
      authorize: async (credentials) => {
        // Identifiants codés en dur pour la démo
        // À remplacer par des variables d'environnement en production
        const validUsername = "jury";
        const validPassword = "actuariat2026";

        if (credentials.username === validUsername && credentials.password === validPassword) {
          return {
            id: "1",
            name: "Jury Mémoire",
            email: "jury@actuariat.fr",
          };
        }
        return null;
      },
    }),
  ],
});
