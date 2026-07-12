import { Background, Controls, ReactFlow } from '@xyflow/react'
import '@xyflow/react/dist/style.css'
import { useMemo } from 'react'

function countBy(items, keyFn) {
  const counts = new Map()
  for (const item of items) {
    const key = keyFn(item)
    if (!key) continue
    counts.set(key, (counts.get(key) || 0) + 1)
  }
  return [...counts.entries()].sort((a, b) => b[1] - a[1])
}

function rootFor(bookmark) {
  if (bookmark.rootFolders?.includes('Dev')) return 'Dev'
  if (bookmark.rootFolders?.includes('Cld')) return 'Cld'
  return bookmark.rootFolders?.[0] || 'Root'
}

function primaryFolder(bookmark) {
  const folder = bookmark.originalFolders?.find((path) => path.startsWith(`${rootFor(bookmark)} > `))
  return folder || bookmark.originalFolders?.[0] || 'Root'
}

function shortTitle(title) {
  return title.length > 42 ? `${title.slice(0, 39)}...` : title
}

function makeNode(id, label, position, className = '') {
  return {
    id,
    position,
    data: { label },
    className,
  }
}

export default function BookmarkMap({ bookmarks, onSelect }) {
  const { nodes, edges } = useMemo(() => {
    const nodes = []
    const edges = []
    const topRoots = countBy(bookmarks, rootFor).slice(0, 4)
    const topFolders = countBy(bookmarks, primaryFolder).slice(0, 18)
    const topDomains = countBy(bookmarks, (bookmark) => bookmark.domain).slice(0, 18)
    const showBookmarks = bookmarks.length <= 35

    topRoots.forEach(([root, count], index) => {
      nodes.push(makeNode(`root:${root}`, `${root} (${count})`, { x: 0, y: index * 95 }, 'root-node'))
    })

    topFolders.forEach(([folder, count], index) => {
      const folderId = `folder:${folder}`
      const root = folder.split(' > ')[0]
      nodes.push(
        makeNode(folderId, `${folder} (${count})`, { x: 260, y: index * 74 }, 'folder-node'),
      )
      edges.push({
        id: `edge:root:${root}:${folder}`,
        source: `root:${root}`,
        target: folderId,
        animated: false,
      })
    })

    topDomains.forEach(([domain, count], index) => {
      nodes.push(
        makeNode(`domain:${domain}`, `${domain} (${count})`, { x: 610, y: index * 74 }, 'domain-node'),
      )
    })

    const visibleFolders = new Set(topFolders.map(([folder]) => folder))
    const visibleDomains = new Set(topDomains.map(([domain]) => domain))
    const folderDomainPairs = new Set()

    for (const bookmark of bookmarks) {
      const folder = primaryFolder(bookmark)
      if (!visibleFolders.has(folder) || !visibleDomains.has(bookmark.domain)) continue

      const edgeKey = `${folder}::${bookmark.domain}`
      if (folderDomainPairs.has(edgeKey)) continue

      folderDomainPairs.add(edgeKey)
      edges.push({
        id: `edge:${edgeKey}`,
        source: `folder:${folder}`,
        target: `domain:${bookmark.domain}`,
      })
    }

    if (showBookmarks) {
      bookmarks.slice(0, 35).forEach((bookmark, index) => {
        const bookmarkId = `bookmark:${bookmark.canonicalUrl}`
        nodes.push(
          makeNode(
            bookmarkId,
            shortTitle(bookmark.title),
            { x: 950, y: index * 66 },
            'bookmark-node',
          ),
        )

        if (visibleDomains.has(bookmark.domain)) {
          edges.push({
            id: `edge:domain:${bookmark.domain}:${bookmark.canonicalUrl}`,
            source: `domain:${bookmark.domain}`,
            target: bookmarkId,
          })
        }
      })
    }

    return { nodes, edges }
  }, [bookmarks])

  return (
    <div className="map-panel">
      <div className="map-toolbar">
        <strong>Live Map</strong>
        <span>
          {bookmarks.length <= 35
            ? 'Showing bookmarks because the current filter is focused.'
            : 'Showing top folders and domains. Filter down to reveal bookmark nodes.'}
        </span>
      </div>
      <ReactFlow
        edges={edges}
        fitView
        nodes={nodes}
        nodesDraggable={false}
        onNodeClick={(_, node) => {
          if (node.id.startsWith('bookmark:')) onSelect(node.id.replace('bookmark:', ''))
        }}
      >
        <Background />
        <Controls />
      </ReactFlow>
    </div>
  )
}
