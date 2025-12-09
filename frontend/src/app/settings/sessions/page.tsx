"use client";

import { useState, useEffect } from "react";
import { Monitor, Smartphone, Globe, Clock, Loader2, LogOut, Shield } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
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
import type { UserSession } from "@/lib/types";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export default function SessionsPage() {
  const [loading, setLoading] = useState(true);
  const [sessions, setSessions] = useState<UserSession[]>([]);
  const [revoking, setRevoking] = useState<number | null>(null);
  const [revokingAll, setRevokingAll] = useState(false);
  const [confirmRevokeAll, setConfirmRevokeAll] = useState(false);

  useEffect(() => {
    fetchSessions();
  }, []);

  const fetchSessions = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem("auth_token");

      const response = await fetch(`${API_URL}/api/v1/auth/sessions`, {
        credentials: "include",
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        throw new Error("Failed to fetch sessions");
      }

      const data = await response.json();
      setSessions(data.sessions);
    } catch (err: any) {
      toast.error(err.message);
    } finally {
      setLoading(false);
    }
  };

  const revokeSession = async (sessionId: number) => {
    try {
      setRevoking(sessionId);
      const token = localStorage.getItem("auth_token");

      const response = await fetch(`${API_URL}/api/v1/auth/sessions/${sessionId}/revoke`, {
        method: "POST",
        credentials: "include",
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        throw new Error("Failed to revoke session");
      }

      toast.success("Session revoked");
      fetchSessions();
    } catch (err: any) {
      toast.error(err.message);
    } finally {
      setRevoking(null);
    }
  };

  const revokeAllSessions = async () => {
    try {
      setRevokingAll(true);
      const token = localStorage.getItem("auth_token");

      const response = await fetch(`${API_URL}/api/v1/auth/sessions/revoke-all`, {
        method: "POST",
        credentials: "include",
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        throw new Error("Failed to revoke sessions");
      }

      toast.success("All other sessions revoked");
      setConfirmRevokeAll(false);
      fetchSessions();
    } catch (err: any) {
      toast.error(err.message);
    } finally {
      setRevokingAll(false);
    }
  };

  const parseUserAgent = (ua: string | null) => {
    if (!ua) return { device: "Unknown", browser: "Unknown" };

    const isMobile = /mobile|android|iphone|ipad/i.test(ua);
    const device = isMobile ? "Mobile" : "Desktop";

    let browser = "Unknown";
    if (ua.includes("Chrome")) browser = "Chrome";
    else if (ua.includes("Firefox")) browser = "Firefox";
    else if (ua.includes("Safari")) browser = "Safari";
    else if (ua.includes("Edge")) browser = "Edge";

    let os = "";
    if (ua.includes("Windows")) os = "Windows";
    else if (ua.includes("Mac")) os = "macOS";
    else if (ua.includes("Linux")) os = "Linux";
    else if (ua.includes("Android")) os = "Android";
    else if (ua.includes("iPhone") || ua.includes("iPad")) os = "iOS";

    return { device, browser, os };
  };

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr);
    const now = new Date();
    const diff = now.getTime() - date.getTime();

    // Less than 1 minute
    if (diff < 60000) return "Just now";
    // Less than 1 hour
    if (diff < 3600000) return `${Math.floor(diff / 60000)} minutes ago`;
    // Less than 24 hours
    if (diff < 86400000) return `${Math.floor(diff / 3600000)} hours ago`;

    return date.toLocaleDateString("sk-SK", {
      day: "2-digit",
      month: "short",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  const otherSessions = sessions.filter((s) => !s.is_current);

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Active Sessions</h1>
          <p className="text-zinc-400">Manage your active login sessions</p>
        </div>
        {otherSessions.length > 0 && (
          <Button
            variant="outline"
            className="text-red-400 border-red-400 hover:bg-red-950/50"
            onClick={() => setConfirmRevokeAll(true)}
          >
            <LogOut className="mr-2 h-4 w-4" />
            Revoke All Others
          </Button>
        )}
      </div>

      {/* Security Notice */}
      <Card className="border-amber-800 bg-amber-950/20">
        <CardContent className="flex items-start gap-4 pt-6">
          <Shield className="h-6 w-6 text-amber-400 flex-shrink-0" />
          <div>
            <p className="font-medium text-amber-400">Security Notice</p>
            <p className="text-sm text-zinc-400 mt-1">
              If you notice any unfamiliar sessions, revoke them immediately and change your
              password. Contact support if you suspect unauthorized access.
            </p>
          </div>
        </CardContent>
      </Card>

      {/* Sessions List */}
      {loading ? (
        <div className="flex items-center justify-center py-12">
          <Loader2 className="h-8 w-8 animate-spin text-emerald-500" />
        </div>
      ) : (
        <div className="space-y-4">
          {sessions.map((session) => {
            const { device, browser, os } = parseUserAgent(session.user_agent);
            const Icon = device === "Mobile" ? Smartphone : Monitor;

            return (
              <Card
                key={session.id}
                className={`border-zinc-800 bg-zinc-900 ${
                  session.is_current ? "ring-2 ring-emerald-500/50" : ""
                }`}
              >
                <CardContent className="flex items-center justify-between py-6">
                  <div className="flex items-center gap-4">
                    <div
                      className={`p-3 rounded-lg ${
                        session.is_current ? "bg-emerald-500/10" : "bg-zinc-800"
                      }`}
                    >
                      <Icon
                        className={`h-6 w-6 ${
                          session.is_current ? "text-emerald-400" : "text-zinc-400"
                        }`}
                      />
                    </div>
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="font-medium">
                          {os} — {browser}
                        </span>
                        {session.is_current && (
                          <Badge className="bg-emerald-600">Current</Badge>
                        )}
                      </div>
                      <div className="flex items-center gap-4 mt-1 text-sm text-zinc-400">
                        <span className="flex items-center gap-1">
                          <Globe className="h-3 w-3" />
                          {session.ip_address || "Unknown IP"}
                        </span>
                        <span className="flex items-center gap-1">
                          <Clock className="h-3 w-3" />
                          Last active: {formatDate(session.last_activity_at)}
                        </span>
                      </div>
                      <p className="text-xs text-zinc-500 mt-1">
                        Created: {formatDate(session.created_at)} • Expires:{" "}
                        {formatDate(session.expires_at)}
                      </p>
                    </div>
                  </div>

                  {!session.is_current && (
                    <Button
                      variant="ghost"
                      size="sm"
                      className="text-red-400 hover:text-red-300 hover:bg-red-950/50"
                      onClick={() => revokeSession(session.id)}
                      disabled={revoking === session.id}
                    >
                      {revoking === session.id ? (
                        <Loader2 className="h-4 w-4 animate-spin" />
                      ) : (
                        <>
                          <LogOut className="mr-2 h-4 w-4" />
                          Revoke
                        </>
                      )}
                    </Button>
                  )}
                </CardContent>
              </Card>
            );
          })}
        </div>
      )}

      {/* Revoke All Confirmation */}
      <AlertDialog open={confirmRevokeAll} onOpenChange={setConfirmRevokeAll}>
        <AlertDialogContent className="bg-zinc-900 border-zinc-800">
          <AlertDialogHeader>
            <AlertDialogTitle>Revoke All Other Sessions</AlertDialogTitle>
            <AlertDialogDescription>
              This will log you out from all other devices. You will remain logged in on this
              device only.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction
              onClick={revokeAllSessions}
              disabled={revokingAll}
              className="bg-red-600 hover:bg-red-700"
            >
              {revokingAll ? (
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              ) : (
                <LogOut className="mr-2 h-4 w-4" />
              )}
              Revoke All
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
}

