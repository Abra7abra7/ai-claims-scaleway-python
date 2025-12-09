"use client";

import { useTranslations } from "next-intl";
import { useQuery } from "@tanstack/react-query";
import Link from "next/link";
import {
  FileText,
  Clock,
  CheckCircle,
  AlertCircle,
  TrendingUp,
  Eye,
  ArrowRight,
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { api } from "@/lib/api";

interface StatCardProps {
  title: string;
  value: number | string;
  icon: React.ReactNode;
  description?: string;
  trend?: number;
}

function StatCard({ title, value, icon, description, trend }: StatCardProps) {
  return (
    <Card className="border-zinc-800 bg-zinc-900">
      <CardHeader className="flex flex-row items-center justify-between pb-2">
        <CardTitle className="text-sm font-medium text-zinc-400">
          {title}
        </CardTitle>
        <div className="text-zinc-500">{icon}</div>
      </CardHeader>
      <CardContent>
        <div className="text-3xl font-bold text-white">{value}</div>
        {description && (
          <p className="mt-1 text-xs text-zinc-500">{description}</p>
        )}
        {trend !== undefined && (
          <div className="mt-2 flex items-center gap-1 text-xs">
            <TrendingUp className="h-3 w-3 text-emerald-500" />
            <span className="text-emerald-500">+{trend}%</span>
            <span className="text-zinc-500">from last month</span>
          </div>
        )}
      </CardContent>
    </Card>
  );
}

function StatCardSkeleton() {
  return (
    <Card className="border-zinc-800 bg-zinc-900">
      <CardHeader className="flex flex-row items-center justify-between pb-2">
        <Skeleton className="h-4 w-24 bg-zinc-800" />
        <Skeleton className="h-5 w-5 rounded bg-zinc-800" />
      </CardHeader>
      <CardContent>
        <Skeleton className="h-8 w-16 bg-zinc-800" />
        <Skeleton className="mt-2 h-3 w-32 bg-zinc-800" />
      </CardContent>
    </Card>
  );
}

interface StatusBadgeProps {
  status: string;
  count: number;
}

function StatusBadge({ status, count }: StatusBadgeProps) {
  const colors: Record<string, string> = {
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

  return (
    <div
      className={`flex items-center justify-between rounded-lg border px-4 py-3 ${colors[status] || "bg-zinc-800 text-zinc-400 border-zinc-700"}`}
    >
      <span className="text-sm font-medium">{status.replace(/_/g, " ")}</span>
      <span className="text-lg font-bold">{count}</span>
    </div>
  );
}

export function DashboardContent() {
  const t = useTranslations("dashboard");
  const tClaims = useTranslations("claims");

  const { data: stats, isLoading } = useQuery({
    queryKey: ["dashboard-stats"],
    queryFn: async () => {
      const { data, error } = await api.GET("/api/v1/stats/dashboard");
      if (error) throw error;
      return data;
    },
  });

  // Fetch claims that need attention
  const { data: claimsList } = useQuery({
    queryKey: ["claims", "needs-attention"],
    queryFn: async () => {
      const { data, error } = await api.GET("/api/v1/claims", {
        params: {
          query: {
            limit: 10,
          },
        },
      });
      if (error) throw error;
      return data;
    },
  });

  const needsAttentionClaims = claimsList?.items?.filter(
    (claim) =>
      claim.status === "OCR_REVIEW" ||
      claim.status === "ANONYMIZATION_REVIEW" ||
      claim.status === "FAILED"
  ) || [];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-white">{t("title")}</h1>
        <p className="text-zinc-400">{t("welcome")}</p>
      </div>

      {/* Stats Grid */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {isLoading ? (
          <>
            <StatCardSkeleton />
            <StatCardSkeleton />
            <StatCardSkeleton />
            <StatCardSkeleton />
          </>
        ) : (
          <>
            <StatCard
              title={t("totalClaims")}
              value={stats?.total_claims ?? 0}
              icon={<FileText className="h-5 w-5" />}
            />
            <StatCard
              title={t("pendingReview")}
              value={(stats?.pending_ocr_review ?? 0) + (stats?.pending_anon_review ?? 0)}
              icon={<Clock className="h-5 w-5" />}
              description="OCR + Anonymization"
            />
            <StatCard
              title={t("completed")}
              value={stats?.completed_today ?? 0}
              icon={<CheckCircle className="h-5 w-5" />}
              description="Today"
            />
            <StatCard
              title={t("failed")}
              value={stats?.failed_count ?? 0}
              icon={<AlertCircle className="h-5 w-5" />}
            />
          </>
        )}
      </div>

      {/* Needs Attention */}
      {needsAttentionClaims.length > 0 && (
        <Card className="border-amber-500/20 bg-amber-500/5">
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle className="text-amber-400 flex items-center gap-2">
                <AlertCircle className="h-5 w-5" />
                {t("needsAttention")}
              </CardTitle>
              <Badge variant="outline" className="bg-amber-500/10 text-amber-400 border-amber-500/20">
                {needsAttentionClaims.length}
              </Badge>
            </div>
          </CardHeader>
          <CardContent className="space-y-2">
            {needsAttentionClaims.map((claim) => (
              <Link
                key={claim.id}
                href={`/claims/${claim.id}`}
                className="flex items-center justify-between rounded-lg border border-zinc-800 bg-zinc-900 p-4 transition-colors hover:bg-zinc-800"
              >
                <div className="flex items-center gap-3">
                  <div className="flex h-10 w-10 items-center justify-center rounded-full bg-amber-500/10">
                    <Eye className="h-5 w-5 text-amber-400" />
                  </div>
                  <div>
                    <p className="font-medium text-white">
                      Claim #{claim.id}
                    </p>
                    <p className="text-sm text-zinc-500">
                      {claim.status.replace(/_/g, " ")}
                    </p>
                  </div>
                </div>
                <ArrowRight className="h-5 w-5 text-zinc-500" />
              </Link>
            ))}
          </CardContent>
        </Card>
      )}

      {/* Status Overview */}
      <div className="grid gap-6 lg:grid-cols-2">
        {/* By Status */}
        <Card className="border-zinc-800 bg-zinc-900">
          <CardHeader>
            <CardTitle className="text-white">{t("byStatus")}</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            {isLoading ? (
              <div className="space-y-2">
                {[...Array(5)].map((_, i) => (
                  <Skeleton key={i} className="h-12 w-full bg-zinc-800" />
                ))}
              </div>
            ) : (
              stats?.claims_by_status?.map((item) => (
                <StatusBadge
                  key={item.status}
                  status={item.status}
                  count={item.count}
                />
              ))
            )}
          </CardContent>
        </Card>

        {/* By Country */}
        <Card className="border-zinc-800 bg-zinc-900">
          <CardHeader>
            <CardTitle className="text-white">{t("byCountry")}</CardTitle>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <div className="space-y-2">
                {[...Array(3)].map((_, i) => (
                  <Skeleton key={i} className="h-12 w-full bg-zinc-800" />
                ))}
              </div>
            ) : (
              <div className="space-y-2">
                {stats?.claims_by_country?.map((item) => (
                  <div
                    key={item.country}
                    className="flex items-center justify-between rounded-lg border border-zinc-800 bg-zinc-800/50 px-4 py-3"
                  >
                    <div className="flex items-center gap-3">
                      <span className="text-xl">
                        {item.country === "SK"
                          ? "🇸🇰"
                          : item.country === "IT"
                            ? "🇮🇹"
                            : item.country === "DE"
                              ? "🇩🇪"
                              : "🌍"}
                      </span>
                      <span className="text-sm font-medium text-white">
                        {item.country}
                      </span>
                    </div>
                    <span className="text-lg font-bold text-white">
                      {item.count}
                    </span>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

