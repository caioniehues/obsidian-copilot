# ⚡ Quick Start Guide

> For experienced users who want to get running in 5 minutes

## Prerequisites Check

```bash
# Verify requirements
docker --version  # Docker version 20+ or Podman
node --version    # v18+
python3 --version # v3.11+
```

## Fast Setup

```bash
# 1. Clone and enter
git clone https://github.com/caioniehues/obsidian-copilot.git && cd obsidian-copilot

# 2. Configure (IMPORTANT: path must end with /)
export OBSIDIAN_PATH=/path/to/vault/
export TRANSFORMER_CACHE=~/.cache/huggingface/hub

# 3. Build and start
make build && make opensearch

# 4. Wait 30 seconds, then in new terminal:
make build-artifacts && make run

# 5. In third terminal, build plugin:
cd plugin && npm install && npm run build && cd .. && make install-plugin
```

## Enable in Obsidian

1. Settings → Community plugins → Reload
2. Find "Obsidian Copilot" → Toggle ON
3. Configure: `http://localhost:8000`

## Test

In any note:
```markdown
## What is quantum computing?
```

## Essential Commands

### Agent Commands
```markdown
## agent:synthesize
## agent:research  
## agent:analyze-vault
```

### System Commands
```bash
make status          # Check system
make restart         # Restart all
make logs           # View logs
make stop-all       # Stop everything
```

## Quick Troubleshooting

| Issue | Fix |
|-------|-----|
| Connection refused | `make restart` |
| No results | `make build-artifacts` |
| Plugin missing | `make install-plugin` then reload Obsidian |
| Slow responses | Use `hierarchical` context strategy |

## Next Steps

- Full guide: [SETUP_GUIDE.md](./SETUP_GUIDE.md)
- Usage: [USER_GUIDE.md](./USER_GUIDE.md)
- Agents: [AGENTS.md](./AGENTS.md)