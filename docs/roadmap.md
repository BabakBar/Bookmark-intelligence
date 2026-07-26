# Current Roadmap

**Updated:** 2026-07-26

**Current phase:** Phase 0C - Daily Memory Workflow Validation

This roadmap uses evidence gates rather than week-number promises. The original
hosted-product roadmap is preserved at
`archive/2025-10-27-roadmap-v1.md`.

## Gate 1: Data Integrity

- [x] Prevent bookmark detail values from leaking across selection changes.
- [x] Use a sanitized committed browser fixture.
- [x] Make the browser test self-starting and repeatable.
- [x] Validate backup records, references, and safe merge behavior.
- [x] Make imports atomic.
- [x] Restrict imported URLs to credential-free HTTP(S).
- [x] Persist sessions and activity in portable version 3 backups.

**Done when:** repeated imports, edits, backup, restore, and failure paths cannot
silently corrupt retained state.

## Gate 2: Daily Workflow

- [x] Default to All Memory instead of hiding records outside Dev/Cld.
- [x] Add a finite, persisted, explainable daily flight.
- [x] Add review/context/merge/learning collection pulse.
- [x] Add transactional bulk review and one-step undo.
- [x] Fix the over-broad local networking classification.
- [x] Code-split the graph from the initial experience.

**Done when:** the product offers both a small daily practice and a safe
high-volume library workflow. This gate is complete.

## Gate 3: Real-Use Validation

- [ ] Use the workspace for one to two weeks.
- [ ] Measure time to find five known bookmarks.
- [ ] Record useful rediscoveries and review decisions.
- [ ] Verify a fresh browser export re-import preserves retention state.
- [ ] Complete a backup and restore drill.
- [ ] Record repeated capture and connection friction before automating it.

**Done when:** the workspace is trustworthy and materially improves Sia's
bookmark retrieval and review workflow.

## Gate 4: Candidate Inbox and Connections

- [ ] Design an app-owned append-only candidate inbox.
- [ ] Add local review before any external orchestration.
- [ ] Derive relationship evidence from shared retained fields.
- [ ] Do not claim semantic similarity without evaluated embeddings.

**Done when:** capture and connection suggestions remain transparent,
reviewable, private, and reversible.

## Gate 5: Controlled AI Experiment

- [ ] Select approximately 20 manually reviewed bookmarks.
- [ ] Compare local heuristics with proposed AI tags, summaries, and projects.
- [ ] Record model, prompt, data sent, tokens, cost, failures, and corrections.
- [ ] Keep all AI output suggest-only until explicitly accepted.

**Done when:** enrichment demonstrates measurable workflow value at an
understood privacy and cost boundary.

## Gate 6: Architecture Decision

- [ ] Decide from evidence whether multi-device synchronization is needed.
- [ ] If needed, design canonical IDs, conflicts, ownership, backup, and
      migration from IndexedDB.
- [ ] Repair or replace the experimental backend only through a new plan.
- [ ] Do not deploy the existing backend scaffold.

**Done when:** architecture expansion answers a demonstrated need and passes
data-ownership, integration-test, security, and rollback gates.

## Optional Gate 7: OpenClaw Onboarding

- [ ] Complete the existing `openclaw-ops` coder canaries.
- [ ] Obtain separate approval for Bookmark Intelligence repository authority.
- [ ] Run a documentation or test-only worktree canary.
- [ ] Design append-only bookmark candidate capture.
- [ ] Keep private exports, backups, provider keys, and retained notes outside
      OpenClaw workspaces.

**Done when:** OpenClaw can help from the phone without becoming the datastore,
receiving the private collection, or gaining unreviewed mutation authority.

OpenClaw is optional and does not block any prior gate.
