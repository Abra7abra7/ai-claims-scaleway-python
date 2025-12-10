"use client";

import { useState, useEffect } from "react";
import { FileText, Download, Loader2, Search, FileBarChart } from "lucide-react";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { toast } from "sonner";
import type { ReportSummary, ClaimSummary } from "@/lib/types";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

// Extended type for UI purposes
interface ClaimWithReports extends Pick<ClaimSummary, "id" | "country" | "status"> {
  reports: ReportSummary[];
}

export default function ReportsPage() {
  const [loading, setLoading] = useState(true);
  const [claims, setClaims] = useState<ClaimWithReports[]>([]);
  const [searchTerm, setSearchTerm] = useState("");
  const [downloading, setDownloading] = useState<number | null>(null);

  useEffect(() => {
    fetchReports();
  }, []);

  const fetchReports = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem("auth_token");

      // First get all analyzed claims
      const claimsRes = await fetch(`${API_URL}/api/v1/claims?status=ANALYZED&limit=100`, {
        credentials: "include",
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (!claimsRes.ok) {
        throw new Error("Failed to fetch claims");
      }

      const claimsData = await claimsRes.json();
      
      // Fetch reports for each claim
      const claimsWithReports: ClaimWithReports[] = [];
      
      for (const claim of claimsData.items) {
        try {
          const reportsRes = await fetch(`${API_URL}/api/v1/reports/claims/${claim.id}`, {
            credentials: "include",
            headers: {
              Authorization: `Bearer ${token}`,
            },
          });

          if (reportsRes.ok) {
            const reportsData = await reportsRes.json();
            if (reportsData.reports.length > 0) {
              claimsWithReports.push({
                id: claim.id,
                country: claim.country,
                status: claim.status,
                reports: reportsData.reports,
              });
            }
          }
        } catch {
          // Skip claims with no reports
        }
      }

      setClaims(claimsWithReports);
    } catch (err: any) {
      toast.error(err.message);
    } finally {
      setLoading(false);
    }
  };

  const downloadReport = async (reportId: number) => {
    try {
      setDownloading(reportId);
      // Direct download from backend proxy
      window.open(`${API_URL}/api/v1/reports/${reportId}/download`, "_blank");
      toast.success("Report download started");
    } catch (err: any) {
      toast.error(err.message);
    } finally {
      setDownloading(null);
    }
  };

  const formatDate = (dateStr: string | null | undefined) => {
    if (!dateStr) return "—";
    return new Date(dateStr).toLocaleDateString("sk-SK", {
      day: "2-digit",
      month: "short",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  const filteredClaims = claims.filter(
    (claim) =>
      claim.id.toString().includes(searchTerm) ||
      claim.country.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const totalReports = claims.reduce((sum, c) => sum + c.reports.length, 0);

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold">Reports</h1>
        <p className="text-zinc-400">Download generated analysis reports</p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-3 gap-4">
        <Card className="border-zinc-800 bg-zinc-900">
          <CardContent className="pt-6">
            <div className="flex items-center gap-4">
              <div className="p-3 rounded-lg bg-emerald-500/10">
                <FileBarChart className="h-6 w-6 text-emerald-400" />
              </div>
              <div>
                <p className="text-2xl font-bold">{totalReports}</p>
                <p className="text-sm text-zinc-400">Total Reports</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card className="border-zinc-800 bg-zinc-900">
          <CardContent className="pt-6">
            <div className="flex items-center gap-4">
              <div className="p-3 rounded-lg bg-blue-500/10">
                <FileText className="h-6 w-6 text-blue-400" />
              </div>
              <div>
                <p className="text-2xl font-bold">{claims.length}</p>
                <p className="text-sm text-zinc-400">Claims with Reports</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card className="border-zinc-800 bg-zinc-900">
          <CardContent className="pt-6">
            <div className="flex items-center gap-4">
              <div className="p-3 rounded-lg bg-purple-500/10">
                <Download className="h-6 w-6 text-purple-400" />
              </div>
              <div>
                <p className="text-2xl font-bold">PDF</p>
                <p className="text-sm text-zinc-400">Format</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Search */}
      <Card className="border-zinc-800 bg-zinc-900">
        <CardContent className="pt-6">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-zinc-400" />
            <Input
              placeholder="Search by claim ID or country..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10 bg-zinc-950 border-zinc-700"
            />
          </div>
        </CardContent>
      </Card>

      {/* Reports Table */}
      <Card className="border-zinc-800 bg-zinc-900">
        <CardContent className="p-0">
          {loading ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="h-8 w-8 animate-spin text-emerald-500" />
            </div>
          ) : filteredClaims.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-12 text-zinc-400">
              <FileBarChart className="h-12 w-12 mb-4" />
              <p>No reports found</p>
              <p className="text-sm mt-2">Analyze claims to generate reports</p>
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow className="border-zinc-800">
                  <TableHead>Claim</TableHead>
                  <TableHead>Country</TableHead>
                  <TableHead>Report ID</TableHead>
                  <TableHead>Model</TableHead>
                  <TableHead>Prompt</TableHead>
                  <TableHead>Generated</TableHead>
                  <TableHead className="text-right">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredClaims.flatMap((claim) =>
                  claim.reports.map((report) => (
                    <TableRow key={report.id} className="border-zinc-800">
                      <TableCell>
                        <Link
                          href={`/claims/${claim.id}`}
                          className="text-emerald-400 hover:underline"
                        >
                          #{claim.id}
                        </Link>
                      </TableCell>
                      <TableCell>
                        <Badge variant="outline">{claim.country}</Badge>
                      </TableCell>
                      <TableCell className="font-mono text-sm">
                        {report.id}
                      </TableCell>
                      <TableCell className="text-zinc-400">
                        {report.model_used || "—"}
                      </TableCell>
                      <TableCell className="text-zinc-400">
                        {report.prompt_id || "default"}
                      </TableCell>
                      <TableCell className="text-zinc-400">
                        {report.created_at ? formatDate(report.created_at) : "—"}
                      </TableCell>
                      <TableCell className="text-right">
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => downloadReport(report.id)}
                          disabled={downloading === report.id}
                          className="text-emerald-400 hover:text-emerald-300"
                        >
                          {downloading === report.id ? (
                            <Loader2 className="h-4 w-4 animate-spin" />
                          ) : (
                            <>
                              <Download className="h-4 w-4 mr-1" />
                              Download
                            </>
                          )}
                        </Button>
                      </TableCell>
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

