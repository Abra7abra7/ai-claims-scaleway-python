"use client";

import { useState, useEffect } from "react";
import { RefreshCw, Filter, Loader2, FileText, Clock, User, Activity } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Input } from "@/components/ui/input";
import { toast } from "sonner";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface AuditLog {
  id: number;
  user: string;
  action: string;
  entity_type: string;
  entity_id: number | null;
  changes: Record<string, any> | null;
  timestamp: string;
}

interface AuditResponse {
  items: AuditLog[];
  total: number;
  skip: number;
  limit: number;
}

const ACTION_COLORS: Record<string, string> = {
  LOGIN_SUCCESS: "text-emerald-400 border-emerald-400",
  LOGIN_FAILED: "text-red-400 border-red-400",
  LOGOUT: "text-zinc-400 border-zinc-400",
  REGISTER_SUCCESS: "text-blue-400 border-blue-400",
  CLAIM_CREATED: "text-emerald-400 border-emerald-400",
  CLAIM_DELETED: "text-red-400 border-red-400",
  OCR_EDITED: "text-amber-400 border-amber-400",
  OCR_APPROVED: "text-emerald-400 border-emerald-400",
  ANON_EDITED: "text-amber-400 border-amber-400",
  ANON_APPROVED: "text-emerald-400 border-emerald-400",
  ANALYSIS_STARTED: "text-blue-400 border-blue-400",
  ANALYSIS_COMPLETED: "text-emerald-400 border-emerald-400",
  PASSWORD_CHANGED: "text-amber-400 border-amber-400",
  SESSION_REVOKED: "text-red-400 border-red-400",
};

export default function AuditPage() {
  const [loading, setLoading] = useState(true);
  const [logs, setLogs] = useState<AuditLog[]>([]);
  const [total, setTotal] = useState(0);
  const [actions, setActions] = useState<string[]>([]);

  // Filters
  const [filterAction, setFilterAction] = useState<string>("all");
  const [filterUser, setFilterUser] = useState<string>("");
  const [filterEntity, setFilterEntity] = useState<string>("all");
  const [page, setPage] = useState(0);
  const limit = 50;

  useEffect(() => {
    fetchActions();
  }, []);

  useEffect(() => {
    fetchLogs();
  }, [filterAction, filterUser, filterEntity, page]);

  const fetchActions = async () => {
    try {
      const response = await fetch(`${API_URL}/api/v1/audit/actions`, {
        credentials: "include",
      });

      if (response.ok) {
        const data = await response.json();
        setActions(data.actions);
      }
    } catch (err) {
      console.error("Failed to fetch actions", err);
    }
  };

  const fetchLogs = async () => {
    try {
      setLoading(true);

      const params = new URLSearchParams();
      params.append("limit", limit.toString());
      params.append("offset", (page * limit).toString());
      if (filterAction !== "all") params.append("action", filterAction);
      if (filterUser) params.append("user", filterUser);
      if (filterEntity !== "all") params.append("entity_type", filterEntity);

      const response = await fetch(`${API_URL}/api/v1/audit/logs?${params}`, {
        credentials: "include",
      });

      if (!response.ok) {
        throw new Error("Failed to fetch audit logs");
      }

      const data: AuditResponse = await response.json();
      setLogs(data.items);
      setTotal(data.total);
    } catch (err: any) {
      toast.error(err.message);
    } finally {
      setLoading(false);
    }
  };

  const formatTimestamp = (ts: string) => {
    const date = new Date(ts);
    return date.toLocaleString("sk-SK", {
      day: "2-digit",
      month: "2-digit",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit",
    });
  };

  const formatChanges = (changes: Record<string, any> | null) => {
    if (!changes) return "—";
    
    const entries = Object.entries(changes);
    if (entries.length === 0) return "—";
    
    return entries.map(([key, value]) => `${key}: ${JSON.stringify(value)}`).join(", ");
  };

  const entityTypes = ["Claim", "ClaimDocument", "User", "UserSession", "RAGDocument"];

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Audit Log</h1>
          <p className="text-zinc-400">Complete activity history for compliance</p>
        </div>
        <Button variant="outline" onClick={fetchLogs} disabled={loading}>
          {loading ? (
            <Loader2 className="mr-2 h-4 w-4 animate-spin" />
          ) : (
            <RefreshCw className="mr-2 h-4 w-4" />
          )}
          Refresh
        </Button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-4 gap-4">
        <Card className="border-zinc-800 bg-zinc-900">
          <CardContent className="pt-6">
            <div className="flex items-center gap-4">
              <div className="p-3 rounded-lg bg-emerald-500/10">
                <Activity className="h-6 w-6 text-emerald-400" />
              </div>
              <div>
                <p className="text-2xl font-bold">{total}</p>
                <p className="text-sm text-zinc-400">Total Events</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card className="border-zinc-800 bg-zinc-900">
          <CardContent className="pt-6">
            <div className="flex items-center gap-4">
              <div className="p-3 rounded-lg bg-blue-500/10">
                <User className="h-6 w-6 text-blue-400" />
              </div>
              <div>
                <p className="text-2xl font-bold">
                  {new Set(logs.map((l) => l.user)).size}
                </p>
                <p className="text-sm text-zinc-400">Active Users</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card className="border-zinc-800 bg-zinc-900">
          <CardContent className="pt-6">
            <div className="flex items-center gap-4">
              <div className="p-3 rounded-lg bg-amber-500/10">
                <FileText className="h-6 w-6 text-amber-400" />
              </div>
              <div>
                <p className="text-2xl font-bold">
                  {logs.filter((l) => l.entity_type === "Claim").length}
                </p>
                <p className="text-sm text-zinc-400">Claim Events</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card className="border-zinc-800 bg-zinc-900">
          <CardContent className="pt-6">
            <div className="flex items-center gap-4">
              <div className="p-3 rounded-lg bg-purple-500/10">
                <Clock className="h-6 w-6 text-purple-400" />
              </div>
              <div>
                <p className="text-2xl font-bold">
                  {logs.filter((l) => l.action.includes("LOGIN")).length}
                </p>
                <p className="text-sm text-zinc-400">Login Events</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Filters */}
      <Card className="border-zinc-800 bg-zinc-900">
        <CardHeader className="pb-3">
          <CardTitle className="flex items-center gap-2 text-base">
            <Filter className="h-4 w-4" />
            Filters
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center gap-4">
            <Select value={filterAction} onValueChange={setFilterAction}>
              <SelectTrigger className="w-[200px] bg-zinc-950 border-zinc-700">
                <SelectValue placeholder="All Actions" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Actions</SelectItem>
                {actions.map((action) => (
                  <SelectItem key={action} value={action}>
                    {action}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>

            <Select value={filterEntity} onValueChange={setFilterEntity}>
              <SelectTrigger className="w-[200px] bg-zinc-950 border-zinc-700">
                <SelectValue placeholder="All Entities" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Entities</SelectItem>
                {entityTypes.map((type) => (
                  <SelectItem key={type} value={type}>
                    {type}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>

            <Input
              placeholder="Filter by user..."
              value={filterUser}
              onChange={(e) => setFilterUser(e.target.value)}
              className="w-[200px] bg-zinc-950 border-zinc-700"
            />
          </div>
        </CardContent>
      </Card>

      {/* Logs Table */}
      <Card className="border-zinc-800 bg-zinc-900">
        <CardContent className="p-0">
          {loading ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="h-8 w-8 animate-spin text-emerald-500" />
            </div>
          ) : logs.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-12 text-zinc-400">
              <Activity className="h-12 w-12 mb-4" />
              <p>No audit logs found</p>
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow className="border-zinc-800">
                  <TableHead className="w-[180px]">Timestamp</TableHead>
                  <TableHead>User</TableHead>
                  <TableHead>Action</TableHead>
                  <TableHead>Entity</TableHead>
                  <TableHead>ID</TableHead>
                  <TableHead>Changes</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {logs.map((log) => (
                  <TableRow key={log.id} className="border-zinc-800">
                    <TableCell className="font-mono text-xs text-zinc-400">
                      {formatTimestamp(log.timestamp)}
                    </TableCell>
                    <TableCell>
                      <Badge variant="outline">{log.user}</Badge>
                    </TableCell>
                    <TableCell>
                      <Badge
                        variant="outline"
                        className={ACTION_COLORS[log.action] || "text-zinc-400 border-zinc-400"}
                      >
                        {log.action}
                      </Badge>
                    </TableCell>
                    <TableCell className="text-zinc-400">{log.entity_type}</TableCell>
                    <TableCell className="text-zinc-400">{log.entity_id || "—"}</TableCell>
                    <TableCell className="max-w-[300px] truncate text-zinc-500 text-xs">
                      {formatChanges(log.changes)}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>

      {/* Pagination */}
      {total > limit && (
        <div className="flex items-center justify-between">
          <p className="text-sm text-zinc-400">
            Showing {page * limit + 1} - {Math.min((page + 1) * limit, total)} of {total}
          </p>
          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="sm"
              disabled={page === 0}
              onClick={() => setPage((p) => p - 1)}
            >
              Previous
            </Button>
            <Button
              variant="outline"
              size="sm"
              disabled={(page + 1) * limit >= total}
              onClick={() => setPage((p) => p + 1)}
            >
              Next
            </Button>
          </div>
        </div>
      )}
    </div>
  );
}

