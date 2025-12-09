"use client";

import { useState } from "react";
import { useTranslations } from "next-intl";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { format } from "date-fns";
import Link from "next/link";
import { useRouter } from "next/navigation";
import {
  ArrowLeft,
  FileText,
  Clock,
  CheckCircle,
  AlertCircle,
  Play,
  Eye,
  Trash2,
  RotateCcw,
  Download,
  Loader2,
  Brain,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { Separator } from "@/components/ui/separator";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog";
import { toast } from "sonner";
import { api } from "@/lib/api";
import { WorkflowProgress } from "./workflow-progress";
import { ActivityTimeline } from "./activity-timeline";
import { QuickActions } from "./quick-actions";
import { DocumentPreview } from "./document-preview";
import { useClaimPolling } from "@/hooks/use-claim-polling";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface ClaimDetailProps {
  claimId: number;
}

const statusColors: Record<string, string> = {
  PROCESSING: "bg-blue-500/10 text-blue-400 border-blue-500/20",
  OCR_REVIEW: "bg-yellow-500/10 text-yellow-400 border-yellow-500/20",
  CLEANING: "bg-purple-500/10 text-purple-400 border-purple-500/20",
  ANONYMIZING: "bg-orange-500/10 text-orange-400 border-orange-500/20",
  ANONYMIZATION_REVIEW: "bg-amber-500/10 text-amber-400 border-amber-500/20",
  READY_FOR_ANALYSIS: "bg-cyan-500/10 text-cyan-400 border-cyan-500/20",
  ANALYZING: "bg-indigo-500/10 text-indigo-400 border-indigo-500/20",
  ANALYZED: "bg-emerald-500/10 text-emerald-400 border-emerald-500/20",
  FAILED: "bg-red-500/10 text-red-400 border-red-500/20",
};

const countryFlags: Record<string, string> = {
  SK: "🇸🇰",
  IT: "🇮🇹",
  DE: "🇩🇪",
};

export function ClaimDetail({ claimId }: ClaimDetailProps) {
  const t = useTranslations("claims");
  const tCommon = useTranslations("common");
  const router = useRouter();
  const queryClient = useQueryClient();

  const [deleting, setDeleting] = useState(false);
  const [showDeleteDialog, setShowDeleteDialog] = useState(false);
  const [previewDocument, setPreviewDocument] = useState<any | null>(null);

  // Use polling hook for real-time updates
  const { claim, isPolling } = useClaimPolling({ claimId });
  
  const { isLoading, error } = useQuery({
    queryKey: ["claim", claimId],
    queryFn: async () => {
      const { data, error } = await api.GET("/api/v1/claims/{claim_id}", {
        params: { path: { claim_id: claimId } },
      });
      if (error) throw error;
      return data;
    },
  });

  const handleDelete = async () => {
    try {
      setDeleting(true);
      const token = localStorage.getItem("auth_token");

      const response = await fetch(`${API_URL}/api/v1/claims/${claimId}`, {
        method: "DELETE",
        credentials: "include",
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        throw new Error("Failed to delete claim");
      }

      toast.success("Claim deleted");
      queryClient.invalidateQueries({ queryKey: ["claims"] });
      router.push("/claims");
    } catch (err: any) {
      toast.error(err.message);
    } finally {
      setDeleting(false);
      setShowDeleteDialog(false);
    }
  };

  if (isLoading) {
    return (
      <div className="space-y-6">
        <Skeleton className="h-8 w-48 bg-zinc-800" />
        <Card className="border-zinc-800 bg-zinc-900">
          <CardContent className="p-6 space-y-4">
            <Skeleton className="h-6 w-32 bg-zinc-800" />
            <Skeleton className="h-4 w-64 bg-zinc-800" />
            <Skeleton className="h-4 w-48 bg-zinc-800" />
          </CardContent>
        </Card>
      </div>
    );
  }

  if (error || !claim) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="text-center">
          <AlertCircle className="mx-auto h-12 w-12 text-red-500" />
          <p className="mt-4 text-zinc-400">Failed to load claim</p>
          <Button asChild variant="outline" className="mt-4">
            <Link href="/claims">
              <ArrowLeft className="mr-2 h-4 w-4" />
              {tCommon("back")}
            </Link>
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Button asChild variant="ghost" size="icon">
            <Link href="/claims">
              <ArrowLeft className="h-5 w-5" />
            </Link>
          </Button>
          <div>
            <h1 className="text-2xl font-bold text-white">
              {t("title")} #{claimId}
            </h1>
            <div className="flex items-center gap-2 mt-1">
              <span className="text-lg">{countryFlags[claim.country] || "🌍"}</span>
              <span className="text-zinc-400">{claim.country}</span>
              <Separator orientation="vertical" className="h-4 bg-zinc-700" />
              <Badge variant="outline" className={statusColors[claim.status] || ""}>
                {t(`statuses.${claim.status}` as any) || claim.status}
              </Badge>
              {isPolling && (
                <>
                  <Separator orientation="vertical" className="h-4 bg-zinc-700" />
                  <div className="flex items-center gap-1 text-xs text-blue-400">
                    <Loader2 className="h-3 w-3 animate-spin" />
                    <span>Auto-updating...</span>
                  </div>
                </>
              )}
            </div>
          </div>
        </div>
        <div className="flex gap-2">
          {claim.status === "OCR_REVIEW" && (
            <Button asChild className="bg-yellow-600 hover:bg-yellow-700">
              <Link href={`/claims/${claimId}/ocr`}>
                <Eye className="mr-2 h-4 w-4" />
                {t("ocrReview")}
              </Link>
            </Button>
          )}
          {claim.status === "ANONYMIZATION_REVIEW" && (
            <Button asChild className="bg-amber-600 hover:bg-amber-700">
              <Link href={`/claims/${claimId}/anon`}>
                <Eye className="mr-2 h-4 w-4" />
                {t("anonymizationReview")}
              </Link>
            </Button>
          )}
          {(claim.status === "READY_FOR_ANALYSIS" || claim.status === "ANALYZED" || claim.status === "ANALYZING") && (
            <Button asChild className="bg-emerald-600 hover:bg-emerald-700">
              <Link href={`/claims/${claimId}/analysis`}>
                <Brain className="mr-2 h-4 w-4" />
                {claim.status === "ANALYZED" ? t("viewAnalysis") : t("startAnalysis")}
              </Link>
            </Button>
          )}
          <Button
            variant="outline"
            className="text-red-400 border-red-400 hover:bg-red-950/50"
            onClick={() => setShowDeleteDialog(true)}
          >
            <Trash2 className="mr-2 h-4 w-4" />
            {tCommon("delete")}
          </Button>
        </div>
      </div>

      {/* Workflow Progress */}
      <WorkflowProgress currentStatus={claim.status} />

      {/* Main Content Grid */}
      <div className="grid gap-6 lg:grid-cols-3">
        {/* Left Column - Claim Details */}
        <div className="lg:col-span-2 space-y-6">
          {/* Info Cards */}
          <div className="grid gap-4 md:grid-cols-3">
        <Card className="border-zinc-800 bg-zinc-900">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-zinc-400">
              {t("createdAt")}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2 text-white">
              <Clock className="h-4 w-4 text-zinc-500" />
              {claim.created_at
                ? format(new Date(claim.created_at), "dd.MM.yyyy HH:mm")
                : "-"}
            </div>
          </CardContent>
        </Card>
        <Card className="border-zinc-800 bg-zinc-900">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-zinc-400">
              {t("documents")}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2 text-white">
              <FileText className="h-4 w-4 text-zinc-500" />
              {claim.documents?.length ?? 0} documents
            </div>
          </CardContent>
        </Card>
        <Card className="border-zinc-800 bg-zinc-900">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-zinc-400">
              Model
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-white">
              {claim.analysis_model || "-"}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Documents */}
      <Card className="border-zinc-800 bg-zinc-900">
        <CardHeader>
          <CardTitle className="text-white">{t("documents")}</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          {claim.documents?.map((doc) => (
            <div
              key={doc.id}
              className="flex items-center justify-between rounded-lg border border-zinc-800 bg-zinc-800/50 p-4"
            >
              <div className="flex items-center gap-3">
                <FileText className="h-8 w-8 text-zinc-500" />
                <div>
                  <p className="font-medium text-white">{doc.filename}</p>
                  <p className="text-sm text-zinc-500">
                    {doc.ocr_reviewed_by && (
                      <span className="text-emerald-500">OCR reviewed ✓</span>
                    )}
                    {doc.anon_reviewed_by && (
                      <span className="ml-2 text-emerald-500">Anon reviewed ✓</span>
                    )}
                  </p>
                </div>
              </div>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setPreviewDocument(doc)}
              >
                <Eye className="h-4 w-4" />
              </Button>
            </div>
          ))}
        </CardContent>
      </Card>

          {/* Analysis Result */}
          {claim.analysis_result && (
            <Card className="border-zinc-800 bg-zinc-900">
              <CardHeader>
                <CardTitle className="text-white">{t("analysis")}</CardTitle>
              </CardHeader>
              <CardContent>
                <pre className="rounded-lg bg-zinc-800 p-4 text-sm text-zinc-300 overflow-auto">
                  {typeof claim.analysis_result === "string"
                    ? claim.analysis_result
                    : JSON.stringify(claim.analysis_result, null, 2)}
                </pre>
              </CardContent>
            </Card>
          )}
        </div>

        {/* Right Column - Activity Timeline & Quick Actions */}
        <div className="lg:col-span-1 space-y-6">
          <QuickActions claimId={claimId} currentStatus={claim.status} />
          <ActivityTimeline claimId={claimId} />
        </div>
      </div>

      {/* Document Preview Modal */}
      {previewDocument && (
        <DocumentPreview
          document={previewDocument}
          analysisResult={claim.analysis_result}
          open={!!previewDocument}
          onOpenChange={(open) => !open && setPreviewDocument(null)}
        />
      )}

      {/* Delete Confirmation */}
      <AlertDialog open={showDeleteDialog} onOpenChange={setShowDeleteDialog}>
        <AlertDialogContent className="bg-zinc-900 border-zinc-800">
          <AlertDialogHeader>
            <AlertDialogTitle>{tCommon("confirmDelete")}</AlertDialogTitle>
            <AlertDialogDescription>
              {t("deleteWarning")}
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>{tCommon("cancel")}</AlertDialogCancel>
            <AlertDialogAction
              onClick={handleDelete}
              disabled={deleting}
              className="bg-red-600 hover:bg-red-700"
            >
              {deleting ? (
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              ) : (
                <Trash2 className="mr-2 h-4 w-4" />
              )}
              {tCommon("delete")}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
}

