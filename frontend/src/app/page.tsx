"use client"

import { useTranslations } from 'next-intl'
import Link from 'next/link'
import {
  FileText,
  Clock,
  CheckCircle,
  AlertCircle,
  Plus,
  Eye,
  Shield,
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { StatsCard } from '@/components/dashboard/stats-card'
import { ActivityChart } from '@/components/dashboard/activity-chart'
import { StatusDistribution } from '@/components/dashboard/status-distribution'
import { RecentClaims } from '@/components/dashboard/recent-claims'
import { Breadcrumbs } from '@/components/layout/breadcrumbs'
import { Skeleton } from '@/components/ui/skeleton'
import { useDashboardStats, useClaimStats } from '@/hooks/use-stats'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'

export default function DashboardPage() {
  const t = useTranslations('dashboard')
  const { data: dashboardStats, isLoading: isLoadingDashboard } = useDashboardStats()
  const { data: claimStats, isLoading: isLoadingStats } = useClaimStats(7)

  const pendingReviewCount = dashboardStats?.by_status
    ? (dashboardStats.by_status['OCR_REVIEW'] || 0) + (dashboardStats.by_status['ANONYMIZATION_REVIEW'] || 0)
    : 0

  const completedCount = dashboardStats?.by_status?.['ANALYZED'] || 0
  const failedCount = dashboardStats?.by_status?.['FAILED'] || 0

  return (
    <div className="container py-6 space-y-6">
      {/* Header */}
      <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">{t('title')}</h1>
          <p className="text-muted-foreground">{t('subtitle')}</p>
        </div>
        <div className="flex items-center gap-2">
          <Button asChild>
            <Link href="/claims/new">
              <Plus className="mr-2 h-4 w-4" />
              {t('newClaim')}
            </Link>
          </Button>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {isLoadingDashboard ? (
          <>
            {[...Array(4)].map((_, i) => (
              <Card key={i}>
                <CardHeader className="pb-2">
                  <Skeleton className="h-4 w-24" />
                </CardHeader>
                <CardContent>
                  <Skeleton className="h-8 w-16" />
                </CardContent>
              </Card>
            ))}
          </>
        ) : (
          <>
            <StatsCard
              title={t('totalClaims')}
              value={dashboardStats?.total_claims || 0}
              icon={FileText}
              description={t('last30Days')}
            />
            <StatsCard
              title={t('pendingReview')}
              value={pendingReviewCount}
              icon={Clock}
              className={pendingReviewCount > 0 ? 'border-warning/50' : ''}
            />
            <StatsCard
              title={t('completed')}
              value={completedCount}
              icon={CheckCircle}
              className={completedCount > 0 ? 'border-success/50' : ''}
            />
            <StatsCard
              title={t('failed')}
              value={failedCount}
              icon={AlertCircle}
              className={failedCount > 0 ? 'border-destructive/50' : ''}
            />
          </>
        )}
      </div>

      {/* Quick Actions */}
      <Card>
        <CardHeader>
          <CardTitle>{t('quickActions')}</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-wrap gap-3">
            <Button variant="outline" asChild>
              <Link href="/claims/new">
                <Plus className="mr-2 h-4 w-4" />
                {t('newClaim')}
              </Link>
            </Button>
            <Button variant="outline" asChild>
              <Link href="/claims/ocr-review">
                <Eye className="mr-2 h-4 w-4" />
                {t('viewOcrQueue')}
              </Link>
            </Button>
            <Button variant="outline" asChild>
              <Link href="/claims/anonymization-review">
                <Shield className="mr-2 h-4 w-4" />
                {t('viewAnonQueue')}
              </Link>
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Charts */}
      <div className="grid gap-6 lg:grid-cols-2">
        {isLoadingStats ? (
          <>
            <Card>
              <CardHeader>
                <Skeleton className="h-6 w-32" />
              </CardHeader>
              <CardContent>
                <Skeleton className="h-[300px] w-full" />
              </CardContent>
            </Card>
            <Card>
              <CardHeader>
                <Skeleton className="h-6 w-32" />
              </CardHeader>
              <CardContent>
                <Skeleton className="h-[300px] w-full" />
              </CardContent>
            </Card>
          </>
        ) : (
          <>
            <ActivityChart
              title={t('recentActivity')}
              description={t('last7Days')}
              data={claimStats?.daily_counts || []}
            />
            {dashboardStats?.by_status && (
              <StatusDistribution
                title={t('processingStats')}
                data={dashboardStats.by_status}
              />
            )}
          </>
        )}
      </div>

      {/* Recent Claims */}
      {isLoadingDashboard ? (
        <Card>
          <CardHeader>
            <Skeleton className="h-6 w-32" />
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {[...Array(5)].map((_, i) => (
                <Skeleton key={i} className="h-16 w-full" />
              ))}
            </div>
          </CardContent>
        </Card>
      ) : (
        <RecentClaims
          title={t('recentActivity')}
          claims={dashboardStats?.recent_claims || []}
        />
      )}
    </div>
  )
}
