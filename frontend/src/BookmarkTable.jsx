import {
  flexRender,
  getCoreRowModel,
  getSortedRowModel,
  useReactTable,
} from '@tanstack/react-table'
import { useMemo, useState } from 'react'

function formatDate(value) {
  if (!value) return 'Unknown'
  return new Intl.DateTimeFormat(undefined, {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  }).format(new Date(value))
}

export default function BookmarkTable({
  bookmarks,
  selectedUrl,
  selectedUrls,
  onSelect,
  onToggleAll,
  onToggleSelection,
}) {
  const [sorting, setSorting] = useState([{ id: 'lastSeenAt', desc: true }])
  const allSelected =
    bookmarks.length > 0 &&
    bookmarks.every((bookmark) => selectedUrls.has(bookmark.canonicalUrl))
  const columns = useMemo(
    () => [
      {
        id: 'select',
        header: () => (
          <input
            aria-label="Select all filtered bookmarks"
            checked={allSelected}
            onChange={(event) => onToggleAll(event.target.checked)}
            type="checkbox"
          />
        ),
        cell: ({ row }) => (
          <input
            aria-label={`Select ${row.original.title}`}
            checked={selectedUrls.has(row.original.canonicalUrl)}
            onChange={() => onToggleSelection(row.original.canonicalUrl)}
            type="checkbox"
          />
        ),
        enableSorting: false,
      },
      {
        accessorKey: 'title',
        header: 'Bookmark',
        cell: ({ row, getValue }) => (
          <button
            className={`link-button ${selectedUrl === row.original.canonicalUrl ? 'is-selected' : ''}`}
            onClick={() => onSelect(row.original.canonicalUrl)}
            type="button"
          >
            {getValue()}
          </button>
        ),
      },
      {
        accessorKey: 'domain',
        header: 'Domain',
      },
      {
        accessorKey: 'provider',
        header: 'Provider',
      },
      {
        accessorKey: 'contentType',
        header: 'Type',
      },
      {
        id: 'topics',
        header: 'Topics',
        accessorFn: (bookmark) => bookmark.topics?.slice(0, 3).join(', ') || '',
      },
      {
        id: 'userTags',
        header: 'User Tags',
        accessorFn: (bookmark) => bookmark.userTags?.slice(0, 3).join(', ') || '',
      },
      {
        id: 'folder',
        header: 'Folder',
        accessorFn: (bookmark) => bookmark.originalFolders?.[0] || 'Root',
      },
      {
        accessorKey: 'reviewState',
        header: 'Review',
      },
      {
        accessorKey: 'status',
        header: 'Status',
      },
      {
        accessorKey: 'lastSeenAt',
        header: 'Last Seen',
        cell: ({ getValue }) => formatDate(getValue()),
      },
    ],
    [
      allSelected,
      onSelect,
      onToggleAll,
      onToggleSelection,
      selectedUrl,
      selectedUrls,
    ],
  )

  const table = useReactTable({
    data: bookmarks,
    columns,
    state: { sorting },
    onSortingChange: setSorting,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
  })

  return (
    <div className="table-wrap">
      <table>
        <thead>
          {table.getHeaderGroups().map((headerGroup) => (
            <tr key={headerGroup.id}>
              {headerGroup.headers.map((header) => (
                <th key={header.id}>
                  {header.column.getCanSort() ? (
                    <button
                      className="table-heading"
                      onClick={header.column.getToggleSortingHandler()}
                      type="button"
                    >
                      {flexRender(
                        header.column.columnDef.header,
                        header.getContext(),
                      )}
                      <span>
                        {header.column.getIsSorted() === 'asc' ? ' up' : ''}
                      </span>
                      <span>
                        {header.column.getIsSorted() === 'desc' ? ' down' : ''}
                      </span>
                    </button>
                  ) : (
                    <div className="table-heading table-heading-static">
                      {flexRender(
                        header.column.columnDef.header,
                        header.getContext(),
                      )}
                    </div>
                  )}
                </th>
              ))}
            </tr>
          ))}
        </thead>
        <tbody>
          {table.getRowModel().rows.map((row) => (
            <tr
              className={selectedUrl === row.original.canonicalUrl ? 'selected-row' : ''}
              key={row.id}
            >
              {row.getVisibleCells().map((cell) => (
                <td key={cell.id}>{flexRender(cell.column.columnDef.cell, cell.getContext())}</td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
