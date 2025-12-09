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

  // Get claim from cache (should already be fetched by parent component)
  const claim = queryClient.getQueryData<any>(["claim", claimId]);

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

  return { isPolling: !!intervalRef.current };
}

