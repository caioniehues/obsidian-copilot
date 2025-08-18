# 🔧 Agent OS Troubleshooting & Advanced Configuration

> Comprehensive guide for diagnosing issues and optimizing Agent OS performance

## Quick Diagnostics

### System Health Check
```bash
# Check if all agents are running
curl http://localhost:8000/agents/list

# Verify scheduler status
curl http://localhost:8000/scheduler/info

# Check system metrics
curl http://localhost:8000/system/metrics
```

### Log Access
```bash
# View agent logs
tail -f ~/.obsidian-copilot/logs/agents.log

# Filter by specific agent
grep "vault-analyzer" ~/.obsidian-copilot/logs/agents.log

# View error logs only
grep "ERROR" ~/.obsidian-copilot/logs/agents.log
```

## Common Issues & Solutions

### Agents Not Running

#### Symptoms
- No agent activity in logs
- API returns empty agent list
- Scheduled tasks not executing

#### Diagnosis Steps
1. **Check Agent Configuration**
   ```bash
   # Verify config file exists
   ls -la .agent-os/agents/config.yaml
   
   # Validate YAML syntax
   python -c "import yaml; yaml.safe_load(open('.agent-os/agents/config.yaml'))"
   ```

2. **Verify Agent Status**
   ```bash
   curl http://localhost:8000/agents/vault-analyzer/status
   ```

3. **Check Process Status**
   ```bash
   ps aux | grep obsidian-copilot
   netstat -tlnp | grep 8000
   ```

#### Solutions

**Agent Disabled in Config**
```yaml
# Fix: Enable in .agent-os/agents/config.yaml
agents:
  vault-analyzer:
    enabled: true  # Change from false
```

**Scheduler Not Running**
```bash
# Restart the scheduler
curl -X POST http://localhost:8000/scheduler/restart

# Or restart entire service
make restart
```

**Port Conflicts**
```bash
# Check what's using port 8000
lsof -i :8000

# Change port in config
export OBSIDIAN_COPILOT_PORT=8001
make run
```

### Poor Quality Suggestions

#### Symptoms
- Irrelevant suggestions
- Repeated suggestions
- No suggestions appearing

#### Diagnosis Steps
1. **Check Agent Memories**
   ```bash
   # View pattern memories
   curl http://localhost:8000/agents/suggestion-engine/memories?type=pattern
   
   # Check feedback history
   curl http://localhost:8000/agents/suggestion-engine/memories?type=feedback
   ```

2. **Verify Learning Data**
   ```bash
   # Search for agent memories in Basic Memory
   grep -r "suggestion-engine" ~/.obsidian-copilot/memories/
   ```

#### Solutions

**Insufficient Learning Time**
- Allow at least 1 week for pattern recognition
- Provide explicit feedback on suggestions
- Use agents regularly to build patterns

**Low Confidence Threshold**
```yaml
# Increase quality bar in config
agents:
  suggestion-engine:
    configuration:
      confidence_threshold: 0.8  # Increase from 0.5
      max_suggestions: 3         # Reduce noise
```

**Clear Bad Patterns**
```bash
# Remove poor quality memories
curl -X DELETE http://localhost:8000/agents/suggestion-engine/memories/mem_12345

# Or reset all memories
curl -X POST http://localhost:8000/agents/suggestion-engine/reset-memories
```

### Performance Issues

#### Symptoms
- Slow query responses
- High CPU/memory usage
- Frequent timeouts

#### Diagnosis Steps
1. **Monitor Resource Usage**
   ```bash
   # Check system metrics
   curl http://localhost:8000/system/metrics
   
   # View cache performance
   curl http://localhost:8000/system/cache/stats
   ```

2. **Identify Bottlenecks**
   ```bash
   # Check query latency
   grep "query_latency" ~/.obsidian-copilot/logs/agents.log
   
   # Monitor token usage
   grep "token_utilization" ~/.obsidian-copilot/logs/agents.log
   ```

#### Solutions

**Reduce Concurrent Agents**
```yaml
global:
  max_concurrent_agents: 2  # Reduce from 3 or higher
  default_timeout: 30       # Shorter timeouts
```

**Optimize Token Usage**
```yaml
global:
  max_context_tokens: 100000  # Reduce from 150000
  
agents:
  vault-analyzer:
    configuration:
      max_documents_per_run: 50  # Reduce batch size
      analysis_depth: 2          # Lighter analysis
```

**Improve Caching**
```yaml
global:
  cache_config:
    hot_cache_mb: 200      # Increase memory cache
    warm_cache_mb: 1000    # Increase Redis cache
    cache_ttl_hours: 2     # Longer cache retention
```

**Disable Resource-Heavy Agents**
```yaml
agents:
  research-assistant:
    enabled: false  # Disable most resource-intensive agent
  
  vault-analyzer:
    trigger:
      interval: weekly  # Reduce frequency from daily
```

### Memory and Learning Issues

#### Symptoms
- Agents not remembering patterns
- Basic Memory integration failures
- Missing memory files

#### Diagnosis Steps
1. **Verify Basic Memory Connection**
   ```bash
   # Test Basic Memory API
   curl http://localhost:8000/basic-memory/status
   
   # Check memory directory
   ls -la ~/.obsidian-copilot/memories/agent-os/
   ```

2. **Validate Memory Format**
   ```bash
   # Check memory file syntax
   head -20 ~/.obsidian-copilot/memories/agent-os/patterns/mem_123.md
   ```

#### Solutions

**Basic Memory Not Configured**
```bash
# Install Basic Memory MCP
pip install basic-memory-mcp

# Configure connection
export BASIC_MEMORY_PATH=~/.obsidian-copilot/memories
```

**Corrupted Memory Files**
```bash
# Validate and repair memories
python scripts/repair_memories.py

# Or reset all memories (nuclear option)
rm -rf ~/.obsidian-copilot/memories/agent-os/
```

**Permission Issues**
```bash
# Fix memory directory permissions
chmod -R 755 ~/.obsidian-copilot/memories/
chown -R $USER ~/.obsidian-copilot/memories/
```

### API and Integration Issues

#### Symptoms
- 500 errors from API endpoints
- WebSocket disconnections
- Plugin communication failures

#### Diagnosis Steps
1. **Check API Health**
   ```bash
   # Test core endpoints
   curl http://localhost:8000/health
   curl http://localhost:8000/agents/list
   ```

2. **Verify WebSocket Connection**
   ```javascript
   // In browser console
   const ws = new WebSocket('ws://localhost:8000/ws/events');
   ws.onopen = () => console.log('Connected');
   ws.onerror = (e) => console.error('Error:', e);
   ```

#### Solutions

**CORS Issues**
```yaml
# Update CORS settings
api:
  cors_origins: 
    - "app://obsidian.md"
    - "http://localhost:3000"  # Add development origins
```

**Authentication Problems**
```bash
# Reset API tokens
curl -X POST http://localhost:8000/auth/reset-tokens
```

**WebSocket Proxy Issues**
```nginx
# Fix nginx proxy config
location /ws/ {
    proxy_pass http://localhost:8000;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
}
```

## Advanced Configuration

### Performance Tuning by Vault Size

#### Small Vaults (<100 notes)
```yaml
global:
  max_concurrent_agents: 5
  max_context_tokens: 200000
  default_timeout: 90

agents:
  vault-analyzer:
    configuration:
      analysis_depth: 5
      max_documents_per_run: 100
  
  context-optimizer:
    configuration:
      cache_size_mb: 100
      optimization_frequency: 1  # Every minute
```

#### Medium Vaults (100-1000 notes)  
```yaml
global:
  max_concurrent_agents: 3
  max_context_tokens: 150000
  default_timeout: 60

agents:
  vault-analyzer:
    configuration:
      analysis_depth: 3
      max_documents_per_run: 75
  
  context-optimizer:
    configuration:
      cache_size_mb: 500
      optimization_frequency: 5  # Every 5 minutes
```

#### Large Vaults (1000+ notes)
```yaml
global:
  max_concurrent_agents: 2
  max_context_tokens: 100000
  default_timeout: 45

agents:
  vault-analyzer:
    configuration:
      analysis_depth: 2
      max_documents_per_run: 50
      batch_processing: true
  
  context-optimizer:
    configuration:
      cache_size_mb: 1000
      optimization_frequency: 10  # Every 10 minutes
      aggressive_pruning: true
```

### Custom Agent Schedules

#### Business Hours Only
```yaml
agents:
  vault-analyzer:
    trigger:
      type: schedule
      cron: "0 9 * * 1-5"  # 9 AM weekdays only
  
  suggestion-engine:
    trigger:
      type: conditional
      conditions:
        - time_range: "09:00-17:00"
        - weekdays_only: true
```

#### Off-Peak Processing
```yaml
agents:
  research-assistant:
    trigger:
      type: schedule
      cron: "0 2 * * *"    # 2 AM daily
      priority: low
  
  synthesis-assistant:
    trigger:
      type: schedule  
      cron: "0 3 * * 0"    # 3 AM Sundays
      batch_mode: true
```

### Memory Management Configuration

#### Memory Retention Policies
```yaml
memory_config:
  retention_policies:
    pattern_memories:
      max_age_days: 90
      min_confidence: 0.7
      max_count: 1000
    
    execution_memories:
      max_age_days: 30
      max_count: 500
    
    feedback_memories:
      max_age_days: 180  # Keep feedback longer
      min_relevance: 0.5
```

#### Memory Cleanup Automation  
```yaml
memory_config:
  cleanup:
    enabled: true
    schedule: "0 4 * * 0"  # 4 AM Sundays
    strategies:
      - remove_duplicates
      - merge_similar_patterns
      - archive_old_executions
      - compress_low_relevance
```

### Advanced Monitoring

#### Custom Metrics Collection
```yaml
monitoring:
  custom_metrics:
    - name: "vault_growth_rate"
      query: "SELECT COUNT(*) FROM notes WHERE created > NOW() - INTERVAL 7 DAY"
      frequency: "daily"
    
    - name: "synthesis_quality_score"
      agent: "synthesis-assistant"
      metric: "average_user_rating"
      window: "30d"
```

#### Alert Configuration
```yaml
alerts:
  rules:
    - name: "Agent Execution Failures"
      condition: "agent_failures > 3 in 1h"
      action: "email"
      recipients: ["user@example.com"]
    
    - name: "High Memory Usage"
      condition: "memory_usage > 80%"
      action: "scale_down_agents"
      auto_remediation: true
```

### Integration Configurations

#### External Tool Integration
```yaml
integrations:
  external_tools:
    notion:
      enabled: true
      api_key: "${NOTION_API_KEY}"
      sync_schedule: "0 */6 * * *"  # Every 6 hours
    
    readwise:
      enabled: true
      api_token: "${READWISE_TOKEN}"  
      import_highlights: true
```

#### Webhook Configuration
```yaml
webhooks:
  endpoints:
    - name: "agent_completion"
      url: "https://api.example.com/agent-webhook"
      events: ["agent_completed", "insight_generated"]
      headers:
        Authorization: "Bearer ${WEBHOOK_TOKEN}"
```

## Debugging Tools

### Enable Debug Mode
```bash
# Set debug environment variables
export OBSIDIAN_COPILOT_DEBUG=true
export OBSIDIAN_COPILOT_LOG_LEVEL=debug

# Restart with debug logging
make run
```

### Trace Execution
```bash
# Enable execution tracing
curl -X POST http://localhost:8000/debug/enable-tracing

# View trace data
curl http://localhost:8000/debug/traces/latest
```

### Memory Analysis
```bash
# Analyze memory usage patterns
python scripts/analyze_memory_usage.py

# Generate memory usage report
curl http://localhost:8000/debug/memory-report > memory_report.json
```

### Performance Profiling
```bash
# Enable performance profiling
curl -X POST http://localhost:8000/debug/enable-profiling

# Generate performance report
curl http://localhost:8000/debug/profile-report > profile_report.json
```

## Best Practices for Troubleshooting

### 1. Systematic Approach
1. **Identify symptoms** - What's not working?
2. **Check logs first** - Look for error messages
3. **Verify configuration** - Ensure settings are correct
4. **Test API endpoints** - Confirm connectivity
5. **Monitor resources** - Check CPU/memory usage
6. **Test in isolation** - Disable other agents to isolate issues

### 2. Preventive Measures
- Regular health checks
- Monitor log files for warnings
- Keep configurations backed up  
- Test configuration changes in staging
- Document known issues and solutions

### 3. When to Restart vs Fix
**Restart When:**
- Memory leaks detected
- Corrupted cache states
- Configuration changes require restart
- Simple connectivity issues

**Fix Without Restart When:**
- Individual agent failures
- Cache performance issues
- Memory cleanup needed
- Configuration tweaks

---

**Navigation**: [← API Reference](./api-reference.md) | [← Overview](./overview.md)