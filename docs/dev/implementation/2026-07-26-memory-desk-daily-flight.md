# Implementation: Memory Desk Daily Flight

**Date:** 2026-07-26

**Plan phases:** 2 and 3

**Status:** Implemented and verified

## Outcome

The former Dev/Cld explorer is now a broader personal Memory Desk. The product
opens on a finite daily briefing over all retained records while preserving
the full Library, Mind Map, Duplicates, and Review Queue tools.

## Dataset Evidence

The private July export contains 936 raw instances and 912 canonical records.
Only 540 are in Dev or Cld, so the prior default hid 372 retained records. The
default scope is now All Memory.

The collection is also highly distributed: hundreds of domains occur only
once, most records are older than six months, and duplicate evidence is
meaningful but limited. This favored a small deterministic daily deck over a
dense dashboard or unsupported semantic claims.

## Daily Flight Contract

- Maximum six records per date.
- Stable order for the same date and retained dataset.
- Archived, delete-candidate, and currently snoozed records are excluded.
- Lanes prioritize time-sensitive decisions, merge evidence, learning,
  missing context, rediscovery, and remaining unreviewed records.
- Every reason is generated from fields the application actually retains.
- The exact deck is stored; later metadata changes cannot reshuffle a flight
  in progress.
- Keep, Learning, Later, and Archive advance one card transactionally.
- Later snoozes for three days.
- App-mediated opens update local `lastOpenedAt`, `openCount`, and activity.

## High-Volume Review

The Library supports explicit row selection and select-all for the current
filtered result. Keep, Learning, and Archive are a closed action set. A
transaction verifies all selected records, updates at most 1,000, and aborts
if any record disappeared. The last bulk action retains an in-memory snapshot
for one-step undo until reload or the next bulk action. Undo verifies that no
affected record changed after the bulk update and aborts on a conflict.

## Backup Version 3

The portable workspace now includes:

- bookmarks;
- import history;
- saved views;
- daily sessions;
- activity events;
- metadata.

Validation occurs before the restore transaction and covers collection sizes,
field types, enums, timestamps, supported URLs, credentials, unique keys,
declared counts, import provenance, session progress, and activity references.
Existing local manual fields win when an overlapping backup is merged.

## Taxonomy Repair

Signal version 2 removes `http` as a networking keyword and uses
boundary-aware topic matching. This fixes the prior defect where almost every
HTTPS URL was marked networking and prevents short signals such as `go` from
matching unrelated words.

## Performance and Design

React Flow is loaded only when Mind Map opens. The production build now emits
a 401.82 kB initial JavaScript chunk and a separate 180.02 kB map chunk rather
than one warning-producing bundle.

The visual system uses a warm local-workspace canvas, a deep-ink daily flight,
cobalt actions, generous information hierarchy, keyboard focus treatment, and
a two-column mobile action/pulse layout. Desktop and 390 px mobile screenshots
were inspected with the synthetic imported fixture.

## Verification

```text
bun run test:unit   7 passed
bun run lint        passed
bun run build       passed
bun run test:e2e    7 passed
```

The browser suite covers all-memory visibility, editor isolation, hostile
restore rejection, local merge preservation, persisted daily completion, and
reversible bulk review.
