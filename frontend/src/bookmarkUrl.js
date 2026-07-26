const TRACKING_PARAMS = new Set([
  'fbclid',
  'gclid',
  'igshid',
  'mc_cid',
  'mc_eid',
  'ref',
  'spm',
])

export function isSupportedBookmarkUrl(rawUrl) {
  try {
    const url = new URL(rawUrl)
    const supportedProtocol = url.protocol === 'http:' || url.protocol === 'https:'
    return supportedProtocol && !url.username && !url.password
  } catch {
    return false
  }
}

export function canonicalizeUrl(rawUrl) {
  if (!isSupportedBookmarkUrl(rawUrl)) return null

  const url = new URL(rawUrl)
  url.hash = ''
  url.hostname = url.hostname.toLowerCase().replace(/^www\./, '')

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
}
