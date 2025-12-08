"use client"

import { useTranslations } from 'next-intl'
import { Badge } from '@/components/ui/badge'
import { cn } from '@/lib/utils'
import type { ClaimStatus } from '@/lib/api-client'
import {
  Loader2,
  Eye,
  Sparkles,
  Shield,
  CheckCircle,
  AlertCircle,
  Clock,
  Zap,
} from 'lucide-react'

const statusConfig: Record<ClaimStatus, { variant: 'default' | 'secondary' | 'destructive' | 'outline'; icon: typeof Loader2 }> = {
  PROCESSING: { variant: 'secondary', icon: Loader2 },
  OCR_REVIEW: { variant: 'default', icon: Eye },
  CLEANING: { variant: 'secondary', icon: Sparkles },
  ANONYMIZING: { variant: 'secondary', icon: Shield },
  ANONYMIZATION_REVIEW: { variant: 'default', icon: Shield },
  READY_FOR_ANALYSIS: { variant: 'outline', icon: Clock },
  ANALYZING: { variant: 'secondary', icon: Zap },
  ANALYZED: { variant: 'default', icon: CheckCircle },
  FAILED: { variant: 'destructive', icon: AlertCircle },
}

interface StatusBadgeProps {
  status: ClaimStatus
  showIcon?: boolean
  className?: string
}

export function StatusBadge({ status, showIcon = true, className }: StatusBadgeProps) {
  const t = useTranslations('status')
  const config = statusConfig[status] || statusConfig.PROCESSING
  const Icon = config.icon

  return (
    <Badge variant={config.variant} className={cn('gap-1', className)}>
      {showIcon && (
        <Icon className={cn(
          'h-3 w-3',
          status === 'PROCESSING' || status === 'CLEANING' || status === 'ANONYMIZING' || status === 'ANALYZING'
            ? 'animate-spin'
            : ''
        )} />
      )}
      {t(status)}
    </Badge>
  )
}

