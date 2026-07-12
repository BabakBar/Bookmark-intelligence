import { db } from './db'
import { deriveBookmarkMetadata } from './bookmarkSignals'

const TRACKING_PARAMS = new Set([
  'fbclid',
  'gclid',
  'igshid',
  'mc_cid',
  'mc_eid',
  'ref',
  'spm',
])

function isElement(node, tagName) {
  return node?.nodeType === Node.ELEMENT_NODE && node.tagName.toLowerCase() === tagName
}

function directChild(element, tagName) {
  return Array.from(element.children).find((child) => child.tagName.toLowerCase() === tagName)
}

function normalizeFolderPath(path) {
  const clean = path.map((part) => part.trim()).filter(Boolean)
  return clean[0] === 'Bookmarks bar' ? clean.slice(1) : clean
}

function rootFolders(folderPath) {
  const root = folderPath[0]
  return root ? [root] : ['Root']
}

function normalizeDomain(hostname) {
  const lower = hostname.toLowerCase()
  return lower.startsWith('www.') ? lower.slice(4) : lower
}

export function canonicalizeUrl(rawUrl) {
  try {
    const url = new URL(rawUrl)
    url.hash = ''
    url.hostname = normalizeDomain(url.hostname)

    for (const key of [...url.searchParams.keys()]) {
      if (key.startsWith('utm_') || TRACKING_PARAMS.has(key)) {
        url.searchParams.delete(key)
      }
    }

    url.searchParams.sort()

    if (url.pathname.length > 1 && url.pathname.endsWith('/')) {
      url.pathname = url.pathname.slice(0, -1)
    }

    return url.toString()
  } catch {
    return rawUrl.trim()
  }
}

function bookmarkFromAnchor(anchor, folderPath) {
  const url = anchor.getAttribute('href')?.trim()
  if (!url || url.startsWith('file://')) return null

  let parsedUrl
  try {
    parsedUrl = new URL(url)
  } catch {
    return null
  }

  const addDate = anchor.getAttribute('add_date')
  const addedAt = addDate ? new Date(Number(addDate) * 1000).toISOString() : null
  const normalizedPath = normalizeFolderPath(folderPath)
  const folderLabel = normalizedPath.length ? normalizedPath.join(' > ') : 'Root'
  const title = anchor.textContent?.trim() || parsedUrl.hostname

  const bookmark = {
    canonicalUrl: canonicalizeUrl(url),
    url,
    title,
    titleLower: title.toLowerCase(),
    domain: normalizeDomain(parsedUrl.hostname),
    addedAt,
    sourceUrls: [url],
    rawInstanceCount: 1,
    originalFolders: [folderLabel],
    folderPaths: [normalizedPath],
    rootFolders: rootFolders(normalizedPath),
  }

  return {
    ...bookmark,
    ...deriveBookmarkMetadata(bookmark),
  }
}

function nestedListFor(folderElement) {
  const childList = directChild(folderElement, 'dl')
  if (childList) return childList

  let sibling = folderElement.nextElementSibling
  while (sibling) {
    if (sibling.tagName.toLowerCase() === 'dl') return sibling
    if (sibling.tagName.toLowerCase() === 'dt') return null
    sibling = sibling.nextElementSibling
  }

  return null
}

function parseList(listElement, folderPath, bookmarks) {
  for (const child of listElement.children) {
    if (isElement(child, 'p')) {
      parseList(child, folderPath, bookmarks)
      continue
    }

    if (!isElement(child, 'dt')) continue

    const folderHeading = directChild(child, 'h3')
    if (folderHeading) {
      const nextPath = [...folderPath, folderHeading.textContent?.trim() || 'Untitled']
      const nestedList = nestedListFor(child)
      if (nestedList) parseList(nestedList, nextPath, bookmarks)
      continue
    }

    const anchor = directChild(child, 'a')
    if (!anchor) continue

    const bookmark = bookmarkFromAnchor(anchor, folderPath)
    if (bookmark) bookmarks.push(bookmark)
  }
}

export function parseBookmarkHtml(html) {
  const document = new DOMParser().parseFromString(html, 'text/html')
  const rootList = document.querySelector('dl')
  if (!rootList) throw new Error('No bookmark list found in the HTML file.')

  const bookmarks = []
  parseList(rootList, [], bookmarks)
  return bookmarks
}

function mergeUnique(values) {
  return [...new Set(values.filter(Boolean))]
}

function mergeFolderPaths(existingPaths = [], incomingPaths = []) {
  const keyed = new Map()

  for (const path of [...existingPaths, ...incomingPaths]) {
    const key = path.join(' > ') || 'Root'
    keyed.set(key, path)
  }

  return [...keyed.values()]
}

export async function importBookmarkFile(file) {
  const html = await file.text()
  const parsedBookmarks = parseBookmarkHtml(html)
  const importedAt = new Date().toISOString()
  const uniqueByUrl = new Map()

  for (const bookmark of parsedBookmarks) {
    const existing = uniqueByUrl.get(bookmark.canonicalUrl)
    if (!existing) {
      uniqueByUrl.set(bookmark.canonicalUrl, bookmark)
      continue
    }

    existing.originalFolders = mergeUnique([...existing.originalFolders, ...bookmark.originalFolders])
    existing.folderPaths = mergeFolderPaths(existing.folderPaths, bookmark.folderPaths)
    existing.rootFolders = mergeUnique([...existing.rootFolders, ...bookmark.rootFolders])
    existing.sourceUrls = mergeUnique([...existing.sourceUrls, ...bookmark.sourceUrls])
    existing.rawInstanceCount += bookmark.rawInstanceCount
  }

  const bookmarks = [...uniqueByUrl.values()]
  const importId = await db.imports.add({
    fileName: file.name,
    importedAt,
    totalCount: bookmarks.length,
    devCount: bookmarks.filter((bookmark) => bookmark.rootFolders.includes('Dev')).length,
    cldCount: bookmarks.filter((bookmark) => bookmark.rootFolders.includes('Cld')).length,
  })

  await db.transaction('rw', db.bookmarks, async () => {
    for (const bookmark of bookmarks) {
      const existing = await db.bookmarks.get(bookmark.canonicalUrl)

      if (!existing) {
        await db.bookmarks.add({
          ...bookmark,
          firstSeenAt: importedAt,
          lastSeenAt: importedAt,
          importIds: [importId],
          status: 'active',
          reviewState: 'unreviewed',
          userTags: [],
          userNote: '',
          keepReason: '',
          createdAt: importedAt,
          updatedAt: importedAt,
        })
        continue
      }

      await db.bookmarks.put({
        ...existing,
        url: bookmark.url,
        title: bookmark.title || existing.title,
        titleLower: (bookmark.title || existing.title).toLowerCase(),
        domain: bookmark.domain || existing.domain,
        addedAt: existing.addedAt || bookmark.addedAt,
        originalFolders: mergeUnique([...existing.originalFolders, ...bookmark.originalFolders]),
        folderPaths: mergeFolderPaths(existing.folderPaths, bookmark.folderPaths),
        rootFolders: mergeUnique([...existing.rootFolders, ...bookmark.rootFolders]),
        sourceUrls: mergeUnique([...(existing.sourceUrls || [existing.url]), ...bookmark.sourceUrls]),
        rawInstanceCount: Math.max(
          existing.rawInstanceCount || 1,
          bookmark.rawInstanceCount || 1,
        ),
        ...deriveBookmarkMetadata({
          ...existing,
          ...bookmark,
          originalFolders: mergeUnique([...existing.originalFolders, ...bookmark.originalFolders]),
          rootFolders: mergeUnique([...existing.rootFolders, ...bookmark.rootFolders]),
        }),
        importIds: mergeUnique([...(existing.importIds || []), importId]),
        lastSeenAt: importedAt,
        updatedAt: importedAt,
      })
    }
  })

  return {
    importId,
    importedAt,
    parsedCount: parsedBookmarks.length,
    uniqueCount: bookmarks.length,
    devCount: bookmarks.filter((bookmark) => bookmark.rootFolders.includes('Dev')).length,
    cldCount: bookmarks.filter((bookmark) => bookmark.rootFolders.includes('Cld')).length,
  }
}
