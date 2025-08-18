# Migration Guide: Claude Integration

## Upgrading from OpenAI-only Version

This guide helps you migrate from the OpenAI-only version of Obsidian Copilot to the new version with Claude support.

## What's New

- **Dual Backend Support**: Choose between OpenAI and Claude for text generation
- **Claude Code CLI Integration**: Use Claude with 200K token context window
- **Improved Settings UI**: Organized settings with backend-specific options
- **Simulated Streaming**: Better UX when using Claude backend
- **Backward Compatibility**: OpenAI continues to work exactly as before

## Migration Steps

### 1. Update Your Code

```bash
# Pull the latest changes
git pull origin main

# Rebuild Docker image with Claude support
make build
```

### 2. Update Dependencies

The backend now requires additional Python packages:

```bash
# These are automatically installed when you rebuild the Docker image
# If running locally, install them manually:
pip install -r requirements.txt
```

### 3. Configure Environment

#### Option A: Using .env file (Recommended)

```bash
# Copy the new environment template
cp .env.example .env

# Edit .env and add Claude configuration
USE_CLAUDE_BACKEND=false  # Set to true when ready to switch
CLAUDE_CODE_PATH=/usr/local/bin/claude
CLAUDE_MODEL=claude-3-5-sonnet-20241022
MAX_CONTEXT_TOKENS=100000
```

#### Option B: Using shell environment

```bash
# Add to ~/.bashrc or ~/.zshrc
export USE_CLAUDE_BACKEND=false
export CLAUDE_CODE_PATH=/usr/local/bin/claude
export CLAUDE_MODEL=claude-3-5-sonnet-20241022
```

### 4. Install Claude Code CLI (Optional)

If you want to use Claude backend:

```bash
# Install Claude Code CLI following Anthropic's instructions
# Verify installation:
claude --version
```

### 5. Update Docker Compose

The `docker-compose.yml` has been updated to support Claude. If you have local modifications:

```yaml
# Add these environment variables to obsidian-copilot service:
environment:
  - USE_CLAUDE_BACKEND=${USE_CLAUDE_BACKEND:-false}
  - CLAUDE_CODE_PATH=${CLAUDE_CODE_PATH:-/usr/local/bin/claude}
  - CLAUDE_MODEL=${CLAUDE_MODEL:-claude-3-5-sonnet-20241022}

# Add Claude CLI mount to volumes:
volumes:
  - ${CLAUDE_CODE_PATH:-/usr/local/bin/claude}:/usr/local/bin/claude:ro
```

### 6. Restart Services

```bash
# Stop existing services
docker-compose down

# Start with new configuration
make run
```

### 7. Update Plugin Settings

1. Open Obsidian
2. Go to Settings → Copilot
3. You'll see new options:
   - **Use Claude Backend**: Toggle to switch between OpenAI and Claude
   - **Backend URL**: Ensure it points to your backend (default: http://localhost:8000)
   - **Claude Model**: Choose your preferred model (when Claude is enabled)

## Troubleshooting

### Issue: "Claude Code not found"

**Solution**: Ensure Claude CLI is installed and the path is correct:
```bash
which claude  # Find Claude installation path
export CLAUDE_CODE_PATH=/path/to/claude
```

### Issue: "No response from retrieval API"

**Solution**: Check backend URL in plugin settings matches your server:
- Local: `http://localhost:8000`
- Docker: `http://localhost:8000`
- Remote: `http://your-server:8000`

### Issue: "Generation timeout"

**Solution**: Claude may take longer for large contexts. Increase timeout:
```bash
export GENERATION_TIMEOUT=120  # 2 minutes
```

### Issue: Docker can't find Claude

**Solution**: Mount Claude from host system:
```bash
docker run -v $(which claude):/usr/local/bin/claude:ro ...
```

## Testing Your Setup

### Test OpenAI (existing functionality)

1. Ensure "Use Claude Backend" is OFF in settings
2. Provide OpenAI API key
3. Try generating content - should work as before

### Test Claude (new functionality)

1. Toggle "Use Claude Backend" to ON
2. Ensure backend server has access to Claude CLI
3. Try generating content - should use Claude

### Test Switching

1. Generate with OpenAI
2. Switch to Claude in settings
3. Generate again - should use Claude
4. Switch back - should use OpenAI

## Performance Comparison

| Aspect | OpenAI | Claude |
|--------|--------|--------|
| **First Token Latency** | 1-2 seconds | 5-10 seconds |
| **Streaming** | Native | Simulated |
| **Context Window** | 4K-16K tokens | 200K tokens |
| **Cost Model** | Per token | Subscription |
| **Quality** | Excellent | Excellent |

## Best Practices

1. **Start with OpenAI**: If you're unsure, keep using OpenAI initially
2. **Test Claude Gradually**: Try Claude on a few documents first
3. **Monitor Performance**: Claude may be slower but handles larger contexts
4. **Use Appropriate Models**:
   - Quick drafts: OpenAI GPT-3.5 or Claude Haiku
   - Quality content: OpenAI GPT-4 or Claude Sonnet/Opus
5. **Adjust Context Size**: With Claude, you can include more context

## Rollback Instructions

If you need to rollback to OpenAI-only version:

```bash
# In plugin settings
1. Set "Use Claude Backend" to OFF
2. Save settings

# Or rollback code (if needed)
git checkout <previous-commit-hash>
make build
make run
```

## Support

For issues or questions:
1. Check the [README](README.md) for general setup
2. Review this migration guide
3. Check [GitHub Issues](https://github.com/eugeneyan/obsidian-copilot/issues)
4. Create a new issue with:
   - Your configuration (OpenAI/Claude)
   - Error messages
   - Steps to reproduce

## Next Steps

After successful migration:
1. Experiment with Claude's larger context window
2. Compare output quality between backends
3. Optimize your prompts for each model
4. Share feedback on performance and quality

---

*Migration guide version: 1.0*
*Last updated: 2025-01-18*