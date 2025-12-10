"use client";

import { useQuery } from "@tanstack/react-query";
import { format } from "date-fns";
import { 
  Clock, 
  User, 
  CheckCircle, 
  XCircle,
  Edit,
  Play,
  FileText,
  Loader2
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { ScrollArea } from "@/components/ui/scroll-area";
import { cn } from "@/lib/utils";
import { api } from "@/lib/api";

interface ActivityTimelineProps {
  claimId: number;
  className?: string;
}

const actionIcons: Record<string, React.ComponentType<{ className?: string }>> = {
  CLAIM_CREATED: Play,
  OCR_EDITED: Edit,
  OCR_APPROVED: CheckCircle,
  CLEANING_COMPLETED: CheckCircle,
  ANON_EDITED: Edit,
  ANON_APPROVED: CheckCircle,
  ANALYSIS_STARTED: Play,
  ANALYSIS_COMPLETED: CheckCircle,
  REPORT_GENERATED: FileText,
  CLAIM_STATUS_CHANGED: Clock,
  RE_CLEAN: Play,
  ANONYMIZATION_RETRY: Play,
  CLEANING_RETRY: Play,
  STATUS_RESET: Clock,
};

const actionColors: Record<string, string> = {
  CLAIM_CREATED: "text-blue-400",
  OCR_EDITED: "text-yellow-400",
  OCR_APPROVED: "text-emerald-400",
  CLEANING_COMPLETED: "text-emerald-400",
  ANON_EDITED: "text-yellow-400",
  ANON_APPROVED: "text-emerald-400",
  ANALYSIS_STARTED: "text-blue-400",
  ANALYSIS_COMPLETED: "text-emerald-400",
  REPORT_GENERATED: "text-purple-400",
  CLAIM_STATUS_CHANGED: "text-cyan-400",
  RE_CLEAN: "text-orange-400",
  ANONYMIZATION_RETRY: "text-orange-400",
  CLEANING_RETRY: "text-orange-400",
  STATUS_RESET: "text-red-400",
};

export function ActivityTimeline({ claimId, className }: ActivityTimelineProps) {
  const { data: auditTrail, isLoading } = useQuery({
    queryKey: ["audit", "claim", claimId],
    queryFn: async () => {
      const { data, error } = await api.GET("/api/v1/audit/claims/{claim_id}", {
        params: { path: { claim_id: claimId } },
      });
      if (error) throw error;
      return data;
    },
    refetchInterval: 30000, // Refresh every 30 seconds
  });

  if (isLoading) {
    return (
      <Card className={cn("border-zinc-800 bg-zinc-900", className)}>
        <CardHeader>
          <CardTitle className="text-sm font-medium text-zinc-400">
            Activity Timeline
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {[1, 2, 3].map((i) => (
            <div key={i} className="flex gap-3">
              <Skeleton className="h-8 w-8 rounded-full bg-zinc-800" />
              <div className="flex-1 space-y-2">
                <Skeleton className="h-4 w-32 bg-zinc-800" />
                <Skeleton className="h-3 w-48 bg-zinc-800" />
              </div>
            </div>
          ))}
        </CardContent>
      </Card>
    );
  }

  const activities = auditTrail?.events || [];

  return (
    <Card className={cn("border-zinc-800 bg-zinc-900", className)}>
      <CardHeader>
        <CardTitle className="text-sm font-medium text-zinc-400">
          Activity Timeline
        </CardTitle>
      </CardHeader>
      <CardContent>
        <ScrollArea className="h-[400px] pr-4">
          {activities.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-8 text-center">
              <Clock className="mb-2 h-8 w-8 text-zinc-600" />
              <p className="text-sm text-zinc-500">No activity yet</p>
            </div>
          ) : (
            <div className="relative space-y-4">
              {/* Vertical line */}
              <div className="absolute left-4 top-0 bottom-0 w-px bg-zinc-800" />

              {activities.map((activity, index) => {
                const Icon = actionIcons[activity.action] || Clock;
                const color = actionColors[activity.action] || "text-zinc-400";

                return (
                  <div key={index} className="relative flex gap-3">
                    {/* Icon */}
                    <div
                      className={cn(
                        "relative z-10 flex h-8 w-8 items-center justify-center rounded-full border-2 border-zinc-800 bg-zinc-900",
                        color
                      )}
                    >
                      <Icon className="h-4 w-4" />
                    </div>

                    {/* Content */}
                    <div className="flex-1 pb-4">
                      <div className="flex items-start justify-between gap-2">
                        <div className="flex-1">
                          <p className="text-sm font-medium text-white">
                            {activity.action.replace(/_/g, " ")}
                          </p>
                          <p className="mt-1 text-xs text-zinc-500">
                            by {activity.user || "System"}
                          </p>
                          {activity.changes && Object.keys(activity.changes).length > 0 && (
                            <div className="mt-2 rounded-md bg-zinc-800/50 p-2 text-xs text-zinc-400">
                              {Object.entries(activity.changes).map(([key, value]) => (
                                <div key={key}>
                                  <span className="text-zinc-500">{key}:</span>{" "}
                                  <span className="text-white">
                                    {typeof value === "object"
                                      ? JSON.stringify(value)
                                      : String(value)}
                                  </span>
                                </div>
                              ))}
                            </div>
                          )}
                        </div>
                        <time className="text-xs text-zinc-500">
                          {activity.timestamp ? format(new Date(activity.timestamp), "MMM d, HH:mm") : "—"}
                        </time>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </ScrollArea>
      </CardContent>
    </Card>
  );
}

