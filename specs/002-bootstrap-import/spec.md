# Feature Specification: Phase 0 Bootstrap - Import & Organize Existing Bookmarks

**Feature Branch**: `002-bootstrap-import`
**Created**: October 27, 2025
**Status**: Draft
**Input**: User description: "Phase 0 Bootstrap: Import and process existing bookmark collections (HTML export from browsers), set up infrastructure (PostgreSQL, Qdrant, FastAPI, AI services), batch process 800+ bookmarks to generate embeddings/tags/summaries/clusters, suggest initial projects, and deliver a working organized bookmark system before building the browser extension for Phase 1"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Import Existing Bookmark Collection (Priority: P1)

As the first user with 800 existing bookmarks saved in my browser over the years, I need to import them all into the system from a browser export file (HTML format). The system should preserve all bookmark URLs, titles, and any existing folder structure from my browser, so I don't lose any data or have to manually re-save everything.

**Why this priority**: This is the absolute foundation - without importing existing bookmarks, the system has no data to work with. No user will start from zero. Every user comes with hundreds of messy, unorganized bookmarks that need to be migrated first. Without this, there's no system to use.

**Independent Test**: Can be fully tested by exporting 800 bookmarks from Chrome as HTML, uploading the file to the system, and verifying all 800 bookmarks appear in the database with correct URLs and titles. Delivers immediate value by centralizing all bookmarks in one system.

**Acceptance Scenarios**:

1. **Given** a user has exported their Chrome bookmarks as an HTML file containing 800 bookmarks, **When** they upload the file to the system, **Then** the system parses the HTML and extracts all bookmark URLs, titles, and original folder paths
2. **Given** the HTML file is parsed, **When** the import process completes, **Then** all 800 bookmarks are stored in the database with zero data loss (100% success rate)
3. **Given** bookmarks are imported, **When** the user views their bookmark list, **Then** they see all 800 bookmarks with their original titles and URLs
4. **Given** the original browser bookmarks had a folder structure (e.g., "Work", "Personal", "Reading List"), **When** import completes, **Then** the folder names are preserved as initial tags or metadata for later clustering
5. **Given** an import is in progress, **When** the user checks the status, **Then** they see a progress indicator showing "Processing 342 of 800 bookmarks"

---

### User Story 2 - AI-Powered Batch Processing of Imported Bookmarks (Priority: P1)

As a user who just imported 800 unorganized bookmarks, I need the system to automatically generate semantic tags and summaries for every bookmark using AI, so I can understand what each bookmark is about without having to open and read every page manually. This should happen automatically after import without me having to click through each bookmark.

**Why this priority**: Raw imported bookmarks are just URLs and titles - they're not searchable or understandable. AI-generated tags and summaries make the bookmark collection useful. This is the intelligence layer that differentiates this from a simple bookmark manager. Without this, we just have a list of links.

**Independent Test**: Can be tested by importing 50 bookmarks, waiting for batch processing to complete, then verifying that every bookmark has 3-7 AI-generated tags and a 2-3 sentence summary. Delivers immediate organizational value by making bookmarks searchable and browsable.

**Acceptance Scenarios**:

1. **Given** 800 bookmarks have been imported, **When** the batch processing job runs, **Then** the system generates embeddings for all 800 bookmarks to enable semantic search
2. **Given** embeddings are generated, **When** AI analysis runs, **Then** each bookmark receives 3-7 automatically generated semantic tags (e.g., #kubernetes, #docker, #devops)
3. **Given** AI tagging is complete, **When** AI summarization runs, **Then** each bookmark receives a 2-3 sentence summary describing the content
4. **Given** batch processing is running, **When** processing completes within 24 hours, **Then** the user receives a notification "All 800 bookmarks have been processed and organized"
5. **Given** some bookmarks are paywalled or inaccessible, **When** AI processing encounters them, **Then** the system generates tags based on the URL and title only, marking them as "Limited preview available"
6. **Given** batch processing is running for 800 bookmarks, **When** the user checks the status, **Then** they see estimated completion time and cost projection

---

### User Story 3 - Automatic Semantic Clustering (Priority: P1)

As a user with 800 newly processed bookmarks, I need the system to automatically group related bookmarks into semantic clusters (e.g., "Docker Tutorials", "React Best Practices", "Infrastructure as Code") so I can see natural topic groupings without manually creating categories. The system should suggest cluster names and let me review, rename, or merge clusters.

**Why this priority**: 800 bookmarks without organization is overwhelming. Automatic clustering provides the first layer of structure that helps users navigate their collection. This transforms a chaotic list into browsable topic groups. Without this, users drown in an unsorted list of 800 items.

**Independent Test**: Can be tested by importing and processing 100 bookmarks across 5 different topics, running the clustering algorithm, and verifying that 5 clusters are created with meaningful names and correct bookmark assignments. Delivers immediate navigation value by grouping similar content.

**Acceptance Scenarios**:

1. **Given** all 800 bookmarks have embeddings and tags, **When** the clustering algorithm runs, **Then** the system identifies 8-15 natural clusters based on semantic similarity
2. **Given** clusters are identified, **When** the system generates cluster names, **Then** each cluster receives a descriptive name based on the most common topics (e.g., "Kubernetes & Container Orchestration", "Python Web Development")
3. **Given** clusters are created, **When** the user reviews the clusters, **Then** they see each cluster with its suggested name, bookmark count, and top 5 representative keywords
4. **Given** a user reviews a cluster named "Infrastructure as Code", **When** they view the cluster contents, **Then** they see all bookmarks grouped under this cluster (e.g., 23 bookmarks about Terraform, Ansible, Pulumi)
5. **Given** a user disagrees with a cluster name, **When** they rename "Cloud Stuff" to "AWS Architecture Patterns", **Then** the cluster name is updated and saved
6. **Given** two clusters are too similar (e.g., "Docker" and "Containers"), **When** the user merges them, **Then** a single cluster "Docker & Containers" is created containing all bookmarks from both
7. **Given** a bookmark fits multiple clusters, **When** the system assigns it, **Then** it's placed in the cluster with the highest similarity score (>80% confidence threshold)

---

### User Story 4 - AI-Suggested Initial Projects (Priority: P1)

As a user who now has organized clusters of bookmarks, I need the system to suggest 3-5 initial projects based on my major topic areas (e.g., "FabrikTakt Work", "Personal Learning", "Side Projects") and automatically assign bookmarks to these projects. This gives me a working project structure to start with, which I can then refine later.

**Why this priority**: Projects are the core organizational unit for context switching (from Phase 1 spec). Users need initial projects to make the system functional. Without project suggestions, users face a blank slate and decision paralysis. This provides a smart starting point based on their actual bookmark content.

**Independent Test**: Can be tested by importing 150 bookmarks across 3 distinct work areas (e.g., work, learning, hobbies), running project suggestion, and verifying that 3 projects are suggested with appropriate names and bookmark distributions (e.g., 70 work, 50 learning, 30 hobbies). Delivers immediate workflow value by creating context-based workspaces.

**Acceptance Scenarios**:

1. **Given** bookmarks are clustered, **When** the project suggestion algorithm analyzes clusters, **Then** the system identifies 3-5 major project areas based on cluster size and topic diversity
2. **Given** project areas are identified, **When** the system generates project suggestions, **Then** each suggested project has a descriptive name (e.g., "Cloud Infrastructure Work", "Web Development Learning") and estimated bookmark count
3. **Given** project suggestions are created, **When** the user reviews them, **Then** they see a list like: "FabrikTakt (187 bookmarks)", "Personal Projects (134 bookmarks)", "Learning & Tutorials (312 bookmarks)", "German Language (89 bookmarks)", "Health & Fitness (78 bookmarks)"
4. **Given** a user accepts a project suggestion, **When** they click "Accept", **Then** the project is created and all relevant bookmarks are assigned to it based on cluster membership
5. **Given** a user wants to customize a suggestion, **When** they rename "Cloud Infrastructure Work" to "FabrikTakt", **Then** the project is created with the custom name
6. **Given** a user rejects a project suggestion (e.g., "Health & Fitness"), **When** they click "Reject", **Then** those bookmarks remain unassigned and can be added to projects later
7. **Given** bookmarks are assigned to projects, **When** assignment completes, **Then** 80%+ of all bookmarks are assigned to at least one project

---

### User Story 5 - Browse and Search Organized Bookmarks (Priority: P2)

As a user with imported, tagged, clustered, and project-organized bookmarks, I need a web interface to browse my bookmark collection, search by tags or keywords, filter by project or cluster, and verify that the AI organization makes sense. This lets me validate that the bootstrap process worked correctly before moving to Phase 1 (browser extension).

**Why this priority**: This is the validation step - users need to see the results of the bootstrap process and verify everything looks correct. It's P2 because the core work (import, tagging, clustering, projects) is more critical, but this is essential for user confidence and making adjustments before building the extension.

**Independent Test**: Can be tested by accessing the web interface, searching for "docker", filtering by a specific project, and browsing a specific cluster - all operations should return relevant results within 2 seconds. Delivers validation value by proving the system works correctly.

**Acceptance Scenarios**:

1. **Given** a user accesses the web interface, **When** they view the dashboard, **Then** they see summary stats: "800 bookmarks, 12 clusters, 5 projects, All processed ✓"
2. **Given** a user wants to search, **When** they type "kubernetes tutorial" in the search bar, **Then** they see all bookmarks matching those keywords within 2 seconds
3. **Given** search results are displayed, **When** results are shown, **Then** each result shows the bookmark title, URL, tags, summary snippet, cluster name, and project assignment
4. **Given** a user wants to browse by cluster, **When** they click on the "Docker & Containers" cluster, **Then** they see all 34 bookmarks in that cluster
5. **Given** a user wants to filter by project, **When** they select "FabrikTakt" from the project dropdown, **Then** only FabrikTakt bookmarks are shown (187 bookmarks)
6. **Given** a user finds an incorrectly tagged bookmark, **When** they edit the tags, **Then** the changes are saved and the bookmark is re-clustered if necessary
7. **Given** a user wants to verify import completeness, **When** they view the import report, **Then** they see "800 of 800 bookmarks imported successfully (100%)"

---

### Edge Cases

- What happens when the HTML export file contains duplicate URLs (same page bookmarked twice)?
- How does the system handle bookmarks with missing titles (URL only)?
- What happens when AI processing fails for specific bookmarks (e.g., dead links, 404s, paywalled content)?
- How does the system handle very large import files (5000+ bookmarks)?
- What happens when a bookmark URL is invalid or malformed?
- How does clustering behave when bookmarks are extremely diverse (no natural groupings)?
- What happens if the user's browser export contains non-English bookmarks?
- How does the system handle bookmarks that belong equally to multiple clusters (ambiguous classification)?
- What happens when AI cost limits are reached mid-processing (e.g., budget cap of $50 for 800 bookmarks)?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST parse HTML bookmark export files from Chrome, Firefox, and Safari browsers
- **FR-002**: System MUST import all bookmarks from the HTML file with zero data loss (100% success rate)
- **FR-003**: System MUST preserve original bookmark metadata (URL, title, folder structure) during import
- **FR-004**: System MUST generate embeddings for all imported bookmarks to enable semantic search
- **FR-005**: System MUST generate 3-7 semantic tags for each imported bookmark using AI analysis
- **FR-006**: System MUST generate a 2-3 sentence summary for each imported bookmark using AI analysis
- **FR-007**: System MUST complete batch processing of 800 bookmarks within 24 hours of import
- **FR-008**: System MUST identify 8-15 semantic clusters from imported bookmarks using clustering algorithms
- **FR-009**: System MUST generate descriptive names for each cluster based on bookmark content and topics
- **FR-010**: System MUST assign each bookmark to the most relevant cluster (>80% similarity threshold)
- **FR-011**: System MUST suggest 3-5 initial projects based on cluster analysis and topic diversity
- **FR-012**: System MUST assign 80%+ of bookmarks to suggested projects automatically
- **FR-013**: Users MUST be able to review, accept, rename, or reject suggested clusters through the web interface
- **FR-014**: Users MUST be able to review, accept, rename, or reject suggested projects through the web interface
- **FR-015**: Users MUST be able to manually edit tags, summaries, cluster assignments, and project assignments
- **FR-016**: System MUST provide a progress indicator showing import and processing status
- **FR-017**: System MUST provide cost estimates before starting batch AI processing
- **FR-018**: System MUST handle processing failures gracefully (e.g., mark failed bookmarks, continue processing others)
- **FR-019**: System MUST provide a web interface for browsing bookmarks by cluster, project, or tags
- **FR-020**: System MUST support keyword search across all bookmark titles, URLs, tags, and summaries
- **FR-021**: System MUST display an import report showing success/failure counts and any issues encountered
- **FR-022**: System MUST detect and handle duplicate URLs during import (keep first occurrence, flag duplicates)

### Key Entities

- **Imported Bookmark**: Represents a bookmark extracted from browser HTML export; contains original URL, title, folder path from browser, import timestamp, processing status (pending/completed/failed), and reference to the user who imported it
- **Processed Bookmark**: Represents a bookmark after AI processing; extends Imported Bookmark with AI-generated tags (array of 3-7 strings), AI-generated summary (2-3 sentences), embedding vector (for semantic search), content type classification, and processing metadata (cost, processing time, AI model used)
- **Cluster**: Represents a semantic grouping of related bookmarks; contains auto-generated descriptive name, list of bookmark IDs (minimum 3 bookmarks), representative keywords (3-5), similarity score threshold, user approval status (suggested/accepted/renamed/rejected), and creation timestamp
- **Project Suggestion**: Represents an AI-suggested project based on bookmark clusters; contains suggested project name, list of bookmark IDs to be assigned, cluster IDs that form this project, confidence score, user decision (pending/accepted/renamed/rejected), and suggested keywords/description
- **Import Job**: Represents a batch import and processing operation; contains import file metadata, total bookmark count, processing progress (count/percentage), status (uploading/importing/processing/clustering/completed), cost tracking, error log, and completion timestamp

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: All 800 bookmarks are imported from browser HTML export with zero data loss (100% import success rate)
- **SC-002**: Every successfully imported bookmark receives AI-generated tags and summary within 24 hours of import
- **SC-003**: Batch AI processing completes within 24 hours for collections up to 1000 bookmarks
- **SC-004**: AI tagging achieves 85%+ user acceptance rate (measured by manual tag edits)
- **SC-005**: System identifies 8-15 meaningful clusters that cover 90%+ of all imported bookmarks
- **SC-006**: Clustering algorithm achieves 80%+ accuracy (measured by user corrections and cluster reassignments)
- **SC-007**: System suggests 3-5 initial projects that collectively cover 80%+ of all bookmarks
- **SC-008**: Project suggestions achieve 70%+ user acceptance rate (measured by accepted vs. rejected projects)
- **SC-009**: Users can search and find a specific bookmark in under 5 seconds using keyword search
- **SC-010**: Web interface loads and displays bookmark lists within 2 seconds for collections up to 1000 bookmarks
- **SC-011**: Total cost for processing 800 bookmarks remains under $50 (approximately $0.06 per bookmark for embeddings + AI analysis)
- **SC-012**: Users successfully complete the entire bootstrap workflow (import → process → review → organize) in under 4 hours of elapsed time

### Assumptions

1. **User has existing bookmarks**: Users come with 200-1000 existing bookmarks from years of browsing, not starting from zero
2. **Browser export format**: Users can export bookmarks as HTML from Chrome, Firefox, or Safari (standard browser feature)
3. **Bookmark quality**: Most bookmarked URLs are still accessible (not 404), though some dead links are expected
4. **Content language**: Majority of bookmarks are English-language content (AI models optimized for English)
5. **Processing time is acceptable**: Users are willing to wait 12-24 hours for complete batch processing of large collections
6. **Cost budget**: Users accept AI processing costs of approximately $40-60 for 800 bookmarks (one-time bootstrap cost)
7. **Web interface access**: Users can access a web dashboard to review and adjust AI suggestions (Phase 0 does not require browser extension)
8. **Infrastructure is operational**: Databases, backend API, and AI services are deployed and configured before users begin import
9. **Single user scenario**: Phase 0 focuses on the first user (Sia) as a pilot; multi-user support comes later
10. **Manual review is expected**: Users will spend 1-2 hours reviewing AI-suggested clusters and projects to ensure accuracy
11. **Folder structure preservation**: Browser bookmark folders are treated as preliminary organizational hints, but AI clustering takes precedence
12. **Duplicate handling**: Some users may have duplicate bookmarks (same URL saved multiple times); system deduplicates automatically
13. **Privacy acceptance**: User accepts that bookmark content will be sent to OpenAI and Anthropic APIs for one-time processing
14. **No real-time requirement**: Phase 0 is a one-time bootstrap operation, not a real-time system (real-time comes in Phase 1)
15. **Success validation needed**: Users need to validate bootstrap results through web interface before committing to Phase 1 development
