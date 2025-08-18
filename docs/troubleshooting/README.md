# 🔧 Troubleshooting

> Solutions and help for common issues

## Available Guides

- **[Common Issues](./common-issues.md)** - Comprehensive troubleshooting guide
  - Content and search problems
  - Performance issues
  - Agent-specific issues
  - Installation and setup problems
  - Configuration issues
  - Debug mode and logging

## Quick Help

### Most Common Issues

1. **"No relevant documents found"**
   - Check vault path ends with `/`
   - Rebuild indices: `make build-artifacts`

2. **"Slow responses"**
   - Use `strategy=hierarchical`
   - Check Context Optimizer status

3. **"Agents not responding"**
   - Check status: `curl http://localhost:8000/agents/list`
   - Restart scheduler: `make restart-scheduler`

### Quick Diagnostics

```bash
# System health check
make health-check

# Service status
curl http://localhost:8000/health
curl http://localhost:9200

# Agent status
curl http://localhost:8000/agents/list
```

---

**Navigation**: [← Documentation Home](../README.md) | [Common Issues →](./common-issues.md)