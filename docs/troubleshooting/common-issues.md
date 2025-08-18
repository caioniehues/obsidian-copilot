# 🔧 Troubleshooting Common Issues

> Solutions to frequently encountered problems with Obsidian Copilot

## Content and Search Issues

### "No relevant documents found"

**Symptoms:**
- Queries return no results despite having relevant content
- Empty responses from agents
- "No documents match your query" message

**Solutions:**
1. **Check vault path configuration:**
   ```bash
   # Ensure path ends with trailing slash
   export OBSIDIAN_PATH=/path/to/obsidian-vault/
   ```

2. **Rebuild search indices:**
   ```bash
   make opensearch
   # In another terminal:
   make build-artifacts
   ```

3. **Try broader search terms:**
   ```markdown
   # Instead of:
   ## specific technical jargon
   
   # Try:
   ## general concepts about [topic]
   ```

4. **Check document format:**
   - Ensure files are in `.md` format
   - Verify files are in the vault directory
   - Check for special characters in filenames

### "Response cut off" or Incomplete Responses

**Symptoms:**
- Responses end abruptly
- Missing conclusions or incomplete thoughts
- Context limit warnings

**Solutions:**
1. **Increase token limit:**
   ```markdown
   ## tokens=180000
   Your query here
   ```

2. **Continue previous response:**
   ```markdown
   ## continue
   Continue where you left off
   ```

3. **Use different strategy:**
   ```markdown
   ## strategy=hierarchical
   Quick overview (uses fewer tokens)
   ```

4. **Split complex queries:**
   ```markdown
   ## Part 1: Overview of topic
   ## Part 2: Deep dive into specifics
   ```

## Performance Issues

### "Slow responses"

**Symptoms:**
- Responses take 30+ seconds
- System feels sluggish
- Long waiting times between query and response

**Solutions:**
1. **Switch to faster strategy:**
   ```markdown
   ## strategy=hierarchical
   Your query here
   ```

2. **Reduce scope:**
   ```markdown
   ## timeframe="7d"
   ## folder="specific-folder"
   Your query here
   ```

3. **Check Context Optimizer status:**
   ```bash
   curl http://localhost:8000/agents/context-optimizer/status
   ```

4. **Clear caches if needed:**
   ```markdown
   ## agent:clear-cache
   ```

5. **Reduce token limit for faster processing:**
   ```markdown
   ## tokens=50000
   Your query here
   ```

### "System running out of memory"

**Symptoms:**
- Python process killed
- Docker containers crashing
- Very slow system performance

**Solutions:**
1. **Increase Docker memory allocation:**
   ```bash
   # Docker Desktop: Settings > Resources > Memory
   # Increase to 8GB or more for large vaults
   ```

2. **Use hierarchical strategy by default:**
   ```bash
   # In your environment variables:
   export DEFAULT_STRATEGY=hierarchical
   ```

3. **Process vault in smaller chunks:**
   ```bash
   make build-artifacts CHUNK_SIZE=500
   ```

## Agent-Specific Issues

### "Agents not responding"

**Symptoms:**
- Agent commands return no response
- Agents seem inactive or unresponsive
- Missing agent reports

**Solutions:**
1. **Check agent status:**
   ```bash
   curl http://localhost:8000/agents/list
   ```

2. **Restart agent scheduler:**
   ```bash
   make restart-scheduler
   ```

3. **Check agent logs:**
   ```bash
   tail -f .agent-os/logs/vault-analyzer.log
   tail -f .agent-os/logs/synthesis-assistant.log
   ```

4. **Manual agent activation:**
   ```markdown
   ## agent:analyze-vault
   Run analysis manually to kickstart system
   ```

5. **Verify agent dependencies:**
   ```bash
   # Ensure all required services are running
   docker ps
   ```

### "Agent memories not updating"

**Symptoms:**
- Agents don't seem to learn from interactions
- Repeated suggestions for same content
- No memory files appearing in vault

**Solutions:**
1. **Check memory storage permissions:**
   ```bash
   # Ensure vault is writable
   ls -la $OBSIDIAN_PATH
   ```

2. **Enable memory storage:**
   ```markdown
   ## agent:config enable-memory=true
   ```

3. **Manual memory save:**
   ```markdown
   ## agent:learn
   Store current context as learning
   ```

4. **Check memory file format:**
   ```markdown
   # Search for existing memories:
   tag:#agent:memory
   ```

## Model Download & Cache Issues

### "Failed to download model" or "Connection timeout"

**Problem**: The E5-small-v2 model can't be downloaded from Hugging Face.

**Solutions**:

1. **Test connectivity to Hugging Face**:
```bash
curl -I https://huggingface.co
# Should return HTTP/2 200
```

2. **Test model accessibility**:
```bash
# Test config file download
curl -L https://huggingface.co/intfloat/e5-small-v2/resolve/main/config.json
```

3. **Try manual Python download**:
```python
from sentence_transformers import SentenceTransformer
model = SentenceTransformer('intfloat/e5-small-v2')
print("✅ Model loaded successfully!")
```

4. **Check firewall/proxy settings** - Hugging Face might be blocked

### "Permission denied" on TRANSFORMER_CACHE

**Problem**: Can't write to the cache directory.

**Solutions**:
```bash
# Create cache directory with proper permissions
mkdir -p ~/.cache/huggingface/hub
chmod 755 ~/.cache/huggingface/hub

# Or use a different location
export TRANSFORMER_CACHE=/tmp/huggingface-cache
```

### "No space left on device"

**Problem**: Not enough disk space for model download.

**Solutions**:
1. Check available space: `df -h`
2. Need at least 200 MB free
3. Clear old cache: `rm -rf ~/.cache/huggingface/hub/models--intfloat--e5-small-v2`
4. Use different disk: `export TRANSFORMER_CACHE=/path/to/larger/disk`

### Model Loading Very Slow

**Problem**: Model takes forever to load.

**Solutions**:
1. **First run is always slow** - downloading 130 MB
2. **Check if already cached**:
```bash
ls -la ~/.cache/huggingface/hub/models--intfloat--e5-small-v2/
```
3. **Pre-download the model**:
```python
from sentence_transformers import SentenceTransformer
model = SentenceTransformer('intfloat/e5-small-v2')
model.save('/tmp/test-model')  # Test save
```

### Semantic Search Not Working

**Problem**: Only getting keyword matches, not semantic matches.

**Check**:
1. Model properly downloaded: Check cache directory
2. Embeddings built: Check `/data/doc_embeddings_array.npy` exists
3. Rebuild if needed: `make build-artifacts`

## Installation and Setup Issues

### "Docker containers won't start"

**Symptoms:**
- `make opensearch` fails
- Port conflicts
- Container build errors

**Solutions:**
1. **Check port availability:**
   ```bash
   lsof -i :8000  # Backend port
   lsof -i :9200  # OpenSearch port
   ```

2. **Clean Docker environment:**
   ```bash
   docker system prune -a
   make clean
   make build
   ```

3. **Use Podman if Docker issues persist:**
   ```bash
   export RUNTIME=podman
   make opensearch
   ```

4. **Check Docker Desktop status:**
   - Ensure Docker Desktop is running
   - Verify sufficient disk space
   - Check for required system updates

### "OpenSearch initialization fails"

**Symptoms:**
- OpenSearch container exits immediately
- Connection refused to localhost:9200
- Index creation failures

**Solutions:**
1. **Wait for full initialization:**
   ```bash
   # OpenSearch needs 30-60 seconds to start
   make opensearch
   # Wait for "OpenSearch is ready" message
   ```

2. **Check OpenSearch logs:**
   ```bash
   docker logs obsidian-copilot-opensearch
   ```

3. **Increase memory limits:**
   ```bash
   # Edit docker-compose.yml
   opensearch:
     environment:
       - "ES_JAVA_OPTS=-Xms2g -Xmx2g"
   ```

4. **Reset OpenSearch data:**
   ```bash
   make clean-opensearch
   make opensearch
   ```

## Plugin Integration Issues

### "Plugin not working in Obsidian"

**Symptoms:**
- No `##` trigger response
- Plugin appears disabled
- Console errors in developer tools

**Solutions:**
1. **Verify plugin installation:**
   ```bash
   make install-plugin
   # Check that files copied to .obsidian/plugins/
   ```

2. **Enable plugin in Obsidian:**
   - Settings > Community Plugins
   - Find "Obsidian Copilot"
   - Toggle to enable

3. **Check plugin configuration:**
   - Settings > Obsidian Copilot
   - Verify OpenAI API key
   - Check backend URL (http://localhost:8000)

4. **Restart Obsidian:**
   - Completely quit and restart Obsidian
   - Try plugin reload: Cmd/Ctrl + R

### "API key issues"

**Symptoms:**
- "Invalid API key" errors
- No response from OpenAI
- Authentication failures

**Solutions:**
1. **Verify API key format:**
   ```markdown
   # Should start with sk-
   sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   ```

2. **Check API key permissions:**
   - Ensure key has GPT-4 access
   - Verify account has sufficient credits
   - Test key directly with OpenAI API

3. **Update API key in settings:**
   - Obsidian Settings > Obsidian Copilot
   - Enter new API key
   - Save and restart plugin

## Configuration Issues

### "Environment variables not working"

**Symptoms:**
- System can't find vault
- Cache directory issues
- Path-related errors

**Solutions:**
1. **Verify environment variables:**
   ```bash
   echo $OBSIDIAN_PATH
   echo $TRANSFORMER_CACHE
   ```

2. **Set variables correctly:**
   ```bash
   # Must have trailing slash for vault path
   export OBSIDIAN_PATH=/Users/username/Documents/ObsidianVault/
   export TRANSFORMER_CACHE=/Users/username/.cache/huggingface/hub
   ```

3. **Make variables persistent:**
   ```bash
   # Add to ~/.bashrc or ~/.zshrc
   echo 'export OBSIDIAN_PATH=/path/to/vault/' >> ~/.bashrc
   ```

4. **Restart terminal and services:**
   ```bash
   source ~/.bashrc
   make restart-all
   ```

## Data and Index Issues

### "Indices out of sync with vault"

**Symptoms:**
- New notes not appearing in results
- Deleted notes still appearing
- Stale search results

**Solutions:**
1. **Rebuild all indices:**
   ```bash
   make clean-indices
   make build-artifacts
   ```

2. **Incremental index update:**
   ```bash
   make update-indices
   ```

3. **Check file modification times:**
   ```bash
   ls -la $OBSIDIAN_PATH
   # Compare with last index build time
   ```

### "Corrupted cache or indices"

**Symptoms:**
- Inconsistent results
- Search returning errors
- Agent behavior anomalies

**Solutions:**
1. **Clear all caches:**
   ```bash
   make clean
   rm -rf data/
   make build-artifacts
   ```

2. **Reset agent memories:**
   ```markdown
   ## agent:reset-memory agent="all"
   ```

3. **Rebuild from scratch:**
   ```bash
   make clean-all
   make build
   make opensearch
   make build-artifacts
   ```

## Debug Mode and Logging

### Enable Debug Logging

1. **Backend debug mode:**
   ```bash
   export LOG_LEVEL=DEBUG
   make run
   ```

2. **View detailed logs:**
   ```bash
   tail -f logs/backend.log
   tail -f .agent-os/logs/
   ```

3. **Plugin debug mode:**
   - Open Obsidian Developer Tools (F12)
   - Check Console tab for errors
   - Enable plugin debug logging in settings

### Common Error Patterns

1. **Connection refused:**
   - Backend not running
   - Port conflicts
   - Firewall blocking connections

2. **Memory errors:**
   - Insufficient system RAM
   - Large vault processing
   - Docker memory limits

3. **Authentication errors:**
   - Invalid or expired API keys
   - Rate limiting from OpenAI
   - Network connectivity issues

## Getting Help

### Information to Collect

When reporting issues, include:

1. **System information:**
   ```bash
   # Operating system and version
   uname -a
   
   # Docker version
   docker --version
   
   # Python version
   python --version
   ```

2. **Configuration:**
   ```bash
   echo "Vault path: $OBSIDIAN_PATH"
   echo "Cache path: $TRANSFORMER_CACHE"
   ```

3. **Error logs:**
   ```bash
   # Backend logs
   tail -50 logs/backend.log
   
   # Agent logs
   ls -la .agent-os/logs/
   ```

4. **Current status:**
   ```bash
   # Service status
   curl http://localhost:8000/health
   curl http://localhost:9200
   
   # Agent status
   curl http://localhost:8000/agents/list
   ```

### Support Channels

1. **Check documentation:**
   - [Installation Guide](../setup/installation.md)
   - [API Reference](../architecture/api-reference.md)

2. **Community support:**
   - GitHub Issues for bug reports
   - Discussions for questions

3. **Diagnostic tools:**
   ```bash
   # Self-diagnostic
   make diagnose
   
   # System health check
   make health-check
   ```

---

**Navigation**: [← Advanced Features](../usage/advanced-features.md) | [Setup →](../setup/installation.md)