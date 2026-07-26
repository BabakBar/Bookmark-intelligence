# Plan: Memory Desk and Bounded Automation

**Date:** 2026-07-26

**Status:** Phases 1-3 complete; Phase 4 active through local use

**Research:** `../research/2026-07-26-repository-goal-openclaw-integration-review.md`

## Objective

Turn the working local bookmark explorer into trusted personal memory:
dependable data first, then a finite daily workflow, then measured enrichment.
OpenClaw is a future optional control plane and does not gate local product
work.

## Locked Decisions

- IndexedDB is the current source of truth.
- The product defaults to all retained memory, not only Dev/Cld.
- Daily surfacing must be deterministic and explainable from stored evidence.
- User decisions and personal context outrank imported or restored metadata.
- Bulk changes are bounded, transactional, and reversible.
- AI output remains proposal-only.
- Private exports, backups, notes, and activity stay outside Git and OpenClaw.
- The experimental hosted backend is not deployable.

## Phase 1: Editor Integrity and Portable Acceptance

- [x] Bind the editor lifecycle to the selected canonical URL.
- [x] Prove record values do not leak across selection changes or reload.
- [x] Replace the private export test dependency with a synthetic fixture.
- [x] Make Playwright start and stop Vite automatically.
- [x] Add repeatable unit and browser test commands.

**Evidence:** `bun run test:e2e` covers editor isolation. See
`../implementation/2026-07-26-editor-integrity-portable-e2e.md`.

## Phase 2: Import and Backup Integrity

- [x] Limit input files and accept only credential-free HTTP(S) records.
- [x] Commit import history and bookmarks atomically.
- [x] Validate complete backup collections before writes.
- [x] Reject unsupported versions, malformed types, count mismatches,
      duplicates, and dangling references.
- [x] Remap imported provenance IDs.
- [x] Preserve existing local manual fields on overlapping restore.
- [x] Include daily sessions and activity in version 3 backups.
- [x] Keep saved-view naming and backup validation mutually compatible.
- [x] Add hostile-backup and merge-preservation browser coverage.

**Done:** invalid input fails before mutation; retained local decisions win.

## Phase 3: Memory Desk

- [x] Make All Memory the default and retain Dev/Cld as optional scopes.
- [x] Correct over-broad topic matching and version inferred signals.
- [x] Build a daily deck of at most six deterministic, explained cards.
- [x] Persist the exact deck, progress, actions, and completion by date.
- [x] Use the browser's local calendar day for sessions and snooze boundaries.
- [x] Implement Keep, Learning, Later, Archive, and honest app-open tracking.
- [x] Add Collection Pulse for review, context, merge, and learning coverage.
- [x] Add multi-select Keep, Learning, and Archive with atomic failure.
- [x] Add one-step bulk undo that fails closed after a newer record change.
- [x] Code-split the graph view from the default experience.
- [x] Verify desktop and mobile layouts visually.

**Done:** the product has a finite daily practice and a safe high-volume path.

## Phase 4: Real-Use Validation

This phase runs continuously; it is not a manual gate that blocks safe local
improvements.

- [ ] Complete daily flights for at least seven use days.
- [ ] Record deck completion, useful rediscovery, deferral, and archive counts.
- [ ] Measure five known-item retrievals; target four under five seconds.
- [ ] Record false or weak “Why now?” explanations.
- [ ] Perform a real export, clear, and restore drill.
- [ ] Record recurring capture and connection-discovery friction.

**Success:** the workflow reliably surfaces useful records and preserves
decisions; observed friction identifies the next feature.

## Phase 5: Candidate Inbox and Connections

Start only from observed local-use friction.

- [ ] Design an app-owned append-only candidate format.
- [ ] Add local candidate review before any OpenClaw transport.
- [ ] Derive transparent relationship evidence from shared topic, folder,
      domain, and duplicate provenance.
- [ ] Avoid semantic-similarity claims until embeddings are actually evaluated.
- [ ] Keep capture and connection suggestions reversible and reviewable.

## Phase 6: Small AI Gold-Set

- [ ] Select about 20 manually reviewed bookmarks.
- [ ] Compare local signals with proposed summaries, tags, projects, and
      relationship candidates.
- [ ] Record exact provider, model, prompt, data, tokens, cost, latency,
      failures, acceptance, correction, and rejection.
- [ ] Apply nothing without explicit review.

**Gate:** no collection-wide or paid run unless the gold set improves a
measured workflow at an understood privacy and cost boundary.

## Optional OpenClaw Onboarding

OpenClaw is never a prerequisite for Phases 1-6.

- [ ] Complete existing OpenClaw coder canaries.
- [ ] Obtain separate repository authority.
- [ ] Run a documentation or test-only worktree canary.
- [ ] Expose only the app-owned candidate boundary.
- [ ] Keep private collection data and retained notes outside the worktree.

## Deferred Backend Gate

Backend synchronization requires demonstrated multi-device need and a new plan
covering canonical IDs, conflicts, authentication, ownership, migrations,
transactional imports, integration tests, secret isolation, backup, rollback,
and migration from the local source of truth.
