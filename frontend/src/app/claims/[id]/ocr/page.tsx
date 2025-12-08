"use client"

import { use, useState } from 'react'
import { useRouter } from 'next/navigation'
import { useTranslations } from 'next-intl'
import {
  ArrowLeft,
  Check,
  Sparkles,
  FileText,
  Loader2,
  Edit,
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Textarea } from '@/components/ui/textarea'
import { Badge } from '@/components/ui/badge'
import { Skeleton } from '@/components/ui/skeleton'
import { ScrollArea } from '@/components/ui/scroll-area'
import {
  useClaim,
  useOcrReview,
  useEditOcr,
  useApproveOcr,
  usePreviewCleaning,
} from '@/hooks/use-claims'

export default function OcrReviewPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params)
  const claimId = parseInt(id)
  const router = useRouter()
  const t = useTranslations('ocr')
  const tCommon = useTranslations('common')

  const [selectedDoc, setSelectedDoc] = useState<number>(0)
  const [editedTexts, setEditedTexts] = useState<Record<number, string>>({})
  const [isEditing, setIsEditing] = useState(false)
  const [showCleaned, setShowCleaned] = useState(false)
  const [cleanedPreview, setCleanedPreview] = useState<Record<number, { text: string; stats: Record<string, number> }>>({})

  const { data: claim, isLoading: isLoadingClaim } = useClaim(claimId)
  const { data: ocrData, isLoading: isLoadingOcr, error } = useOcrReview(claimId)
  const editMutation = useEditOcr()
  const approveMutation = useApproveOcr()
  const previewMutation = usePreviewCleaning()

  const documents = ocrData?.documents || []
  const currentDoc = documents[selectedDoc]

  const handlePreviewCleaning = async () => {
    const result = await previewMutation.mutateAsync(claimId)
    const preview: Record<number, { text: string; stats: Record<string, number> }> = {}
    result.documents.forEach((doc) => {
      preview[doc.id] = { text: doc.cleaned_text, stats: doc.stats }
    })
    setCleanedPreview(preview)
    setShowCleaned(true)
  }

  const handleSaveEdits = async () => {
    if (Object.keys(editedTexts).length === 0) return
    
    // Convert number keys to string keys for API
    const edits: Record<string, string> = {}
    Object.entries(editedTexts).forEach(([id, text]) => {
      edits[id] = text
    })
    
    await editMutation.mutateAsync({ claimId, edits })
    setEditedTexts({})
    setIsEditing(false)
  }

  const handleApprove = async () => {
    // Save any pending edits first
    if (Object.keys(editedTexts).length > 0) {
      await handleSaveEdits()
    }
    
    await approveMutation.mutateAsync(claimId)
    router.push(`/claims/${claimId}`)
  }

  const handleTextChange = (docId: number, text: string) => {
    setEditedTexts(prev => ({ ...prev, [docId]: text }))
  }

  const isLoading = isLoadingClaim || isLoadingOcr

  if (isLoading) {
    return (
      <div className="container py-6 space-y-6">
        <Skeleton className="h-8 w-64" />
        <Skeleton className="h-[600px] w-full" />
      </div>
    )
  }

  if (error) {
    return (
      <div className="container py-6">
        <Card>
          <CardContent className="py-8 text-center">
            <p className="text-destructive">
              {(error as Error).message || 'Failed to load OCR data'}
            </p>
            <Button variant="outline" className="mt-4" onClick={() => router.back()}>
              {tCommon('back')}
            </Button>
          </CardContent>
        </Card>
      </div>
    )
  }

  if (!documents || documents.length === 0) {
    return (
      <div className="container py-6">
        <Card>
          <CardContent className="py-8 text-center">
            <p className="text-muted-foreground">{tCommon('noResults')}</p>
            <Button variant="outline" className="mt-4" onClick={() => router.back()}>
              {tCommon('back')}
            </Button>
          </CardContent>
        </Card>
      </div>
    )
  }

  const currentText = editedTexts[currentDoc?.id] ?? currentDoc?.original_text ?? ''

  return (
    <div className="container py-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Button variant="ghost" size="icon" onClick={() => router.back()}>
            <ArrowLeft className="h-5 w-5" />
          </Button>
          <div>
            <h1 className="text-2xl font-bold tracking-tight">{t('title')}</h1>
            <p className="text-muted-foreground">{t('subtitle')}</p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <Badge variant="outline">
            Document {selectedDoc + 1} of {documents.length}
          </Badge>
        </div>
      </div>

      {/* Document selector (if multiple) */}
      {documents.length > 1 && (
        <Card>
          <CardContent className="pt-6">
            <div className="flex flex-wrap gap-2">
              {documents.map((doc, index) => (
                <Button
                  key={doc.id}
                  variant={selectedDoc === index ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => {
                    setSelectedDoc(index)
                    setShowCleaned(false)
                  }}
                >
                  <FileText className="mr-2 h-4 w-4" />
                  {doc.filename}
                </Button>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Main content */}
      <div className="grid gap-6 lg:grid-cols-2">
        {/* Original OCR Text */}
        <Card className="flex flex-col">
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle>{t('originalText')}</CardTitle>
                <CardDescription>
                  {currentText.length} {t('characters')}
                </CardDescription>
              </div>
              <Button
                variant="outline"
                size="sm"
                onClick={() => setIsEditing(!isEditing)}
              >
                <Edit className="mr-2 h-4 w-4" />
                {isEditing ? 'Cancel Edit' : t('editText')}
              </Button>
            </div>
          </CardHeader>
          <CardContent className="flex-1">
            {isEditing ? (
              <Textarea
                className="h-[500px] font-mono text-sm resize-none"
                placeholder="Edit OCR text here..."
                value={currentText}
                onChange={(e) => handleTextChange(currentDoc.id, e.target.value)}
              />
            ) : (
              <ScrollArea className="h-[500px] w-full rounded-md border p-4">
                <pre className="text-sm whitespace-pre-wrap font-mono">
                  {currentText || '(No OCR text)'}
                </pre>
              </ScrollArea>
            )}
          </CardContent>
        </Card>

        {/* Cleaned Preview */}
        <Card className="flex flex-col">
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle>{t('cleanedText')}</CardTitle>
                {showCleaned && cleanedPreview[currentDoc?.id] && (
                  <CardDescription>
                    {cleanedPreview[currentDoc.id].text.length} {t('characters')}
                    {' '}
                    ({cleanedPreview[currentDoc.id].stats.reduction_percent?.toFixed(1) || 0}% {t('reduction')})
                  </CardDescription>
                )}
              </div>
              <Button
                variant="outline"
                size="sm"
                onClick={handlePreviewCleaning}
                disabled={previewMutation.isPending}
              >
                {previewMutation.isPending ? (
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                ) : (
                  <Sparkles className="mr-2 h-4 w-4" />
                )}
                {t('previewCleaning')}
              </Button>
            </div>
          </CardHeader>
          <CardContent className="flex-1">
            <ScrollArea className="h-[500px] w-full rounded-md border p-4 bg-muted/30">
              <pre className="text-sm whitespace-pre-wrap font-mono">
                {showCleaned && cleanedPreview[currentDoc?.id]
                  ? cleanedPreview[currentDoc.id].text
                  : '(Click "Preview Cleaning" to see cleaned text)'}
              </pre>
            </ScrollArea>
          </CardContent>
        </Card>
      </div>

      {/* Actions */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              {isEditing && Object.keys(editedTexts).length > 0 && (
                <Button
                  variant="secondary"
                  onClick={handleSaveEdits}
                  disabled={editMutation.isPending}
                >
                  {editMutation.isPending ? (
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  ) : (
                    <Check className="mr-2 h-4 w-4" />
                  )}
                  Save Edits
                </Button>
              )}
            </div>
            <div className="flex items-center gap-2">
              <Button variant="outline" onClick={() => router.back()}>
                {tCommon('cancel')}
              </Button>
              <Button
                onClick={handleApprove}
                disabled={approveMutation.isPending}
              >
                {approveMutation.isPending ? (
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                ) : (
                  <Check className="mr-2 h-4 w-4" />
                )}
                {t('approveOcr')}
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
