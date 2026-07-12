import { expect, test } from '@playwright/test'
import fs from 'node:fs/promises'
import path from 'node:path'

test('imports the July bookmark export into the Dev/Cld workspace', async ({ page }) => {
  await page.goto('http://127.0.0.1:5173/')
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
    path.resolve('../bookmarks_06_07_2026.html'),
  )

  await expect(page.getByText(/Imported 912 unique bookmarks/)).toBeVisible()
  await expect(page.getByTestId('stat-total')).toHaveText('912')
  await expect(page.getByTestId('stat-dev')).toHaveText('259')
  await expect(page.getByTestId('stat-cld')).toHaveText('281')
  await expect(page.getByTestId('stat-filtered')).toHaveText('540')

  await page.getByTestId('filter-topic').selectOption('aws')
  await expect.poll(async () => Number(await page.getByTestId('stat-filtered').textContent())).toBeGreaterThan(0)
  await expect.poll(async () => Number(await page.getByTestId('stat-filtered').textContent())).toBeLessThan(540)
  await page.getByTestId('filter-topic').selectOption('All topics')

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
  expect(backup.counts.bookmarks).toBe(912)
  expect(backup.counts.savedViews).toBe(1)

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
