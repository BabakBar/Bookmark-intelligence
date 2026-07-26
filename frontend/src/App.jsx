import { useLiveQuery } from 'dexie-react-hooks'
import { lazy, Suspense, useEffect, useMemo, useState } from 'react'
import Briefing from './Briefing'
import BookmarkTable from './BookmarkTable'
import DuplicateReview from './DuplicateReview'
import ReviewQueue from './ReviewQueue'
import { importBookmarkFile } from './bookmarkImport'
import { BOOKMARK_SIGNAL_VERSION, deriveBookmarkMetadata } from './bookmarkSignals'
import {
  REVIEW_STATES,
  STATUSES,
  applyBulkReviewAction,
  clearWorkspace,
  deleteSavedView,
  db,
  exportWorkspaceData,
  importWorkspaceData,
  recordBookmarkOpen,
  saveView,
  undoBulkReviewAction,
  updateBookmark,
} from './db'
import './App.css'

const BookmarkMap = lazy(() => import('./BookmarkMap'))
const ROOT_OPTIONS = ['All Memory', 'Dev + Cld', 'Dev', 'Cld']
const MAX_BACKUP_FILE_BYTES = 25 * 1024 * 1024

function folderLabel(bookmark) {
  return bookmark.originalFolders?.[0] || 'Root'
}

function formatDate(value) {
  if (!value) return 'Never'
  return new Intl.DateTimeFormat(undefined, {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  }).format(new Date(value))
}

function matchesRoot(bookmark, rootFilter) {
  if (rootFilter === 'All Memory') return true
  if (rootFilter === 'Dev + Cld') {
    return bookmark.rootFolders?.includes('Dev') || bookmark.rootFolders?.includes('Cld')
  }

  return bookmark.rootFolders?.includes(rootFilter)
}

function uniqueSorted(values) {
  return [...new Set(values.filter(Boolean))].sort((a, b) => a.localeCompare(b))
}

function parseTags(value) {
  return uniqueSorted(
    value
      .split(',')
      .map((tag) => tag.trim().toLowerCase())
      .filter(Boolean),
  )
}

function countBy(items, keyFn) {
  const counts = new Map()
  for (const item of items) {
    const key = keyFn(item)
    if (!key) continue
    counts.set(key, (counts.get(key) || 0) + 1)
  }
  return [...counts.entries()].sort((a, b) => b[1] - a[1])
}

function FilterSelect({ label, value, options, onChange }) {
  const testId = `filter-${label.toLowerCase().replaceAll(' ', '-')}`

  return (
    <label className="field">
      <span>{label}</span>
      <select data-testid={testId} onChange={(event) => onChange(event.target.value)} value={value}>
        {options.map((option) => (
          <option key={option} value={option}>
            {option}
          </option>
        ))}
      </select>
    </label>
  )
}

function filtersFromState({
  rootFilter,
  domainFilter,
  folderFilter,
  reviewFilter,
  statusFilter,
  topicFilter,
  providerFilter,
  contentTypeFilter,
  userTagFilter,
  query,
}) {
  return {
    rootFilter,
    domainFilter,
    folderFilter,
    reviewFilter,
    statusFilter,
    topicFilter,
    providerFilter,
    contentTypeFilter,
    userTagFilter,
    query,
  }
}

function BookmarkDetail({ bookmark }) {
  if (!bookmark) {
    return (
      <aside className="detail-panel empty-state">
        <h2>No Bookmark Selected</h2>
        <p>Select a row or a focused map node to review retention details.</p>
      </aside>
    )
  }

  return (
    <aside className="detail-panel">
      <div>
        <p className="eyebrow">Selected Bookmark</p>
        <h2>{bookmark.title}</h2>
        <a
          href={bookmark.url}
          onClick={() => recordBookmarkOpen(bookmark.canonicalUrl)}
          rel="noreferrer"
          target="_blank"
        >
          Open bookmark
        </a>
      </div>

      <dl className="detail-list">
        <div>
          <dt>Domain</dt>
          <dd>{bookmark.domain}</dd>
        </div>
        <div>
          <dt>Provider</dt>
          <dd>{bookmark.provider || 'Unknown'}</dd>
        </div>
        <div>
          <dt>Content type</dt>
          <dd>{bookmark.contentType || 'reference'}</dd>
        </div>
        <div>
          <dt>Topics</dt>
          <dd>{bookmark.topics?.join(', ') || 'None inferred'}</dd>
        </div>
        <div>
          <dt>User tags</dt>
          <dd>{bookmark.userTags?.join(', ') || 'None yet'}</dd>
        </div>
        <div>
          <dt>Folders</dt>
          <dd>{bookmark.originalFolders?.join(', ') || 'Root'}</dd>
        </div>
        <div>
          <dt>First seen</dt>
          <dd>{formatDate(bookmark.firstSeenAt)}</dd>
        </div>
        <div>
          <dt>Last seen</dt>
          <dd>{formatDate(bookmark.lastSeenAt)}</dd>
        </div>
      </dl>

      <FilterSelect
        label="Review state"
        onChange={(value) => updateBookmark(bookmark.canonicalUrl, { reviewState: value })}
        options={REVIEW_STATES}
        value={bookmark.reviewState}
      />
      <FilterSelect
        label="Status"
        onChange={(value) => updateBookmark(bookmark.canonicalUrl, { status: value })}
        options={STATUSES}
        value={bookmark.status}
      />

      <label className="field">
        <span>User tags</span>
        <input
          onBlur={(event) => updateBookmark(bookmark.canonicalUrl, { userTags: parseTags(event.target.value) })}
          placeholder="Comma-separated: aws-cert, project-x..."
          defaultValue={bookmark.userTags?.join(', ')}
        />
      </label>

      <label className="field">
        <span>Keep reason</span>
        <input
          onBlur={(event) => updateBookmark(bookmark.canonicalUrl, { keepReason: event.target.value })}
          placeholder="Why should this stay?"
          defaultValue={bookmark.keepReason}
        />
      </label>

      <label className="field">
        <span>Notes</span>
        <textarea
          onBlur={(event) => updateBookmark(bookmark.canonicalUrl, { userNote: event.target.value })}
          placeholder="Context, project link, cleanup note..."
          defaultValue={bookmark.userNote}
          rows={5}
        />
      </label>
    </aside>
  )
}

function StatCard({ id, label, value, note }) {
  return (
    <div className="stat-card">
      <span>{label}</span>
      <strong data-testid={id}>{value}</strong>
      <small>{note}</small>
    </div>
  )
}

export default function App() {
  const bookmarks = useLiveQuery(() => db.bookmarks.toArray(), [], [])
  const imports = useLiveQuery(() => db.imports.orderBy('importedAt').reverse().toArray(), [], [])
  const savedViews = useLiveQuery(() => db.savedViews.orderBy('updatedAt').reverse().toArray(), [], [])
  const [rootFilter, setRootFilter] = useState('All Memory')
  const [domainFilter, setDomainFilter] = useState('All domains')
  const [folderFilter, setFolderFilter] = useState('All folders')
  const [reviewFilter, setReviewFilter] = useState('All review states')
  const [statusFilter, setStatusFilter] = useState('All statuses')
  const [topicFilter, setTopicFilter] = useState('All topics')
  const [providerFilter, setProviderFilter] = useState('All providers')
  const [contentTypeFilter, setContentTypeFilter] = useState('All content types')
  const [userTagFilter, setUserTagFilter] = useState('All user tags')
  const [query, setQuery] = useState('')
  const [activeView, setActiveView] = useState('briefing')
  const [selectedUrl, setSelectedUrl] = useState('')
  const [bulkSelectedUrls, setBulkSelectedUrls] = useState([])
  const [bulkUndo, setBulkUndo] = useState(null)
  const [importMessage, setImportMessage] = useState('')
  const [isImporting, setIsImporting] = useState(false)
  const [savedViewName, setSavedViewName] = useState('')

  const rootScopedBookmarks = useMemo(
    () => bookmarks.filter((bookmark) => matchesRoot(bookmark, rootFilter)),
    [bookmarks, rootFilter],
  )

  useEffect(() => {
    const stale = bookmarks.filter(
      (bookmark) =>
        !Array.isArray(bookmark.topics) ||
        !bookmark.provider ||
        !bookmark.contentType ||
        !bookmark.reviewPriority ||
        bookmark.signalVersion !== BOOKMARK_SIGNAL_VERSION,
    )

    if (stale.length === 0) return

    db.transaction('rw', db.bookmarks, async () => {
      await db.bookmarks.bulkPut(
        stale.map((bookmark) => ({
          ...bookmark,
          ...deriveBookmarkMetadata(bookmark),
          updatedAt: new Date().toISOString(),
        })),
      )
    })
  }, [bookmarks])

  const folders = useMemo(
    () => ['All folders', ...uniqueSorted(rootScopedBookmarks.map(folderLabel))],
    [rootScopedBookmarks],
  )

  const domains = useMemo(
    () => ['All domains', ...uniqueSorted(rootScopedBookmarks.map((bookmark) => bookmark.domain))],
    [rootScopedBookmarks],
  )

  const topics = useMemo(
    () => ['All topics', ...uniqueSorted(rootScopedBookmarks.flatMap((bookmark) => bookmark.topics || []))],
    [rootScopedBookmarks],
  )

  const providers = useMemo(
    () => ['All providers', ...uniqueSorted(rootScopedBookmarks.map((bookmark) => bookmark.provider))],
    [rootScopedBookmarks],
  )

  const contentTypes = useMemo(
    () => [
      'All content types',
      ...uniqueSorted(rootScopedBookmarks.map((bookmark) => bookmark.contentType)),
    ],
    [rootScopedBookmarks],
  )

  const userTags = useMemo(
    () => [
      'All user tags',
      ...uniqueSorted(rootScopedBookmarks.flatMap((bookmark) => bookmark.userTags || [])),
    ],
    [rootScopedBookmarks],
  )

  const filteredBookmarks = useMemo(() => {
    const normalizedQuery = query.trim().toLowerCase()

    return rootScopedBookmarks.filter((bookmark) => {
      const matchesDomain = domainFilter === 'All domains' || bookmark.domain === domainFilter
      const matchesFolder = folderFilter === 'All folders' || folderLabel(bookmark) === folderFilter
      const matchesReview =
        reviewFilter === 'All review states' || bookmark.reviewState === reviewFilter
      const matchesStatus = statusFilter === 'All statuses' || bookmark.status === statusFilter
      const matchesTopic = topicFilter === 'All topics' || bookmark.topics?.includes(topicFilter)
      const matchesProvider =
        providerFilter === 'All providers' || bookmark.provider === providerFilter
      const matchesContentType =
        contentTypeFilter === 'All content types' || bookmark.contentType === contentTypeFilter
      const matchesUserTag =
        userTagFilter === 'All user tags' || bookmark.userTags?.includes(userTagFilter)
      const matchesQuery =
        !normalizedQuery ||
        [
          bookmark.title,
          bookmark.url,
          bookmark.domain,
          bookmark.provider,
          bookmark.contentType,
          folderLabel(bookmark),
          ...(bookmark.topics || []),
          ...(bookmark.userTags || []),
          bookmark.userNote,
        ]
          .join(' ')
          .toLowerCase()
          .includes(normalizedQuery)

      return (
        matchesDomain &&
        matchesFolder &&
        matchesReview &&
        matchesStatus &&
        matchesTopic &&
        matchesProvider &&
        matchesContentType &&
        matchesUserTag &&
        matchesQuery
      )
    })
  }, [
    contentTypeFilter,
    domainFilter,
    folderFilter,
    providerFilter,
    query,
    reviewFilter,
    rootScopedBookmarks,
    statusFilter,
    topicFilter,
    userTagFilter,
  ])

  const activeFilters = useMemo(
    () =>
      filtersFromState({
        rootFilter,
        domainFilter,
        folderFilter,
        reviewFilter,
        statusFilter,
        topicFilter,
        providerFilter,
        contentTypeFilter,
        userTagFilter,
        query,
      }),
    [
      contentTypeFilter,
      domainFilter,
      folderFilter,
      providerFilter,
      query,
      reviewFilter,
      rootFilter,
      statusFilter,
      topicFilter,
      userTagFilter,
    ],
  )

  const selectedBookmark =
    bookmarks.find((bookmark) => bookmark.canonicalUrl === selectedUrl) || null
  const selectedUrlSet = useMemo(
    () => new Set(bulkSelectedUrls),
    [bulkSelectedUrls],
  )
  const visibleBulkSelection = useMemo(
    () =>
      filteredBookmarks
        .map((bookmark) => bookmark.canonicalUrl)
        .filter((canonicalUrl) => selectedUrlSet.has(canonicalUrl)),
    [filteredBookmarks, selectedUrlSet],
  )

  const stats = useMemo(() => {
    const devCount = bookmarks.filter((bookmark) => bookmark.rootFolders?.includes('Dev')).length
    const cldCount = bookmarks.filter((bookmark) => bookmark.rootFolders?.includes('Cld')).length
    const needsReview = rootScopedBookmarks.filter(
      (bookmark) => bookmark.reviewState === 'unreviewed',
    ).length
    const multiFolder = rootScopedBookmarks.filter(
      (bookmark) => (bookmark.originalFolders?.length || 0) > 1,
    ).length
    const topDomains = countBy(rootScopedBookmarks, (bookmark) => bookmark.domain).slice(0, 5)

    return {
      total: bookmarks.length,
      devCount,
      cldCount,
      scoped: rootScopedBookmarks.length,
      filtered: filteredBookmarks.length,
      needsReview,
      multiFolder,
      topDomains,
    }
  }, [bookmarks, filteredBookmarks.length, rootScopedBookmarks])

  async function handleImport(event) {
    const file = event.target.files?.[0]
    if (!file) return

    setIsImporting(true)
    setImportMessage('')

    try {
      const result = await importBookmarkFile(file)
      setImportMessage(
        `Imported ${result.uniqueCount} unique bookmarks from ${file.name}. Dev: ${result.devCount}, Cld: ${result.cldCount}.`,
      )
    } catch (error) {
      setImportMessage(error instanceof Error ? error.message : 'Import failed.')
    } finally {
      event.target.value = ''
      setIsImporting(false)
    }
  }

  async function handleClear() {
    if (!window.confirm('Clear all locally stored bookmark data and review notes?')) return
    await clearWorkspace()
    setSelectedUrl('')
    setImportMessage('Local workspace cleared.')
  }

  async function handleBackupExport() {
    const data = await exportWorkspaceData()
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    const date = new Date().toISOString().slice(0, 10)

    link.href = url
    link.download = `bookmark-intelligence-workspace-${date}.json`
    link.click()
    URL.revokeObjectURL(url)
    setImportMessage(`Exported ${data.counts.bookmarks} retained records and ${data.counts.imports} imports.`)
  }

  async function handleBackupImport(event) {
    const file = event.target.files?.[0]
    if (!file) return

    setIsImporting(true)
    setImportMessage('')

    try {
      if (file.size > MAX_BACKUP_FILE_BYTES) {
        throw new Error('Workspace backup is larger than the 25 MB safety limit.')
      }
      const data = JSON.parse(await file.text())
      const result = await importWorkspaceData(data)
      setImportMessage(
        `Restored ${result.bookmarks} retained records and ${result.imports} imports from ${file.name}.`,
      )
    } catch (error) {
      setImportMessage(error instanceof Error ? error.message : 'Workspace restore failed.')
    } finally {
      event.target.value = ''
      setIsImporting(false)
    }
  }

  function applySavedView(view) {
    const filters = view.filters || {}

    setRootFilter(filters.rootFilter || 'All Memory')
    setDomainFilter(filters.domainFilter || 'All domains')
    setFolderFilter(filters.folderFilter || 'All folders')
    setReviewFilter(filters.reviewFilter || 'All review states')
    setStatusFilter(filters.statusFilter || 'All statuses')
    setTopicFilter(filters.topicFilter || 'All topics')
    setProviderFilter(filters.providerFilter || 'All providers')
    setContentTypeFilter(filters.contentTypeFilter || 'All content types')
    setUserTagFilter(filters.userTagFilter || 'All user tags')
    setQuery(filters.query || '')
    setImportMessage(`Applied saved view "${view.name}".`)
  }

  async function handleSaveView() {
    try {
      await saveView(savedViewName, activeFilters)
      setImportMessage(`Saved view "${savedViewName.trim()}".`)
      setSavedViewName('')
    } catch (error) {
      setImportMessage(error instanceof Error ? error.message : 'Could not save view.')
    }
  }

  function toggleBulkSelection(canonicalUrl) {
    setBulkSelectedUrls((current) =>
      current.includes(canonicalUrl)
        ? current.filter((url) => url !== canonicalUrl)
        : [...current, canonicalUrl],
    )
    setBulkUndo(null)
  }

  function toggleAllFiltered(checked) {
    const visibleUrls = filteredBookmarks.map(
      (bookmark) => bookmark.canonicalUrl,
    )
    setBulkSelectedUrls((current) => {
      const next = new Set(current)
      for (const canonicalUrl of visibleUrls) {
        if (checked) next.add(canonicalUrl)
        else next.delete(canonicalUrl)
      }
      return [...next]
    })
    setBulkUndo(null)
  }

  async function handleBulkReview(action) {
    try {
      const result = await applyBulkReviewAction(visibleBulkSelection, action)
      setBulkUndo(result)
      setBulkSelectedUrls([])
      setImportMessage(
        `Updated ${result.count} bookmark${result.count === 1 ? '' : 's'} to ${action}.`,
      )
    } catch (error) {
      setImportMessage(
        error instanceof Error ? error.message : 'Bulk review failed.',
      )
    }
  }

  async function handleBulkUndo() {
    try {
      const count = await undoBulkReviewAction(bulkUndo?.snapshots)
      setBulkUndo(null)
      setImportMessage(
        `Restored ${count} bookmark${count === 1 ? '' : 's'} to the previous review state.`,
      )
    } catch (error) {
      setImportMessage(
        error instanceof Error ? error.message : 'Bulk undo failed.',
      )
    }
  }

  return (
    <main className="app-shell">
      <section className="topbar">
        <div>
          <p className="eyebrow">Bookmark Intelligence · Personal knowledge</p>
          <h1>Memory Desk</h1>
        </div>
        <div className="import-box">
          <label className="upload-button">
            <input accept=".html" disabled={isImporting} onChange={handleImport} type="file" />
            {isImporting ? 'Importing...' : 'Import bookmark HTML'}
          </label>
          <button className="secondary-button" onClick={handleBackupExport} type="button">
            Export backup
          </button>
          <label className="secondary-button restore-button">
            <input
              accept="application/json,.json"
              disabled={isImporting}
              onChange={handleBackupImport}
              type="file"
            />
            Restore backup
          </label>
          <button className="secondary-button" onClick={handleClear} type="button">
            Clear local data
          </button>
        </div>
      </section>

      {importMessage && (
        <p aria-live="polite" className="status-message">
          {importMessage}
        </p>
      )}

      <section className="stats-grid">
        <StatCard id="stat-total" label="Total retained" note="canonical local records" value={stats.total} />
        <StatCard id="stat-dev" label="Dev" note="live retained records" value={stats.devCount} />
        <StatCard id="stat-cld" label="Cld" note="live retained records" value={stats.cldCount} />
        <StatCard
          id="stat-review"
          label="Needs review"
          note={`${stats.scoped} in current scope`}
          value={stats.needsReview}
        />
        <StatCard
          id="stat-filtered"
          label="Filtered view"
          note="after active filters"
          value={stats.filtered}
        />
        <StatCard
          id="stat-multifolder"
          label="Multi-folder"
          note="merged duplicate context"
          value={stats.multiFolder}
        />
      </section>

      <section className={`workspace ${activeView === 'briefing' ? 'today-workspace' : ''}`}>
        <aside className="filter-panel">
          <FilterSelect
            label="Root scope"
            onChange={(value) => {
              setRootFilter(value)
              setFolderFilter('All folders')
              setDomainFilter('All domains')
              setTopicFilter('All topics')
              setProviderFilter('All providers')
              setContentTypeFilter('All content types')
              setUserTagFilter('All user tags')
            }}
            options={ROOT_OPTIONS}
            value={rootFilter}
          />
          <label className="field">
            <span>Search</span>
            <input
              onChange={(event) => setQuery(event.target.value)}
              placeholder="Title, URL, domain, note..."
              value={query}
            />
          </label>
          <FilterSelect
            label="Folder"
            onChange={setFolderFilter}
            options={folders}
            value={folderFilter}
          />
          <FilterSelect
            label="Domain"
            onChange={setDomainFilter}
            options={domains}
            value={domainFilter}
          />
          <FilterSelect
            label="Topic"
            onChange={setTopicFilter}
            options={topics}
            value={topicFilter}
          />
          <FilterSelect
            label="Provider"
            onChange={setProviderFilter}
            options={providers}
            value={providerFilter}
          />
          <FilterSelect
            label="Content"
            onChange={setContentTypeFilter}
            options={contentTypes}
            value={contentTypeFilter}
          />
          <FilterSelect
            label="User tag"
            onChange={setUserTagFilter}
            options={userTags}
            value={userTagFilter}
          />
          <FilterSelect
            label="Review"
            onChange={setReviewFilter}
            options={['All review states', ...REVIEW_STATES]}
            value={reviewFilter}
          />
          <FilterSelect
            label="Status"
            onChange={setStatusFilter}
            options={['All statuses', ...STATUSES]}
            value={statusFilter}
          />

          <div className="top-domains">
            <h2>Top Domains</h2>
            {stats.topDomains.map(([domain, count]) => (
              <button
                key={domain}
                onClick={() => setDomainFilter(domain)}
                type="button"
              >{`${domain} (${count})`}</button>
            ))}
          </div>

          <div className="saved-views">
            <h2>Saved Views</h2>
            <label className="field">
              <span>Name</span>
              <input
                onChange={(event) => setSavedViewName(event.target.value)}
                placeholder="AWS cert cleanup"
                value={savedViewName}
              />
            </label>
            <button onClick={handleSaveView} type="button">
              Save current view
            </button>
            {savedViews.length === 0 ? (
              <p>No saved views yet.</p>
            ) : (
              savedViews.slice(0, 8).map((view) => (
                <div className="saved-view-item" key={view.id}>
                  <button onClick={() => applySavedView(view)} type="button">
                    {view.name}
                  </button>
                  <button
                    className="icon-button"
                    onClick={() => deleteSavedView(view.id)}
                    title={`Delete ${view.name}`}
                    type="button"
                  >
                    x
                  </button>
                </div>
              ))
            )}
          </div>

          <div className="import-history">
            <h2>Imports</h2>
            {imports.length === 0 ? (
              <p>No imports yet.</p>
            ) : (
              imports.slice(0, 5).map((item) => (
                <div className="import-item" key={item.id}>
                  <strong>{item.fileName}</strong>
                  <span>{formatDate(item.importedAt)}</span>
                  <small>
                    {item.totalCount} total, {item.devCount} Dev, {item.cldCount} Cld
                  </small>
                </div>
              ))
            )}
          </div>
        </aside>

        <section className="main-panel">
          <div className="view-tabs">
            <button
              aria-pressed={activeView === 'briefing'}
              className={activeView === 'briefing' ? 'active' : ''}
              onClick={() => setActiveView('briefing')}
              type="button"
            >
              Today
            </button>
            <button
              aria-pressed={activeView === 'explorer'}
              className={activeView === 'explorer' ? 'active' : ''}
              onClick={() => setActiveView('explorer')}
              type="button"
            >
              Library
            </button>
            <button
              aria-pressed={activeView === 'map'}
              className={activeView === 'map' ? 'active' : ''}
              onClick={() => setActiveView('map')}
              type="button"
            >
              Mind Map
            </button>
            <button
              aria-pressed={activeView === 'duplicates'}
              className={activeView === 'duplicates' ? 'active' : ''}
              onClick={() => setActiveView('duplicates')}
              type="button"
            >
              Duplicates
            </button>
            <button
              aria-pressed={activeView === 'review'}
              className={activeView === 'review' ? 'active' : ''}
              onClick={() => setActiveView('review')}
              type="button"
            >
              Review Queue
            </button>
          </div>

          {bookmarks.length === 0 ? (
            <div className="empty-state main-empty">
              <h2>Import a bookmark export to begin.</h2>
              <p>The workspace stores review state locally and updates live as you import newer exports.</p>
            </div>
          ) : activeView === 'briefing' ? (
            <Briefing
              bookmarks={bookmarks}
              imports={imports}
              onInspect={(canonicalUrl) => {
                setSelectedUrl(canonicalUrl)
                setActiveView('explorer')
              }}
            />
          ) : activeView === 'explorer' ? (
            <>
              {(visibleBulkSelection.length > 0 || bulkUndo) && (
                <div className="bulk-review-bar">
                  {visibleBulkSelection.length > 0 ? (
                    <>
                      <strong>
                        {visibleBulkSelection.length} selected
                      </strong>
                      <button
                        onClick={() => handleBulkReview('keep')}
                        type="button"
                      >
                        Mark keep
                      </button>
                      <button
                        className="secondary-button"
                        onClick={() => handleBulkReview('learning')}
                        type="button"
                      >
                        Continue learning
                      </button>
                      <button
                        className="secondary-button"
                        onClick={() => handleBulkReview('archive')}
                        type="button"
                      >
                        Archive
                      </button>
                      <button
                        className="quiet-control"
                        onClick={() => setBulkSelectedUrls([])}
                        type="button"
                      >
                        Clear selection
                      </button>
                    </>
                  ) : (
                    <>
                      <span>
                        {bulkUndo.count} bookmarks updated to {bulkUndo.action}.
                      </span>
                      <button onClick={handleBulkUndo} type="button">
                        Undo
                      </button>
                    </>
                  )}
                </div>
              )}
              <BookmarkTable
                bookmarks={filteredBookmarks}
                onSelect={setSelectedUrl}
                onToggleAll={toggleAllFiltered}
                onToggleSelection={toggleBulkSelection}
                selectedUrl={selectedBookmark?.canonicalUrl}
                selectedUrls={selectedUrlSet}
              />
            </>
          ) : activeView === 'map' ? (
            <Suspense
              fallback={
                <div className="empty-state main-empty">
                  <h2>Opening the map…</h2>
                </div>
              }
            >
              <BookmarkMap bookmarks={filteredBookmarks} onSelect={setSelectedUrl} />
            </Suspense>
          ) : activeView === 'duplicates' ? (
            <DuplicateReview bookmarks={filteredBookmarks} onSelect={setSelectedUrl} />
          ) : (
            <ReviewQueue bookmarks={filteredBookmarks} onSelect={setSelectedUrl} />
          )}
        </section>

        <BookmarkDetail
          bookmark={selectedBookmark}
          key={selectedBookmark?.canonicalUrl || 'no-selection'}
        />
      </section>
    </main>
  )
}
