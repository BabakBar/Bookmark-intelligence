import { describe, expect, test } from 'bun:test'
import { localDateKey, localMidnightAfterDays } from './localDate'

describe('local calendar dates', () => {
  test('uses the local day around midnight', () => {
    const afterMidnight = new Date(2026, 6, 27, 0, 30)

    expect(localDateKey(afterMidnight)).toBe('2026-07-27')
  })

  test('adds calendar days at local midnight', () => {
    const result = new Date(localMidnightAfterDays('2026-07-26', 3))

    expect(localDateKey(result)).toBe('2026-07-29')
    expect(result.getHours()).toBe(0)
    expect(result.getMinutes()).toBe(0)
  })
})
