export const locales = ['en', 'sk'] as const
export type Locale = (typeof locales)[number]
export const defaultLocale: Locale = 'en'

export const localeNames: Record<Locale, string> = {
  en: 'English',
  sk: 'Slovenčina'
}

export const localeFlags: Record<Locale, string> = {
  en: '🇬🇧',
  sk: '🇸🇰'
}

