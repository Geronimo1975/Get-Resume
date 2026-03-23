import { format, formatDistanceToNow, parseISO } from 'date-fns'
import { de } from 'date-fns/locale'

export function formatDateDE(dateStr: string): string {
  return format(parseISO(dateStr), 'd. MMMM yyyy', { locale: de })
}

export function formatDateShortDE(dateStr: string): string {
  return format(parseISO(dateStr), 'dd.MM.yyyy', { locale: de })
}

export function formatRelativeDE(dateStr: string): string {
  return formatDistanceToNow(parseISO(dateStr), { addSuffix: true, locale: de })
}

export function formatMonthYearDE(dateStr: string): string {
  if (!dateStr) return ''
  return format(parseISO(dateStr), 'MMMM yyyy', { locale: de })
}

export function formatCurrencyDE(amount: number): string {
  return new Intl.NumberFormat('de-DE', {
    style: 'currency',
    currency: 'EUR',
  }).format(amount)
}
