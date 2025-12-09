import createMiddleware from 'next-intl/middleware';
import { locales, defaultLocale } from './i18n/request';

export default createMiddleware({
  locales,
  defaultLocale,
  localePrefix: 'as-needed',
  localeDetection: true,
});

export const config = {
  // Match all pathnames except for
  // - API routes
  // - Static files
  // - _next internal paths
  matcher: ['/((?!api|_next|.*\\..*).*)'],
};

