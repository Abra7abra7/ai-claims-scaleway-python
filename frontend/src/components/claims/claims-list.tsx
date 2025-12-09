"use client";

import { useState } from "react";
import Link from "next/link";
import { useTranslations } from "next-intl";
import { useQuery } from "@tanstack/react-query";
import { format } from "date-fns";
import {
  Plus,
  Search,
  Eye,
  MoreHorizontal,
  FileText,
  AlertCircle,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { api } from "@/lib/api";

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

export function ClaimsList() {
  const t = useTranslations("claims");
  const tCommon = useTranslations("common");
  const [statusFilter, setStatusFilter] = useState<string>("all");
  const [countryFilter, setCountryFilter] = useState<string>("all");
  const [search, setSearch] = useState("");

  const { data, isLoading, error } = useQuery({
    queryKey: ["claims", statusFilter, countryFilter],
    queryFn: async () => {
      const params: Record<string, string | number> = {
        skip: 0,
        limit: 100,
      };
      if (statusFilter !== "all") params.status = statusFilter;
      if (countryFilter !== "all") params.country = countryFilter;

      const { data, error } = await api.GET("/api/v1/claims", {
        params: { query: params as any },
      });
      if (error) throw error;
      return data;
    },
  });

  const claims = data?.items || [];

  if (error) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="text-center">
          <AlertCircle className="mx-auto h-12 w-12 text-red-500" />
          <p className="mt-4 text-zinc-400">Failed to load claims</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">{t("title")}</h1>
          <p className="text-zinc-400">
            {data?.total ?? 0} {t("title").toLowerCase()}
          </p>
        </div>
        <Button asChild className="bg-emerald-600 hover:bg-emerald-700">
          <Link href="/claims/new">
            <Plus className="mr-2 h-4 w-4" />
            {t("newClaim")}
          </Link>
        </Button>
      </div>

      {/* Filters */}
      <Card className="border-zinc-800 bg-zinc-900">
        <CardContent className="flex flex-wrap items-center gap-4 p-4">
          <div className="relative flex-1 min-w-[200px]">
            <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-zinc-500" />
            <Input
              placeholder={tCommon("search")}
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="border-zinc-700 bg-zinc-800 pl-10 text-white placeholder:text-zinc-500"
            />
          </div>
          <Select value={statusFilter} onValueChange={setStatusFilter}>
            <SelectTrigger className="w-[180px] border-zinc-700 bg-zinc-800 text-white">
              <SelectValue placeholder={t("status")} />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Statuses</SelectItem>
              <SelectItem value="PROCESSING">{t("statuses.PROCESSING")}</SelectItem>
              <SelectItem value="OCR_REVIEW">{t("statuses.OCR_REVIEW")}</SelectItem>
              <SelectItem value="ANONYMIZATION_REVIEW">{t("statuses.ANONYMIZATION_REVIEW")}</SelectItem>
              <SelectItem value="READY_FOR_ANALYSIS">{t("statuses.READY_FOR_ANALYSIS")}</SelectItem>
              <SelectItem value="ANALYZED">{t("statuses.ANALYZED")}</SelectItem>
              <SelectItem value="FAILED">{t("statuses.FAILED")}</SelectItem>
            </SelectContent>
          </Select>
          <Select value={countryFilter} onValueChange={setCountryFilter}>
            <SelectTrigger className="w-[140px] border-zinc-700 bg-zinc-800 text-white">
              <SelectValue placeholder={t("country")} />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Countries</SelectItem>
              <SelectItem value="SK">🇸🇰 Slovakia</SelectItem>
              <SelectItem value="IT">🇮🇹 Italy</SelectItem>
              <SelectItem value="DE">🇩🇪 Germany</SelectItem>
            </SelectContent>
          </Select>
        </CardContent>
      </Card>

      {/* Table */}
      <Card className="border-zinc-800 bg-zinc-900">
        <Table>
          <TableHeader>
            <TableRow className="border-zinc-800 hover:bg-zinc-800/50">
              <TableHead className="text-zinc-400">ID</TableHead>
              <TableHead className="text-zinc-400">{t("country")}</TableHead>
              <TableHead className="text-zinc-400">{t("status")}</TableHead>
              <TableHead className="text-zinc-400">{t("documents")}</TableHead>
              <TableHead className="text-zinc-400">{t("createdAt")}</TableHead>
              <TableHead className="text-right text-zinc-400">
                {t("actions")}
              </TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {isLoading ? (
              [...Array(5)].map((_, i) => (
                <TableRow key={i} className="border-zinc-800">
                  <TableCell>
                    <Skeleton className="h-4 w-12 bg-zinc-800" />
                  </TableCell>
                  <TableCell>
                    <Skeleton className="h-6 w-16 bg-zinc-800" />
                  </TableCell>
                  <TableCell>
                    <Skeleton className="h-6 w-24 bg-zinc-800" />
                  </TableCell>
                  <TableCell>
                    <Skeleton className="h-4 w-8 bg-zinc-800" />
                  </TableCell>
                  <TableCell>
                    <Skeleton className="h-4 w-24 bg-zinc-800" />
                  </TableCell>
                  <TableCell>
                    <Skeleton className="ml-auto h-8 w-8 bg-zinc-800" />
                  </TableCell>
                </TableRow>
              ))
            ) : claims.length === 0 ? (
              <TableRow className="border-zinc-800">
                <TableCell colSpan={6} className="py-12 text-center">
                  <FileText className="mx-auto h-12 w-12 text-zinc-600" />
                  <p className="mt-4 text-zinc-400">{tCommon("noData")}</p>
                </TableCell>
              </TableRow>
            ) : (
              claims.map((claim) => (
                <TableRow
                  key={claim.id}
                  className="border-zinc-800 hover:bg-zinc-800/50"
                >
                  <TableCell className="font-medium text-white">
                    #{claim.id}
                  </TableCell>
                  <TableCell>
                    <span className="text-lg">
                      {countryFlags[claim.country] || "🌍"}{" "}
                    </span>
                    <span className="text-zinc-300">{claim.country}</span>
                  </TableCell>
                  <TableCell>
                    <Badge
                      variant="outline"
                      className={statusColors[claim.status] || ""}
                    >
                      {t(`statuses.${claim.status}` as any) || claim.status}
                    </Badge>
                  </TableCell>
                  <TableCell className="text-zinc-300">
                    {claim.document_count ?? 0}
                  </TableCell>
                  <TableCell className="text-zinc-400">
                    {claim.created_at
                      ? format(new Date(claim.created_at), "dd.MM.yyyy HH:mm")
                      : "-"}
                  </TableCell>
                  <TableCell className="text-right">
                    <DropdownMenu>
                      <DropdownMenuTrigger asChild>
                        <Button
                          variant="ghost"
                          size="icon"
                          className="text-zinc-400 hover:text-white"
                        >
                          <MoreHorizontal className="h-4 w-4" />
                        </Button>
                      </DropdownMenuTrigger>
                      <DropdownMenuContent align="end">
                        <DropdownMenuItem asChild>
                          <Link href={`/claims/${claim.id}`}>
                            <Eye className="mr-2 h-4 w-4" />
                            {t("viewDetails")}
                          </Link>
                        </DropdownMenuItem>
                        {claim.status === "OCR_REVIEW" && (
                          <DropdownMenuItem asChild>
                            <Link href={`/claims/${claim.id}/ocr`}>
                              {t("ocrReview")}
                            </Link>
                          </DropdownMenuItem>
                        )}
                        {claim.status === "ANONYMIZATION_REVIEW" && (
                          <DropdownMenuItem asChild>
                            <Link href={`/claims/${claim.id}/anonymization`}>
                              {t("anonymizationReview")}
                            </Link>
                          </DropdownMenuItem>
                        )}
                      </DropdownMenuContent>
                    </DropdownMenu>
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </Card>
    </div>
  );
}

