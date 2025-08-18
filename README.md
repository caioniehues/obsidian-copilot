# Obsidian Copilot - Claude-Exclusive Edition (Private Fork)

**⚠️ PRIVATE CUSTOM IMPLEMENTATION**  
This is a private fork optimized exclusively for Claude Code CLI, with all OpenAI dependencies removed.  
Not intended for public use. For the original multi-backend version, see [eugeneyan/obsidian-copilot](https://github.com/eugeneyan/obsidian-copilot).

![Claude Exclusive](https://img.shields.io/badge/Claude-Exclusive-blue)
![Context Window](https://img.shields.io/badge/Context-200K_tokens-green)
![Private Fork](https://img.shields.io/badge/Fork-Private-red)
![Local Processing](https://img.shields.io/badge/Processing-Local-orange)

## 🚀 Features

### Core Capabilities
- **🧠 200K Context Window** - Process entire documents, not just chunks
- **📚 Vault-Wide Analysis** - Analyze relationships across 50+ documents simultaneously
- **🔄 Multi-Document Synthesis** - Create comprehensive summaries from complete notes
- **🎯 Context Strategies** - Choose between full documents, smart chunks, or hierarchical processing
- **💻 Local Processing** - Uses Claude Code CLI for complete privacy
- **⚡ Optimized Architecture** - 40% less complex than dual-backend version

### New Claude-Exclusive Endpoints
- `/analyze_vault` - Perform comprehensive vault analysis on any topic
- `/synthesize_notes` - Create summaries, outlines, or connection maps from multiple notes
- `/generate` - Optimized generation with context strategies
- `/get_context` - Smart context retrieval with multiple strategies

## 📋 Prerequisites

- **Claude Code CLI** installed and configured
- **Obsidian** with community plugins enabled
- **Docker** or **Podman** for containerized deployment
- **Python 3.9+** (if running locally)
- At least 8GB RAM recommended for optimal performance

## 🛠️ Installation

### Quick Start

1. **Clone this repository**
   ```bash
   git clone https://github.com/caioniehues/obsidian-copilot.git
   cd obsidian-copilot
   ```

2. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your paths and settings
   ```

3. **Set required environment variables**
   ```bash
   export OBSIDIAN_PATH=/path/to/your/obsidian-vault/  # Trailing slash required!
   export TRANSFORMER_CACHE=/path/to/.cache/huggingface/hub
   export CLAUDE_CODE_PATH=/usr/local/bin/claude  # Or your Claude CLI path
   ```

4. **Build and start services**
   ```bash
   # Build Docker image
   make build
   
   # Start OpenSearch
   make opensearch
   
   # In another terminal, build indices
   make build-artifacts
   
   # Start the backend
   make run
   ```

5. **Install Obsidian plugin**
   ```bash
   make install-plugin
   ```
   Then enable "Copilot" in Obsidian's Community Plugins settings.

## ⚙️ Configuration

### Context Strategies

Choose your context strategy based on your use case:

| Strategy | Description | Best For | Token Usage |
|----------|-------------|----------|-------------|
| `full_docs` | Send complete documents | Comprehensive understanding | High (up to 200K) |
| `smart_chunks` | Intelligent chunking | Balanced performance | Medium (50-100K) |
| `hierarchical` | Summaries + details | Large vaults | Optimized |

### Environment Variables

```bash
# Required
OBSIDIAN_PATH=/path/to/vault/          # Your Obsidian vault path
TRANSFORMER_CACHE=/path/to/cache       # HuggingFace model cache
CLAUDE_CODE_PATH=/usr/local/bin/claude # Claude CLI location

# Optional Configuration
CLAUDE_MODEL=claude-3-5-sonnet-20241022  # Claude model to use
MAX_CONTEXT_TOKENS=100000                # Maximum context (up to 200000)
CONTEXT_STRATEGY=smart_chunks            # Default context strategy
```

## 🎯 Usage

### Basic Document Drafting
1. Select text in Obsidian (your section heading)
2. Run command: "Copilot: Draft Section"
3. Claude analyzes your vault and generates content

### Vault-Wide Analysis
```bash
curl -X POST http://localhost:8000/analyze_vault \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "machine learning",
    "depth": 3,
    "max_documents": 50
  }'
```

### Multi-Document Synthesis
```bash
curl -X POST http://localhost:8000/synthesize_notes \
  -H "Content-Type: application/json" \
  -d '{
    "note_paths": ["note1.md", "note2.md", "note3.md"],
    "synthesis_type": "summary"
  }'
```

## 🏗️ Architecture

### System Overview
```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  Obsidian       │────▶│  FastAPI Backend │────▶│  Claude CLI     │
│  Plugin (TS)    │     │  (Python)        │     │  (Local)        │
└─────────────────┘     └──────────────────┘     └─────────────────┘
                               │
                    ┌──────────┴──────────┐
                    ▼                     ▼
            ┌──────────────┐     ┌──────────────┐
            │  OpenSearch  │     │  Semantic    │
            │  (BM25)      │     │  Index       │
            └──────────────┘     └──────────────┘
```

### Context Flow
1. **Query** → Retrieve relevant documents/chunks
2. **Strategy** → Apply context strategy (full/chunks/hierarchical)
3. **Claude** → Process with 200K context window
4. **Response** → Stream back to Obsidian

## 📊 Performance

| Metric | Value | Notes |
|--------|-------|-------|
| Context Window | 200,000 tokens | ~500 pages of text |
| Documents per Query | 50+ | Full documents |
| Generation Time | 5-15 seconds | Depends on context size |
| Retrieval Time | <1 second | Dual index system |
| Memory Usage | 2-4 GB | With models loaded |

## 🔧 Advanced Features

### Custom Context Strategies
Configure in plugin settings or via API:
```json
{
  "context_strategy": "full_docs",
  "max_context_tokens": 150000,
  "include_full_docs": true
}
```

### Batch Processing
Process multiple queries efficiently:
```python
# See API_DOCUMENTATION.md for batch endpoints
```

### Caching
Redis caching available for frequent queries:
```bash
# Enable in docker-compose.yml
```

## 📝 Documentation

- [**CLAUDE_FEATURES.md**](./CLAUDE_FEATURES.md) - Detailed Claude-specific capabilities
- [**API_DOCUMENTATION.md**](./API_DOCUMENTATION.md) - Complete API reference
- [**SETUP_GUIDE.md**](./SETUP_GUIDE.md) - Detailed installation instructions
- [**ARCHITECTURE.md**](./ARCHITECTURE.md) - Technical deep-dive
- [**EXAMPLES.md**](./EXAMPLES.md) - Usage examples and patterns
- [**TROUBLESHOOTING.md**](./TROUBLESHOOTING.md) - Common issues and solutions

## 🚨 Important Notes

### This is a Private Fork
- **Not backward compatible** with OpenAI configurations
- **Requires Claude Code CLI** - No API key support
- **Optimized for single backend** - Simpler but less flexible
- **Breaking changes** from original repository

### Differences from Original
| Feature | Original | This Fork |
|---------|----------|-----------|
| OpenAI Support | ✅ | ❌ Removed |
| Claude Support | ✅ | ✅ Exclusive |
| Backend Options | 2 | 1 |
| Max Context | 16K | 200K |
| Complexity | Higher | 40% Lower |
| Vault Analysis | ❌ | ✅ |
| Multi-Doc Synthesis | ❌ | ✅ |

## 🤝 Attribution

This is a fork of [eugeneyan/obsidian-copilot](https://github.com/eugeneyan/obsidian-copilot), heavily modified for Claude-exclusive operation. Original concept and retrieval system architecture by Eugene Yan.

## ⚖️ License

Maintained under original MIT License. See [LICENSE](./LICENSE) file.

## 🔒 Privacy

- **Local Processing**: All Claude processing via local CLI
- **No API Keys**: No credentials transmitted
- **Your Data Stays Local**: Vault never leaves your machine

## 📮 Support

This is a private implementation. For issues:
1. Check [TROUBLESHOOTING.md](./TROUBLESHOOTING.md)
2. Review [API_DOCUMENTATION.md](./API_DOCUMENTATION.md)
3. See original project for general concepts

---

**Built with Claude 🤖 | Optimized for 200K Context 🧠 | Private Fork 🔒**