"use client"

import { useState, useEffect } from 'react'
import { useTranslations } from 'next-intl'
import { useTheme } from 'next-themes'
import { useRouter } from 'next/navigation'
import { Sun, Moon, Monitor, Globe, User, Bell } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Label } from '@/components/ui/label'
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group'
import { Switch } from '@/components/ui/switch'
import { Separator } from '@/components/ui/separator'
import { locales, localeNames, localeFlags, type Locale } from '@/i18n/config'

export default function SettingsPage() {
  const t = useTranslations('settings')
  const { theme, setTheme } = useTheme()
  const router = useRouter()
  const [currentLocale, setCurrentLocale] = useState<Locale>('en')

  useEffect(() => {
    const match = document.cookie.match(/locale=(\w+)/)
    if (match && locales.includes(match[1] as Locale)) {
      setCurrentLocale(match[1] as Locale)
    }
  }, [])

  const handleLocaleChange = (locale: Locale) => {
    document.cookie = `locale=${locale};path=/;max-age=31536000`
    setCurrentLocale(locale)
    router.refresh()
  }

  return (
    <div className="container py-6 max-w-2xl space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold tracking-tight">{t('title')}</h1>
        <p className="text-muted-foreground">{t('subtitle')}</p>
      </div>

      {/* Appearance */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Sun className="h-5 w-5" />
            {t('appearance')}
          </CardTitle>
          <CardDescription>
            Customize how the application looks
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Theme */}
          <div className="space-y-3">
            <Label>{t('theme')}</Label>
            <RadioGroup
              value={theme}
              onValueChange={setTheme}
              className="grid grid-cols-3 gap-4"
            >
              <Label
                htmlFor="light"
                className="flex flex-col items-center justify-between rounded-md border-2 border-muted bg-popover p-4 hover:bg-accent hover:text-accent-foreground cursor-pointer [&:has([data-state=checked])]:border-primary"
              >
                <RadioGroupItem value="light" id="light" className="sr-only" />
                <Sun className="h-6 w-6 mb-2" />
                <span className="text-sm">{t('themeLight')}</span>
              </Label>
              <Label
                htmlFor="dark"
                className="flex flex-col items-center justify-between rounded-md border-2 border-muted bg-popover p-4 hover:bg-accent hover:text-accent-foreground cursor-pointer [&:has([data-state=checked])]:border-primary"
              >
                <RadioGroupItem value="dark" id="dark" className="sr-only" />
                <Moon className="h-6 w-6 mb-2" />
                <span className="text-sm">{t('themeDark')}</span>
              </Label>
              <Label
                htmlFor="system"
                className="flex flex-col items-center justify-between rounded-md border-2 border-muted bg-popover p-4 hover:bg-accent hover:text-accent-foreground cursor-pointer [&:has([data-state=checked])]:border-primary"
              >
                <RadioGroupItem value="system" id="system" className="sr-only" />
                <Monitor className="h-6 w-6 mb-2" />
                <span className="text-sm">{t('themeSystem')}</span>
              </Label>
            </RadioGroup>
          </div>
        </CardContent>
      </Card>

      {/* Language */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Globe className="h-5 w-5" />
            {t('language')}
          </CardTitle>
          <CardDescription>
            Select your preferred language
          </CardDescription>
        </CardHeader>
        <CardContent>
          <RadioGroup
            value={currentLocale}
            onValueChange={(value) => handleLocaleChange(value as Locale)}
            className="space-y-3"
          >
            {locales.map((locale) => (
              <Label
                key={locale}
                htmlFor={locale}
                className="flex items-center justify-between rounded-lg border p-4 cursor-pointer hover:bg-accent [&:has([data-state=checked])]:border-primary"
              >
                <div className="flex items-center gap-3">
                  <span className="text-2xl">{localeFlags[locale]}</span>
                  <span className="font-medium">{localeNames[locale]}</span>
                </div>
                <RadioGroupItem value={locale} id={locale} />
              </Label>
            ))}
          </RadioGroup>
        </CardContent>
      </Card>

      {/* Notifications */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Bell className="h-5 w-5" />
            {t('notifications')}
          </CardTitle>
          <CardDescription>
            Configure notification preferences
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <Label>Email notifications</Label>
              <p className="text-sm text-muted-foreground">
                Receive email updates about claim status changes
              </p>
            </div>
            <Switch />
          </div>
          <Separator />
          <div className="flex items-center justify-between">
            <div>
              <Label>Browser notifications</Label>
              <p className="text-sm text-muted-foreground">
                Show desktop notifications for important events
              </p>
            </div>
            <Switch />
          </div>
        </CardContent>
      </Card>

      {/* Profile */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <User className="h-5 w-5" />
            {t('profile')}
          </CardTitle>
          <CardDescription>
            Your account information
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="flex items-center gap-4">
              <div className="flex h-16 w-16 items-center justify-center rounded-full bg-primary text-primary-foreground text-xl font-bold">
                A
              </div>
              <div>
                <p className="font-medium">Admin User</p>
                <p className="text-sm text-muted-foreground">admin@example.com</p>
              </div>
            </div>
            <Separator />
            <p className="text-sm text-muted-foreground">
              Authentication is coming soon with Better Auth integration.
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

