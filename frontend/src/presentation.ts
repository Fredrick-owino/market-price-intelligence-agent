// Dates without a clock are source observations, never workflow timestamps.
export function sourceDate(value: string): string {
  if (!/^\d{4}-\d{2}-\d{2}$/.test(value)) return 'not available'
  const date = new Date(`${value}T00:00:00Z`)
  if (!Number.isFinite(date.getTime()) || date.toISOString().slice(0, 10) !== value) return 'not available'
  return new Intl.DateTimeFormat('en-GB', { day: '2-digit', month: 'short', year: 'numeric', timeZone: 'UTC' }).format(date)
}

export function workflowTime(value?: string | null): string {
  // An offset is required: interpreting a naive value in browser time invents evidence.
  if (!value || !/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})$/.test(value)) return 'not available'
  if (sourceDate(value.slice(0, 10)) === 'not available') return 'not available'
  const date = new Date(value)
  if (!Number.isFinite(date.getTime())) return 'not available'
  return new Intl.DateTimeFormat('en-GB', {
    day: '2-digit', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit', second: '2-digit',
    hourCycle: 'h23', timeZone: 'Africa/Nairobi',
  }).format(date) + ' EAT'
}

export function recordedQuantity(draft?: { content: { calculation: { quantity: string; unit: string } } } | null): string {
  return draft ? `${draft.content.calculation.quantity} ${draft.content.calculation.unit}` : 'not available'
}
