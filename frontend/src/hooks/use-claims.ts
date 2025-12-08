"use client"

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { claimsApi, ocrApi, anonApi, analysisApi, promptsApi, type ClaimStatus } from '@/lib/api-client'
import { toast } from 'sonner'

export function useClaims(params?: { skip?: number; limit?: number; status?: string }) {
  return useQuery({
    queryKey: ['claims', params],
    queryFn: () => claimsApi.list(params),
  })
}

export function useClaim(id: number) {
  return useQuery({
    queryKey: ['claim', id],
    queryFn: () => claimsApi.get(id),
    enabled: !!id,
  })
}

export function useCreateClaim() {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: ({ country, files }: { country: string; files: File[] }) =>
      claimsApi.create(country, files),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['claims'] })
      queryClient.invalidateQueries({ queryKey: ['stats'] })
      toast.success('Claim created successfully')
    },
    onError: (error) => {
      toast.error(`Failed to create claim: ${error.message}`)
    },
  })
}

export function useDeleteClaim() {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: (id: number) => claimsApi.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['claims'] })
      queryClient.invalidateQueries({ queryKey: ['stats'] })
      toast.success('Claim deleted successfully')
    },
    onError: (error) => {
      toast.error(`Failed to delete claim: ${error.message}`)
    },
  })
}

export function useUpdateClaimStatus() {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: ({ id, status }: { id: number; status: ClaimStatus }) =>
      claimsApi.updateStatus(id, status),
    onSuccess: (_, { id }) => {
      queryClient.invalidateQueries({ queryKey: ['claim', id] })
      queryClient.invalidateQueries({ queryKey: ['claims'] })
      toast.success('Status updated successfully')
    },
    onError: (error) => {
      toast.error(`Failed to update status: ${error.message}`)
    },
  })
}

// OCR Hooks
export function useOcrReview(claimId: number) {
  return useQuery({
    queryKey: ['ocr-review', claimId],
    queryFn: () => ocrApi.getReview(claimId),
    enabled: !!claimId,
  })
}

export function useEditOcr() {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: ({ claimId, edits }: { claimId: number; edits: Record<string, string> }) =>
      ocrApi.edit(claimId, edits),
    onSuccess: (_, { claimId }) => {
      queryClient.invalidateQueries({ queryKey: ['ocr-review', claimId] })
      toast.success('OCR text updated')
    },
    onError: (error) => {
      toast.error(`Failed to edit OCR: ${error.message}`)
    },
  })
}

export function useApproveOcr() {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: (claimId: number) => ocrApi.approve(claimId),
    onSuccess: (_, claimId) => {
      queryClient.invalidateQueries({ queryKey: ['ocr-review', claimId] })
      queryClient.invalidateQueries({ queryKey: ['claim', claimId] })
      queryClient.invalidateQueries({ queryKey: ['claims'] })
      toast.success('OCR approved successfully')
    },
    onError: (error) => {
      toast.error(`Failed to approve OCR: ${error.message}`)
    },
  })
}

export function usePreviewCleaning() {
  return useMutation({
    mutationFn: (claimId: number) => ocrApi.previewCleaning(claimId),
    onError: (error) => {
      toast.error(`Failed to preview cleaning: ${error.message}`)
    },
  })
}

export function useRerunOcr() {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: (claimId: number) => ocrApi.rerun(claimId),
    onSuccess: (_, claimId) => {
      queryClient.invalidateQueries({ queryKey: ['ocr-review', claimId] })
      queryClient.invalidateQueries({ queryKey: ['claim', claimId] })
      toast.success('OCR re-run started')
    },
    onError: (error) => {
      toast.error(`Failed to rerun OCR: ${error.message}`)
    },
  })
}

// Anonymization Hooks
export function useAnonReview(claimId: number) {
  return useQuery({
    queryKey: ['anon-review', claimId],
    queryFn: () => anonApi.getReview(claimId),
    enabled: !!claimId,
  })
}

export function useEditAnon() {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: ({ claimId, edits }: { claimId: number; edits: Record<string, string> }) =>
      anonApi.edit(claimId, edits),
    onSuccess: (_, { claimId }) => {
      queryClient.invalidateQueries({ queryKey: ['anon-review', claimId] })
      toast.success('Anonymized text updated')
    },
    onError: (error) => {
      toast.error(`Failed to edit anonymization: ${error.message}`)
    },
  })
}

export function useApproveAnon() {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: (claimId: number) => anonApi.approve(claimId),
    onSuccess: (_, claimId) => {
      queryClient.invalidateQueries({ queryKey: ['anon-review', claimId] })
      queryClient.invalidateQueries({ queryKey: ['claim', claimId] })
      queryClient.invalidateQueries({ queryKey: ['claims'] })
      toast.success('Anonymization approved successfully')
    },
    onError: (error) => {
      toast.error(`Failed to approve anonymization: ${error.message}`)
    },
  })
}

export function useReClean() {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: (claimId: number) => anonApi.reClean(claimId),
    onSuccess: (_, claimId) => {
      queryClient.invalidateQueries({ queryKey: ['anon-review', claimId] })
      queryClient.invalidateQueries({ queryKey: ['claim', claimId] })
      toast.success('Re-cleaning started')
    },
    onError: (error) => {
      toast.error(`Failed to re-clean: ${error.message}`)
    },
  })
}

export function useRetryAnon() {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: (claimId: number) => anonApi.retry(claimId),
    onSuccess: (_, claimId) => {
      queryClient.invalidateQueries({ queryKey: ['anon-review', claimId] })
      queryClient.invalidateQueries({ queryKey: ['claim', claimId] })
      toast.success('Retry started')
    },
    onError: (error) => {
      toast.error(`Failed to retry: ${error.message}`)
    },
  })
}

// Prompts Hooks
export function usePrompts() {
  return useQuery({
    queryKey: ['prompts'],
    queryFn: () => promptsApi.list(),
  })
}

export function usePromptsConfig() {
  return useQuery({
    queryKey: ['prompts-config'],
    queryFn: () => promptsApi.getConfig(),
  })
}

export function usePrompt(promptId: string) {
  return useQuery({
    queryKey: ['prompt', promptId],
    queryFn: () => promptsApi.get(promptId),
    enabled: !!promptId,
  })
}

// Analysis Hooks
export function useStartAnalysis() {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: ({ claimId, promptId }: { claimId: number; promptId: string }) =>
      analysisApi.start(claimId, promptId),
    onSuccess: (_, { claimId }) => {
      queryClient.invalidateQueries({ queryKey: ['claim', claimId] })
      queryClient.invalidateQueries({ queryKey: ['claims'] })
      toast.success('Analysis started')
    },
    onError: (error) => {
      toast.error(`Failed to start analysis: ${error.message}`)
    },
  })
}

export function useAnalysisResult(claimId: number) {
  return useQuery({
    queryKey: ['analysis-result', claimId],
    queryFn: () => analysisApi.getResult(claimId),
    enabled: !!claimId,
  })
}
