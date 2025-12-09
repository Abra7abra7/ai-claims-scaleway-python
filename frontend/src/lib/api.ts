import createClient from "openapi-fetch";
import type { paths } from "./api-types";

// Create type-safe API client
export const api = createClient<paths>({
  baseUrl: process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000",
  headers: {
    "Content-Type": "application/json",
  },
});

// Helper to add auth headers
export function withAuth(userId?: string, userEmail?: string) {
  return createClient<paths>({
    baseUrl: process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000",
    headers: {
      "Content-Type": "application/json",
      ...(userId && { "X-User-Id": userId }),
      ...(userEmail && { "X-User-Email": userEmail }),
    },
  });
}

