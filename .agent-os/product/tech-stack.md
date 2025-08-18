# Technical Stack

> Last Updated: 2025-08-18
> Version: 1.0.0

## Application Framework

- **Framework:** FastAPI (Python)
- **Version:** 0.104+
- **Purpose:** High-performance async API for retrieval operations

## Database

- **Primary Database:** OpenSearch 2.11+
- **Purpose:** Full-text search and document indexing
- **Secondary:** Local file system for embeddings and metadata

## JavaScript

- **Framework:** TypeScript
- **Runtime:** Node.js (Obsidian plugin environment)
- **Purpose:** Obsidian plugin frontend and editor integration

## CSS Framework

- **Framework:** Obsidian native styling
- **Purpose:** Seamless integration with Obsidian UI themes

## AI/ML Stack

- **Primary Model:** Claude 3.5 Sonnet via API
- **Context Window:** 200K tokens (target utilization: 150-180K)
- **Embeddings:** E5-small-v2 (local inference)
- **Vector Storage:** NumPy arrays with Pickle serialization

## Development Tools

- **CLI Integration:** Claude Code CLI
- **Build System:** Make + Docker Compose
- **Package Manager:** npm (plugin), pip (backend)
- **Code Quality:** ESLint, Prettier (TypeScript), Black, Ruff (Python)

## Infrastructure

- **Containerization:** Docker with multi-stage builds
- **Orchestration:** Docker Compose for local development
- **Storage:** Local filesystem with configurable paths
- **Networking:** HTTP REST API (localhost only)

## Search & Retrieval

- **Hybrid Search:** OpenSearch (BM25) + Semantic similarity
- **Document Processing:** Python with markdown parsing
- **Index Management:** Custom pipeline with incremental updates
- **Context Optimization:** Smart chunking for 200K token utilization

## Security & Privacy

- **Data Processing:** 100% local (no external indexing services)
- **API Keys:** User-managed Claude API credentials
- **Storage:** Local encrypted options available
- **Network:** Localhost-only communication by default

## Plugin Architecture

- **Base:** Obsidian Plugin API
- **Language:** TypeScript 4.9+
- **Bundling:** Rollup with plugin-specific configuration
- **Integration:** Native Obsidian editor hooks and UI components