"use client"

import { useTranslations } from 'next-intl'
import Link from 'next/link'
import { Eye, FileText, Clock } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Skeleton } from '@/components/ui/skeleton'
import { useClaims } from '@/hooks/use-claims'
import { formatDistanceToNow } from 'date-fns'

export default function OcrReviewQueuePage() {
  const t = useTranslations('ocr')
  const tClaims = useTranslations('claims')
  const tCountries = useTranslations('countries')
  const tCommon = useTranslations('common')

  const { data, isLoading } = useClaims({ status: 'OCR_REVIEW' })

  return (
    <div className="container py-6 space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold tracking-tight">{t('title')}</h1>
        <p className="text-muted-foreground">{t('subtitle')}</p>
      </div>

      {/* Queue */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle>Review Queue</CardTitle>
              <CardDescription>
                {data?.total || 0} claims pending OCR review
              </CardDescription>
            </div>
            <Badge variant="secondary">
              <Clock className="mr-1 h-3 w-3" />
              {data?.total || 0} pending
            </Badge>
          </div>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="space-y-4">
              {[...Array(3)].map((_, i) => (
                <Skeleton key={i} className="h-20 w-full" />
              ))}
            </div>
          ) : data?.items.length === 0 ? (
            <div className="text-center py-8">
              <Eye className="mx-auto h-12 w-12 text-muted-foreground mb-4" />
              <p className="text-muted-foreground">{tCommon('noResults')}</p>
              <p className="text-sm text-muted-foreground mt-1">
                No claims waiting for OCR review
              </p>
            </div>
          ) : (
            <div className="space-y-4">
              {data?.items.map((claim) => (
                <Link
                  key={claim.id}
                  href={`/claims/${claim.id}/ocr`}
                  className="flex items-center justify-between p-4 rounded-lg border hover:bg-muted/50 transition-colors"
                >
                  <div className="flex items-center gap-4">
                    <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10">
                      <FileText className="h-5 w-5 text-primary" />
                    </div>
                    <div>
                      <p className="font-medium">Claim #{claim.id}</p>
                      <p className="text-sm text-muted-foreground">
                        {claim.document_count} {tClaims('documents').toLowerCase()} • {' '}
                        {claim.created_at ? formatDistanceToNow(new Date(claim.created_at), { addSuffix: true }) : '-'}
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center gap-3">
                    <Badge variant="outline">{tCountries(claim.country)}</Badge>
                    <Button variant="ghost" size="sm">
                      <Eye className="mr-2 h-4 w-4" />
                      Review
                    </Button>
                  </div>
                </Link>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}

