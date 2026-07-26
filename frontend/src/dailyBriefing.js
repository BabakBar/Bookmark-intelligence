import { localDateKey } from './localDate'

const DAY_MS = 24 * 60 * 60 * 1000

function stableHash(value) {
  let hash = 2166136261
  for (let index = 0; index < value.length; index += 1) {
    hash ^= value.charCodeAt(index)
    hash = Math.imul(hash, 16777619)
  }
  return hash >>> 0
}

function dateValue(value) {
  const parsed = Date.parse(value || '')
  return Number.isNaN(parsed) ? 0 : parsed
}

function daysSince(value, asOf) {
  const timestamp = dateValue(value)
  if (!timestamp) return null
  return Math.max(0, Math.floor((asOf.getTime() - timestamp) / DAY_MS))
}

function isAvailable(bookmark, asOf) {
  if (bookmark.status === 'archived' || bookmark.status === 'delete-candidate') {
    return false
  }
  return (
    !bookmark.snoozedUntil ||
    dateValue(bookmark.snoozedUntil) <= asOf.getTime()
  )
}

function hasContext(bookmark) {
  return Boolean(
    bookmark.keepReason?.trim() ||
      bookmark.userNote?.trim() ||
      bookmark.userTags?.length,
  )
}

function duplicateEvidence(bookmark) {
  return (
    (bookmark.rawInstanceCount || 1) > 1 ||
    (bookmark.sourceUrls?.length || 0) > 1 ||
    (bookmark.originalFolders?.length || 0) > 1
  )
}

function deterministicOrder(items, dateKey, lane) {
  return [...items].sort((left, right) => {
    const leftHash = stableHash(`${dateKey}:${lane}:${left.canonicalUrl}`)
    const rightHash = stableHash(`${dateKey}:${lane}:${right.canonicalUrl}`)
    return leftHash - rightHash
  })
}

function reasonFor(bookmark, kind, asOf) {
  const age = daysSince(bookmark.addedAt, asOf)
  const ageLabel = age === null ? '' : ` · added ${age} days ago`

  if (kind === 'merge') {
    const folderCount = bookmark.originalFolders?.length || 1
    return `Merge evidence · ${folderCount} folder${folderCount === 1 ? '' : 's'}`
  }
  if (kind === 'continue') return `Learning thread${ageLabel}`
  if (kind === 'context') return 'Kept without a personal note or reason'
  if (kind === 'rediscover') {
    const opened = daysSince(bookmark.lastOpenedAt, asOf)
    return opened === null
      ? `Kept but never opened from this workspace${ageLabel}`
      : `Kept · last opened ${opened} days ago`
  }
  if (bookmark.reviewPriority === 'time-sensitive') {
    return `Time-sensitive decision${ageLabel}`
  }
  if (bookmark.reviewPriority === 'durable-reference') {
    return `Durable reference awaiting a decision${ageLabel}`
  }
  return `Unreviewed bookmark${ageLabel}`
}

function addFromLane(deck, used, candidates, count, kind, dateKey, asOf) {
  const ordered = deterministicOrder(candidates, dateKey, kind)
  for (const bookmark of ordered) {
    if (deck.length >= count || used.has(bookmark.canonicalUrl)) continue
    used.add(bookmark.canonicalUrl)
    deck.push({
      canonicalUrl: bookmark.canonicalUrl,
      kind,
      reason: reasonFor(bookmark, kind, asOf),
    })
  }
}

export function buildDailyDeck(bookmarks, asOf = new Date()) {
  const dateKey = localDateKey(asOf)
  const available = bookmarks.filter((bookmark) => isAvailable(bookmark, asOf))
  const used = new Set()
  const deck = []

  addFromLane(
    deck,
    used,
    available.filter(
      (bookmark) =>
        bookmark.reviewState === 'unreviewed' &&
        bookmark.reviewPriority === 'time-sensitive',
    ),
    2,
    'decide',
    dateKey,
    asOf,
  )
  addFromLane(
    deck,
    used,
    available.filter(
      (bookmark) =>
        bookmark.reviewState === 'unreviewed' && duplicateEvidence(bookmark),
    ),
    3,
    'merge',
    dateKey,
    asOf,
  )
  addFromLane(
    deck,
    used,
    available.filter((bookmark) => bookmark.reviewState === 'learning'),
    4,
    'continue',
    dateKey,
    asOf,
  )
  addFromLane(
    deck,
    used,
    available.filter(
      (bookmark) =>
        ['keep', 'active', 'learning'].includes(bookmark.reviewState) &&
        !hasContext(bookmark),
    ),
    5,
    'context',
    dateKey,
    asOf,
  )
  addFromLane(
    deck,
    used,
    available.filter(
      (bookmark) =>
        ['keep', 'active', 'learning'].includes(bookmark.reviewState) &&
        (!bookmark.lastOpenedAt || daysSince(bookmark.lastOpenedAt, asOf) >= 14),
    ),
    6,
    'rediscover',
    dateKey,
    asOf,
  )
  addFromLane(
    deck,
    used,
    available.filter((bookmark) => bookmark.reviewState === 'unreviewed'),
    6,
    'decide',
    dateKey,
    asOf,
  )

  return { date: dateKey, items: deck.slice(0, 6) }
}

export function collectionPulse(bookmarks) {
  const active = bookmarks.filter(
    (bookmark) => bookmark.status !== 'delete-candidate',
  )
  const reviewed = active.filter(
    (bookmark) => bookmark.reviewState !== 'unreviewed',
  )
  const contextualized = active.filter(hasContext)
  const mergeRisks = active.filter(duplicateEvidence)
  const learning = active.filter(
    (bookmark) => bookmark.reviewState === 'learning',
  )

  const percentage = (count) =>
    active.length === 0 ? 0 : Math.round((count / active.length) * 100)

  return {
    total: bookmarks.length,
    reviewCoverage: percentage(reviewed.length),
    contextCoverage: percentage(contextualized.length),
    mergeRisks: mergeRisks.length,
    learning: learning.length,
  }
}
