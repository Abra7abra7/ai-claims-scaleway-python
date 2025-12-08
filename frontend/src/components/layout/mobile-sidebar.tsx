"use client"

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { useTranslations } from 'next-intl'
import { cn } from '@/lib/utils'
import {
  LayoutDashboard,
  FileText,
  Eye,
  Shield,
  Database,
  FileBarChart,
  Settings,
  History,
} from 'lucide-react'
import { ScrollArea } from '@/components/ui/scroll-area'
import { SheetHeader, SheetTitle } from '@/components/ui/sheet'

const navItems = [
  { href: '/', icon: LayoutDashboard, labelKey: 'dashboard' },
  { href: '/claims', icon: FileText, labelKey: 'claims' },
  { href: '/claims/ocr-review', icon: Eye, labelKey: 'ocrReview' },
  { href: '/claims/anonymization-review', icon: Shield, labelKey: 'anonReview' },
  { href: '/rag', icon: Database, labelKey: 'rag' },
  { href: '/reports', icon: FileBarChart, labelKey: 'reports' },
  { href: '/audit', icon: History, labelKey: 'audit' },
  { href: '/settings', icon: Settings, labelKey: 'settings' },
]

export function MobileSidebar() {
  const pathname = usePathname()
  const t = useTranslations('nav')
  const tCommon = useTranslations('common')

  return (
    <div className="flex h-full flex-col bg-sidebar">
      <SheetHeader className="border-b border-sidebar-border p-4">
        <SheetTitle className="flex items-center gap-2">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-sidebar-primary">
            <FileText className="h-5 w-5 text-sidebar-primary-foreground" />
          </div>
          <span className="font-semibold text-sidebar-foreground">{tCommon('appName')}</span>
        </SheetTitle>
      </SheetHeader>
      
      <ScrollArea className="flex-1 py-4">
        <nav className="space-y-1 px-2">
          {navItems.map((item) => {
            const isActive = pathname === item.href || 
              (item.href !== '/' && pathname.startsWith(item.href))
            
            return (
              <Link
                key={item.href}
                href={item.href}
                className={cn(
                  'flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors',
                  isActive
                    ? 'bg-sidebar-accent text-sidebar-accent-foreground'
                    : 'text-sidebar-foreground hover:bg-sidebar-accent/50 hover:text-sidebar-accent-foreground'
                )}
              >
                <item.icon className="h-5 w-5 shrink-0" />
                <span>{t(item.labelKey)}</span>
              </Link>
            )
          })}
        </nav>
      </ScrollArea>
    </div>
  )
}

