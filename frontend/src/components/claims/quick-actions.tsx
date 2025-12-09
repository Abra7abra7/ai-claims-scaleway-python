"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useTranslations } from "next-intl";
import { useQueryClient } from "@tanstack/react-query";
import {
  Eye,
  Brain,
  RotateCcw,
  Sparkles,
  Lock,
  FileText,
  AlertCircle,
  Loader2,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { toast } from "sonner";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface QuickActionsProps {
  claimId: number;
  currentStatus: string;
  className?: string;
}

export function QuickActions({ claimId, currentStatus, className }: QuickActionsProps) {
  const t = useTranslations("claims");
  const router = useRouter();
  const queryClient = useQueryClient();
  const [loading, setLoading] = useState<string | null>(null);

  const handleReClean = async () => {
    try {
      setLoading("re-clean");
      const response = await fetch(
        `${API_URL}/api/v1/anonymization/${claimId}/re-clean`,
        {
          method: "POST",
          credentials: "include",
        }
      );

      if (!response.ok) {
        throw new Error("Failed to re-clean");
      }

      toast.success("Re-cleaning started");
      queryClient.invalidateQueries({ queryKey: ["claim", claimId] });
    } catch (error: any) {
      toast.error(error.message || "Failed to re-clean");
    } finally {
      setLoading(null);
    }
  };

  const handleRetryAnonymization = async () => {
    try {
      setLoading("retry-anon");
      const response = await fetch(
        `${API_URL}/api/v1/anonymization/${claimId}/retry`,
        {
          method: "POST",
          credentials: "include",
        }
      );

      if (!response.ok) {
        throw new Error("Failed to retry anonymization");
      }

      toast.success("Anonymization retry started");
      queryClient.invalidateQueries({ queryKey: ["claim", claimId] });
    } catch (error: any) {
      toast.error(error.message || "Failed to retry anonymization");
    } finally {
      setLoading(null);
    }
  };

  const handleResetStatus = async () => {
    try {
      setLoading("reset");
      const response = await fetch(
        `${API_URL}/api/v1/anonymization/${claimId}/reset-status`,
        {
          method: "POST",
          credentials: "include",
        }
      );

      if (!response.ok) {
        throw new Error("Failed to reset status");
      }

      toast.success("Status reset");
      queryClient.invalidateQueries({ queryKey: ["claim", claimId] });
    } catch (error: any) {
      toast.error(error.message || "Failed to reset status");
    } finally {
      setLoading(null);
    }
  };

  // Determine available actions based on status
  const actions = [];

  if (currentStatus === "OCR_REVIEW") {
    actions.push({
      id: "ocr-review",
      label: "Review OCR",
      icon: Eye,
      variant: "default" as const,
      onClick: () => router.push(`/claims/${claimId}/ocr`),
      color: "bg-yellow-600 hover:bg-yellow-700",
    });
  }

  if (currentStatus === "ANONYMIZATION_REVIEW") {
    actions.push({
      id: "anon-review",
      label: "Review Anonymization",
      icon: Eye,
      variant: "default" as const,
      onClick: () => router.push(`/claims/${claimId}/anon`),
      color: "bg-amber-600 hover:bg-amber-700",
    });
  }

  if (currentStatus === "READY_FOR_ANALYSIS" || currentStatus === "ANALYZED") {
    actions.push({
      id: "analysis",
      label: currentStatus === "ANALYZED" ? "View Analysis" : "Start Analysis",
      icon: Brain,
      variant: "default" as const,
      onClick: () => router.push(`/claims/${claimId}/analysis`),
      color: "bg-emerald-600 hover:bg-emerald-700",
    });
  }

  if (currentStatus === "FAILED") {
    actions.push(
      {
        id: "re-clean",
        label: "Re-clean Text",
        icon: Sparkles,
        variant: "outline" as const,
        onClick: handleReClean,
        loading: loading === "re-clean",
      },
      {
        id: "retry-anon",
        label: "Retry Anonymization",
        icon: Lock,
        variant: "outline" as const,
        onClick: handleRetryAnonymization,
        loading: loading === "retry-anon",
      }
    );
  }

  // Admin actions (always available)
  actions.push({
    id: "reset",
    label: "Reset Status",
    icon: RotateCcw,
    variant: "outline" as const,
    onClick: handleResetStatus,
    loading: loading === "reset",
    destructive: true,
  });

  if (actions.length === 0) {
    return null;
  }

  return (
    <Card className={className}>
      <CardHeader>
        <CardTitle className="text-sm font-medium text-zinc-400">
          Quick Actions
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-2">
        {actions.map((action) => {
          const Icon = action.icon;
          return (
            <Button
              key={action.id}
              variant={action.variant}
              className={`w-full justify-start ${action.color || ""} ${
                action.destructive ? "text-red-400 border-red-400 hover:bg-red-950/50" : ""
              }`}
              onClick={action.onClick}
              disabled={action.loading}
            >
              {action.loading ? (
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              ) : (
                <Icon className="mr-2 h-4 w-4" />
              )}
              {action.label}
            </Button>
          );
        })}
      </CardContent>
    </Card>
  );
}

