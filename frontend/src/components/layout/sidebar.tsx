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
  ChevronLeft,
  ChevronRight,
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Tooltip, TooltipContent, TooltipTrigger, TooltipProvider } from '@/components/ui/tooltip'
import { useState } from 'react'

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

export function Sidebar() {
  const pathname = usePathname()
  const t = useTranslations('nav')
  const [collapsed, setCollapsed] = useState(false)

  return (
    <TooltipProvider delayDuration={0}>
      <aside
        className={cn(
          'flex flex-col border-r border-border bg-sidebar transition-all duration-300',
          collapsed ? 'w-16' : 'w-64'
        )}
      >
        {/* Logo */}
        <div className="flex h-16 items-center justify-between border-b border-sidebar-border px-4">
          {!collapsed && (
            <Link href="/" className="flex items-center gap-2">
              <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-sidebar-primary">
                <FileText className="h-5 w-5 text-sidebar-primary-foreground" />
              </div>
              <span className="font-semibold text-sidebar-foreground">AI Claims</span>
            </Link>
          )}
          <Button
            variant="ghost"
            size="icon"
            className="h-8 w-8 shrink-0"
            onClick={() => setCollapsed(!collapsed)}
          >
            {collapsed ? (
              <ChevronRight className="h-4 w-4" />
            ) : (
              <ChevronLeft className="h-4 w-4" />
            )}
          </Button>
        </div>

        {/* Navigation */}
        <ScrollArea className="flex-1 py-4">
          <nav className="space-y-1 px-2">
            {navItems.map((item) => {
              const isActive = pathname === item.href || 
                (item.href !== '/' && pathname.startsWith(item.href))
              
              const linkContent = (
                <Link
                  href={item.href}
                  className={cn(
                    'flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors',
                    isActive
                      ? 'bg-sidebar-accent text-sidebar-accent-foreground'
                      : 'text-sidebar-foreground hover:bg-sidebar-accent/50 hover:text-sidebar-accent-foreground'
                  )}
                >
                  <item.icon className="h-5 w-5 shrink-0" />
                  {!collapsed && <span>{t(item.labelKey)}</span>}
                </Link>
              )

              if (collapsed) {
                return (
                  <Tooltip key={item.href}>
                    <TooltipTrigger asChild>
                      {linkContent}
                    </TooltipTrigger>
                    <TooltipContent side="right">
                      {t(item.labelKey)}
                    </TooltipContent>
                  </Tooltip>
                )
              }

              return <div key={item.href}>{linkContent}</div>
            })}
          </nav>
        </ScrollArea>

        {/* Footer */}
        {!collapsed && (
          <div className="border-t border-sidebar-border p-4">
            <p className="text-xs text-muted-foreground">
              © 2025 AI Claims
            </p>
          </div>
        )}
      </aside>
    </TooltipProvider>
  )
}

