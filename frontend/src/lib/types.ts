/**
 * Re-exports of auto-generated API types for convenient imports.
 * 
 * Instead of importing manually defined interfaces, import from here:
 * 
 * @example
 * import { ClaimDetail, RAGDocument, AuditLog } from "@/lib/types";
 * 
 * Types are auto-generated from backend OpenAPI spec.
 * Run `npm run generate-types` to update after backend changes.
 */

import type { components, operations } from "./api-types";

// ==================== Claims ====================
export type ClaimSummary = components["schemas"]["ClaimSummary"];
export type ClaimDetail = components["schemas"]["ClaimDetail"];
export type ClaimStatus = components["schemas"]["ClaimStatus"];
export type ClaimListResponse = components["schemas"]["ClaimListResponse"];
export type ClaimStatsResponse = components["schemas"]["ClaimStatsResponse"];
export type DocumentResponse = components["schemas"]["DocumentResponse"];

// ==================== OCR & Anonymization ====================
export type OCRReviewDocument = components["schemas"]["OCRReviewDocument"];
export type OCRReviewResponse = components["schemas"]["OCRReviewResponse"];
export type AnonReviewDocument = components["schemas"]["AnonReviewDocument"];
export type AnonReviewResponse = components["schemas"]["AnonReviewResponse"];
export type CleaningStats = components["schemas"]["CleaningStats"];
export type CleaningPreviewDocument = components["schemas"]["CleaningPreviewDocument"];
export type CleaningPreviewResponse = components["schemas"]["CleaningPreviewResponse"];

// ==================== RAG Documents ====================
export type RAGDocument = components["schemas"]["RAGDocumentSummary"];
export type RAGDocumentSummary = components["schemas"]["RAGDocumentSummary"];
export type RAGFolderStructure = components["schemas"]["RAGFolderStructure"];
export type RAGDocumentType = components["schemas"]["RAGDocumentType"];
export type RAGUploadResponse = components["schemas"]["RAGUploadResponse"];

// ==================== Reports ====================
export type ReportSummary = components["schemas"]["ReportSummary"];
export type ReportListResponse = components["schemas"]["ReportListResponse"];

// ==================== Prompts ====================
export type PromptSummary = components["schemas"]["PromptSummary"];
export type PromptListResponse = components["schemas"]["PromptListResponse"];
export type PromptConfigResponse = components["schemas"]["PromptConfigResponse"];

// ==================== Audit ====================
export type AuditLog = components["schemas"]["AuditLogDetail"];
export type AuditLogDetail = components["schemas"]["AuditLogDetail"];
export type AuditLogListResponse = components["schemas"]["AuditLogListResponse"];
export type ClaimAuditTrail = components["schemas"]["ClaimAuditTrail"];

// ==================== Auth & Users ====================
export type User = components["schemas"]["UserResponse"];
export type UserResponse = components["schemas"]["UserResponse"];
export type UserSession = components["schemas"]["SessionResponse"];
export type SessionResponse = components["schemas"]["SessionResponse"];
export type SessionListResponse = components["schemas"]["SessionListResponse"];
export type LoginResponse = components["schemas"]["LoginResponse"];
export type AuthStatusResponse = components["schemas"]["AuthStatusResponse"];

// ==================== Statistics ====================
export type DashboardStats = components["schemas"]["DashboardStats"];
export type ClaimCountByStatus = components["schemas"]["ClaimCountByStatus"];
export type ClaimCountByCountry = components["schemas"]["ClaimCountByCountry"];
export type ClaimProcessingStats = components["schemas"]["ClaimProcessingStats"];
export type TimeRangeStats = components["schemas"]["TimeRangeStats"];

// ==================== Misc ====================
export type HealthResponse = components["schemas"]["HealthResponse"];
export type MessageResponse = components["schemas"]["app__api__v1__schemas__base__MessageResponse"];
export type Country = components["schemas"]["Country"];

// ==================== Password Reset & Email Verification ====================
export type PasswordResetRequest = components["schemas"]["PasswordResetRequest"];
export type PasswordResetConfirm = components["schemas"]["PasswordResetConfirm"];
export type EmailVerificationRequest = components["schemas"]["EmailVerificationRequest"];

// ==================== Operations (for API client) ====================
export type Operations = operations;

