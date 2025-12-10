"use client";

import { useEffect, useRef, useState } from "react";
import { useQueryClient } from "@tanstack/react-query";

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

interface ClaimData {
  status: string;
  [key: string]: unknown;
}

export function useClaimPolling({ claimId, enabled = true }: UseClaimPollingOptions) {
  const queryClient = useQueryClient();
  const intervalRef = useRef<NodeJS.Timeout | null>(null);
  const [isPolling, setIsPolling] = useState(false);

  // Get claim from cache (should already be fetched by parent component)
  const claim = queryClient.getQueryData<ClaimData>(["claim", claimId]);

  const shouldPoll = claim && PROCESSING_STATUSES.includes(claim.status);

  useEffect(() => {
    if (!enabled || !shouldPoll) {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
      setIsPolling(false);
      return;
    }

    // Start polling
    intervalRef.current = setInterval(() => {
      queryClient.invalidateQueries({ queryKey: ["claim", claimId] });
    }, POLLING_INTERVAL);
    setIsPolling(true);

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
      setIsPolling(false);
    };
  }, [enabled, shouldPoll, claimId, queryClient]);

  return { isPolling };
}

