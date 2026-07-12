import { updateBookmark } from './db'

function isDuplicateCandidate(bookmark) {
  return (
    (bookmark.originalFolders?.length || 0) > 1 ||
    (bookmark.sourceUrls?.length || 0) > 1 ||
    (bookmark.rawInstanceCount || 1) > 1
  )
}

function candidateReason(bookmark) {
  const reasons = []
  if ((bookmark.originalFolders?.length || 0) > 1) reasons.push('multiple folders')
  if ((bookmark.sourceUrls?.length || 0) > 1) reasons.push('URL variants')
  if ((bookmark.rawInstanceCount || 1) > 1) reasons.push('raw duplicates')
  return reasons.join(', ')
}

export default function DuplicateReview({ bookmarks, onSelect }) {
  const candidates = bookmarks.filter(isDuplicateCandidate)

  if (candidates.length === 0) {
    return (
      <div className="duplicate-panel empty-state">
        <h2>No duplicate candidates in this scope.</h2>
        <p>Canonical URL normalization has not found repeated folders or URL variants here.</p>
      </div>
    )
  }

  return (
    <div className="duplicate-panel">
      <div className="duplicate-header">
        <div>
          <h2>Duplicate Review</h2>
          <p>{candidates.length} canonical records need merge or retention decisions.</p>
        </div>
      </div>

      <div className="duplicate-list">
        {candidates.map((bookmark) => (
          <article className="duplicate-card" key={bookmark.canonicalUrl}>
            <div className="duplicate-card-header">
              <div>
                <span className="pill">{candidateReason(bookmark)}</span>
                <h3>{bookmark.title}</h3>
                <a href={bookmark.url} rel="noreferrer" target="_blank">
                  {bookmark.domain}
                </a>
              </div>
              <button onClick={() => onSelect(bookmark.canonicalUrl)} type="button">
                Inspect
              </button>
            </div>

            <dl className="duplicate-meta">
              <div>
                <dt>Canonical</dt>
                <dd>{bookmark.canonicalUrl}</dd>
              </div>
              <div>
                <dt>Raw instances</dt>
                <dd>{bookmark.rawInstanceCount || 1}</dd>
              </div>
              <div>
                <dt>Folders</dt>
                <dd>{bookmark.originalFolders?.join(' | ') || 'Root'}</dd>
              </div>
              <div>
                <dt>Source URLs</dt>
                <dd>{(bookmark.sourceUrls || [bookmark.url]).join(' | ')}</dd>
              </div>
            </dl>

            <div className="duplicate-actions">
              <button
                onClick={() =>
                  updateBookmark(bookmark.canonicalUrl, {
                    reviewState: 'keep',
                    status: 'active',
                  })
                }
                type="button"
              >
                Keep
              </button>
              <button
                className="secondary-button"
                onClick={() =>
                  updateBookmark(bookmark.canonicalUrl, {
                    reviewState: 'archive',
                    status: 'archived',
                  })
                }
                type="button"
              >
                Archive
              </button>
              <button
                className="secondary-button"
                onClick={() =>
                  updateBookmark(bookmark.canonicalUrl, {
                    reviewState: 'delete-candidate',
                    status: 'delete-candidate',
                  })
                }
                type="button"
              >
                Delete candidate
              </button>
            </div>
          </article>
        ))}
      </div>
    </div>
  )
}
