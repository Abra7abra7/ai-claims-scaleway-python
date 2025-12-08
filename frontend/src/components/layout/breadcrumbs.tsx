"use client"

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { useTranslations } from 'next-intl'
import { ChevronRight, Home } from 'lucide-react'
import { cn } from '@/lib/utils'

export function Breadcrumbs() {
  const pathname = usePathname()
  const t = useTranslations('nav')

  const segments = pathname.split('/').filter(Boolean)
  
  if (segments.length === 0) return null

  const breadcrumbs = segments.map((segment, index) => {
    const href = '/' + segments.slice(0, index + 1).join('/')
    const isLast = index === segments.length - 1
    
    // Try to translate, fallback to formatted segment
    let label = segment
    try {
      const translated = t(segment as any)
      if (translated !== segment) {
        label = translated
      }
    } catch {
      // Format segment: claim-detail -> Claim Detail
      label = segment
        .split('-')
        .map(word => word.charAt(0).toUpperCase() + word.slice(1))
        .join(' ')
    }

    // Handle numeric IDs
    if (!isNaN(Number(segment))) {
      label = `#${segment}`
    }

    return {
      href,
      label,
      isLast,
    }
  })

  return (
    <nav className="flex items-center space-x-1 text-sm text-muted-foreground">
      <Link
        href="/"
        className="flex items-center hover:text-foreground transition-colors"
      >
        <Home className="h-4 w-4" />
      </Link>
      {breadcrumbs.map((crumb, index) => (
        <div key={crumb.href} className="flex items-center">
          <ChevronRight className="h-4 w-4 mx-1" />
          {crumb.isLast ? (
            <span className="font-medium text-foreground">{crumb.label}</span>
          ) : (
            <Link
              href={crumb.href}
              className="hover:text-foreground transition-colors"
            >
              {crumb.label}
            </Link>
          )}
        </div>
      ))}
    </nav>
  )
}

