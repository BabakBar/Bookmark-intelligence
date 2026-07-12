# BookmarkAI

AI-powered bookmark manager with context-aware search and automatic organization.

## Goal

Transform bookmarks from static lists into an intelligent knowledge base:
- Semantic search across bookmark content
- Automatic tagging and categorization
- AI-generated summaries
- Project-based clustering

## Tech Stack

Python 3.13 + FastAPI | PostgreSQL 17 + Qdrant + Valkey | OpenAI + Claude | Self-hosted

## Current Implemented Workspace

The active Phase 0 UI is a local-first Dev/Cld bookmark workspace in `frontend/`.

- Import browser bookmark HTML directly in the browser
- Retain canonical bookmark records in IndexedDB
- Preserve review state, status, notes, and keep reasons across imports
- Explore large `Dev` and `Cld` folders with filters, a sortable table, and a live mind map
- Review duplicate/canonical URL merges and export/restore local review state as JSON
- Triage with local topic/provider/content inference and a prioritized review queue
- Add personal user tags and save recurring filter views

See `docs/dev/implementation/2026-07-06-devcld-local-workspace.md` and `docs/run.md`.
