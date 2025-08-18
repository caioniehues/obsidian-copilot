# Obsidian Copilot: Claude-Exclusive Edition with Agent OS

> **⚡ PRIVATE CUSTOM IMPLEMENTATION**  
> This is a private fork optimized exclusively for Claude's 200K context window with autonomous Agent OS capabilities.  
> Not intended for public use. Original project: [obsidian-copilot](https://github.com/logancyang/obsidian-copilot)

## 🚀 What Makes This Special

This isn't just another RAG plugin. It's an **intelligent knowledge companion** that:

- **Leverages Claude's 200K Context Window**: Analyze entire documents, not just fragments
- **Autonomous Agents**: 5 specialized agents that continuously analyze, optimize, and learn from your vault
- **Semantic Memory**: Agents build knowledge graphs using Basic Memory integration
- **Proactive Intelligence**: Get suggestions before you ask, discover patterns you didn't know existed
- **Privacy-First**: All processing happens locally, only Claude API calls leave your machine

## 🤖 Agent OS: Your Knowledge Companions

### The Agent Team

| Agent | Type | Purpose | Trigger |
|-------|------|---------|---------|
| **Vault Analyzer** | Autonomous | Daily analysis of your entire vault for patterns and insights | 2 AM daily |
| **Synthesis Assistant** | Reactive | Creates comprehensive syntheses from multiple documents | On-demand |
| **Context Optimizer** | Background | Continuously optimizes retrieval performance and caching | Every 5 min |
| **Suggestion Engine** | Proactive | Provides real-time suggestions based on context | Context-aware |
| **Research Assistant** | Interactive | Conducts deep research across your knowledge base | On-demand |

### What Agents Can Do

- **Learn Your Patterns**: Track how you work and optimize accordingly
- **Share Knowledge**: Agents share insights with each other through Basic Memory
- **Improve Over Time**: Every interaction makes them smarter
- **Work Autonomously**: Run scheduled analyses while you sleep
- **Provide Insights**: Surface connections and patterns you might miss

## 📋 Prerequisites

- **Obsidian** (v0.12.0+)
- **Docker** or **Podman**
- **Claude API Access** (via Claude Code CLI)
- **Basic Memory MCP Server** (for agent memory)
- **Python 3.11+**
- **Node.js 18+**

## 🛠️ Installation

### 1. Clone and Setup Environment

```bash
git clone https://github.com/yourusername/obsidian-copilot.git
cd obsidian-copilot

# Set required environment variables
export OBSIDIAN_PATH=/path/to/your/vault/  # Note: trailing slash required!
export TRANSFORMER_CACHE=/path/to/.cache/huggingface/hub
export CLAUDE_API_KEY=your-claude-api-key  # If using direct API
```

### 2. Build and Start Services

```bash
# Build Docker image
make build

# Start OpenSearch (for RAG)
make opensearch

# Wait 30 seconds for OpenSearch to initialize, then in another terminal:
make build-artifacts

# Start the backend with Agent OS
make run
```

### 3. Install Obsidian Plugin

```bash
# Build and install plugin
cd plugin
npm install
npm run build
cd ..
make install-plugin

# Enable the plugin in Obsidian settings
```

### 4. Configure Basic Memory (for Agent Memory)

Ensure Basic Memory MCP server is running and accessible. Agents will use it to store and retrieve memories.

## ⚙️ Configuration

### Plugin Settings (in Obsidian)

```javascript
{
  "backendUrl": "http://localhost:8000",
  "claudeModel": "claude-3-5-sonnet-20241022",
  "contextStrategy": "smart_chunks",  // or "full_docs", "hierarchical"
  "maxContextTokens": 150000,
  "showGenerationTime": true
}
```

### Agent Configuration

Edit `.agent-os/agents/config.yaml` to customize agent behavior:

```yaml
agents:
  vault-analyzer:
    enabled: true
    trigger:
      type: schedule
      interval: daily
      time: "02:00"  # Run at 2 AM
```

## 🎯 Usage

### Basic RAG Queries

1. **In Obsidian**: Type `##` followed by your question
2. **Context Building**: The system retrieves relevant documents
3. **Claude Analysis**: Sends context to Claude for analysis
4. **Response**: Get comprehensive answers leveraging your entire vault

### Agent Commands

```markdown
## agent:synthesize
Create a synthesis of my notes on [topic]

## agent:research
Deep dive into [research question]

## agent:analyze-vault
Run vault analysis now
```

### Context Strategies

- **`full_docs`**: Include complete documents (best for comprehensive analysis)
- **`smart_chunks`**: Intelligent chunking with relevance scoring (balanced)
- **`hierarchical`**: Build from most to least relevant (memory efficient)

## 🏗️ Architecture

### System Components

```
┌─────────────────────────────────────────────────┐
│                   Obsidian UI                   │
│                  (TypeScript)                   │
└─────────────────┬───────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────┐
│              FastAPI Backend                    │
│                 (Python)                        │
├─────────────────────────────────────────────────┤
│  • RAG Engine (OpenSearch + Semantic Search)   │
│  • Claude Integration (CLI)                    │
│  • Agent OS (5 Autonomous Agents)              │
│  • Basic Memory Integration                    │
└─────────────────────────────────────────────────┘
```

### Agent Memory Structure

```
agent-os/memory/
├── patterns/        # Learned patterns
├── preferences/     # User preferences
├── executions/      # Execution history
├── insights/        # Generated insights
└── feedback/        # User feedback
```

## 📡 API Endpoints

### Core Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/generate` | POST | Generate response with Claude |
| `/query` | POST | RAG query (backward compatibility) |
| `/analyze_vault` | POST | Comprehensive vault analysis |
| `/synthesize_notes` | POST | Multi-document synthesis |
| `/get_context` | GET | Retrieve built context |

### Agent Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/agents/list` | GET | List all agents |
| `/agents/{name}/status` | GET | Get agent status |
| `/agents/{name}/execute` | POST | Execute agent |
| `/agents/{name}/history` | GET | Get execution history |
| `/scheduler/info` | GET | Get schedule information |

## 🧠 Agent Capabilities

### Vault Analyzer
- Daily pattern detection
- Knowledge gap identification
- Connection discovery
- Trend analysis
- Quality assessment

### Synthesis Assistant
- Thematic synthesis
- Chronological organization
- Argumentative synthesis
- Comparative analysis
- Contradiction detection

### Context Optimizer
- Index optimization
- Cache management
- Query pattern learning
- Performance tuning
- Token allocation

### Suggestion Engine
- Related note discovery
- Query improvements
- Workflow enhancements
- Knowledge gap alerts
- Proactive insights

### Research Assistant
- Literature review
- Evidence gathering
- Hypothesis testing
- Citation tracking
- Comprehensive reports

## 🔧 Development

### Local Development

```bash
# Backend development with hot reload
make app-local

# Plugin development with auto-rebuild
cd plugin && npm run dev

# Run tests
make test
```

### Adding New Agents

1. Define agent in `.agent-os/agents/config.yaml`
2. Create instructions in `.agent-os/instructions/agents/`
3. Implement agent class in `src/agents.py`
4. Add scheduler configuration if needed

## 📊 Performance Optimization

### Caching
- Redis for query caching
- Local context cache
- Precomputed common queries

### Indexing
- Incremental index updates
- Parallel document processing
- Optimized chunk sizes

### Context Strategies
- Smart token allocation
- Relevance-based prioritization
- Dynamic context adjustment

## 🐛 Troubleshooting

### Common Issues

**OpenSearch won't start**
```bash
# Check if port 9200 is already in use
lsof -i :9200
# Kill the process or change the port
```

**Indices not building**
```bash
# Ensure OBSIDIAN_PATH has trailing slash
echo $OBSIDIAN_PATH  # Should end with /
# Rebuild indices
make build-artifacts
```

**Agent not executing**
```bash
# Check agent status
curl http://localhost:8000/agents/vault-analyzer/status
# Check scheduler
curl http://localhost:8000/scheduler/info
```

## 📝 Memory and Learning

Agents store memories in your Obsidian vault via Basic Memory:

```markdown
# Pattern Memory
**Agent**: vault-analyzer
**Type**: pattern
## Observations
- [pattern] Detected pattern: Daily journaling
- [frequency] Occurrence count: 30
- [confidence] Confidence level: 0.95
```

This creates a searchable knowledge graph of agent learning that improves over time.

## 🔒 Privacy and Security

- **Local Processing**: All indexing and retrieval happens locally
- **No Data Collection**: No telemetry or usage tracking
- **API Security**: Only Claude API calls leave your machine
- **Vault Integrity**: Read-only access to your notes

## 🤝 Contributing

This is a private implementation. For the original project, see [obsidian-copilot](https://github.com/logancyang/obsidian-copilot).

## 📄 License

Private implementation based on MIT-licensed original.

## 🙏 Acknowledgments

- Original [obsidian-copilot](https://github.com/logancyang/obsidian-copilot) by Logan Yang
- Claude by Anthropic for the powerful LLM
- Basic Memory for semantic knowledge management
- OpenSearch for robust search capabilities

---

*Built with ❤️ for the Obsidian + Claude power user*