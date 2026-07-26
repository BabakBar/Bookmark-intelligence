import { describe, expect, test } from 'bun:test'
import { buildDailyDeck, collectionPulse } from './dailyBriefing'

const asOf = new Date('2026-07-26T12:00:00.000Z')

function bookmark(id, changes = {}) {
  return {
    canonicalUrl: `https://example.com/${id}`,
    url: `https://example.com/${id}`,
    title: id,
    status: 'active',
    reviewState: 'unreviewed',
    reviewPriority: 'normal',
    originalFolders: ['Dev'],
    sourceUrls: [`https://example.com/${id}`],
    rawInstanceCount: 1,
    addedAt: '2025-01-01T00:00:00.000Z',
    userTags: [],
    userNote: '',
    keepReason: '',
    ...changes,
  }
}

describe('daily briefing', () => {
  test('builds a stable, finite, explainable deck', () => {
    const bookmarks = [
      bookmark('cert', { reviewPriority: 'time-sensitive' }),
      bookmark('duplicate', { rawInstanceCount: 2 }),
      bookmark('learning', { reviewState: 'learning' }),
      bookmark('context', { reviewState: 'keep' }),
      bookmark('rediscover', {
        reviewState: 'keep',
        keepReason: 'Durable reference',
      }),
      bookmark('normal-a'),
      bookmark('normal-b'),
    ]

    const first = buildDailyDeck(bookmarks, asOf)
    const second = buildDailyDeck(bookmarks, asOf)

    expect(first).toEqual(second)
    expect(first.items).toHaveLength(6)
    expect(first.items.map((item) => item.kind)).toEqual([
      'decide',
      'merge',
      'continue',
      'context',
      'rediscover',
      'decide',
    ])
    expect(first.items.every((item) => item.reason.length > 0)).toBe(true)
  })

  test('excludes archived and snoozed records', () => {
    const result = buildDailyDeck(
      [
        bookmark('archived', { status: 'archived' }),
        bookmark('snoozed', { snoozedUntil: '2026-07-30T00:00:00.000Z' }),
        bookmark('available'),
      ],
      asOf,
    )

    expect(result.items.map((item) => item.canonicalUrl)).toEqual([
      'https://example.com/available',
    ])
  })

  test('reports honest collection coverage', () => {
    const pulse = collectionPulse([
      bookmark('reviewed', {
        reviewState: 'keep',
        keepReason: 'Useful',
      }),
      bookmark('unreviewed', { rawInstanceCount: 2 }),
      bookmark('learning', { reviewState: 'learning' }),
      bookmark('delete', { status: 'delete-candidate' }),
    ])

    expect(pulse).toEqual({
      total: 4,
      reviewCoverage: 67,
      contextCoverage: 33,
      mergeRisks: 1,
      learning: 1,
    })
  })
})
