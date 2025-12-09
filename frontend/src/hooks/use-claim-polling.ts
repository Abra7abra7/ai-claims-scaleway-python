"use client";

import { useEffect, useRef } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api";

const POLLING_INTERVAL = 10000; // 10 seconds

const PROCESSING_STATUSES = [
  "PROCESSING",
  "CLEANING",
  "ANONYMIZING",
  "ANALYZING",
];

interface UseClaimPollingOptions {
  claimId: number;
  enabled?: boolean;
}

export function useClaimPolling({ claimId, enabled = true }: UseClaimPollingOptions) {
  const queryClient = useQueryClient();
  const intervalRef = useRef<NodeJS.Timeout | null>(null);

  const { data: claim } = useQuery({
    queryKey: ["claim", claimId],
    queryFn: async () => {
      const { data, error } = await api.GET("/api/v1/claims/{claim_id}", {
        params: { path: { claim_id: claimId } },
      });
      if (error) throw error;
      return data;
    },
    enabled,
  });

  const shouldPoll = claim && PROCESSING_STATUSES.includes(claim.status);

  useEffect(() => {
    if (!enabled || !shouldPoll) {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
      return;
    }

    // Start polling
    intervalRef.current = setInterval(() => {
      queryClient.invalidateQueries({ queryKey: ["claim", claimId] });
    }, POLLING_INTERVAL);

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
    };
  }, [enabled, shouldPoll, claimId, queryClient]);

  return { claim, isPolling: !!intervalRef.current };
}

