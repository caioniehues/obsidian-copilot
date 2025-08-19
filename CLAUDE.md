# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Obsidian Copilot is a streamlined TypeScript plugin for Obsidian that provides intelligent document chat and generation capabilities using Claude or OpenAI APIs directly.

**Key Features:**
- **Direct API Integration**: Communicates directly with Claude/OpenAI APIs
- **H2 Header Detection**: Auto-generates content when typing `##` headers
- **Vault Context**: Uses entire vault as context for intelligent responses
- **Document Display**: Shows retrieved context in a dedicated pane
- **Plugin Settings**: Configure API keys and preferences within Obsidian

## Architecture

### Simplified Plugin-Only Design
- **Single Plugin**: TypeScript-based Obsidian plugin (`/plugin/` directory)
- **Direct API Calls**: No backend service required - plugin calls APIs directly
- **Vault Processing**: Plugin reads and processes Obsidian vault content locally
- **Context Assembly**: Assembles relevant context from vault for AI queries

## Essential Commands

### Plugin Setup
```bash
# Set environment variable (required for Makefile)
export OBSIDIAN_PATH=/path/to/obsidian-vault/  # Note: trailing slash is required

# Complete plugin setup and installation
make setup-plugin

# Development setup only
make dev-setup
```

### Development Commands

#### Plugin Development
```bash
# Build plugin
make build-plugin

# Development mode (auto-rebuild)
make dev-plugin

# Install plugin to Obsidian
make install-plugin

# Sync plugin changes from Obsidian back to repo
make sync-plugin
```

### Testing Commands

#### Plugin Testing (TypeScript)
```bash
# Run all tests
make test-plugin

# Watch mode for continuous testing
make test-plugin-watch

# Generate coverage report (requires 90% coverage)
make test-plugin-coverage
```

Coverage reports are generated in `plugin/coverage/` with HTML reports at `plugin/coverage/lcov-report/index.html`.

## Key Implementation Details

### Plugin Configuration
- **API Keys**: Set in Obsidian Settings → Community Plugins → Copilot
- **Supported APIs**: Both Anthropic Claude and OpenAI
- **No Backend**: Plugin operates entirely standalone

### Document Processing
- **Vault Reading**: Plugin directly reads `.md` files from vault
- **Context Assembly**: Intelligently selects relevant documents for context
- **Source Attribution**: Context includes `([source](filename.md))` references
- **Real-time Generation**: Streams responses from Claude/OpenAI APIs

### Testing Infrastructure
- **Coverage Requirements**: 90% minimum coverage with Jest
- **TypeScript Support**: Full TypeScript testing with proper type checking
- **Mock Strategy**: Comprehensive mocking of Obsidian API
- **Fast Execution**: Tests run locally without external dependencies

## Common Development Tasks

### Plugin Development Workflow
```bash
# 1. Setup development environment
make dev-setup

# 2. Start development mode
make dev-plugin

# 3. Make changes to plugin code
# Changes auto-rebuild and can be tested in Obsidian

# 4. Run tests
make test-plugin

# 5. Install to Obsidian for testing
make install-plugin
```

### Debugging Common Issues

#### Plugin Issues
1. Check browser developer tools in Obsidian (Ctrl+Shift+I)
2. Verify API keys in plugin settings: Settings → Community Plugins → Copilot
3. Check console for error messages
4. Verify plugin is enabled in Community Plugins list

#### API Connection Issues
1. Verify API keys are correctly set in plugin settings
2. Check network connectivity
3. Verify API key permissions and rate limits
4. Test with different models if available

## Project Structure

```
obsidian-copilot/
├── plugin/                 # Main TypeScript plugin
│   ├── src/               # Plugin source code
│   ├── tests/             # Jest test files
│   ├── main.ts            # Main plugin entry point
│   ├── manifest.json      # Plugin manifest
│   ├── package.json       # Dependencies and scripts
│   └── styles.css         # Plugin styles
├── .agent-os/             # Agent OS configuration (preserved)
├── docs/                  # Documentation
├── CLAUDE.md              # This file
├── README.md              # Project README
└── Makefile              # Build and development commands
```

## Removed Components

The following Python backend and Docker infrastructure has been removed to simplify the project:

**Removed Directories:**
- `src/` - Python backend code
- `tests/` - Python test suite  
- `venv/` - Python virtual environment
- `data/` - Search indices and artifacts
- `monitoring/` - Monitoring configurations
- `scripts/` - Backend scripts

**Removed Files:**
- `Dockerfile` and `docker-compose*.yml` - Container infrastructure
- `requirements*.txt` - Python dependencies
- `pytest.ini` - Python testing configuration
- `setup.sh` and `build.sh` - Backend setup scripts
- `.python-version` and `.pre-commit-config.yaml` - Python tooling
- `.github/workflows/python_app.yml` - Python CI workflow

**Updated Files:**
- `Makefile` - Simplified to plugin-only commands
- `.gitignore` - Removed Python-specific entries
- `.env.example` - Updated for plugin-only configuration

## Migration Notes

This project has been simplified from a complex Python backend + TypeScript plugin architecture to a streamlined TypeScript plugin-only approach. The plugin now:

1. **Operates Standalone**: No backend service required
2. **Direct API Integration**: Calls Claude/OpenAI APIs directly
3. **Simplified Setup**: Single `make setup-plugin` command
4. **Faster Development**: No container builds or Python dependencies
5. **Easier Maintenance**: Single codebase in TypeScript

The core functionality remains the same - intelligent document chat and generation within Obsidian.