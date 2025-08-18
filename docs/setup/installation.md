# 🚀 Complete Setup Guide for Obsidian Copilot + Agent OS

> Time required: ~20 minutes  
> Difficulty: Intermediate  
> Result: Intelligent AI companion for your Obsidian vault

## 📋 Before You Start

### Required Software

1. **Obsidian** (v0.12.0 or higher)
   - Download from: https://obsidian.md
   - Enable community plugins in Settings → Community Plugins

2. **Docker Desktop** or **Podman**
   - Docker Desktop: https://www.docker.com/products/docker-desktop
   - Or Podman: https://podman.io/getting-started/installation

3. **Node.js** (v18 or higher)
   - Download from: https://nodejs.org
   - Verify: `node --version` should show v18.x.x or higher

4. **Python** (v3.11 or higher)
   - Download from: https://python.org
   - Verify: `python3 --version` should show 3.11.x or higher

5. **Claude Access** (choose one):
   - Claude Code CLI: https://claude.ai/code
   - Or Claude API key from Anthropic

6. **Basic Memory MCP Server** (for agent memory)
   - Installation guide: https://github.com/waldzx/basic-memory

### System Requirements

- **RAM**: 8GB minimum, 16GB recommended
- **Storage**: 5GB free space
- **OS**: macOS, Linux, or Windows with WSL2

## 🛠️ Step-by-Step Installation

### Step 1: Clone the Repository

```bash
# Clone the repository
git clone https://github.com/caioniehues/obsidian-copilot.git

# Enter the directory
cd obsidian-copilot
```

### Step 2: Set Environment Variables

```bash
# Create environment file from template
cp .env.example .env

# Edit the .env file with your settings
nano .env  # or use your preferred editor
```

**Required variables to set:**

```bash
# Path to your Obsidian vault (MUST end with /)
OBSIDIAN_PATH=/Users/yourname/Documents/ObsidianVault/

# Path for AI model cache (stores the E5-small-v2 semantic search model)
# This ~130 MB model enables intelligent note retrieval by understanding meaning, not just keywords
TRANSFORMER_CACHE=/Users/yourname/.cache/huggingface/hub

# Claude configuration (choose one)
CLAUDE_CLI_PATH=/usr/local/bin/claude  # If using Claude Code CLI
# OR
CLAUDE_API_KEY=sk-ant-xxxxx  # If using API key
```

**Optional variables:**

```bash
# Claude model selection
CLAUDE_MODEL=claude-3-5-sonnet-20241022

# Context settings
MAX_CONTEXT_TOKENS=150000
CONTEXT_STRATEGY=smart_chunks

# Performance tuning
CACHE_ENABLED=true
MAX_CONCURRENT_AGENTS=3
```

**📊 About Model Caching**: 
The TRANSFORMER_CACHE stores the E5-small-v2 model used for semantic search. This model:
- Downloads automatically on first use (~130 MB)
- Converts your notes into mathematical vectors for similarity matching
- Enables finding conceptually related notes (e.g., "productivity" finds notes about "efficiency", "GTD", "time management")
- Only downloads once - cached for all future uses
- Can be safely deleted and will re-download if needed

### Step 3: Build Docker Image

```bash
# Build the Docker image (this takes 5-10 minutes)
make build
```

**Expected output:**
```
Building Docker image...
[+] Building 234.5s (15/15) FINISHED
Successfully built obsidian-copilot:latest
```

### Step 4: Start OpenSearch

```bash
# Start OpenSearch container
make opensearch
```

**Expected output:**
```
Starting OpenSearch...
OpenSearch is running on http://localhost:9200
```

⏱️ **Wait 30 seconds** for OpenSearch to fully initialize before proceeding.

### Step 5: Build Search Indices

Open a **new terminal** window and run:

```bash
# Build the search indices from your vault
make build-artifacts
```

**Expected output:**
```
Building search indices...
Processing 523 notes...
✓ OpenSearch index created
✓ Semantic index created
✓ Graph relationships mapped
Indices built successfully!
```

This step analyzes all your notes and creates searchable indices. Time depends on vault size:
- 100 notes: ~1 minute
- 500 notes: ~3 minutes
- 1000+ notes: ~5-10 minutes

### Step 6: Start the Backend with Agent OS

```bash
# Start the FastAPI backend with agents
make run
```

**Expected output:**
```
Starting Obsidian Copilot backend...
INFO: Agent OS initialized with 5 agents
INFO: Scheduler started
INFO: Uvicorn running on http://0.0.0.0:8000
INFO: Application startup complete
```

✅ The backend is now running! Keep this terminal open.

### Step 7: Build and Install the Obsidian Plugin

Open another **new terminal** and run:

```bash
# Navigate to plugin directory
cd plugin

# Install dependencies
npm install

# Build the plugin
npm run build
```

**Expected output:**
```
> obsidian-copilot@1.0.0 build
> node esbuild.config.mjs

✓ Plugin built successfully
✓ Output: main.js (2.3 MB)
```

Now install to Obsidian:

```bash
# Go back to root directory
cd ..

# Install plugin to your vault
make install-plugin
```

**Note**: If this fails, manually copy the plugin:

```bash
# Manual installation (replace path with your vault path)
cp -r plugin/* /path/to/your/vault/.obsidian/plugins/obsidian-copilot/
```

### Step 8: Enable Plugin in Obsidian

1. Open Obsidian
2. Go to **Settings** (⚙️ icon)
3. Navigate to **Community plugins**
4. Click **Reload plugins** button
5. Find **Obsidian Copilot** in the list
6. Toggle it **ON** ✅

### Step 9: Configure Plugin Settings

In Obsidian settings, find **Obsidian Copilot** and configure:

```javascript
Backend URL: http://localhost:8000
Claude Model: claude-3-5-sonnet-20241022
Context Strategy: smart_chunks
Max Context Tokens: 150000
Show Generation Time: true
Enable Agents: true
```

### Step 10: Verify Everything Works

#### Test Basic Generation

1. Create a new note in Obsidian
2. Type:
   ```markdown
   ## What is machine learning?
   ```
3. Wait 5-10 seconds
4. You should see a response generated below

#### Check Agent Status

In terminal:

```bash
# List all agents
curl http://localhost:8000/agents/list

# Check scheduler
curl http://localhost:8000/scheduler/info
```

**Expected response:**
```json
[
  {"name": "vault-analyzer", "enabled": true, "type": "autonomous"},
  {"name": "synthesis-assistant", "enabled": true, "type": "reactive"},
  {"name": "context-optimizer", "enabled": true, "type": "background"},
  {"name": "suggestion-engine", "enabled": true, "type": "proactive"},
  {"name": "research-assistant", "enabled": true, "type": "interactive"}
]
```

## 🎯 Quick Test Commands

Try these in any Obsidian note:

```markdown
## Tell me about transformers in AI

## agent:synthesize
Synthesize my notes on productivity

## agent:research
Research the history of neural networks

## agent:analyze-vault
Run vault analysis now
```

## 🐛 Troubleshooting

### Common Issues and Solutions

#### "Cannot connect to backend"
```bash
# Check if backend is running
curl http://localhost:8000/health

# If not, restart:
make restart
```

#### "OpenSearch connection refused"
```bash
# Check if OpenSearch is running
docker ps | grep opensearch

# If not running:
docker start opensearch-node1
```

#### "No documents retrieved"
```bash
# Rebuild indices
make build-artifacts
```

#### "Plugin not showing in Obsidian"
1. Check plugin is in correct folder:
   ```bash
   ls ~/.obsidian/plugins/obsidian-copilot/
   ```
2. Should see: `main.js`, `manifest.json`, `styles.css`
3. Reload Obsidian: Cmd/Ctrl + R

#### "Agents not running"
```bash
# Check agent status
curl http://localhost:8000/agents/vault-analyzer/status

# Manually trigger agent
curl -X POST http://localhost:8000/agents/vault-analyzer/execute
```

#### "Permission denied errors"
```bash
# Fix permissions
chmod -R 755 obsidian-copilot/
chmod +x obsidian-copilot/scripts/*
```

## 🔄 Daily Usage

### Starting the System

Every time you want to use Obsidian Copilot:

```bash
# 1. Start OpenSearch (if not running)
make opensearch

# 2. Start backend
make run

# 3. Open Obsidian
# Plugin loads automatically
```

### Stopping the System

```bash
# Stop backend: Ctrl+C in terminal

# Stop OpenSearch
docker stop opensearch-node1

# Or stop everything
make stop-all
```

### Updating Indices

After adding many new notes:

```bash
make update-indices
```

## 📊 Performance Tips

### For Large Vaults (1000+ notes)

1. **Initial indexing**: Use smaller batches
   ```bash
   BATCH_SIZE=100 make build-artifacts
   ```

2. **Reduce memory usage**: Edit `.env`
   ```bash
   MAX_CONTEXT_TOKENS=100000
   CONTEXT_STRATEGY=hierarchical
   ```

3. **Limit concurrent agents**: Edit `.agent-os/agents/config.yaml`
   ```yaml
   global:
     max_concurrent_agents: 2
   ```

### For Faster Responses

1. Enable caching in `.env`:
   ```bash
   CACHE_ENABLED=true
   REDIS_HOST=localhost
   ```

2. Use smart_chunks strategy (balanced performance)

3. Precompute common queries:
   ```bash
   make precompute-common
   ```

## 🎓 Next Steps

### Learn the Commands

See [USER_GUIDE.md](../usage/basic-usage.md) for:
- All agent commands
- Context strategies
- Advanced features

### Configure Agents

Edit `.agent-os/agents/config.yaml` to:
- Change schedules
- Enable/disable agents
- Customize behaviors

### Monitor Agent Learning

Agents store memories in your vault:
- Search `tag:#agent:vault-analyzer` to see what Vault Analyzer learned
- Search `tag:#type:pattern` to see detected patterns
- Search `tag:#type:insight` to see generated insights

## 🆘 Getting Help

### Check Logs

```bash
# Backend logs
docker logs obsidian-copilot-backend

# Agent logs
cat .agent-os/logs/agents.log

# System diagnostics
make diagnose
```

### Resources

- **User Guide**: [USER_GUIDE.md](../usage/basic-usage.md)
- **Agent Documentation**: [AGENTS.md](../agents/overview.md)
- **API Reference**: [API.md](./API.md)
- **GitHub Issues**: Report bugs or request features

## ✅ Success Checklist

- [ ] Docker/Podman installed and running
- [ ] Node.js v18+ installed
- [ ] Repository cloned
- [ ] Environment variables set
- [ ] Docker image built
- [ ] OpenSearch running
- [ ] Indices built from vault
- [ ] Backend running
- [ ] Plugin built and installed
- [ ] Plugin enabled in Obsidian
- [ ] Test query successful
- [ ] Agents responding

Once all items are checked, you have a fully functional AI-powered Obsidian companion!

---

**Tip**: Keep the backend terminal open while using Obsidian Copilot. The system needs to be running for the plugin to work.