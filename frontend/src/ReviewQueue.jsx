import { updateBookmark } from './db'

const PRIORITY_ORDER = {
  'merge-review': 0,
  'time-sensitive': 1,
  'durable-reference': 2,
  normal: 3,
}

function scoreBookmark(bookmark) {
  const reviewedPenalty = bookmark.reviewState === 'unreviewed' ? 0 : 10
  return (PRIORITY_ORDER[bookmark.reviewPriority] ?? 4) + reviewedPenalty
}

function sortedQueue(bookmarks) {
  return [...bookmarks]
    .filter((bookmark) => bookmark.status !== 'delete-candidate')
    .sort((a, b) => {
      const priority = scoreBookmark(a) - scoreBookmark(b)
      if (priority !== 0) return priority
      return (b.lastSeenAt || '').localeCompare(a.lastSeenAt || '')
    })
    .slice(0, 120)
}

function QueueAction({ bookmark, label, changes }) {
  return (
    <button
      className={label === 'Keep' ? '' : 'secondary-button'}
      onClick={() => updateBookmark(bookmark.canonicalUrl, changes)}
      type="button"
    >
      {label}
    </button>
  )
}

export default function ReviewQueue({ bookmarks, onSelect }) {
  const queue = sortedQueue(bookmarks)
  const unreviewedCount = bookmarks.filter((bookmark) => bookmark.reviewState === 'unreviewed').length

  if (queue.length === 0) {
    return (
      <div className="queue-panel empty-state">
        <h2>No reviewable bookmarks in this scope.</h2>
        <p>Change filters or import a fresh export to continue reviewing.</p>
      </div>
    )
  }

  return (
    <div className="queue-panel">
      <div className="duplicate-header">
        <div>
          <h2>Review Queue</h2>
          <p>
            {unreviewedCount} unreviewed in current scope. Showing the next {queue.length} records.
          </p>
        </div>
      </div>

      <div className="queue-list">
        {queue.map((bookmark) => (
          <article className="queue-card" key={bookmark.canonicalUrl}>
            <div className="queue-main">
              <div>
                <span className="pill">{bookmark.reviewPriority || 'normal'}</span>
                <h3>{bookmark.title}</h3>
                <p>
                  {bookmark.provider || 'Unknown'} · {bookmark.contentType || 'reference'} ·{' '}
                  {bookmark.topics?.slice(0, 4).join(', ') || 'no inferred topics'}
                </p>
                <small>{bookmark.originalFolders?.join(' | ') || 'Root'}</small>
              </div>
              <button onClick={() => onSelect(bookmark.canonicalUrl)} type="button">
                Inspect
              </button>
            </div>

            <div className="queue-actions">
              <QueueAction
                bookmark={bookmark}
                changes={{ reviewState: 'keep', status: 'active' }}
                label="Keep"
              />
              <QueueAction
                bookmark={bookmark}
                changes={{ reviewState: 'learning', status: 'active' }}
                label="Learning"
              />
              <QueueAction
                bookmark={bookmark}
                changes={{ reviewState: 'archive', status: 'archived' }}
                label="Archive"
              />
              <QueueAction
                bookmark={bookmark}
                changes={{ reviewState: 'delete-candidate', status: 'delete-candidate' }}
                label="Delete candidate"
              />
            </div>
          </article>
        ))}
      </div>
    </div>
  )
}
