# Feature Specification: BookmarkAI MVP Foundation

**Feature Branch**: `001-mvp-foundation`
**Created**: October 27, 2025
**Status**: Draft
**Input**: User description: "based on phase 1 and the md files in the @docs/ folder"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Save and Auto-Tag Bookmarks (Priority: P1)

A developer is reading a Kubernetes tutorial and wants to save it for later. They click the browser extension icon, click "Save bookmark", and the system automatically generates semantic tags like #kubernetes, #containers, #orchestration without requiring manual categorization. The bookmark is saved with a 2-3 sentence AI-generated summary.

**Why this priority**: This is the core value proposition - eliminating manual bookmark organization. Without this, users fall back to native browser bookmarks. This must work for the product to have any value.

**Independent Test**: Can be fully tested by installing the extension, saving a bookmark, and verifying that AI-generated tags and summary appear within 3 seconds. Delivers immediate value by reducing manual tagging work.

**Acceptance Scenarios**:

1. **Given** a user is browsing a technical article, **When** they click "Save bookmark" in the extension, **Then** the system captures the URL, title, and page context
2. **Given** the bookmark capture is complete, **When** the backend processes the content, **Then** AI generates 3-7 semantic tags and a 2-3 sentence summary within 3 seconds
3. **Given** the AI processing completes, **When** the user views the saved bookmark, **Then** they see the auto-generated tags and summary displayed in the extension popup
4. **Given** a bookmark has auto-generated tags, **When** the user disagrees with a tag, **Then** they can manually edit or remove tags

---

### User Story 2 - Discover Similar Bookmarks on Save (Priority: P1)

A cloud engineer is about to save a Docker tutorial but has already saved 3 similar Docker resources months ago that they forgot about. When saving the new bookmark, the sidebar automatically shows "You have 3 similar bookmarks" with titles, tags, and relevance scores. This prevents duplicate saves and helps rediscover forgotten resources.

**Why this priority**: This addresses the "bookmark graveyard" problem - the primary pain point. Without this, the product is just another bookmark manager. This feature differentiates the product from competitors.

**Independent Test**: Can be tested by saving 5 Docker bookmarks, waiting for embeddings to generate, then saving a 6th Docker-related page. The sidebar should display the 5 similar bookmarks with relevance scores. Delivers immediate discovery value.

**Acceptance Scenarios**:

1. **Given** a user has saved 5 Docker-related bookmarks, **When** they save a new Docker tutorial, **Then** the system generates an embedding and performs vector similarity search within 2 seconds
2. **Given** similar bookmarks are found (>70% similarity), **When** the sidebar refreshes, **Then** it displays up to 5 similar bookmarks with titles, tags, and relevance percentages
3. **Given** the sidebar shows similar bookmarks, **When** the user clicks on a suggested bookmark, **Then** the browser navigates to that URL
4. **Given** a user is browsing a page without saving, **When** they click "Show Related Bookmarks" in the extension popup, **Then** the system performs the same similarity search for the current page
5. **Given** a user has saved a completely unique bookmark (first bookmark or unrelated topic), **When** the similarity search runs, **Then** the sidebar displays "No similar bookmarks found yet"

---

### User Story 3 - Filter Bookmarks by Project Context (Priority: P1)

A software consultant works on multiple client projects simultaneously (FabrikTakt, PersonalSite, German Learning). When working on FabrikTakt, they activate that project in the extension, and only FabrikTakt-related bookmarks appear in searches and suggestions. This eliminates noise from unrelated bookmarks and provides focused context.

**Why this priority**: Context-switching overhead is the second major pain point. Without project mode, users see all 500+ bookmarks mixed together, making the system overwhelming. This is critical for the target user (developers managing multiple projects).

**Independent Test**: Can be tested by creating two projects (e.g., "ProjectA", "ProjectB"), manually adding 3 bookmarks to each, then switching between active projects and verifying that only project-specific bookmarks appear in the sidebar and search results. Delivers immediate organization value.

**Acceptance Scenarios**:

1. **Given** a user has no projects, **When** they create a new project named "FabrikTakt" with description "Client project for factory automation", **Then** the system creates the project and stores it in the database
2. **Given** a project exists, **When** the user adds 5 bookmarks to it manually, **Then** the project's context embedding is calculated as the average of all bookmark embeddings
3. **Given** a user saves a new bookmark about Grafana dashboards, **When** the system compares the bookmark embedding to all project embeddings, **Then** it suggests "FabrikTakt" project with 87% confidence (if FabrikTakt contains similar monitoring content)
4. **Given** a project suggestion appears, **When** the user confirms the suggestion, **Then** the bookmark is added to the project and the project embedding is recalculated
5. **Given** a user has 3 active projects, **When** they activate "FabrikTakt" project, **Then** the extension icon badge shows "FT" and sidebar filters show only FabrikTakt bookmarks
6. **Given** a project is active, **When** the user performs a context-aware search, **Then** results are filtered to only include bookmarks from the active project
7. **Given** a project has not been accessed for 30 days, **When** the system runs the weekly cleanup job, **Then** it suggests archiving the project to the user

---

### User Story 4 - Organize Bookmarks into Semantic Clusters (Priority: P2)

A knowledge worker has saved 200+ bookmarks over 3 months. The weekly batch job analyzes all bookmarks and groups related ones into clusters like "Infrastructure as Code" (13 bookmarks), "React Best Practices" (8 bookmarks), "Docker Tutorials" (11 bookmarks). The user reviews these suggested clusters and can accept, rename, or split them.

**Why this priority**: This is an intelligence enhancement that improves organization over time, but the system provides value without it (via tags and projects). This can be delayed if Phase 1 runs behind schedule.

**Independent Test**: Can be tested by saving 20 bookmarks across 3 topics (e.g., 7 Docker, 7 React, 6 Kubernetes), manually triggering the clustering batch job, and verifying that 3 clusters are suggested with appropriate names and members. Delivers long-term organization value.

**Acceptance Scenarios**:

1. **Given** a user has 50+ bookmarks, **When** the weekly batch job runs (Saturday 2 AM), **Then** the K-means clustering algorithm analyzes embeddings and identifies clusters with minimum 3 bookmarks each
2. **Given** clusters are identified, **When** the algorithm determines representative keywords, **Then** each cluster is assigned 3-5 keywords that best represent the group
3. **Given** new clusters are created, **When** the user opens the extension, **Then** they see a notification "3 new bookmark clusters suggested"
4. **Given** cluster suggestions are shown, **When** the user reviews a cluster named "Infrastructure as Code", **Then** they see all 13 member bookmarks and can accept, rename ("IaC Tools"), or ignore the cluster
5. **Given** a bookmark belongs to multiple potential clusters, **When** the system evaluates cluster membership, **Then** the bookmark is assigned to the cluster with the highest similarity score

---

### Edge Cases

- What happens when a user saves a bookmark from a page with very little text content (e.g., a landing page with mostly images)?
- How does the system handle duplicate URL saves (same URL saved twice)?
- What happens if OpenAI API is temporarily unavailable during bookmark save?
- How does the system handle very long page titles (>200 characters)?
- What happens when a user creates a project but never adds any bookmarks to it?
- How does similarity search behave when a user has only 1-2 bookmarks (not enough for meaningful comparisons)?
- What happens if a bookmark's target URL returns 404 or becomes unavailable?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST capture bookmark metadata (URL, title, page keywords) when user clicks "Save bookmark" in the extension
- **FR-002**: System MUST generate text embeddings for bookmark content using OpenAI text-embedding-3-small within 500ms (p95)
- **FR-003**: System MUST generate 3-7 semantic tags and a 2-3 sentence summary for each bookmark using Claude 3.5 Haiku
- **FR-004**: System MUST perform vector similarity search using Qdrant and return results within 100ms (p95)
- **FR-005**: System MUST display up to 5 similar bookmarks in the sidebar when a bookmark is saved or "Show Related" is clicked
- **FR-006**: System MUST calculate relevance scores as a percentage (0-100%) for displayed similar bookmarks
- **FR-007**: Users MUST be able to manually edit or remove AI-generated tags
- **FR-008**: System MUST allow users to create projects with name and description
- **FR-009**: System MUST calculate project embeddings as the average of all member bookmark embeddings
- **FR-010**: System MUST suggest the most relevant project for new bookmarks when similarity exceeds 70% threshold
- **FR-011**: System MUST filter sidebar and search results to show only bookmarks from the active project when a project is activated
- **FR-012**: System MUST display active project abbreviation in the extension icon badge (e.g., "FT" for FabrikTakt)
- **FR-013**: System MUST run weekly batch clustering job (Saturday 2 AM) to identify bookmark clusters with minimum 3 members
- **FR-014**: System MUST use K-means clustering with automatic K detection (elbow method) for cluster identification
- **FR-015**: System MUST generate representative keywords (3-5 per cluster) for identified clusters
- **FR-016**: System MUST prevent duplicate bookmark saves by checking URL uniqueness per user
- **FR-017**: System MUST provide fallback behavior when AI services are unavailable (save bookmark without tags/summary, allow manual tagging)
- **FR-018**: System MUST persist all bookmark data in PostgreSQL and embedding vectors in Qdrant
- **FR-019**: System MUST authenticate users via JWT tokens with 24-hour expiry
- **FR-020**: System MUST provide API endpoints for bookmark CRUD operations, project management, and similarity search

### Key Entities *(include if feature involves data)*

- **User**: Represents an authenticated user of the system; has unique ID, email, and hashed password; owns bookmarks and projects
- **Bookmark**: Represents a saved web page; contains URL (unique per user), title, auto-generated tags (array of strings), AI summary (2-3 sentences), content type classification (tutorial, documentation, article, video, tool), embedding vector (1536 dimensions), optional project association, creation timestamp, and user ownership
- **Project**: Represents a work context or area of interest; contains name, description, active status (boolean), list of bookmark IDs, context keywords (array), calculated embedding (average of member bookmarks), last active timestamp, and user ownership
- **Cluster**: Represents a group of semantically similar bookmarks; contains auto-generated name, list of bookmark IDs (minimum 3), representative keywords (3-5), creation timestamp, and user ownership
- **Embedding**: A 1536-dimension vector representation of text content stored in Qdrant; used for semantic similarity search via cosine similarity; associated with bookmarks and projects

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can save a bookmark and see AI-generated tags and summary within 3 seconds (end-to-end latency p95 <3s)
- **SC-002**: Context-aware similarity search returns results within 2 seconds from save action to sidebar display (p95 <2s)
- **SC-003**: 85% or more of auto-generated tags are accepted by users without modification (measured by tag edit rate)
- **SC-004**: 70% or more of bookmark save sessions with similar bookmark suggestions result in the user clicking at least one suggested bookmark within 5 minutes (click-through rate)
- **SC-005**: 80% or more of AI project suggestions are accepted by users (project suggestion acceptance rate)
- **SC-006**: Users can find a specific bookmark in under 5 seconds when using project filtering
- **SC-007**: System handles users with 1000+ bookmarks without performance degradation (search latency remains <2s)
- **SC-008**: Clustering accuracy achieves 80% or higher, measured by the rate of user corrections (renaming or rejecting clusters)
- **SC-009**: Zero data loss occurs during bookmark save operations (100% persistence success rate)
- **SC-010**: System maintains 99.5% uptime for bookmark save and retrieval operations

### Assumptions

1. **Target users**: Developers, cloud engineers, and knowledge workers managing 200-500+ bookmarks across multiple projects
2. **Bookmark volume**: Average user saves 5-10 bookmarks per week (~40 per month)
3. **Content language**: Bookmarks are primarily in English (AI models optimized for English)
4. **Browser support**: Chrome and Chromium-based browsers (Brave, Edge) with Manifest V3 support; Firefox support is future work
5. **Network connectivity**: Users have reliable internet connection for AI API calls during bookmark save
6. **AI service availability**: OpenAI and Anthropic APIs have 99%+ uptime; system provides graceful degradation when unavailable
7. **Content accessibility**: Most bookmarked pages are publicly accessible and can be analyzed (not behind paywalls or authentication)
8. **User authentication**: Users create accounts with email/password; social login is future work
9. **Project count**: Average user manages 2-5 active projects simultaneously
10. **Cluster size**: Meaningful clusters contain at least 3 bookmarks to avoid noise
11. **Infrastructure**: Self-hosted deployment on Hetzner VPS CX32 (8GB RAM, 80GB SSD) via Coolify can support 100-200 concurrent users
12. **Cost model**: AI costs remain within $0.04-0.15 per user per month (40 bookmarks/month using Haiku or Sonnet)
13. **Privacy**: Users are comfortable with bookmark content being sent to OpenAI and Anthropic APIs for processing (disclosed in privacy policy)
14. **Data retention**: Bookmarks are retained indefinitely unless user explicitly deletes them; no automatic cleanup of old bookmarks in MVP
15. **Embedding model**: OpenAI text-embedding-3-small (1536 dimensions) provides sufficient semantic quality for similarity search
