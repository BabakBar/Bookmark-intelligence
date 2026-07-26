function pad(value) {
  return String(value).padStart(2, '0')
}

export function localDateKey(date = new Date()) {
  return [
    date.getFullYear(),
    pad(date.getMonth() + 1),
    pad(date.getDate()),
  ].join('-')
}

export function localMidnightAfterDays(dateKey, days) {
  const match = /^(\d{4})-(\d{2})-(\d{2})$/.exec(dateKey)
  if (!match || !Number.isInteger(days)) {
    throw new Error('A valid local date and whole-day offset are required.')
  }

  const [, year, month, day] = match
  const result = new Date(Number(year), Number(month) - 1, Number(day) + days)
  result.setHours(0, 0, 0, 0)
  return result.toISOString()
}
