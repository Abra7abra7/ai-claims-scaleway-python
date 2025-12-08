"use client"

import { useState } from 'react'
import { useTranslations } from 'next-intl'
import Link from 'next/link'
import { Plus, Search, Trash2, Eye, MoreHorizontal, Filter } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
  DropdownMenuSeparator,
} from '@/components/ui/dropdown-menu'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from '@/components/ui/alert-dialog'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import { StatusBadge } from '@/components/claims/status-badge'
import { useClaims, useDeleteClaim } from '@/hooks/use-claims'
import { formatDistanceToNow, format } from 'date-fns'
import type { ClaimStatus } from '@/lib/api-client'

const statusOptions: ClaimStatus[] = [
  'PROCESSING',
  'OCR_REVIEW',
  'CLEANING',
  'ANONYMIZING',
  'ANONYMIZATION_REVIEW',
  'READY_FOR_ANALYSIS',
  'ANALYZING',
  'ANALYZED',
  'FAILED',
]

export default function ClaimsPage() {
  const t = useTranslations('claims')
  const tStatus = useTranslations('status')
  const tCountries = useTranslations('countries')
  const tCommon = useTranslations('common')
  
  const [statusFilter, setStatusFilter] = useState<string>('')
  const [deleteId, setDeleteId] = useState<number | null>(null)
  
  const { data, isLoading } = useClaims({ status: statusFilter || undefined })
  const deleteMutation = useDeleteClaim()

  const handleDelete = async () => {
    if (deleteId) {
      await deleteMutation.mutateAsync(deleteId)
      setDeleteId(null)
    }
  }

  return (
    <div className="container py-6 space-y-6">
      {/* Header */}
      <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">{t('title')}</h1>
          <p className="text-muted-foreground">{t('subtitle')}</p>
        </div>
        <Button asChild>
          <Link href="/claims/new">
            <Plus className="mr-2 h-4 w-4" />
            {t('newClaim')}
          </Link>
        </Button>
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
            <div className="flex items-center gap-2">
              <Filter className="h-4 w-4 text-muted-foreground" />
              <Select value={statusFilter} onValueChange={setStatusFilter}>
                <SelectTrigger className="w-[200px]">
                  <SelectValue placeholder={t('status')} />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All statuses</SelectItem>
                  {statusOptions.map((status) => (
                    <SelectItem key={status} value={status}>
                      {tStatus(status)}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Table */}
      <Card>
        <CardContent className="p-0">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead className="w-20">ID</TableHead>
                <TableHead>{t('country')}</TableHead>
                <TableHead>{t('status')}</TableHead>
                <TableHead>{t('documents')}</TableHead>
                <TableHead>{t('createdAt')}</TableHead>
                <TableHead className="w-20">{t('actions')}</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {isLoading ? (
                [...Array(5)].map((_, i) => (
                  <TableRow key={i}>
                    <TableCell><Skeleton className="h-4 w-12" /></TableCell>
                    <TableCell><Skeleton className="h-4 w-20" /></TableCell>
                    <TableCell><Skeleton className="h-6 w-24" /></TableCell>
                    <TableCell><Skeleton className="h-4 w-8" /></TableCell>
                    <TableCell><Skeleton className="h-4 w-32" /></TableCell>
                    <TableCell><Skeleton className="h-8 w-8" /></TableCell>
                  </TableRow>
                ))
              ) : data?.items.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={6} className="text-center py-8 text-muted-foreground">
                    {tCommon('noResults')}
                  </TableCell>
                </TableRow>
              ) : (
                data?.items.map((claim) => (
                  <TableRow key={claim.id}>
                    <TableCell className="font-medium">#{claim.id}</TableCell>
                    <TableCell>
                      <Badge variant="outline">{tCountries(claim.country)}</Badge>
                    </TableCell>
                    <TableCell>
                      <StatusBadge status={claim.status} />
                    </TableCell>
                    <TableCell>{claim.document_count}</TableCell>
                    <TableCell>
                      <span title={claim.created_at ? format(new Date(claim.created_at), 'PPpp') : ''}>
                        {claim.created_at ? formatDistanceToNow(new Date(claim.created_at), { addSuffix: true }) : '-'}
                      </span>
                    </TableCell>
                    <TableCell>
                      <DropdownMenu>
                        <DropdownMenuTrigger asChild>
                          <Button variant="ghost" size="icon">
                            <MoreHorizontal className="h-4 w-4" />
                          </Button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent align="end">
                          <DropdownMenuItem asChild>
                            <Link href={`/claims/${claim.id}`}>
                              <Eye className="mr-2 h-4 w-4" />
                              {t('viewDetails')}
                            </Link>
                          </DropdownMenuItem>
                          <DropdownMenuSeparator />
                          <DropdownMenuItem
                            className="text-destructive"
                            onClick={() => setDeleteId(claim.id)}
                          >
                            <Trash2 className="mr-2 h-4 w-4" />
                            {tCommon('delete')}
                          </DropdownMenuItem>
                        </DropdownMenuContent>
                      </DropdownMenu>
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      {/* Pagination info */}
      {data && (
        <div className="text-sm text-muted-foreground">
          Showing {data.items.length} of {data.total} claims
        </div>
      )}

      {/* Delete confirmation dialog */}
      <AlertDialog open={deleteId !== null} onOpenChange={() => setDeleteId(null)}>
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
              className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
            >
              {tCommon('delete')}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  )
}

