# Installation Guide

Complete step-by-step installation for Obsidian Copilot with Agent OS.

## Prerequisites

### Required Software

1. **Obsidian** (v0.12.0+) - [Download](https://obsidian.md)
2. **Docker Desktop** or **Podman** - [Docker](https://docker.com) | [Podman](https://podman.io)
3. **Node.js** (v18+) - [Download](https://nodejs.org)
4. **Python** (3.11+) - [Download](https://python.org)
5. **Git** - [Download](https://git-scm.com)
6. **Claude Access** - Either Claude CLI or API key
7. **Basic Memory MCP** - [Setup Guide](https://github.com/waldzx/basic-memory)

### System Requirements

- **RAM**: 8GB minimum (16GB recommended)
- **Storage**: 5GB free space
- **OS**: macOS, Linux, or Windows with WSL2

## Step-by-Step Installation

### Step 1: Clone Repository

```bash
git clone https://github.com/caioniehues/obsidian-copilot.git
cd obsidian-copilot
```

### Step 2: Configure Environment

Create `.env` file:

```bash
cp .env.example .env
nano .env  # or your preferred editor
```

Required variables:

```bash
# MUST end with trailing slash!
OBSIDIAN_PATH=/path/to/your/vault/

# Model cache location
TRANSFORMER_CACHE=/home/user/.cache/huggingface/hub

# Claude configuration (choose one)
CLAUDE_CLI_PATH=/usr/local/bin/claude
# OR
CLAUDE_API_KEY=sk-ant-xxxxx
```

### Step 3: Build Docker Image

```bash
make build
```

Expected output:
```
Building Docker image...
Successfully built obsidian-copilot:latest
```

This takes 5-10 minutes on first run.

### Step 4: Start OpenSearch

```bash
make opensearch
```

Expected output:
```
Starting OpenSearch...
OpenSearch is running on http://localhost:9200
```

⏰ **Wait 30 seconds for initialization**

### Step 5: Build Search Indices

In a **new terminal**:

```bash
make build-artifacts
```

Expected output:
```
Processing 523 notes...
✓ OpenSearch index created
✓ Semantic index created
Indices built successfully!
```

Time depends on vault size:
- 100 notes: ~1 minute
- 500 notes: ~3 minutes  
- 1000+ notes: ~5-10 minutes

### Step 6: Start Backend

```bash
make run
```

Expected output:
```
INFO: Agent OS initialized with 5 agents
INFO: Scheduler started
INFO: Uvicorn running on http://0.0.0.0:8000
```

Keep this terminal open!

### Step 7: Build Obsidian Plugin

In another **new terminal**:

```bash
cd plugin
npm install
npm run build
```

Expected output:
```
✓ Plugin built successfully
✓ Output: main.js (2.3 MB)
```

### Step 8: Install Plugin

```bash
cd ..
make install-plugin
```

If this fails, manually copy:

```bash
cp -r plugin/* /path/to/vault/.obsidian/plugins/obsidian-copilot/
```

### Step 9: Enable in Obsidian

1. Open Obsidian
2. Go to **Settings** → **Community plugins**
3. Click **Reload plugins**
4. Find **Obsidian Copilot**
5. Toggle **ON** ✅

### Step 10: Configure Plugin

In Obsidian settings → Obsidian Copilot:

- **Backend URL**: `http://localhost:8000`
- **Claude Model**: `claude-3-5-sonnet-20241022`
- **Context Strategy**: `smart_chunks`
- **Max Tokens**: `150000`

## Verification

### Test Basic Generation

In any note:

```markdown
## What is quantum computing?
```

Should generate response in 5-10 seconds.

### Check Agents

```bash
curl http://localhost:8000/agents/list
```

Should show 5 agents with `enabled: true`.

## Platform-Specific Notes

### macOS

Install Xcode tools first:
```bash
xcode-select --install
```

### Linux

Install build essentials:
```bash
sudo apt update
sudo apt install build-essential curl wget
```

### Windows

Use WSL2:
```powershell
wsl --install
```

Then follow Linux instructions inside WSL.

## Troubleshooting

### "Cannot connect to backend"

Check backend is running:
```bash
curl http://localhost:8000/health
```

### "No documents retrieved"

Rebuild indices:
```bash
make build-artifacts
```

### "Plugin not showing"

1. Check plugin folder exists
2. Reload Obsidian with Cmd/Ctrl + R
3. Check Community Plugins enabled

## Next Steps

- Read [[First Steps]] guide
- Explore [[Agent Overview]]
- Learn [[Basic Commands]]

---

[[Home]] | [[Quick Start]] →