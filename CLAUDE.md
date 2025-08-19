# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Obsidian Copilot is a retrieval-augmented generation (RAG) system for Obsidian that helps users draft content based on their vault notes. It consists of two main components:
1. **Obsidian Plugin** (TypeScript) - Frontend UI that integrates with Obsidian editor
2. **FastAPI Backend** (Python) - Retrieval service using OpenSearch and semantic search

## Essential Commands

### Initial Setup
```bash
# Set environment variables (required)
export OBSIDIAN_PATH=/path/to/obsidian-vault/  # Note: trailing slash is required
export TRANSFORMER_CACHE=/path/to/.cache/huggingface/hub

# Build Docker image
make build

# Start OpenSearch container (wait for initialization)
make opensearch

# Build search indices (run in separate terminal)
make build-artifacts

# Run the backend service
make run

# Install plugin to Obsidian
make install-plugin
```

### Development Commands

#### Plugin Development
```bash
# Build plugin
cd plugin && npm run build

# Development mode (auto-rebuild)
cd plugin && npm run dev

# Sync plugin changes from Obsidian back to repo
make sync-plugin
```

#### Backend Development
```bash
# Run backend locally (without Docker)
make app-local

# Run backend in Docker with hot reload
make app

# Interactive development shell
make dev
```

## Architecture & Key Components

### Retrieval System
The backend implements dual retrieval:
- **OpenSearch** (`src/prep/build_opensearch_index.py`): BM25 keyword search
- **Semantic Search** (`src/prep/build_semantic_index.py`): Using E5-small-v2 embeddings

Both indices are built from the Obsidian vault and stored in `/data/`:
- `vault_dict.pickle` - Document chunks dictionary
- `doc_embeddings_array.npy` - Semantic embeddings
- `embedding_index.pickle` - Embedding to document mapping

### Plugin → Backend Communication
- Plugin sends queries to `http://localhost:8000`
- Endpoints:
  - `POST /query` - Main retrieval endpoint
  - `POST /reflect_week` - Weekly reflection feature
- OpenAI API calls are made from the plugin, not the backend

### Key Integration Points
1. **Editor Hook** (`plugin/main.ts`): Monitors for H2 headers (##) and triggers generation
2. **Retrieved Docs Display**: Opens in separate pane (`Retrieved docs.md`)
3. **Streaming Response**: Uses OpenAI streaming API for real-time generation

## Important Implementation Details

- The plugin expects OpenAI API key in settings (not backend)
- Document chunking preserves markdown structure and links
- Retrieved context includes source links in format `([source](filename.md))`
- The system uses `intfloat/e5-small-v2` model (max 512 tokens)
- OpenSearch runs in single-node mode on port 9200
- Backend serves on port 8000 with CORS enabled for `app://obsidian.md`

## Common Tasks

### Rebuilding Indices After Vault Changes
```bash
make opensearch  # Start OpenSearch
# In another terminal:
make build-artifacts  # Rebuild indices
```

### Updating Plugin Settings
Edit default settings in `plugin/main.ts:DEFAULT_SETTINGS`

### Debugging Retrieval Issues
1. Check OpenSearch is running: `curl localhost:9200`
2. Verify indices exist in `/data/` directory
3. Check backend logs for query processing
4. Ensure OBSIDIAN_PATH has trailing slash

## Docker vs Podman
The project supports both Docker and Podman. Set runtime with:
```bash
export RUNTIME=podman  # or docker (default)
```
- CRITICAL: ALWAYS USE MULTIPLE PARALLEL TASKS AND AGENTS FOR GREAT PERFORMANCE