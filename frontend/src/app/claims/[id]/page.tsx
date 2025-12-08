"use client"

import { use } from 'react'
import { useTranslations } from 'next-intl'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import {
  ArrowLeft,
  FileText,
  Eye,
  Shield,
  Zap,
  Trash2,
  RefreshCw,
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Skeleton } from '@/components/ui/skeleton'
import { Separator } from '@/components/ui/separator'
import { StatusBadge } from '@/components/claims/status-badge'
import { AnalysisDialog } from '@/components/claims/analysis-dialog'
import { useClaim, useDeleteClaim } from '@/hooks/use-claims'
import { format } from 'date-fns'
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from '@/components/ui/alert-dialog'

// Status timeline component
function StatusTimeline({ status }: { status: string }) {
  const t = useTranslations('status')
  const statuses = [
    'PROCESSING',
    'OCR_REVIEW',
    'CLEANING',
    'ANONYMIZING',
    'ANONYMIZATION_REVIEW',
    'READY_FOR_ANALYSIS',
    'ANALYZING',
    'ANALYZED',
  ]
  
  const currentIndex = statuses.indexOf(status)
  const isFailed = status === 'FAILED'

  return (
    <div className="flex items-center gap-2 overflow-x-auto pb-2">
      {statuses.map((s, index) => {
        const isActive = index === currentIndex
        const isCompleted = index < currentIndex
        const isPending = index > currentIndex

        return (
          <div key={s} className="flex items-center">
            <div className="flex flex-col items-center">
              <div
                className={`w-8 h-8 rounded-full flex items-center justify-center text-xs font-medium ${
                  isFailed && isActive
                    ? 'bg-destructive text-destructive-foreground'
                    : isCompleted
                    ? 'bg-success text-success-foreground'
                    : isActive
                    ? 'bg-primary text-primary-foreground'
                    : 'bg-muted text-muted-foreground'
                }`}
              >
                {index + 1}
              </div>
              <span className={`text-xs mt-1 whitespace-nowrap ${
                isActive ? 'font-medium' : 'text-muted-foreground'
              }`}>
                {t(s as any)}
              </span>
            </div>
            {index < statuses.length - 1 && (
              <div className={`w-8 h-0.5 mx-1 ${
                isCompleted ? 'bg-success' : 'bg-muted'
              }`} />
            )}
          </div>
        )
      })}
    </div>
  )
}

export default function ClaimDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params)
  const claimId = parseInt(id)
  const router = useRouter()
  const t = useTranslations('claims')
  const tCommon = useTranslations('common')
  const tCountries = useTranslations('countries')
  const tAnalysis = useTranslations('analysis')

  const { data: claim, isLoading, refetch } = useClaim(claimId)
  const deleteMutation = useDeleteClaim()

  const handleDelete = async () => {
    await deleteMutation.mutateAsync(claimId)
    router.push('/claims')
  }

  const handleAnalysisSuccess = () => {
    refetch()
  }

  if (isLoading) {
    return (
      <div className="container py-6 space-y-6">
        <Skeleton className="h-8 w-64" />
        <Skeleton className="h-48 w-full" />
        <Skeleton className="h-96 w-full" />
      </div>
    )
  }

  if (!claim) {
    return (
      <div className="container py-6">
        <Card>
          <CardContent className="py-8 text-center">
            <p className="text-muted-foreground">{tCommon('noResults')}</p>
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="container py-6 space-y-6">
      {/* Header */}
      <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <div className="flex items-center gap-4">
          <Button variant="ghost" size="icon" onClick={() => router.back()}>
            <ArrowLeft className="h-5 w-5" />
          </Button>
          <div>
            <h1 className="text-3xl font-bold tracking-tight">
              Claim #{claim.id}
            </h1>
            <div className="flex items-center gap-2 mt-1">
              <Badge variant="outline">{tCountries(claim.country)}</Badge>
              <StatusBadge status={claim.status} />
            </div>
          </div>
        </div>
        <div className="flex items-center gap-2">
          {claim.status === 'READY_FOR_ANALYSIS' && (
            <AnalysisDialog 
              claimId={claimId} 
              onSuccess={handleAnalysisSuccess}
            />
          )}
          <AlertDialog>
            <AlertDialogTrigger asChild>
              <Button variant="destructive">
                <Trash2 className="mr-2 h-4 w-4" />
                {tCommon('delete')}
              </Button>
            </AlertDialogTrigger>
            <AlertDialogContent>
              <AlertDialogHeader>
                <AlertDialogTitle>{tCommon('confirm')}</AlertDialogTitle>
                <AlertDialogDescription>
                  {t('deleteConfirm')}
                </AlertDialogDescription>
              </AlertDialogHeader>
              <AlertDialogFooter>
                <AlertDialogCancel>{tCommon('cancel')}</AlertDialogCancel>
                <AlertDialogAction
                  onClick={handleDelete}
                  className="bg-destructive text-destructive-foreground"
                >
                  {tCommon('delete')}
                </AlertDialogAction>
              </AlertDialogFooter>
            </AlertDialogContent>
          </AlertDialog>
        </div>
      </div>

      {/* Status Timeline */}
      <Card>
        <CardHeader>
          <CardTitle>{t('status')}</CardTitle>
        </CardHeader>
        <CardContent>
          <StatusTimeline status={claim.status} />
        </CardContent>
      </Card>

      {/* Tabs */}
      <Tabs defaultValue="documents" className="space-y-4">
        <TabsList>
          <TabsTrigger value="documents">
            <FileText className="mr-2 h-4 w-4" />
            {t('documents')} ({claim.documents.length})
          </TabsTrigger>
          {claim.status === 'OCR_REVIEW' && (
            <TabsTrigger value="ocr" asChild>
              <Link href={`/claims/${claim.id}/ocr`}>
                <Eye className="mr-2 h-4 w-4" />
                OCR Review
              </Link>
            </TabsTrigger>
          )}
          {claim.status === 'ANONYMIZATION_REVIEW' && (
            <TabsTrigger value="anon" asChild>
              <Link href={`/claims/${claim.id}/anonymization`}>
                <Shield className="mr-2 h-4 w-4" />
                Anon Review
              </Link>
            </TabsTrigger>
          )}
          {claim.analysis_result && (
            <TabsTrigger value="analysis">
              <Zap className="mr-2 h-4 w-4" />
              {tAnalysis('result')}
            </TabsTrigger>
          )}
        </TabsList>

        <TabsContent value="documents">
          <Card>
            <CardHeader>
              <CardTitle>{t('documents')}</CardTitle>
              <CardDescription>
                {claim.documents.length} {t('documents').toLowerCase()} uploaded
              </CardDescription>
            </CardHeader>
            <CardContent>
              {claim.documents.length === 0 ? (
                <p className="text-muted-foreground text-center py-4">
                  {t('noDocuments')}
                </p>
              ) : (
                <div className="space-y-4">
                  {claim.documents.map((doc, index) => (
                    <div
                      key={doc.id}
                      className="flex items-center justify-between p-4 rounded-lg border"
                    >
                      <div className="flex items-center gap-4">
                        <FileText className="h-8 w-8 text-muted-foreground" />
                        <div>
                          <p className="font-medium">{doc.filename}</p>
                          <p className="text-sm text-muted-foreground">
                            {doc.created_at ? format(new Date(doc.created_at), 'PPpp') : '-'}
                          </p>
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        {doc.ocr_text && (
                          <Badge variant="outline">OCR ✓</Badge>
                        )}
                        {doc.cleaned_text && (
                          <Badge variant="outline">Cleaned ✓</Badge>
                        )}
                        {doc.anonymized_text && (
                          <Badge variant="outline">Anonymized ✓</Badge>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {claim.analysis_result && (
          <TabsContent value="analysis">
            <Card>
              <CardHeader>
                <CardTitle>{tAnalysis('result')}</CardTitle>
                {claim.analysis_model && (
                  <CardDescription>
                    {tAnalysis('model')}: {claim.analysis_model}
                  </CardDescription>
                )}
              </CardHeader>
              <CardContent>
                <pre className="bg-muted p-4 rounded-lg overflow-auto text-sm">
                  {JSON.stringify(claim.analysis_result, null, 2)}
                </pre>
              </CardContent>
            </Card>
          </TabsContent>
        )}
      </Tabs>

      {/* Info */}
      <Card>
        <CardHeader>
          <CardTitle>Details</CardTitle>
        </CardHeader>
        <CardContent>
          <dl className="grid grid-cols-2 gap-4">
            <div>
              <dt className="text-sm text-muted-foreground">ID</dt>
              <dd className="font-medium">{claim.id}</dd>
            </div>
            <div>
              <dt className="text-sm text-muted-foreground">{t('country')}</dt>
              <dd className="font-medium">{tCountries(claim.country)}</dd>
            </div>
            <div>
              <dt className="text-sm text-muted-foreground">{t('status')}</dt>
              <dd><StatusBadge status={claim.status} /></dd>
            </div>
            <div>
              <dt className="text-sm text-muted-foreground">{t('createdAt')}</dt>
              <dd className="font-medium">{claim.created_at ? format(new Date(claim.created_at), 'PPpp') : '-'}</dd>
            </div>
          </dl>
        </CardContent>
      </Card>
    </div>
  )
}

