import { getRequestConfig } from 'next-intl/server';
import { cookies, headers } from 'next/headers';

export const locales = ['sk', 'en'] as const;
export type Locale = (typeof locales)[number];
export const defaultLocale: Locale = 'sk';

export default getRequestConfig(async () => {
  // Try to get locale from cookie first
  const cookieStore = await cookies();
  const localeCookie = cookieStore.get('locale')?.value as Locale | undefined;
  
  // Fallback to Accept-Language header
  let locale: Locale = defaultLocale;
  
  if (localeCookie && locales.includes(localeCookie)) {
    locale = localeCookie;
  } else {
    const headersList = await headers();
    const acceptLanguage = headersList.get('Accept-Language') || '';
    
    // Parse Accept-Language header
    if (acceptLanguage.includes('en')) {
      locale = 'en';
    } else if (acceptLanguage.includes('sk')) {
      locale = 'sk';
    }
  }

  return {
    locale,
    messages: (await import(`../messages/${locale}.json`)).default,
  };
});

