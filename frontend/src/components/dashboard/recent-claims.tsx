"use client"

import Link from 'next/link'
import { useTranslations } from 'next-intl'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { ArrowRight } from 'lucide-react'
import type { ClaimSummary } from '@/lib/api-client'
import { StatusBadge } from '@/components/claims/status-badge'
import { formatDistanceToNow } from 'date-fns'

interface RecentClaimsProps {
  title: string
  description?: string
  claims: ClaimSummary[]
}

export function RecentClaims({ title, description, claims }: RecentClaimsProps) {
  const t = useTranslations('claims')
  const tCountries = useTranslations('countries')

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between">
        <div>
          <CardTitle>{title}</CardTitle>
          {description && <CardDescription>{description}</CardDescription>}
        </div>
        <Button variant="ghost" size="sm" asChild>
          <Link href="/claims">
            {t('viewDetails')}
            <ArrowRight className="ml-2 h-4 w-4" />
          </Link>
        </Button>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {claims.length === 0 ? (
            <p className="text-sm text-muted-foreground text-center py-4">
              {t('noDocuments')}
            </p>
          ) : (
            claims.map((claim) => (
              <Link
                key={claim.id}
                href={`/claims/${claim.id}`}
                className="flex items-center justify-between p-3 rounded-lg hover:bg-muted/50 transition-colors"
              >
                <div className="flex items-center gap-4">
                  <div className="flex flex-col">
                    <span className="font-medium">
                      Claim #{claim.id}
                    </span>
                    <span className="text-xs text-muted-foreground">
                      {claim.created_at ? formatDistanceToNow(new Date(claim.created_at), { addSuffix: true }) : '-'}
                    </span>
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  <Badge variant="outline">{tCountries(claim.country)}</Badge>
                  <StatusBadge status={claim.status} />
                  <span className="text-sm text-muted-foreground">
                    {claim.document_count} {t('documents').toLowerCase()}
                  </span>
                </div>
              </Link>
            ))
          )}
        </div>
      </CardContent>
    </Card>
  )
}

