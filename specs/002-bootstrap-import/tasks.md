# Phase 0: Bootstrap Import - Implementation Tasks

## Week 1: Infrastructure & Import API

- [ ] **Task 1: Deploy Infrastructure**
  - Create `docker-compose.yml` for PostgreSQL, Qdrant, and Valkey.
  - Configure environment variables for database connections.
  - Write a script to start and stop the services.
  - Verify all services are running and accessible.

- [ ] **Task 2: Set Up FastAPI Backend Skeleton**
  - Initialize a new FastAPI project.
  - Create the basic directory structure (`src/app`, `src/core`, `src/models`, etc.).
  - Set up `pyproject.toml` with initial dependencies (FastAPI, Uvicorn, SQLAlchemy).
  - Create a basic `/health` endpoint to verify the server is running.

- [ ] **Task 3: Implement HTML Bookmark Parser**
  - Research Python libraries for HTML parsing (e.g., BeautifulSoup).
  - Create a `bookmarks_parser` module.
  - Implement a function to parse a bookmarks HTML file and extract URLs, names, and folders.
  - Write unit tests for the parser.

- [ ] **Task 4: Build `/api/v1/import` Endpoint**
  - Create the API endpoint to handle HTML file uploads.
  - Integrate the `bookmarks_parser` to process the uploaded file.
  - Define the database models for `ImportJob` and `Bookmark`.
  - Save the parsed bookmarks to the PostgreSQL database.

- [ ] **Task 5: Create Basic Web Dashboard**
  - Set up a new React project using Vite.
  - Create a simple UI with a file upload component for the bookmarks HTML file.
  - Connect the UI to the `/api/v1/import` endpoint.
  - Display the status of the import job.

## Week 2: AI Processing & Web Dashboard

- [ ] **Task 6: Implement Batch AI Processing**
  - Create a service to handle batch processing of bookmarks.
  - Use the OpenAI Batch API to generate embeddings for bookmark content.
  - Use the Claude 3.5 Haiku API to generate tags and summaries.
  - Store the AI-generated data in the database.

- [ ] **Task 7: Implement MiniBatchKMeans Clustering**
  - Use scikit-learn's `MiniBatchKMeans` to cluster bookmarks based on their embeddings.
  - Create a service to run the clustering algorithm.
  - Store the cluster results in the database.

- [ ] **Task 8: Build Project Suggestion Algorithm**
  - Analyze the clustered bookmarks.
  - Develop an algorithm to suggest project names based on the content of each cluster.
  - Create an API endpoint to retrieve project suggestions.

- [ ] **Task 9: Complete Web Dashboard**
  - Create a view to browse the organized bookmarks.
  - Implement search and filtering based on tags, clusters, and projects.
  - Display the AI-generated summaries for each bookmark.

- [ ] **Task 10: Test with Sia's 800 Bookmarks**
  - Run a full end-to-end test with the provided 800 bookmarks.
  - Verify the import, AI processing, clustering, and project suggestions.
  - Document the results and any issues found.
