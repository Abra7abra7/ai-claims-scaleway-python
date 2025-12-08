"use client"

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { ragApi } from '@/lib/api-client'
import { toast } from 'sonner'

export function useRAGDocuments(params?: { country?: string; category?: string }) {
  return useQuery({
    queryKey: ['rag-documents', params],
    queryFn: () => ragApi.list(params),
  })
}

export function useUploadRAGDocument() {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: ({ file, country, category }: { file: File; country: string; category: string }) =>
      ragApi.upload(file, country, category),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['rag-documents'] })
      toast.success('Document uploaded successfully')
    },
    onError: (error) => {
      toast.error(`Failed to upload document: ${error.message}`)
    },
  })
}

export function useDeleteRAGDocument() {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: (id: number) => ragApi.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['rag-documents'] })
      toast.success('Document deleted successfully')
    },
    onError: (error) => {
      toast.error(`Failed to delete document: ${error.message}`)
    },
  })
}
