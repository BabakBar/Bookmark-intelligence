import { describe, expect, test } from 'bun:test'
import { deriveBookmarkMetadata } from './bookmarkSignals'

function metadata(title, url, folders = ['Dev']) {
  const domain = new URL(url).hostname
  return deriveBookmarkMetadata({
    title,
    url,
    domain,
    originalFolders: folders,
    rootFolders: [folders[0]],
  })
}

describe('bookmark signals', () => {
  test('does not classify every HTTPS URL as networking', () => {
    const result = metadata('Python documentation', 'https://docs.python.org/3/')

    expect(result.topics).toContain('python')
    expect(result.topics).not.toContain('networking')
  })

  test('uses boundary-aware topic matching', () => {
    const generic = metadata('Google Cloud guide', 'https://cloud.google.com/docs')
    const networking = metadata(
      'TCP and DNS networking guide',
      'https://example.com/networking',
    )

    expect(generic.topics).not.toContain('go')
    expect(networking.topics).toContain('networking')
  })
})
