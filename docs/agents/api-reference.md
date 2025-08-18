# 🔧 Agent OS API Reference

> Complete API documentation for interacting with Agent OS programmatically

## Base URL

All API endpoints are available at:
```
http://localhost:8000
```

## Authentication

Currently, no authentication is required for local API access.

## Core Endpoints

### Agent Management

#### List All Agents
```http
GET /agents/list
```

**Response:**
```json
{
  "agents": [
    {
      "name": "vault-analyzer",
      "type": "autonomous",
      "status": "active",
      "last_execution": "2024-01-15T10:30:00Z"
    },
    {
      "name": "synthesis-assistant", 
      "type": "reactive",
      "status": "idle",
      "last_execution": "2024-01-15T09:15:00Z"
    }
  ]
}
```

#### Get Agent Status
```http
GET /agents/{agent-name}/status
```

**Example:**
```bash
curl http://localhost:8000/agents/vault-analyzer/status
```

**Response:**
```json
{
  "agent": "vault-analyzer",
  "status": "running",
  "current_task": "pattern_analysis",
  "progress": 0.65,
  "estimated_completion": "2024-01-15T10:45:00Z",
  "last_execution": {
    "start_time": "2024-01-15T10:30:00Z",
    "duration": "00:12:34",
    "status": "completed",
    "documents_processed": 127
  }
}
```

#### Execute Agent Manually
```http
POST /agents/{agent-name}/execute
```

**Request Body:**
```json
{
  "parameters": {
    "depth": 3,
    "focus": "recent_changes",
    "max_documents": 100
  }
}
```

**Example:**
```bash
curl -X POST http://localhost:8000/agents/vault-analyzer/execute \
  -H "Content-Type: application/json" \
  -d '{
    "parameters": {
      "depth": 3,
      "focus": "recent_changes"
    }
  }'
```

**Response:**
```json
{
  "execution_id": "exec_123456",
  "agent": "vault-analyzer",
  "status": "started",
  "estimated_duration": "00:15:00",
  "parameters": {
    "depth": 3,
    "focus": "recent_changes"
  }
}
```

#### Get Agent Execution History
```http
GET /agents/{agent-name}/history?limit={limit}&offset={offset}
```

**Parameters:**
- `limit`: Number of executions to return (default: 10, max: 100)
- `offset`: Number of executions to skip (default: 0)

**Example:**
```bash
curl http://localhost:8000/agents/vault-analyzer/history?limit=10
```

**Response:**
```json
{
  "agent": "vault-analyzer",
  "executions": [
    {
      "execution_id": "exec_123456",
      "start_time": "2024-01-15T10:30:00Z",
      "end_time": "2024-01-15T10:45:00Z",
      "status": "completed",
      "duration": "00:15:00",
      "documents_processed": 127,
      "patterns_found": 8,
      "insights_generated": 3
    }
  ],
  "total": 42,
  "limit": 10,
  "offset": 0
}
```

### Scheduler Management

#### Get Scheduler Information
```http
GET /scheduler/info
```

**Response:**
```json
{
  "status": "active",
  "scheduled_jobs": [
    {
      "agent": "vault-analyzer",
      "schedule": "daily",
      "time": "02:00",
      "timezone": "local",
      "next_execution": "2024-01-16T02:00:00Z"
    }
  ],
  "active_executions": 1,
  "max_concurrent": 3
}
```

#### View Scheduled Jobs
```http
GET /scheduler/jobs
```

**Response:**
```json
{
  "jobs": [
    {
      "job_id": "job_vault_analyzer_daily",
      "agent": "vault-analyzer",
      "schedule": "0 2 * * *",
      "enabled": true,
      "next_run": "2024-01-16T02:00:00Z",
      "last_run": {
        "execution_time": "2024-01-15T02:00:00Z",
        "status": "completed",
        "duration": "00:15:23"
      }
    }
  ]
}
```

### Agent-Specific Endpoints

#### Vault Analyzer

**Trigger Analysis**
```http
POST /agents/vault-analyzer/analyze
```

**Request Body:**
```json
{
  "scope": "recent_changes|full_vault|specific_folder",
  "folder_path": "optional/folder/path",
  "depth": 3,
  "include_patterns": ["theme", "connection", "gap"],
  "max_documents": 200
}
```

#### Synthesis Assistant

**Create Synthesis**
```http
POST /agents/synthesis-assistant/synthesize
```

**Request Body:**
```json
{
  "documents": ["note1.md", "note2.md", "note3.md"],
  "synthesis_type": "thematic|chronological|argumentative|comparative",
  "focus": "optional focus area",
  "max_length": 2000
}
```

#### Research Assistant

**Conduct Research**
```http
POST /agents/research-assistant/research
```

**Request Body:**
```json
{
  "query": "Research question or topic",
  "depth": "exploratory|focused|comprehensive",
  "max_documents": 100,
  "research_type": "literature_review|evidence_gathering|hypothesis_testing",
  "time_limit_minutes": 30
}
```

### Memory and Learning

#### Get Agent Memories
```http
GET /agents/{agent-name}/memories?type={type}&limit={limit}
```

**Parameters:**
- `type`: pattern|preference|execution|insight|feedback
- `limit`: Number of memories to return

**Response:**
```json
{
  "agent": "vault-analyzer",
  "memories": [
    {
      "memory_id": "mem_123456",
      "type": "pattern",
      "created": "2024-01-15T10:30:00Z",
      "confidence": 0.92,
      "content": {
        "pattern_type": "weekly_review",
        "frequency": 12,
        "description": "User creates weekly review notes every Sunday"
      }
    }
  ]
}
```

#### Add Agent Memory
```http
POST /agents/{agent-name}/memories
```

**Request Body:**
```json
{
  "type": "pattern|preference|execution|insight|feedback",
  "content": {
    "description": "Memory description",
    "metadata": {
      "confidence": 0.85,
      "source": "user_feedback"
    }
  }
}
```

### Configuration

#### Get Agent Configuration
```http
GET /agents/{agent-name}/config
```

**Response:**
```json
{
  "agent": "vault-analyzer",
  "configuration": {
    "enabled": true,
    "trigger": {
      "type": "schedule",
      "interval": "daily",
      "time": "02:00"
    },
    "parameters": {
      "max_documents_per_run": 100,
      "analysis_depth": 3,
      "timeout_minutes": 30
    }
  }
}
```

#### Update Agent Configuration
```http
PUT /agents/{agent-name}/config
```

**Request Body:**
```json
{
  "enabled": true,
  "trigger": {
    "type": "schedule", 
    "interval": "daily",
    "time": "03:00"
  },
  "parameters": {
    "analysis_depth": 2,
    "max_documents_per_run": 150
  }
}
```

### Performance and Monitoring

#### Get System Performance Metrics
```http
GET /system/metrics
```

**Response:**
```json
{
  "timestamp": "2024-01-15T10:30:00Z",
  "system": {
    "cpu_usage": 0.65,
    "memory_usage": 0.42,
    "disk_usage": 0.78
  },
  "agents": {
    "active_agents": 2,
    "queued_tasks": 1,
    "completed_today": 15
  },
  "performance": {
    "avg_query_latency_ms": 450,
    "cache_hit_rate": 0.68,
    "token_utilization": 0.82
  }
}
```

#### Get Cache Statistics
```http
GET /system/cache/stats
```

**Response:**
```json
{
  "cache_levels": {
    "hot_cache": {
      "size_mb": 95.2,
      "capacity_mb": 100,
      "hit_rate": 0.85,
      "ttl_hours": 1
    },
    "warm_cache": {
      "size_mb": 320.5,
      "capacity_mb": 500,
      "hit_rate": 0.72,
      "ttl_hours": 24
    },
    "cold_cache": {
      "size_mb": 1250.8,
      "capacity_gb": 2,
      "hit_rate": 0.45,
      "ttl_days": 7
    }
  }
}
```

## Error Responses

### Standard Error Format
```json
{
  "error": {
    "code": "AGENT_NOT_FOUND",
    "message": "Agent 'invalid-agent' not found",
    "details": {
      "agent_name": "invalid-agent",
      "available_agents": ["vault-analyzer", "synthesis-assistant"]
    }
  }
}
```

### Common Error Codes

| Code | Description | HTTP Status |
|------|-------------|-------------|
| `AGENT_NOT_FOUND` | Specified agent doesn't exist | 404 |
| `AGENT_BUSY` | Agent is currently executing | 409 |
| `AGENT_DISABLED` | Agent is disabled in configuration | 403 |
| `INVALID_PARAMETERS` | Request parameters are invalid | 400 |
| `EXECUTION_FAILED` | Agent execution failed | 500 |
| `TIMEOUT_EXCEEDED` | Operation timed out | 408 |
| `MEMORY_LIMIT` | Memory limit exceeded | 507 |

## Rate Limiting

API endpoints have the following rate limits:
- **GET requests**: 100 requests/minute
- **POST requests**: 20 requests/minute
- **Agent execution**: 5 executions/minute per agent

## WebSocket Events

For real-time updates, connect to:
```
ws://localhost:8000/ws/events
```

### Event Types

**Agent Status Updates**
```json
{
  "type": "agent_status",
  "agent": "vault-analyzer",
  "status": "completed",
  "execution_id": "exec_123456",
  "results": {
    "patterns_found": 5,
    "insights_generated": 2
  }
}
```

**System Alerts**
```json
{
  "type": "system_alert",
  "level": "warning|error|info",
  "message": "High memory usage detected",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

## SDK Examples

### Python SDK Usage
```python
from agent_os_client import AgentOSClient

client = AgentOSClient("http://localhost:8000")

# Execute agent
result = client.agents.vault_analyzer.execute({
    "depth": 3,
    "focus": "recent_changes"
})

# Get status
status = client.agents.vault_analyzer.status()

# Get memories
memories = client.agents.vault_analyzer.memories(type="pattern")
```

### JavaScript SDK Usage
```javascript
import { AgentOSClient } from 'agent-os-client';

const client = new AgentOSClient('http://localhost:8000');

// Execute agent
const result = await client.agents.vaultAnalyzer.execute({
  depth: 3,
  focus: 'recent_changes'
});

// Get status  
const status = await client.agents.vaultAnalyzer.status();

// Get memories
const memories = await client.agents.vaultAnalyzer.memories({ type: 'pattern' });
```

---

**Navigation**: [← Overview](./overview.md) | [Troubleshooting →](./troubleshooting.md)