const PROVIDER_RULES = [
  ['AWS', ['aws.amazon.com', 'skillbuilder.aws', 'aws.training', 'd1.awsstatic.com']],
  ['Azure', ['learn.microsoft.com', 'portal.azure.com', 'azure.github.io']],
  ['Google Cloud', ['cloud.google.com', 'cloudskillsboost.google']],
  ['GitHub', ['github.com', 'github.blog', 'gist.github.com']],
  ['Reddit', ['reddit.com']],
  ['YouTube', ['youtube.com', 'youtu.be']],
  ['HashiCorp', ['developer.hashicorp.com', 'hashicorp.com']],
  ['Databricks', ['databricks.com', 'customer-academy.databricks.com']],
  ['Cloudflare', ['cloudflare.com']],
  ['OpenAI', ['openai.com', 'platform.openai.com']],
]

export const BOOKMARK_SIGNAL_VERSION = 2

const TOPIC_RULES = [
  ['ai-agents', ['agent', 'agents', 'claude', 'openai', 'llm', 'mcp', 'rag']],
  ['aws', ['aws', 'saa', 'ccp', 'dea', 'cloud practitioner', 'skillbuilder']],
  ['azure', ['azure', 'az-104', 'az104', 'microsoft learn']],
  ['cloud', ['cloud', 'architecture', 'architect', 'sysarch']],
  ['containers', ['docker', 'container', 'containers', 'compose']],
  ['kubernetes', ['kubernetes', 'k8s', 'kubectl', 'helm']],
  ['terraform', ['terraform', 'iac', 'infrastructure as code', 'pulumi']],
  ['networking', ['network', 'networking', 'dns', 'tcp', 'load balancer']],
  ['observability', ['observability', 'monitoring', 'metrics', 'logging', 'prometheus']],
  ['linux', ['linux', 'shell', 'bash', 'terminal', 'systemd']],
  ['python', ['python', 'pydantic', 'fastapi', 'pytest']],
  ['go', ['golang', 'go.dev', ' gopher', 'go ']],
  ['frontend-design', ['frontend', 'design', 'icons', 'figma', 'react', 'css']],
  ['self-hosting', ['self-host', 'homelab', 'nas', 'raspberry', 'adguard']],
  ['devops', ['devops', 'ci/cd', 'cicd', 'github actions', 'pipeline']],
  ['career-interview', ['interview', 'hiring', 'career', 'resume']],
  ['certification', ['certification', 'exam', 'saa-c03', 'az-104', 'ccp']],
]

const CONTENT_TYPE_RULES = [
  ['repository', ['github.com']],
  ['video', ['youtube.com', 'youtu.be', 'vimeo.com']],
  ['discussion', ['reddit.com', 'x.com', 'news.ycombinator.com']],
  ['course', ['udemy.com', 'coursera.org', 'skillbuilder.aws', 'cloudskillsboost.google']],
  ['documentation', ['docs.', 'learn.microsoft.com', 'developer.hashicorp.com', 'kubernetes.io']],
  ['tool', ['app.', 'console.', 'dashboard.', 'portal.']],
]

function normalizedText(bookmark) {
  return [
    bookmark.title,
    bookmark.url,
    bookmark.domain,
    ...(bookmark.originalFolders || []),
  ]
    .join(' ')
    .toLowerCase()
}

function escapePattern(value) {
  return value.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
}

function matchesSignal(text, value) {
  const pattern = new RegExp(`(^|[^a-z0-9])${escapePattern(value)}(?=$|[^a-z0-9])`)
  return pattern.test(text)
}

function matchesAny(text, values) {
  return values.some((value) => matchesSignal(text, value))
}

function providerFor(bookmark) {
  const domain = bookmark.domain || ''
  const text = normalizedText(bookmark)
  const provider = PROVIDER_RULES.find(([name, domains]) => {
    return domains.some((rule) => domain === rule || domain.endsWith(`.${rule}`)) || text.includes(name.toLowerCase())
  })

  if (provider) return provider[0]
  if (domain.includes('.')) return domain.split('.').slice(-2, -1)[0]
  return 'Unknown'
}

function contentTypeFor(bookmark) {
  const domain = bookmark.domain || ''
  const text = normalizedText(bookmark)
  const explicit = CONTENT_TYPE_RULES.find(([, rules]) => {
    return rules.some((rule) => domain.includes(rule) || text.includes(rule))
  })

  if (explicit) return explicit[0]
  if (text.includes('blog')) return 'article'
  if (text.includes('docs') || text.includes('documentation')) return 'documentation'
  return 'reference'
}

function topicsFor(bookmark) {
  const text = normalizedText(bookmark)
  const topics = TOPIC_RULES.filter(([, keywords]) => matchesAny(text, keywords)).map(
    ([topic]) => topic,
  )

  if (bookmark.rootFolders?.includes('Dev')) topics.push('development')
  if (bookmark.rootFolders?.includes('Cld')) topics.push('cloud')

  return [...new Set(topics)].slice(0, 8)
}

function reviewPriorityFor(bookmark, topics, contentType) {
  if ((bookmark.rawInstanceCount || 1) > 1 || (bookmark.sourceUrls?.length || 0) > 1) {
    return 'merge-review'
  }

  if (topics.includes('certification') || topics.includes('career-interview')) {
    return 'time-sensitive'
  }

  if (contentType === 'documentation' || contentType === 'repository') {
    return 'durable-reference'
  }

  return 'normal'
}

export function deriveBookmarkMetadata(bookmark) {
  const topics = topicsFor(bookmark)
  const contentType = contentTypeFor(bookmark)

  return {
    topics,
    provider: providerFor(bookmark),
    contentType,
    reviewPriority: reviewPriorityFor(bookmark, topics, contentType),
    inferredAt: new Date().toISOString(),
    signalVersion: BOOKMARK_SIGNAL_VERSION,
  }
}
