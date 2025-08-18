# API Documentation - Claude-Exclusive Obsidian Copilot

## Base URL
```
http://localhost:8000
```

## Authentication
No authentication required for local deployment. All processing happens locally via Claude Code CLI.

## Endpoints

### 1. Generate Content with Claude

#### `POST /generate`

Generate text using Claude with optimized context strategies.

**Request Body:**
```json
{
  "query": "string",
  "context_strategy": "full_docs | smart_chunks | hierarchical",
  "system_prompt": "string",
  "temperature": 0.7,
  "model": "claude-3-5-sonnet-20241022",
  "max_tokens": 4000,
  "max_context_tokens": 100000,
  "include_full_docs": false
}
```

**Parameters:**
- `query` (required): The user's query or section heading
- `context_strategy`: Strategy for building context (default: "smart_chunks")
- `system_prompt` (required): System instructions for Claude
- `temperature`: Generation temperature 0-1 (default: 0.7)
- `model`: Claude model to use (default: "claude-3-5-sonnet-20241022")
- `max_tokens`: Maximum tokens for response (default: 4000)
- `max_context_tokens`: Maximum context size (default: 100000, max: 200000)
- `include_full_docs`: Whether to include complete documents

**Response:**
```json
{
  "response": "Generated text content...",
  "context_used": "smart_chunks with 5 documents",
  "tokens_used": 45000,
  "model": "claude-3-5-sonnet-20241022",
  "generation_time": 8.5
}
```

**Example:**
```bash
curl -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Benefits of retrieval-augmented generation",
    "context_strategy": "full_docs",
    "system_prompt": "You are a helpful AI assistant...",
    "max_context_tokens": 150000
  }'
```

---

### 2. Generate with Streaming (Simulated)

#### `POST /generate_streaming`

Generate text with simulated streaming for better UX.

**Request Body:**
Same as `/generate`

**Response:**
Server-Sent Events (SSE) stream
```
data: {"content": "First few words..."}
data: {"content": "Next few words..."}
data: {"done": true}
```

**Example:**
```javascript
const response = await fetch('http://localhost:8000/generate_streaming', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    query: "Your query",
    context_strategy: "smart_chunks",
    system_prompt: "Your prompt"
  })
});

const reader = response.body.getReader();
// Process streaming response
```

---

### 3. Analyze Vault

#### `POST /analyze_vault`

Perform comprehensive analysis across multiple documents in your vault.

**Request Body:**
```json
{
  "topic": "string",
  "depth": 3,
  "max_documents": 50
}
```

**Parameters:**
- `topic` (required): Topic to analyze across vault
- `depth`: Analysis depth 1-5 (default: 3)
  - 1: High-level overview
  - 2: Main themes
  - 3: Detailed analysis
  - 4: Comprehensive with citations
  - 5: Exhaustive academic level
- `max_documents`: Maximum documents to analyze (default: 50)

**Response:**
```json
{
  "analysis": "Comprehensive analysis text...",
  "documents_analyzed": 42,
  "tokens_used": 125000,
  "generation_time": 15.3,
  "documents": ["doc1.md", "doc2.md", "..."]
}
```

**Example:**
```bash
curl -X POST http://localhost:8000/analyze_vault \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "machine learning optimization techniques",
    "depth": 4,
    "max_documents": 30
  }'
```

---

### 4. Synthesize Notes

#### `POST /synthesize_notes`

Create synthesis from multiple complete notes.

**Request Body:**
```json
{
  "note_paths": ["note1.md", "note2.md"],
  "synthesis_type": "summary | outline | connections"
}
```

**Parameters:**
- `note_paths` (required): Array of note paths to synthesize
- `synthesis_type`: Type of synthesis (default: "summary")
  - `summary`: Comprehensive summary
  - `outline`: Structured outline
  - `connections`: Relationship mapping

**Response:**
```json
{
  "synthesis": "Synthesized content...",
  "type": "summary",
  "notes_synthesized": 5,
  "tokens_used": 80000,
  "generation_time": 10.2
}
```

**Example:**
```bash
curl -X POST http://localhost:8000/synthesize_notes \
  -H "Content-Type: application/json" \
  -d '{
    "note_paths": [
      "meetings/2024-01-15.md",
      "meetings/2024-01-16.md",
      "meetings/2024-01-17.md"
    ],
    "synthesis_type": "summary"
  }'
```

---

### 5. Get Context

#### `GET /get_context`

Retrieve optimized context for a query.

**Query Parameters:**
- `query` (required): Search query
- `strategy`: Context strategy (default: "smart_chunks")
- `max_tokens`: Maximum tokens (default: 100000)

**Response:**
```json
{
  "chunks": [
    {
      "title": "Document Title",
      "content": "Content...",
      "type": "chunk | full_document"
    }
  ],
  "metadata": {
    "tokens_used": 45000,
    "documents_included": ["doc1.md", "doc2.md"],
    "strategy": "smart_chunks"
  }
}
```

**Example:**
```bash
curl "http://localhost:8000/get_context?query=quantum%20computing&strategy=full_docs&max_tokens=150000"
```

---

## Context Strategies

### Strategy Comparison

| Strategy | Description | Token Usage | Best For |
|----------|-------------|-------------|----------|
| `full_docs` | Complete documents | High (100K-200K) | Deep understanding |
| `smart_chunks` | Intelligent chunking | Medium (50K-100K) | Balanced performance |
| `hierarchical` | Summaries + details | Optimized | Large vaults |

### Strategy Selection Guide

```python
# For research and analysis
strategy = "full_docs"
max_tokens = 150000

# For daily notes and drafting
strategy = "smart_chunks"  
max_tokens = 80000

# For large vaults (>1000 notes)
strategy = "hierarchical"
max_tokens = 100000
```

## Error Responses

### Standard Error Format
```json
{
  "detail": "Error description",
  "status_code": 500,
  "timestamp": "2024-01-18T10:30:00Z"
}
```

### Common Error Codes

| Code | Description | Resolution |
|------|-------------|------------|
| 400 | Bad Request | Check request parameters |
| 404 | Not Found | Verify note paths exist |
| 500 | Internal Server Error | Check logs, verify Claude CLI |
| 504 | Generation Timeout | Reduce context size |

## Rate Limits

No built-in rate limits for local deployment. Processing is limited by:
- Claude Code CLI processing speed
- Local CPU/memory resources
- Context size (larger = slower)

## Performance Guidelines

### Response Times

| Context Size | Expected Time | Notes |
|--------------|---------------|-------|
| < 10K tokens | 2-5 seconds | Fast responses |
| 10K-50K tokens | 5-10 seconds | Standard usage |
| 50K-100K tokens | 10-15 seconds | Large contexts |
| 100K-200K tokens | 15-30 seconds | Maximum context |

### Optimization Tips

1. **Use appropriate context strategy**
   - Start with `smart_chunks`
   - Use `full_docs` only when needed
   
2. **Cache frequent queries**
   - Enable Redis caching
   - Set appropriate TTL
   
3. **Batch related requests**
   - Group similar queries
   - Reuse context when possible

## WebSocket Support (Future)

Planned WebSocket support for real-time streaming:
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/generate');
ws.send(JSON.stringify({ query: "...", ... }));
ws.onmessage = (event) => {
  // Handle streaming chunks
};
```

## Batch Processing (Future)

Planned batch endpoint for multiple queries:
```json
POST /batch_generate
{
  "queries": [
    { "query": "Query 1", "context_strategy": "smart_chunks" },
    { "query": "Query 2", "context_strategy": "full_docs" }
  ]
}
```

## Health Check

#### `GET /health`

Check service health status.

**Response:**
```json
{
  "status": "healthy",
  "claude_available": true,
  "opensearch_connected": true,
  "semantic_index_loaded": true,
  "vault_documents": 1234
}
```

## Metrics

#### `GET /metrics`

Get service metrics (if enabled).

**Response:**
```json
{
  "total_requests": 1000,
  "average_generation_time": 8.5,
  "average_context_size": 75000,
  "cache_hit_rate": 0.65
}
```

## Examples

### Example 1: Research Paper Analysis
```python
import requests

response = requests.post('http://localhost:8000/analyze_vault', json={
    'topic': 'transformer architectures',
    'depth': 4,
    'max_documents': 40
})

analysis = response.json()
print(f"Analyzed {analysis['documents_analyzed']} documents")
print(analysis['analysis'])
```

### Example 2: Weekly Journal Synthesis
```python
import requests

dates = ['2024-01-15', '2024-01-16', '2024-01-17', '2024-01-18', '2024-01-19']
note_paths = [f'daily/{date}.md' for date in dates]

response = requests.post('http://localhost:8000/synthesize_notes', json={
    'note_paths': note_paths,
    'synthesis_type': 'summary'
})

synthesis = response.json()
print(synthesis['synthesis'])
```

### Example 3: Streaming Generation (JavaScript)
```javascript
async function generateWithStreaming(query) {
  const response = await fetch('http://localhost:8000/generate_streaming', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      query: query,
      context_strategy: 'smart_chunks',
      system_prompt: 'You are a helpful assistant...',
      max_context_tokens: 100000
    })
  });

  const reader = response.body.getReader();
  const decoder = new TextDecoder();

  while (true) {
    const { value, done } = await reader.read();
    if (done) break;
    
    const chunk = decoder.decode(value);
    const lines = chunk.split('\n');
    
    for (const line of lines) {
      if (line.startsWith('data: ')) {
        const data = JSON.parse(line.slice(6));
        if (data.content) {
          process.stdout.write(data.content);
        }
      }
    }
  }
}
```

## Testing

### Using cURL
```bash
# Test health
curl http://localhost:8000/health

# Test context retrieval
curl "http://localhost:8000/get_context?query=test&strategy=smart_chunks"

# Test generation
curl -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d '{"query": "test", "system_prompt": "Test prompt", "context_strategy": "smart_chunks"}'
```

### Using Python
```python
import requests

# Base URL
base_url = "http://localhost:8000"

# Test endpoints
def test_api():
    # Health check
    health = requests.get(f"{base_url}/health").json()
    print(f"Health: {health['status']}")
    
    # Get context
    context = requests.get(f"{base_url}/get_context", params={
        "query": "machine learning",
        "strategy": "smart_chunks"
    }).json()
    print(f"Context chunks: {len(context['chunks'])}")
    
    # Generate
    generation = requests.post(f"{base_url}/generate", json={
        "query": "What is machine learning?",
        "system_prompt": "You are a helpful assistant",
        "context_strategy": "smart_chunks"
    }).json()
    print(f"Generated in {generation['generation_time']}s")

test_api()
```

## Troubleshooting

### Claude Code CLI Not Found
```bash
# Verify Claude installation
which claude

# Update environment variable
export CLAUDE_CODE_PATH=/path/to/claude
```

### Context Too Large
```python
# Reduce max tokens
{
  "max_context_tokens": 50000  # Reduce from 100000
}
```

### Slow Generation
```python
# Use smart_chunks instead of full_docs
{
  "context_strategy": "smart_chunks"
}
```

## Support

For API issues:
1. Check service logs: `docker logs obsidian-copilot`
2. Verify Claude CLI: `claude --version`
3. Test endpoints individually
4. Review error responses

---

**API Version**: 2.0.0-claude  
**Last Updated**: 2024-01-18  
**Status**: Production Ready