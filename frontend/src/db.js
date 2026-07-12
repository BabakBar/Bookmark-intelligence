import Dexie from 'dexie'

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

export const REVIEW_STATES = [
  'unreviewed',
  'keep',
  'active',
  'learning',
  'archive',
  'delete-candidate',
]

export const STATUSES = ['active', 'archived', 'delete-candidate']

export async function clearWorkspace() {
  await db.transaction('rw', db.bookmarks, db.imports, db.savedViews, async () => {
    await db.bookmarks.clear()
    await db.imports.clear()
    await db.savedViews.clear()
  })
}

export async function updateBookmark(canonicalUrl, changes) {
  await db.bookmarks.update(canonicalUrl, {
    ...changes,
    updatedAt: new Date().toISOString(),
  })
}

export async function exportWorkspaceData() {
  const [bookmarks, imports, savedViews] = await Promise.all([
    db.bookmarks.toArray(),
    db.imports.toArray(),
    db.savedViews.toArray(),
  ])

  return {
    schema: 'bookmark-intelligence-workspace',
    version: 2,
    exportedAt: new Date().toISOString(),
    counts: {
      bookmarks: bookmarks.length,
      imports: imports.length,
      savedViews: savedViews.length,
    },
    bookmarks,
    imports,
    savedViews,
  }
}

export async function importWorkspaceData(data) {
  if (
    data?.schema !== 'bookmark-intelligence-workspace' ||
    ![1, 2].includes(data.version)
  ) {
    throw new Error('Unsupported workspace backup format.')
  }

  if (!Array.isArray(data.bookmarks) || !Array.isArray(data.imports)) {
    throw new Error('Workspace backup is missing bookmarks or imports.')
  }

  const savedViews = Array.isArray(data.savedViews) ? data.savedViews : []

  await db.transaction('rw', db.bookmarks, db.imports, db.savedViews, async () => {
    await db.bookmarks.bulkPut(data.bookmarks)
    await db.imports.bulkPut(data.imports)
    if (savedViews.length > 0) await db.savedViews.bulkPut(savedViews)
  })

  return {
    bookmarks: data.bookmarks.length,
    imports: data.imports.length,
    savedViews: savedViews.length,
  }
}

export async function saveView(name, filters) {
  const now = new Date().toISOString()
  const trimmedName = name.trim()

  if (!trimmedName) throw new Error('Saved view name is required.')

  const existing = await db.savedViews.where('name').equals(trimmedName).first()
  const payload = {
    name: trimmedName,
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
