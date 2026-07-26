import { expect, test } from '@playwright/test'
import { Buffer } from 'node:buffer'
import fs from 'node:fs/promises'
import path from 'node:path'

async function importFixture(page) {
  await page.goto('/')
  await page.evaluate(async () => {
    await new Promise((resolve, reject) => {
      const request = indexedDB.deleteDatabase('BookmarkIntelligence')
      request.onsuccess = resolve
      request.onerror = reject
      request.onblocked = resolve
    })
  })
  await page.reload()

  await page.getByLabel('Import bookmark HTML').setInputFiles(
    path.resolve('e2e/fixtures/devcld-bookmarks.html'),
  )
}

test('imports the sanitized fixture into All Memory', async ({ page }) => {
  await importFixture(page)

  await expect(page.getByText(/Imported 5 unique bookmarks/)).toBeVisible()
  await expect(page.getByTestId('stat-total')).toHaveText('5')
  await expect(page.getByTestId('stat-dev')).toHaveText('3')
  await expect(page.getByTestId('stat-cld')).toHaveText('2')
  await expect(page.getByTestId('stat-filtered')).toHaveText('5')

  await page.getByRole('button', { name: 'Library', exact: true }).click()
  await page.getByTestId('filter-root-scope').selectOption('Dev + Cld')
  await expect(page.getByTestId('stat-filtered')).toHaveText('4')
  await page.getByTestId('filter-root-scope').selectOption('All Memory')
  await page.getByTestId('filter-topic').selectOption('aws')
  await expect(page.getByTestId('stat-filtered')).toHaveText('1')
  await page.getByTestId('filter-topic').selectOption('All topics')

  await page.getByRole('button', { name: 'AWS Documentation' }).click()
  await page.getByPlaceholder('Comma-separated: aws-cert, project-x...').fill('aws-cert, cleanup')
  await page.getByText('Keep reason').click()
  await page.getByTestId('filter-user-tag').selectOption('aws-cert')
  await expect.poll(async () => Number(await page.getByTestId('stat-filtered').textContent())).toBe(1)

  await page.getByPlaceholder('AWS cert cleanup').fill('AWS cert cleanup')
  await page.getByRole('button', { name: 'Save current view' }).click()
  await expect(page.getByText('Saved view "AWS cert cleanup".')).toBeVisible()
  await expect(page.getByRole('button', { name: 'AWS cert cleanup' })).toBeVisible()

  const downloadPromise = page.waitForEvent('download')
  await page.getByRole('button', { name: 'Export backup' }).click()
  const download = await downloadPromise
  const backupPath = await download.path()
  const backup = JSON.parse(await fs.readFile(backupPath, 'utf8'))

  expect(download.suggestedFilename()).toMatch(/^bookmark-intelligence-workspace-\d{4}-\d{2}-\d{2}\.json$/)
  expect(backup.schema).toBe('bookmark-intelligence-workspace')
  expect(backup.version).toBe(3)
  expect(backup.counts.bookmarks).toBe(5)
  expect(backup.counts.savedViews).toBe(1)
  expect(backup.counts.dailySessions).toBe(1)

  await page.getByTestId('filter-user-tag').selectOption('All user tags')
  await page.getByRole('button', { name: 'Mind Map', exact: true }).click()
  await expect(page.getByText('Live Map')).toBeVisible()
  await expect(page.locator('.react-flow__node')).not.toHaveCount(0)

  await page.getByRole('button', { name: 'Duplicates' }).click()
  await expect(page.getByRole('heading', { name: 'Duplicate Review' })).toBeVisible()
  await expect(page.locator('.duplicate-card').first()).toBeVisible()

  await page.getByRole('button', { name: 'Review Queue', exact: true }).click()
  await expect(page.getByRole('heading', { name: 'Review Queue' })).toBeVisible()
  await expect(page.locator('.queue-card').first()).toBeVisible()
})

test('keeps detail drafts attached to the selected bookmark', async ({ page }) => {
  await importFixture(page)

  await page.getByRole('button', { name: 'Library', exact: true }).click()
  await page.getByRole('button', { name: 'OpenClaw Repository' }).click()
  await page.getByLabel('User tags', { exact: true }).fill('openclaw, agent')
  await page.getByLabel('Keep reason').fill('Reference for the agent control plane')
  await page.getByLabel('Notes').fill('Review after the guarded coder canary')

  await page.getByRole('button', { name: 'AWS Documentation' }).click()

  await expect(page.getByLabel('User tags', { exact: true })).toHaveValue('')
  await expect(page.getByLabel('Keep reason')).toHaveValue('')
  await expect(page.getByLabel('Notes')).toHaveValue('')

  await page.getByLabel('Notes').fill('AWS record only')
  await page.getByRole('button', { name: 'OpenClaw Repository' }).click()

  await expect(page.getByLabel('User tags', { exact: true })).toHaveValue('agent, openclaw')
  await expect(page.getByLabel('Keep reason')).toHaveValue(
    'Reference for the agent control plane',
  )
  await expect(page.getByLabel('Notes')).toHaveValue(
    'Review after the guarded coder canary',
  )

  await page.reload()
  await page.getByRole('button', { name: 'Library', exact: true }).click()
  await page.getByRole('button', { name: 'AWS Documentation' }).click()
  await expect(page.getByLabel('Notes')).toHaveValue('AWS record only')
})

test('rejects unsafe backups and preserves newer local review state', async ({ page }) => {
  await importFixture(page)

  await page.getByRole('button', { name: 'Library', exact: true }).click()
  await page.getByRole('button', { name: 'OpenClaw Repository' }).click()
  await page.getByLabel('Notes').fill('Local state is newer')
  await page.getByText('Keep reason').click()

  const unsafeBackup = {
    schema: 'bookmark-intelligence-workspace',
    version: 2,
    exportedAt: '2026-07-26T00:00:00.000Z',
    counts: { bookmarks: 1, imports: 0, savedViews: 0 },
    bookmarks: [
      {
        canonicalUrl: 'javascript:alert(1)',
        url: 'javascript:alert(1)',
        title: 'Unsafe record',
      },
    ],
    imports: [],
    savedViews: [],
  }

  await page.getByLabel('Restore backup').setInputFiles({
    name: 'unsafe-backup.json',
    mimeType: 'application/json',
    buffer: Buffer.from(JSON.stringify(unsafeBackup)),
  })

  await expect(page.getByText(/unsupported bookmark URL/)).toBeVisible()
  await expect(page.getByTestId('stat-total')).toHaveText('5')
  await expect(page.getByLabel('Notes')).toHaveValue('Local state is newer')

  const olderBackup = {
    schema: 'bookmark-intelligence-workspace',
    version: 2,
    exportedAt: '2026-07-26T00:00:00.000Z',
    counts: { bookmarks: 1, imports: 0, savedViews: 0 },
    bookmarks: [
      {
        canonicalUrl: 'https://github.com/openclaw/openclaw',
        url: 'https://github.com/openclaw/openclaw',
        title: 'OpenClaw Repository',
        userNote: 'Stale backup state',
        updatedAt: '2025-01-01T00:00:00.000Z',
      },
    ],
    imports: [],
    savedViews: [],
  }

  await page.getByLabel('Restore backup').setInputFiles({
    name: 'older-backup.json',
    mimeType: 'application/json',
    buffer: Buffer.from(JSON.stringify(olderBackup)),
  })

  await expect(page.getByText(/Restored 1 retained records/)).toBeVisible()
  await page.getByRole('button', { name: 'AWS Documentation' }).click()
  await page.getByRole('button', { name: 'OpenClaw Repository' }).click()
  await expect(page.getByLabel('Notes')).toHaveValue('Local state is newer')
})

test('persists a finite daily flight across reloads', async ({ page }) => {
  await importFixture(page)

  await expect(page.getByRole('heading', { name: 'Your memory, ready for today.' })).toBeVisible()
  await expect(page.getByText('Why now?')).toBeVisible()
  await expect(page.locator('.flight-progress > span')).toHaveText('5 remaining')

  await page.getByRole('button', { name: 'Keep', exact: true }).click()
  await expect(page.locator('.flight-progress > span')).toHaveText('4 remaining')

  await page.reload()
  await expect(page.locator('.flight-progress > span')).toHaveText('4 remaining')

  for (let remaining = 3; remaining >= 0; remaining -= 1) {
    await page.getByRole('button', { name: 'Keep', exact: true }).click()
    await expect(page.locator('.flight-progress > span')).toHaveText(
      `${remaining} remaining`,
    )
  }

  await expect(page.getByRole('heading', { name: 'Done for today.' })).toBeVisible()
  await page.reload()
  await expect(page.getByRole('heading', { name: 'Done for today.' })).toBeVisible()
})

test('bulk review is transactional and reversible', async ({ page }) => {
  await importFixture(page)
  await page.getByRole('button', { name: 'Library', exact: true }).click()

  await page.getByLabel('Select OpenClaw Repository').check()
  await page.getByLabel('Select AWS Documentation').check()
  await expect(page.getByText('2 selected')).toBeVisible()

  await page.getByRole('button', { name: 'Mark keep' }).click()
  await expect(page.getByTestId('stat-review')).toHaveText('3')
  await expect(page.getByText('2 bookmarks updated to keep.')).toBeVisible()

  await page.getByRole('button', { name: 'Undo', exact: true }).click()
  await expect(page.getByTestId('stat-review')).toHaveText('5')
  await expect(page.getByText(/Restored 2 bookmarks/)).toBeVisible()
})

test('bulk undo stops when a reviewed bookmark changed afterward', async ({ page }) => {
  await importFixture(page)
  await page.getByRole('button', { name: 'Library', exact: true }).click()

  await page.getByLabel('Select OpenClaw Repository').check()
  await page.getByRole('button', { name: 'Mark keep' }).click()
  await page.getByRole('button', { name: 'OpenClaw Repository' }).click()
  await page.getByLabel('Notes').fill('A newer note must survive undo')
  await page.getByText('Keep reason').click()
  await expect
    .poll(async () =>
      page.evaluate(async () => {
        const database = await new Promise((resolve, reject) => {
          const request = indexedDB.open('BookmarkIntelligence')
          request.onsuccess = () => resolve(request.result)
          request.onerror = () => reject(request.error)
        })
        return new Promise((resolve, reject) => {
          const transaction = database.transaction('bookmarks', 'readonly')
          const request = transaction
            .objectStore('bookmarks')
            .get('https://github.com/openclaw/openclaw')
          request.onsuccess = () => resolve(request.result?.userNote)
          request.onerror = () => reject(request.error)
        })
      }),
    )
    .toBe('A newer note must survive undo')

  await page.getByRole('button', { name: 'Undo', exact: true }).click()
  await expect(page.getByText(/changed after the bulk action/)).toBeVisible()
  await expect(page.getByLabel('Notes')).toHaveValue('A newer note must survive undo')
  await expect(page.getByTestId('stat-review')).toHaveText('4')
})

test('saved view names are unique regardless of letter case', async ({ page }) => {
  await importFixture(page)
  await page.getByRole('button', { name: 'Library', exact: true }).click()

  await page.getByPlaceholder('AWS cert cleanup').fill('AWS')
  await page.getByRole('button', { name: 'Save current view' }).click()
  await page.getByTestId('filter-topic').selectOption('aws')
  await page.getByPlaceholder('AWS cert cleanup').fill('aws')
  await page.getByRole('button', { name: 'Save current view' }).click()

  await expect(page.getByRole('button', { name: 'AWS', exact: true })).toHaveCount(1)
  await expect(page.getByRole('button', { name: 'aws', exact: true })).toHaveCount(0)

  const downloadPromise = page.waitForEvent('download')
  await page.getByRole('button', { name: 'Export backup' }).click()
  const download = await downloadPromise
  const backupPath = await download.path()
  const backup = JSON.parse(await fs.readFile(backupPath, 'utf8'))
  expect(backup.savedViews).toHaveLength(1)
})
