import Dexie from 'dexie'
import { canonicalizeUrl, isSupportedBookmarkUrl } from './bookmarkUrl'
import { localMidnightAfterDays } from './localDate'

export const db = new Dexie('BookmarkIntelligence')

db.version(1).stores({
  bookmarks:
    '&canonicalUrl, domain, *rootFolders, status, reviewState, firstSeenAt, lastSeenAt, addedAt, titleLower',
  imports: '++id, importedAt, fileName, totalCount, devCount, cldCount',
})

db.version(2).stores({
  bookmarks:
    '&canonicalUrl, domain, *rootFolders, status, reviewState, firstSeenAt, lastSeenAt, addedAt, titleLower, *topics, provider, contentType, reviewPriority',
  imports: '++id, importedAt, fileName, totalCount, devCount, cldCount',
})

db.version(3).stores({
  bookmarks:
    '&canonicalUrl, domain, *rootFolders, status, reviewState, firstSeenAt, lastSeenAt, addedAt, titleLower, *topics, *userTags, provider, contentType, reviewPriority',
  imports: '++id, importedAt, fileName, totalCount, devCount, cldCount',
  savedViews: '++id, name, createdAt, updatedAt',
})

db.version(4).stores({
  bookmarks:
    '&canonicalUrl, domain, *rootFolders, status, reviewState, firstSeenAt, lastSeenAt, addedAt, titleLower, *topics, *userTags, provider, contentType, reviewPriority',
  imports: '++id, importedAt, fileName, totalCount, devCount, cldCount',
  savedViews: '++id, name, createdAt, updatedAt',
  dailySessions: '&date, status, startedAt, completedAt',
  activityEvents: '++id, canonicalUrl, type, occurredAt, sessionDate',
  meta: '&key',
})

export const REVIEW_STATES = [
  'unreviewed',
  'keep',
  'active',
  'learning',
  'archive',
  'delete-candidate',
]

export const STATUSES = ['active', 'archived', 'delete-candidate']

const MAX_BACKUP_BOOKMARKS = 50_000
const MAX_BACKUP_IMPORTS = 5_000
const MAX_BACKUP_SAVED_VIEWS = 1_000
const MAX_BACKUP_DAILY_SESSIONS = 5_000
const MAX_BACKUP_ACTIVITY_EVENTS = 100_000
const MAX_BULK_REVIEW_BOOKMARKS = 1_000
const MANUAL_FIELDS = ['status', 'reviewState', 'userNote', 'keepReason', 'userTags']
const LEGACY_EPOCH = '1970-01-01T00:00:00.000Z'
const DAILY_ACTIONS = {
  keep: { reviewState: 'keep', status: 'active', eventType: 'reviewed' },
  learning: { reviewState: 'learning', status: 'active', eventType: 'reviewed' },
  archive: { reviewState: 'archive', status: 'archived', eventType: 'reviewed' },
  later: { eventType: 'deferred' },
}
const BULK_REVIEW_ACTIONS = {
  keep: { reviewState: 'keep', status: 'active' },
  learning: { reviewState: 'learning', status: 'active' },
  archive: { reviewState: 'archive', status: 'archived' },
}

function isPlainObject(value) {
  return value !== null && typeof value === 'object' && !Array.isArray(value)
}

function requiredString(value, label) {
  if (typeof value !== 'string' || !value.trim()) {
    throw new Error(`${label} must be a non-empty string.`)
  }
  return value.trim()
}

function optionalString(value, label, fallback = '') {
  if (value === undefined || value === null) return fallback
  if (typeof value !== 'string') throw new Error(`${label} must be a string.`)
  return value
}

function stringArray(value, label, fallback = []) {
  if (value === undefined || value === null) return fallback
  if (!Array.isArray(value) || value.some((item) => typeof item !== 'string')) {
    throw new Error(`${label} must be an array of strings.`)
  }
  return [...new Set(value.filter(Boolean))]
}

function folderPathArray(value, label) {
  if (value === undefined || value === null) return []
  if (
    !Array.isArray(value) ||
    value.some(
      (path) => !Array.isArray(path) || path.some((segment) => typeof segment !== 'string'),
    )
  ) {
    throw new Error(`${label} must be an array of folder paths.`)
  }
  return value
}

function timestamp(value, label, fallback = null) {
  if (value === undefined || value === null || value === '') return fallback
  if (typeof value !== 'string' || Number.isNaN(Date.parse(value))) {
    throw new Error(`${label} must be an ISO timestamp.`)
  }
  return value
}

function nonNegativeInteger(value, label, fallback = 0) {
  if (value === undefined || value === null) return fallback
  if (!Number.isInteger(value) || value < 0) {
    throw new Error(`${label} must be a non-negative integer.`)
  }
  return value
}

function timestampNumber(value) {
  const parsed = Date.parse(value || '')
  return Number.isNaN(parsed) ? 0 : parsed
}

function unique(values) {
  return [...new Set(values.filter(Boolean))]
}

function uniqueFolderPaths(paths) {
  const keyed = new Map()
  for (const path of paths) keyed.set(path.join(' > ') || 'Root', path)
  return [...keyed.values()]
}

function normalizeBookmark(record, index) {
  if (!isPlainObject(record)) {
    throw new Error(`bookmarks[${index}] must be an object.`)
  }

  const rawCanonicalUrl = requiredString(
    record.canonicalUrl,
    `bookmarks[${index}].canonicalUrl`,
  )
  const rawUrl = requiredString(record.url, `bookmarks[${index}].url`)

  if (!isSupportedBookmarkUrl(rawCanonicalUrl) || !isSupportedBookmarkUrl(rawUrl)) {
    throw new Error(`bookmarks[${index}] contains an unsupported bookmark URL.`)
  }

  const canonicalUrl = canonicalizeUrl(rawCanonicalUrl)
  const url = rawUrl
  const title = requiredString(record.title, `bookmarks[${index}].title`)
  const parsedUrl = new URL(url)
  const status = optionalString(record.status, `bookmarks[${index}].status`, 'active')
  const reviewState = optionalString(
    record.reviewState,
    `bookmarks[${index}].reviewState`,
    'unreviewed',
  )

  if (!STATUSES.includes(status)) {
    throw new Error(`bookmarks[${index}].status is not supported.`)
  }
  if (!REVIEW_STATES.includes(reviewState)) {
    throw new Error(`bookmarks[${index}].reviewState is not supported.`)
  }

  const sourceUrls = stringArray(
    record.sourceUrls,
    `bookmarks[${index}].sourceUrls`,
    [url],
  )
  if (sourceUrls.some((sourceUrl) => !isSupportedBookmarkUrl(sourceUrl))) {
    throw new Error(`bookmarks[${index}].sourceUrls contains an unsupported URL.`)
  }

  const importIds = record.importIds ?? []
  if (!Array.isArray(importIds) || importIds.some((id) => !Number.isInteger(id) || id <= 0)) {
    throw new Error(`bookmarks[${index}].importIds is invalid.`)
  }

  const createdAt = timestamp(
    record.createdAt,
    `bookmarks[${index}].createdAt`,
    LEGACY_EPOCH,
  )
  const firstSeenAt = timestamp(
    record.firstSeenAt,
    `bookmarks[${index}].firstSeenAt`,
    createdAt,
  )
  const lastSeenAt = timestamp(
    record.lastSeenAt,
    `bookmarks[${index}].lastSeenAt`,
    firstSeenAt,
  )

  return {
    canonicalUrl,
    url,
    title,
    titleLower: title.toLowerCase(),
    domain: optionalString(
      record.domain,
      `bookmarks[${index}].domain`,
      parsedUrl.hostname.replace(/^www\./, ''),
    ),
    addedAt: timestamp(record.addedAt, `bookmarks[${index}].addedAt`),
    sourceUrls: unique(sourceUrls),
    rawInstanceCount: nonNegativeInteger(
      record.rawInstanceCount,
      `bookmarks[${index}].rawInstanceCount`,
      1,
    ),
    topics: stringArray(record.topics, `bookmarks[${index}].topics`),
    userTags: stringArray(record.userTags, `bookmarks[${index}].userTags`),
    provider: optionalString(record.provider, `bookmarks[${index}].provider`, 'Unknown'),
    contentType: optionalString(
      record.contentType,
      `bookmarks[${index}].contentType`,
      'reference',
    ),
    reviewPriority: optionalString(
      record.reviewPriority,
      `bookmarks[${index}].reviewPriority`,
      'normal',
    ),
    inferredAt: timestamp(record.inferredAt, `bookmarks[${index}].inferredAt`),
    signalVersion: nonNegativeInteger(
      record.signalVersion,
      `bookmarks[${index}].signalVersion`,
    ),
    originalFolders: stringArray(
      record.originalFolders,
      `bookmarks[${index}].originalFolders`,
      ['Root'],
    ),
    folderPaths: folderPathArray(record.folderPaths, `bookmarks[${index}].folderPaths`),
    rootFolders: stringArray(
      record.rootFolders,
      `bookmarks[${index}].rootFolders`,
      ['Root'],
    ),
    firstSeenAt,
    lastSeenAt,
    importIds: unique(importIds),
    status,
    reviewState,
    userNote: optionalString(record.userNote, `bookmarks[${index}].userNote`),
    keepReason: optionalString(record.keepReason, `bookmarks[${index}].keepReason`),
    createdAt,
    updatedAt: timestamp(record.updatedAt, `bookmarks[${index}].updatedAt`, lastSeenAt),
    reviewedAt: timestamp(record.reviewedAt, `bookmarks[${index}].reviewedAt`),
    lastOpenedAt: timestamp(record.lastOpenedAt, `bookmarks[${index}].lastOpenedAt`),
    snoozedUntil: timestamp(record.snoozedUntil, `bookmarks[${index}].snoozedUntil`),
    openCount: nonNegativeInteger(record.openCount, `bookmarks[${index}].openCount`),
  }
}

function normalizeImport(record, index) {
  if (!isPlainObject(record)) throw new Error(`imports[${index}] must be an object.`)
  if (record.id !== undefined && (!Number.isInteger(record.id) || record.id <= 0)) {
    throw new Error(`imports[${index}].id is invalid.`)
  }
  const importedAt = timestamp(record.importedAt, `imports[${index}].importedAt`)
  if (!importedAt) throw new Error(`imports[${index}].importedAt is required.`)
  return {
    backupId: record.id,
    fileName: requiredString(record.fileName, `imports[${index}].fileName`),
    importedAt,
    totalCount: nonNegativeInteger(record.totalCount, `imports[${index}].totalCount`),
    devCount: nonNegativeInteger(record.devCount, `imports[${index}].devCount`),
    cldCount: nonNegativeInteger(record.cldCount, `imports[${index}].cldCount`),
  }
}

function normalizeSavedView(record, index) {
  if (!isPlainObject(record)) {
    throw new Error(`savedViews[${index}] must be an object.`)
  }
  if (!isPlainObject(record.filters)) {
    throw new Error(`savedViews[${index}].filters must be an object.`)
  }
  if (Object.values(record.filters).some((value) => typeof value !== 'string')) {
    throw new Error(`savedViews[${index}].filters contains an invalid value.`)
  }

  const now = new Date().toISOString()
  return {
    name: requiredString(record.name, `savedViews[${index}].name`),
    filters: record.filters,
    createdAt: timestamp(record.createdAt, `savedViews[${index}].createdAt`, now),
    updatedAt: timestamp(record.updatedAt, `savedViews[${index}].updatedAt`, now),
  }
}

function normalizeDailySession(record, index) {
  if (!isPlainObject(record)) {
    throw new Error(`dailySessions[${index}] must be an object.`)
  }
  const date = requiredString(record.date, `dailySessions[${index}].date`)
  if (!/^\d{4}-\d{2}-\d{2}$/.test(date)) {
    throw new Error(`dailySessions[${index}].date is invalid.`)
  }
  if (!['active', 'completed'].includes(record.status)) {
    throw new Error(`dailySessions[${index}].status is invalid.`)
  }
  if (!Array.isArray(record.items)) {
    throw new Error(`dailySessions[${index}].items must be an array.`)
  }

  const items = record.items.map((item, itemIndex) => {
    if (!isPlainObject(item) || !isSupportedBookmarkUrl(item.canonicalUrl)) {
      throw new Error(`dailySessions[${index}].items[${itemIndex}] is invalid.`)
    }
    return {
      canonicalUrl: canonicalizeUrl(item.canonicalUrl),
      kind: requiredString(item.kind, `dailySessions[${index}].items[${itemIndex}].kind`),
      reason: requiredString(
        item.reason,
        `dailySessions[${index}].items[${itemIndex}].reason`,
      ),
    }
  })
  const currentIndex = nonNegativeInteger(
    record.currentIndex,
    `dailySessions[${index}].currentIndex`,
  )
  if (currentIndex > items.length) {
    throw new Error(`dailySessions[${index}].currentIndex exceeds its deck.`)
  }
  if (!isPlainObject(record.actionCounts)) {
    throw new Error(`dailySessions[${index}].actionCounts must be an object.`)
  }
  if (
    Object.entries(record.actionCounts).some(
      ([action, count]) =>
        !DAILY_ACTIONS[action] || !Number.isInteger(count) || count < 0,
    )
  ) {
    throw new Error(`dailySessions[${index}].actionCounts is invalid.`)
  }

  return {
    date,
    status: record.status,
    startedAt: timestamp(
      record.startedAt,
      `dailySessions[${index}].startedAt`,
      LEGACY_EPOCH,
    ),
    completedAt: timestamp(
      record.completedAt,
      `dailySessions[${index}].completedAt`,
    ),
    items,
    currentIndex,
    actionCounts: record.actionCounts,
  }
}

function normalizeActivityEvent(record, index) {
  if (!isPlainObject(record) || !isSupportedBookmarkUrl(record.canonicalUrl)) {
    throw new Error(`activityEvents[${index}] is invalid.`)
  }
  if (!['opened', 'reviewed', 'deferred'].includes(record.type)) {
    throw new Error(`activityEvents[${index}].type is invalid.`)
  }
  const sessionDate = record.sessionDate ?? null
  if (sessionDate !== null && !/^\d{4}-\d{2}-\d{2}$/.test(sessionDate)) {
    throw new Error(`activityEvents[${index}].sessionDate is invalid.`)
  }
  const action = record.action ?? null
  if (action !== null && !DAILY_ACTIONS[action]) {
    throw new Error(`activityEvents[${index}].action is invalid.`)
  }

  return {
    canonicalUrl: canonicalizeUrl(record.canonicalUrl),
    type: record.type,
    occurredAt: timestamp(
      record.occurredAt,
      `activityEvents[${index}].occurredAt`,
      LEGACY_EPOCH,
    ),
    sessionDate,
    action,
  }
}

function normalizeMetaRecord(record, index) {
  if (!isPlainObject(record)) throw new Error(`meta[${index}] must be an object.`)
  const key = requiredString(record.key, `meta[${index}].key`)
  try {
    const serialized = JSON.stringify(record.value)
    if (serialized === undefined || serialized.length > 100_000) throw new Error()
  } catch {
    throw new Error(`meta[${index}].value is invalid.`)
  }
  return { key, value: record.value }
}

function verifyBackupCount(counts, key, actual) {
  if (counts?.[key] !== undefined && counts[key] !== actual) {
    throw new Error(`Backup count for ${key} does not match its records.`)
  }
}

export function validateWorkspaceBackup(data) {
  if (
    data?.schema !== 'bookmark-intelligence-workspace' ||
    ![1, 2, 3].includes(data.version)
  ) {
    throw new Error('Unsupported workspace backup format.')
  }
  if (!Array.isArray(data.bookmarks) || !Array.isArray(data.imports)) {
    throw new Error('Workspace backup is missing bookmarks or imports.')
  }

  const savedViews = data.savedViews ?? []
  const dailySessions = data.dailySessions ?? []
  const activityEvents = data.activityEvents ?? []
  const meta = data.meta ?? []
  if (!Array.isArray(savedViews)) {
    throw new Error('Workspace backup savedViews must be an array.')
  }
  if (
    !Array.isArray(dailySessions) ||
    !Array.isArray(activityEvents) ||
    !Array.isArray(meta)
  ) {
    throw new Error('Workspace backup activity data must use arrays.')
  }
  if (data.bookmarks.length > MAX_BACKUP_BOOKMARKS) {
    throw new Error('Workspace backup exceeds the bookmark safety limit.')
  }
  if (data.imports.length > MAX_BACKUP_IMPORTS) {
    throw new Error('Workspace backup exceeds the import-history safety limit.')
  }
  if (savedViews.length > MAX_BACKUP_SAVED_VIEWS) {
    throw new Error('Workspace backup exceeds the saved-view safety limit.')
  }
  if (dailySessions.length > MAX_BACKUP_DAILY_SESSIONS) {
    throw new Error('Workspace backup exceeds the daily-session safety limit.')
  }
  if (activityEvents.length > MAX_BACKUP_ACTIVITY_EVENTS) {
    throw new Error('Workspace backup exceeds the activity-event safety limit.')
  }
  if (data.counts !== undefined && !isPlainObject(data.counts)) {
    throw new Error('Workspace backup counts must be an object.')
  }

  if (data.version >= 2 && !timestamp(data.exportedAt, 'exportedAt')) {
    throw new Error('Workspace backup exportedAt is required.')
  }

  verifyBackupCount(data.counts, 'bookmarks', data.bookmarks.length)
  verifyBackupCount(data.counts, 'imports', data.imports.length)
  verifyBackupCount(data.counts, 'savedViews', savedViews.length)
  verifyBackupCount(data.counts, 'dailySessions', dailySessions.length)
  verifyBackupCount(data.counts, 'activityEvents', activityEvents.length)
  verifyBackupCount(data.counts, 'meta', meta.length)

  const imports = data.imports.map(normalizeImport)
  const backupImportIds = new Set()
  for (const record of imports) {
    if (record.backupId === undefined) continue
    if (backupImportIds.has(record.backupId)) {
      throw new Error('Workspace backup contains duplicate import IDs.')
    }
    backupImportIds.add(record.backupId)
  }

  const bookmarks = data.bookmarks.map(normalizeBookmark)
  const canonicalUrls = new Set()
  for (const record of bookmarks) {
    if (canonicalUrls.has(record.canonicalUrl)) {
      throw new Error('Workspace backup contains duplicate canonical bookmarks.')
    }
    canonicalUrls.add(record.canonicalUrl)

    if (record.importIds.some((id) => !backupImportIds.has(id))) {
      throw new Error('Workspace backup contains a dangling bookmark import reference.')
    }
  }

  const normalizedSavedViews = savedViews.map(normalizeSavedView)
  const savedViewNames = new Set()
  for (const view of normalizedSavedViews) {
    if (savedViewNames.has(view.name)) {
      throw new Error('Workspace backup contains duplicate saved-view names.')
    }
    savedViewNames.add(view.name)
  }

  const normalizedDailySessions = dailySessions.map(normalizeDailySession)
  const sessionDates = new Set()
  for (const session of normalizedDailySessions) {
    if (sessionDates.has(session.date)) {
      throw new Error('Workspace backup contains duplicate daily sessions.')
    }
    sessionDates.add(session.date)
    if (
      session.items.some((item) => !canonicalUrls.has(item.canonicalUrl))
    ) {
      throw new Error('Workspace backup contains a dangling daily-session bookmark.')
    }
    const actionCount = Object.values(session.actionCounts).reduce(
      (total, count) => total + count,
      0,
    )
    if (actionCount !== session.currentIndex) {
      throw new Error('Workspace backup daily-session progress is inconsistent.')
    }
    const isComplete = session.currentIndex === session.items.length
    if (
      (session.status === 'completed') !== isComplete ||
      (isComplete && !session.completedAt)
    ) {
      throw new Error('Workspace backup daily-session status is inconsistent.')
    }
  }

  const normalizedActivityEvents = activityEvents.map(normalizeActivityEvent)
  if (
    normalizedActivityEvents.some(
      (event) => !canonicalUrls.has(event.canonicalUrl),
    )
  ) {
    throw new Error('Workspace backup contains a dangling activity bookmark.')
  }

  return {
    bookmarks,
    imports,
    savedViews: normalizedSavedViews,
    dailySessions: normalizedDailySessions,
    activityEvents: normalizedActivityEvents,
    meta: meta.map(normalizeMetaRecord),
  }
}

function mergedBookmark(existing, incoming) {
  const merged = {
    ...existing,
    sourceUrls: unique([...(existing.sourceUrls || []), ...incoming.sourceUrls]),
    originalFolders: unique([
      ...(existing.originalFolders || []),
      ...incoming.originalFolders,
    ]),
    folderPaths: uniqueFolderPaths([
      ...(existing.folderPaths || []),
      ...incoming.folderPaths,
    ]),
    rootFolders: unique([...(existing.rootFolders || []), ...incoming.rootFolders]),
    importIds: unique([...(existing.importIds || []), ...incoming.importIds]),
    firstSeenAt:
      timestampNumber(existing.firstSeenAt) <= timestampNumber(incoming.firstSeenAt)
        ? existing.firstSeenAt
        : incoming.firstSeenAt,
    lastSeenAt:
      timestampNumber(existing.lastSeenAt) >= timestampNumber(incoming.lastSeenAt)
        ? existing.lastSeenAt
        : incoming.lastSeenAt,
    createdAt:
      timestampNumber(existing.createdAt) <= timestampNumber(incoming.createdAt)
        ? existing.createdAt
        : incoming.createdAt,
  }

  for (const field of MANUAL_FIELDS) merged[field] = existing[field]
  return merged
}

export async function clearWorkspace() {
  await db.transaction(
    'rw',
    db.bookmarks,
    db.imports,
    db.savedViews,
    db.dailySessions,
    db.activityEvents,
    db.meta,
    async () => {
      await db.bookmarks.clear()
      await db.imports.clear()
      await db.savedViews.clear()
      await db.dailySessions.clear()
      await db.activityEvents.clear()
      await db.meta.clear()
    },
  )
}

export async function updateBookmark(canonicalUrl, changes) {
  return updateBookmarks([canonicalUrl], changes)
}

export async function updateBookmarks(canonicalUrls, changes) {
  const urls = unique(canonicalUrls)
  if (urls.length === 0) return 0
  const now = new Date().toISOString()

  let updatedCount = 0
  await db.transaction('rw', db.bookmarks, async () => {
    const records = await db.bookmarks.bulkGet(urls)
    const existingRecords = records.filter(Boolean)
    updatedCount = existingRecords.length
    await db.bookmarks.bulkPut(
      existingRecords.map((record) => ({
        ...record,
        ...changes,
        reviewedAt:
          changes.reviewState && changes.reviewState !== 'unreviewed'
            ? now
            : record.reviewedAt,
        updatedAt: now,
      })),
    )
  })

  return updatedCount
}

export async function applyBulkReviewAction(canonicalUrls, action) {
  const changes = BULK_REVIEW_ACTIONS[action]
  if (!changes) throw new Error('Unsupported bulk review action.')

  const urls = unique(canonicalUrls)
  if (urls.length === 0) throw new Error('Select at least one bookmark.')
  if (urls.length > MAX_BULK_REVIEW_BOOKMARKS) {
    throw new Error('Bulk review is limited to 1,000 bookmarks at a time.')
  }

  return db.transaction('rw', db.bookmarks, async () => {
    const records = await db.bookmarks.bulkGet(urls)
    if (records.some((record) => !record)) {
      throw new Error('A selected bookmark no longer exists. Refresh the selection.')
    }

    const reviewedAt = new Date().toISOString()
    const snapshots = records.map((record) => ({
      canonicalUrl: record.canonicalUrl,
      reviewState: record.reviewState,
      status: record.status,
      reviewedAt: record.reviewedAt ?? null,
      snoozedUntil: record.snoozedUntil ?? null,
      bulkUpdatedAt: reviewedAt,
    }))

    await db.bookmarks.bulkPut(
      records.map((record) => ({
        ...record,
        ...changes,
        reviewedAt,
        snoozedUntil: null,
        updatedAt: reviewedAt,
      })),
    )

    return { action, count: records.length, snapshots }
  })
}

export async function undoBulkReviewAction(snapshots) {
  if (!Array.isArray(snapshots) || snapshots.length === 0) {
    throw new Error('There is no bulk review action to undo.')
  }
  if (snapshots.length > MAX_BULK_REVIEW_BOOKMARKS) {
    throw new Error('Bulk undo exceeds the safety limit.')
  }

  return db.transaction('rw', db.bookmarks, async () => {
    const urls = snapshots.map((snapshot) => snapshot.canonicalUrl)
    const records = await db.bookmarks.bulkGet(urls)
    if (records.some((record) => !record)) {
      throw new Error('A reviewed bookmark no longer exists, so undo was stopped.')
    }
    if (
      records.some(
        (record, index) => record.updatedAt !== snapshots[index].bulkUpdatedAt,
      )
    ) {
      throw new Error(
        'A reviewed bookmark changed after the bulk action, so undo was stopped.',
      )
    }

    const undoneAt = new Date().toISOString()
    await db.bookmarks.bulkPut(
      records.map((record, index) => ({
        ...record,
        reviewState: snapshots[index].reviewState,
        status: snapshots[index].status,
        reviewedAt: snapshots[index].reviewedAt,
        snoozedUntil: snapshots[index].snoozedUntil,
        updatedAt: undoneAt,
      })),
    )

    return records.length
  })
}

export async function recordBookmarkOpen(canonicalUrl, sessionDate = null) {
  const occurredAt = new Date().toISOString()
  await db.transaction('rw', db.bookmarks, db.activityEvents, async () => {
    const bookmark = await db.bookmarks.get(canonicalUrl)
    if (!bookmark) return
    await db.bookmarks.update(canonicalUrl, {
      lastOpenedAt: occurredAt,
      openCount: (bookmark.openCount || 0) + 1,
    })
    await db.activityEvents.add({
      canonicalUrl,
      type: 'opened',
      occurredAt,
      sessionDate,
    })
  })
}

export async function getOrCreateDailySession(dailyDeck) {
  const existing = await db.dailySessions.get(dailyDeck.date)
  if (existing) return existing

  const startedAt = new Date().toISOString()
  const session = {
    date: dailyDeck.date,
    status: dailyDeck.items.length === 0 ? 'completed' : 'active',
    startedAt,
    completedAt: dailyDeck.items.length === 0 ? startedAt : null,
    items: dailyDeck.items,
    currentIndex: 0,
    actionCounts: {},
  }
  await db.dailySessions.put(session)
  return session
}

export async function applyDailyAction(date, canonicalUrl, action) {
  const actionConfig = DAILY_ACTIONS[action]
  if (!actionConfig) throw new Error('Unsupported daily action.')

  return db.transaction(
    'rw',
    db.bookmarks,
    db.dailySessions,
    db.activityEvents,
    async () => {
      const [bookmark, session] = await Promise.all([
        db.bookmarks.get(canonicalUrl),
        db.dailySessions.get(date),
      ])
      if (!bookmark || !session) throw new Error('Daily session record is missing.')

      const currentItem = session.items[session.currentIndex]
      if (currentItem?.canonicalUrl !== canonicalUrl) {
        throw new Error('Daily action does not match the current card.')
      }

      const occurredAt = new Date().toISOString()
      const bookmarkChanges =
        action === 'later'
          ? {
              snoozedUntil: localMidnightAfterDays(date, 3),
              updatedAt: occurredAt,
            }
          : {
              reviewState: actionConfig.reviewState,
              status: actionConfig.status,
              reviewedAt: occurredAt,
              updatedAt: occurredAt,
            }

      await db.bookmarks.update(canonicalUrl, bookmarkChanges)
      await db.activityEvents.add({
        canonicalUrl,
        type: actionConfig.eventType,
        occurredAt,
        sessionDate: date,
        action,
      })

      const currentIndex = Math.min(session.currentIndex + 1, session.items.length)
      const completed = currentIndex >= session.items.length
      const updatedSession = {
        ...session,
        currentIndex,
        status: completed ? 'completed' : 'active',
        completedAt: completed ? occurredAt : null,
        actionCounts: {
          ...session.actionCounts,
          [action]: (session.actionCounts?.[action] || 0) + 1,
        },
      }
      await db.dailySessions.put(updatedSession)
      return updatedSession
    },
  )
}

export async function exportWorkspaceData() {
  const [bookmarks, imports, savedViews, dailySessions, activityEvents, meta] =
    await Promise.all([
      db.bookmarks.toArray(),
      db.imports.toArray(),
      db.savedViews.toArray(),
      db.dailySessions.toArray(),
      db.activityEvents.toArray(),
      db.meta.toArray(),
    ])

  return {
    schema: 'bookmark-intelligence-workspace',
    version: 3,
    exportedAt: new Date().toISOString(),
    counts: {
      bookmarks: bookmarks.length,
      imports: imports.length,
      savedViews: savedViews.length,
      dailySessions: dailySessions.length,
      activityEvents: activityEvents.length,
      meta: meta.length,
    },
    bookmarks,
    imports,
    savedViews,
    dailySessions,
    activityEvents,
    meta,
  }
}

export async function importWorkspaceData(data) {
  const { bookmarks, imports, savedViews, dailySessions, activityEvents, meta } =
    validateWorkspaceBackup(data)

  await db.transaction(
    'rw',
    db.bookmarks,
    db.imports,
    db.savedViews,
    db.dailySessions,
    db.activityEvents,
    db.meta,
    async () => {
      const importIdMap = new Map()

      for (const incoming of imports) {
        const { backupId, ...record } = incoming
        const existing = await db.imports
          .where('importedAt')
          .equals(record.importedAt)
          .filter(
            (candidate) =>
              candidate.fileName === record.fileName &&
              candidate.totalCount === record.totalCount &&
              candidate.devCount === record.devCount &&
              candidate.cldCount === record.cldCount,
          )
          .first()
        const restoredId = existing?.id ?? (await db.imports.add(record))
        if (backupId !== undefined) importIdMap.set(backupId, restoredId)
      }

      for (const incoming of bookmarks) {
        const remapped = {
          ...incoming,
          importIds: unique(
            incoming.importIds
              .map((backupId) => importIdMap.get(backupId))
              .filter((id) => id !== undefined),
          ),
        }
        const existing = await db.bookmarks.get(remapped.canonicalUrl)
        await db.bookmarks.put(
          existing ? mergedBookmark(existing, remapped) : remapped,
        )
      }

      for (const incoming of savedViews) {
        const existing = await db.savedViews
          .where('name')
          .equals(incoming.name)
          .first()
        if (!existing) {
          await db.savedViews.add(incoming)
        } else if (
          timestampNumber(incoming.updatedAt) >
          timestampNumber(existing.updatedAt)
        ) {
          await db.savedViews.put({ ...incoming, id: existing.id })
        }
      }

      for (const incoming of dailySessions) {
        const existing = await db.dailySessions.get(incoming.date)
        if (!existing) await db.dailySessions.add(incoming)
      }

      for (const incoming of activityEvents) {
        const existing = await db.activityEvents
          .where('occurredAt')
          .equals(incoming.occurredAt)
          .filter(
            (event) =>
              event.canonicalUrl === incoming.canonicalUrl &&
              event.type === incoming.type &&
              event.sessionDate === incoming.sessionDate,
          )
          .first()
        if (!existing) await db.activityEvents.add(incoming)
      }

      for (const incoming of meta) {
        const existing = await db.meta.get(incoming.key)
        if (!existing) await db.meta.add(incoming)
      }
    },
  )

  return {
    bookmarks: bookmarks.length,
    imports: imports.length,
    savedViews: savedViews.length,
    dailySessions: dailySessions.length,
    activityEvents: activityEvents.length,
  }
}

export async function saveView(name, filters) {
  const now = new Date().toISOString()
  const trimmedName = name.trim()

  if (!trimmedName) throw new Error('Saved view name is required.')

  const normalizedName = trimmedName.toLowerCase()
  const existing = await db.savedViews
    .filter((view) => view.name.toLowerCase() === normalizedName)
    .first()
  const payload = {
    name: existing?.name ?? trimmedName,
    filters,
    updatedAt: now,
  }

  if (existing) {
    await db.savedViews.put({
      ...existing,
      ...payload,
    })
    return existing.id
  }

  return db.savedViews.add({
    ...payload,
    createdAt: now,
  })
}

export async function deleteSavedView(id) {
  await db.savedViews.delete(id)
}
