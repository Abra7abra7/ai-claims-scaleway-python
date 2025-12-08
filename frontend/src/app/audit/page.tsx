"use client"

import { useTranslations } from 'next-intl'
import { History, Search, Filter } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import { Badge } from '@/components/ui/badge'
import { Skeleton } from '@/components/ui/skeleton'
import { useQuery } from '@tanstack/react-query'
import { auditApi, type AuditEntry } from '@/lib/api-client'
import { format } from 'date-fns'

const actionColors: Record<string, 'default' | 'secondary' | 'destructive' | 'outline'> = {
  create: 'default',
  update: 'secondary',
  delete: 'destructive',
  approve: 'default',
  reject: 'destructive',
}

export default function AuditPage() {
  const t = useTranslations('audit')
  const tCommon = useTranslations('common')

  const { data: entries, isLoading } = useQuery({
    queryKey: ['audit'],
    queryFn: () => auditApi.list({ limit: 100 }),
  })

  return (
    <div className="container py-6 space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold tracking-tight">{t('title')}</h1>
        <p className="text-muted-foreground">{t('subtitle')}</p>
      </div>

      {/* Filters */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex flex-col gap-4 md:flex-row md:items-center">
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                <Input
                  placeholder={tCommon('search')}
                  className="pl-9"
                />
              </div>
            </div>
            <Button variant="outline">
              <Filter className="mr-2 h-4 w-4" />
              Filters
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Table */}
      <Card>
        <CardContent className="p-0">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>{t('timestamp')}</TableHead>
                <TableHead>{t('action')}</TableHead>
                <TableHead>{t('user')}</TableHead>
                <TableHead>{t('claimId')}</TableHead>
                <TableHead>{t('details')}</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {isLoading ? (
                [...Array(10)].map((_, i) => (
                  <TableRow key={i}>
                    <TableCell><Skeleton className="h-4 w-32" /></TableCell>
                    <TableCell><Skeleton className="h-6 w-20" /></TableCell>
                    <TableCell><Skeleton className="h-4 w-24" /></TableCell>
                    <TableCell><Skeleton className="h-4 w-16" /></TableCell>
                    <TableCell><Skeleton className="h-4 w-48" /></TableCell>
                  </TableRow>
                ))
              ) : !entries || entries.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={5} className="text-center py-8 text-muted-foreground">
                    <History className="mx-auto h-12 w-12 text-muted-foreground mb-4" />
                    {tCommon('noResults')}
                  </TableCell>
                </TableRow>
              ) : (
                entries.map((entry) => (
                  <TableRow key={entry.id}>
                    <TableCell className="font-mono text-sm">
                      {entry.created_at ? format(new Date(entry.created_at), 'PPpp') : '-'}
                    </TableCell>
                    <TableCell>
                      <Badge variant={actionColors[entry.action.toLowerCase()] || 'outline'}>
                        {entry.action}
                      </Badge>
                    </TableCell>
                    <TableCell>{entry.user}</TableCell>
                    <TableCell>
                      {entry.claim_id ? (
                        <Badge variant="outline">#{entry.claim_id}</Badge>
                      ) : (
                        <span className="text-muted-foreground">-</span>
                      )}
                    </TableCell>
                    <TableCell className="max-w-xs truncate">
                      {entry.details ? JSON.stringify(entry.details) : '-'}
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  )
}

