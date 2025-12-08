"use client"

import { useQuery } from '@tanstack/react-query'
import { statsApi } from '@/lib/api-client'

export function useDashboardStats() {
  return useQuery({
    queryKey: ['stats', 'dashboard'],
    queryFn: () => statsApi.dashboard(),
    refetchInterval: 30000, // Refetch every 30 seconds
  })
}

export function useClaimStats(days?: number) {
  return useQuery({
    queryKey: ['stats', 'claims', days],
    queryFn: () => statsApi.claims(days),
  })
}

