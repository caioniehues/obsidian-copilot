# Obsidian Copilot: Claude-Exclusive Edition with Agent OS

[![Claude](https://img.shields.io/badge/Claude-Exclusive-blue)](https://claude.ai)
[![Context](https://img.shields.io/badge/Context-200K_tokens-green)](https://www.anthropic.com)
[![Agents](https://img.shields.io/badge/Agents-5_Autonomous-purple)](./docs/agents/overview.md)
[![License](https://img.shields.io/badge/License-MIT-yellow)](./LICENSE)

> **⚡ PRIVATE CUSTOM IMPLEMENTATION**  
> An intelligent knowledge companion powered by Claude's 200K context window and 5 autonomous agents.  
> Fork of [obsidian-copilot](https://github.com/logancyang/obsidian-copilot) optimized for Claude + Agent OS.

## 🌟 Key Features

### 🧠 Claude Integration
- **200K Context Window** - Analyze entire documents, not fragments
- **Three Context Strategies** - Full docs, smart chunks, or hierarchical
- **Local Processing** - Privacy-first with Claude CLI

### 🤖 Five Autonomous Agents
- **Vault Analyzer** - Daily pattern detection and insights
- **Synthesis Assistant** - Multi-document synthesis
- **Context Optimizer** - Continuous performance tuning
- **Suggestion Engine** - Proactive recommendations
- **Research Assistant** - Deep knowledge exploration

### 💾 Intelligent Memory
- **Basic Memory Integration** - Agents learn and remember
- **Knowledge Graphs** - Semantic connections between memories
- **Continuous Learning** - Improves with every interaction

## 🚀 Quick Start

```bash
# 1. Clone repository
git clone https://github.com/caioniehues/obsidian-copilot.git
cd obsidian-copilot

# 2. Set environment (path MUST end with /)
export OBSIDIAN_PATH=/path/to/vault/
export TRANSFORMER_CACHE=~/.cache/huggingface/hub

# 3. Build and start
make build && make opensearch
# Wait 30 seconds, then in new terminal:
make build-artifacts && make run

# 4. Install plugin
cd plugin && npm install && npm run build
cd .. && make install-plugin
```

Enable in Obsidian: Settings → Community Plugins → Obsidian Copilot

## 📚 Complete Documentation

> **📖 [Full Documentation Hub](./docs/README.md)** - Your one-stop destination for all guides, references, and tutorials

### 🚀 Quick Navigation

| Getting Started | Core Features | Advanced | Technical |
|-----------------|---------------|----------|-----------|
| [Installation Guide](./docs/setup/installation.md) | [Basic Usage](./docs/usage/basic-usage.md) | [Advanced Features](./docs/usage/advanced-features.md) | [API Reference](./docs/architecture/api-reference.md) |
| [Quick Start (5 min)](./docs/setup/quick-start.md) | [Agent Commands](./docs/usage/agent-commands.md) | [Claude Features](./docs/features/claude-features.md) | [Agent API](./docs/agents/api-reference.md) |
| [Requirements](./docs/setup/requirements.md) | [Agent Overview](./docs/agents/overview.md) | [Migration Guide](./docs/migration/migration-guide.md) | [Troubleshooting](./docs/troubleshooting/common-issues.md) |

### 📋 Documentation Categories

- **🛠️ Setup & Installation** - Complete setup guides from requirements to testing
- **👤 Usage Guides** - From first-time use to advanced workflows and agent collaboration  
- **🤖 Agent Documentation** - Comprehensive agent system guides, API references, and troubleshooting
- **⭐ Claude Features** - Claude-exclusive features, context strategies, and performance optimization
- **🏗️ Technical Reference** - API documentation, architecture details, and integration guides
- **📦 Migration & Upgrades** - Complete migration guide from OpenAI-only versions
- **🔧 Troubleshooting** - Common issues, advanced debugging, and support resources

## 🎯 Basic Usage

In any Obsidian note:

```markdown
## What is machine learning?

## agent:synthesize
Create a synthesis of my productivity notes

## agent:research depth=comprehensive
Deep dive into quantum computing

## agent:suggest
What should I explore next?
```

## 🏗️ Architecture

```mermaid
graph LR
    A[Obsidian Plugin] --> B[FastAPI Backend]
    B --> C[Claude CLI]
    B --> D[OpenSearch + Semantic RAG]
    B --> E[Agent OS]
    E --> F[5 Specialized Agents]
    F --> G[Basic Memory]
    G --> H[Continuous Learning]
```

## ⚙️ Configuration

### Context Strategies

| Strategy | Use Case | Tokens | Speed |
|----------|----------|---------|-------|
| `full_docs` | Complete understanding | 150-200K | 10-15s |
| `smart_chunks` | Balanced (default) | 50-100K | 5-10s |
| `hierarchical` | Quick overview | 30-50K | 2-5s |

### Agent Configuration

Edit `.agent-os/agents/config.yaml`:

```yaml
agents:
  vault-analyzer:
    enabled: true
    trigger:
      interval: daily
      time: "02:00"
```

## 🔒 Privacy & Security

- ✅ **Local Processing** - All indexing and retrieval on your machine
- ✅ **No Telemetry** - Zero usage tracking
- ✅ **Secure API** - Only Claude calls leave your system
- ✅ **Your Data** - Complete control over your vault

## 🤝 Contributing

This is a private fork. For the original project, see [obsidian-copilot](https://github.com/logancyang/obsidian-copilot).

## 📄 License

MIT License - See [LICENSE](./LICENSE)

## 🙏 Acknowledgments

- Original [obsidian-copilot](https://github.com/logancyang/obsidian-copilot) by Logan Yang
- [Claude](https://claude.ai) by Anthropic
- [Basic Memory](https://github.com/waldzx/basic-memory) for semantic knowledge
- [OpenSearch](https://opensearch.org) for robust retrieval

---

<div align="center">
  <b>Built with ❤️ for the Obsidian + Claude power user</b>
  <br>
  <a href="./docs/README.md">📚 Full Documentation</a> • 
  <a href="./docs/setup/quick-start.md">⚡ Quick Start</a> • 
  <a href="./docs/troubleshooting/common-issues.md">🔧 Troubleshooting</a>
</div>