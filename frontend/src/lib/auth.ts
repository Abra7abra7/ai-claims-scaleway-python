import { betterAuth } from "better-auth";
import { Pool } from "pg";

// PostgreSQL connection pool
const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
});

export const auth = betterAuth({
  database: pool,
  
  // Email + Password authentication
  emailAndPassword: {
    enabled: true,
    requireEmailVerification: false, // Set to true in production with email service
  },
  
  // Social authentication providers
  socialProviders: {
    google: {
      clientId: process.env.GOOGLE_CLIENT_ID!,
      clientSecret: process.env.GOOGLE_CLIENT_SECRET!,
    },
  },
  
  // Session configuration
  session: {
    expiresIn: 60 * 60 * 24 * 7, // 7 days
    updateAge: 60 * 60 * 24, // Update session every 24 hours
    cookieCache: {
      enabled: true,
      maxAge: 5 * 60, // 5 minutes
    },
  },
  
  // User configuration
  user: {
    additionalFields: {
      role: {
        type: "string",
        defaultValue: "user",
      },
      locale: {
        type: "string", 
        defaultValue: "sk",
      },
    },
  },
  
  // Trusted origins for CORS
  trustedOrigins: [
    process.env.NEXT_PUBLIC_APP_URL || "http://localhost:3000",
  ],
});

export type Session = typeof auth.$Infer.Session;
export type User = typeof auth.$Infer.Session.user;

