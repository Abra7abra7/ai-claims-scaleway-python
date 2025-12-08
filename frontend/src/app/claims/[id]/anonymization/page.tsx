"use client"

import { use, useState } from 'react'
import { useRouter } from 'next/navigation'
import { useTranslations } from 'next-intl'
import {
  ArrowLeft,
  Check,
  RefreshCw,
  Shield,
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
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import {
  useClaim,
  useAnonReview,
  useEditAnon,
  useApproveAnon,
  useReClean,
} from '@/hooks/use-claims'

export default function AnonymizationReviewPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params)
  const claimId = parseInt(id)
  const router = useRouter()
  const t = useTranslations('anonymization')
  const tCommon = useTranslations('common')

  const [selectedDoc, setSelectedDoc] = useState<number>(0)
  const [editedTexts, setEditedTexts] = useState<Record<number, string>>({})
  const [isEditing, setIsEditing] = useState(false)
  const [viewMode, setViewMode] = useState<'side-by-side' | 'edit'>('side-by-side')

  const { data: claim, isLoading: isLoadingClaim } = useClaim(claimId)
  const { data: anonData, isLoading: isLoadingAnon, error } = useAnonReview(claimId)
  const editMutation = useEditAnon()
  const approveMutation = useApproveAnon()
  const reCleanMutation = useReClean()

  const documents = anonData?.documents || []
  const currentDoc = documents[selectedDoc]

  const handleSaveEdits = async () => {
    if (Object.keys(editedTexts).length === 0) return
    
    const edits: Record<string, string> = {}
    Object.entries(editedTexts).forEach(([id, text]) => {
      edits[id] = text
    })
    
    await editMutation.mutateAsync({ claimId, edits })
    setEditedTexts({})
    setIsEditing(false)
  }

  const handleApprove = async () => {
    if (Object.keys(editedTexts).length > 0) {
      await handleSaveEdits()
    }
    
    await approveMutation.mutateAsync(claimId)
    router.push(`/claims/${claimId}`)
  }

  const handleReClean = async () => {
    await reCleanMutation.mutateAsync(claimId)
    router.push(`/claims/${claimId}`)
  }

  const handleTextChange = (docId: number, text: string) => {
    setEditedTexts(prev => ({ ...prev, [docId]: text }))
  }

  const isLoading = isLoadingClaim || isLoadingAnon

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
              {(error as Error).message || 'Failed to load anonymization data'}
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

  const currentAnonymizedText = editedTexts[currentDoc?.id] ?? currentDoc?.anonymized_text ?? ''

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
                    setViewMode('side-by-side')
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

      {/* View mode tabs */}
      <Tabs value={viewMode} onValueChange={(v) => setViewMode(v as 'side-by-side' | 'edit')}>
        <TabsList>
          <TabsTrigger value="side-by-side">{t('comparison')}</TabsTrigger>
          <TabsTrigger value="edit">{t('editAnon')}</TabsTrigger>
        </TabsList>

        <TabsContent value="side-by-side" className="mt-4">
          <div className="grid gap-6 lg:grid-cols-2">
            {/* Cleaned Text */}
            <Card className="flex flex-col">
              <CardHeader>
                <CardTitle>{t('cleanedText')}</CardTitle>
                <CardDescription>
                  {currentDoc?.cleaned_text?.length || 0} characters
                </CardDescription>
              </CardHeader>
              <CardContent className="flex-1">
                <ScrollArea className="h-[500px] w-full rounded-md border p-4">
                  <pre className="text-sm whitespace-pre-wrap font-mono">
                    {currentDoc?.cleaned_text || '(No cleaned text)'}
                  </pre>
                </ScrollArea>
              </CardContent>
            </Card>

            {/* Anonymized Text */}
            <Card className="flex flex-col">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Shield className="h-5 w-5" />
                  {t('anonymizedText')}
                </CardTitle>
                <CardDescription>
                  {currentAnonymizedText.length} characters
                </CardDescription>
              </CardHeader>
              <CardContent className="flex-1">
                <ScrollArea className="h-[500px] w-full rounded-md border p-4 bg-muted/30">
                  <pre className="text-sm whitespace-pre-wrap font-mono">
                    {currentAnonymizedText || '(No anonymized text)'}
                  </pre>
                </ScrollArea>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="edit" className="mt-4">
          <Card>
            <CardHeader>
              <CardTitle>{t('editAnon')}</CardTitle>
              <CardDescription>
                Make corrections to the anonymized text if needed
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Textarea
                className="h-[500px] font-mono text-sm resize-none"
                placeholder="Edit anonymized text here..."
                value={currentAnonymizedText}
                onChange={(e) => handleTextChange(currentDoc.id, e.target.value)}
              />
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Actions */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Button
                variant="outline"
                onClick={handleReClean}
                disabled={reCleanMutation.isPending}
              >
                {reCleanMutation.isPending ? (
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                ) : (
                  <RefreshCw className="mr-2 h-4 w-4" />
                )}
                {t('rerunAnon')}
              </Button>
              {viewMode === 'edit' && Object.keys(editedTexts).length > 0 && (
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
                {t('approveAnon')}
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

