import { useLiveQuery } from 'dexie-react-hooks'
import { useEffect, useMemo, useState } from 'react'
import { buildDailyDeck, collectionPulse } from './dailyBriefing'
import {
  applyDailyAction,
  db,
  getOrCreateDailySession,
  recordBookmarkOpen,
} from './db'

const ACTION_LABELS = {
  keep: 'Keep',
  learning: 'Continue learning',
  archive: 'Archive',
  later: 'Later',
}

function PulseCard({ label, value, note }) {
  return (
    <div className="pulse-card">
      <strong>{value}</strong>
      <span>{label}</span>
      <small>{note}</small>
    </div>
  )
}

function actionSummary(actionCounts = {}) {
  return Object.entries(actionCounts)
    .filter(([, count]) => count > 0)
    .map(([action, count]) => `${count} ${ACTION_LABELS[action].toLowerCase()}`)
    .join(' · ')
}

export default function Briefing({ bookmarks, imports, onInspect }) {
  const dailyDeck = useMemo(() => buildDailyDeck(bookmarks), [bookmarks])
  const session = useLiveQuery(
    async () => (await db.dailySessions.get(dailyDeck.date)) || null,
    [dailyDeck.date],
  )
  const [actionError, setActionError] = useState('')
  const [isActing, setIsActing] = useState(false)
  const pulse = useMemo(() => collectionPulse(bookmarks), [bookmarks])

  useEffect(() => {
    if (session !== null) return

    getOrCreateDailySession(dailyDeck).catch((error) => {
      setActionError(
        error instanceof Error
          ? error.message
          : "Could not prepare today's flight.",
      )
    })
  }, [dailyDeck, session])

  const currentItem = session?.items?.[session.currentIndex]
  const currentBookmark = bookmarks.find(
    (bookmark) => bookmark.canonicalUrl === currentItem?.canonicalUrl,
  )
  const latestImport = imports[0]
  const remaining = Math.max(
    0,
    (session?.items?.length || 0) - (session?.currentIndex || 0),
  )

  async function handleAction(action) {
    if (!currentBookmark || !session) return
    setIsActing(true)
    setActionError('')
    try {
      await applyDailyAction(session.date, currentBookmark.canonicalUrl, action)
    } catch (error) {
      setActionError(error instanceof Error ? error.message : 'Could not save the decision.')
    } finally {
      setIsActing(false)
    }
  }

  return (
    <div className="briefing">
      <header className="briefing-hero">
        <div>
          <div className="briefing-kicker">
            <span>Today</span>
            <span className="local-badge">Local only</span>
          </div>
          <h2>Your memory, ready for today.</h2>
          <p>
            A small, explainable flight through decisions, learning threads, and
            useful material worth seeing again.
          </p>
        </div>
        <div className="briefing-facts">
          <span>{bookmarks.length} retained records</span>
          <span>
            {latestImport
              ? `Last import ${new Date(latestImport.importedAt).toLocaleDateString()}`
              : 'No imports yet'}
          </span>
        </div>
      </header>

      <section className="daily-flight" aria-labelledby="daily-flight-title">
        <div className="flight-progress">
          <div>
            <p className="eyebrow">Daily flight</p>
            <h3 id="daily-flight-title">
              {session?.status === 'completed' ? 'Complete for today' : 'One useful move'}
            </h3>
          </div>
          <span>{remaining} remaining</span>
        </div>

        {!session || session.status === 'active' ? (
          currentBookmark ? (
            <article className="flight-card">
              <div className="flight-card-main">
                <div className="why-now">
                  <span>{currentItem.kind}</span>
                  <strong>Why now?</strong>
                  <p>{currentItem.reason}</p>
                </div>
                <div>
                  <p className="domain-label">{currentBookmark.domain}</p>
                  <h3>{currentBookmark.title}</h3>
                  <p className="flight-folders">
                    {currentBookmark.originalFolders?.slice(0, 2).join(' · ') || 'Root'}
                  </p>
                  <div className="topic-row">
                    {currentBookmark.topics?.slice(0, 4).map((topic) => (
                      <span key={topic}>{topic}</span>
                    ))}
                  </div>
                </div>
              </div>

              <div className="flight-actions">
                <a
                  className="button-link primary-action"
                  href={currentBookmark.url}
                  onClick={() =>
                    recordBookmarkOpen(currentBookmark.canonicalUrl, session?.date)
                  }
                  rel="noreferrer"
                  target="_blank"
                >
                  Open
                </a>
                <button disabled={isActing} onClick={() => handleAction('keep')} type="button">
                  Keep
                </button>
                <button
                  className="secondary-button"
                  disabled={isActing}
                  onClick={() => handleAction('learning')}
                  type="button"
                >
                  Learning
                </button>
                <button
                  className="secondary-button"
                  disabled={isActing}
                  onClick={() => handleAction('later')}
                  type="button"
                >
                  Later
                </button>
                <button
                  className="quiet-button"
                  onClick={() => onInspect(currentBookmark.canonicalUrl)}
                  type="button"
                >
                  Inspect
                </button>
                <button
                  className="quiet-button danger-text"
                  disabled={isActing}
                  onClick={() => handleAction('archive')}
                  type="button"
                >
                  Archive
                </button>
              </div>
            </article>
          ) : (
            <div className="flight-empty">
              <h3>Preparing today's flight…</h3>
            </div>
          )
        ) : (
          <div className="flight-complete">
            <span aria-hidden="true">✓</span>
            <div>
              <h3>Done for today.</h3>
              <p>
                {actionSummary(session.actionCounts) ||
                  'Your library has no pending cards for this flight.'}
              </p>
            </div>
          </div>
        )}

        {actionError && (
          <p className="inline-error" role="alert">
            {actionError}
          </p>
        )}
      </section>

      <section className="pulse-section" aria-labelledby="pulse-title">
        <div className="section-heading">
          <div>
            <p className="eyebrow">Collection pulse</p>
            <h3 id="pulse-title">Trust, not vanity metrics</h3>
          </div>
        </div>
        <div className="pulse-grid">
          <PulseCard
            label="Reviewed"
            note="retained records with a decision"
            value={`${pulse.reviewCoverage}%`}
          />
          <PulseCard
            label="With context"
            note="note, keep reason, or personal tag"
            value={`${pulse.contextCoverage}%`}
          />
          <PulseCard
            label="Merge risks"
            note="duplicate or multi-folder evidence"
            value={pulse.mergeRisks}
          />
          <PulseCard
            label="Learning threads"
            note="explicitly marked for continuation"
            value={pulse.learning}
          />
        </div>
      </section>
    </div>
  )
}
