# API Reference - Obsidian Copilot

A comprehensive reference for the Claude-exclusive Obsidian Copilot API endpoints.

## Quick Start

```bash
# Base URL
BASE_URL="http://localhost:8000"

# Test health
curl "$BASE_URL/health"

# Generate content
curl -X POST "$BASE_URL/generate" \
  -H "Content-Type: application/json" \
  -d '{"query": "Your query", "system_prompt": "You are a helpful assistant"}'
```

---

## Core Configuration

### Base URL
```
http://localhost:8000
```

### Authentication
**None required** - All processing happens locally via Claude Code CLI for complete privacy.

### Headers
```http
Content-Type: application/json
Accept: application/json
```

---

## Endpoints Reference

### 1. Content Generation

#### `POST /generate`

Generate text using Claude with optimized context strategies.

**Request:**
```json
{
  "query": "string (required)",
  "context_strategy": "full_docs | smart_chunks | hierarchical",
  "system_prompt": "string (required)",
  "temperature": 0.7,
  "model": "claude-3-5-sonnet-20241022",
  "max_tokens": 4000,
  "max_context_tokens": 100000,
  "include_full_docs": false
}
```

**Parameters:**
- **`query`** *(required)*: User query or section heading
- **`context_strategy`** *(optional)*: Context building strategy
  - `"full_docs"` - Complete documents (high token usage)
  - `"smart_chunks"` - Intelligent chunking (balanced)
  - `"hierarchical"` - Summaries + details (optimized)
- **`system_prompt`** *(required)*: System instructions for Claude
- **`temperature`** *(optional)*: Generation randomness 0-1 (default: 0.7)
- **`model`** *(optional)*: Claude model (default: "claude-3-5-sonnet-20241022")
- **`max_tokens`** *(optional)*: Response token limit (default: 4000)
- **`max_context_tokens`** *(optional)*: Context size limit (default: 100000, max: 200000)
- **`include_full_docs`** *(optional)*: Include complete documents (default: false)

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
    "system_prompt": "You are a helpful AI assistant that provides comprehensive analysis.",
    "max_context_tokens": 150000
  }'
```

---

#### `POST /generate_streaming`

Generate text with simulated streaming for enhanced user experience.

**Request Body:** Same as `/generate`

**Response:** Server-Sent Events (SSE) stream
```
data: {"content": "First few words..."}
data: {"content": "Next few words..."}
data: {"done": true}
```

**JavaScript Example:**
```javascript
const response = await fetch('http://localhost:8000/generate_streaming', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    query: "Explain quantum computing principles",
    context_strategy: "smart_chunks",
    system_prompt: "You are an expert physics educator..."
  })
});

const reader = response.body.getReader();
const decoder = new TextDecoder();

while (true) {
  const { value, done } = await reader.read();
  if (done) break;
  
  const chunk = decoder.decode(value);
  // Process streaming content
}
```

---

### 2. Vault Analysis

#### `POST /analyze_vault`

Perform comprehensive cross-document analysis across your knowledge base.

**Request:**
```json
{
  "topic": "string (required)",
  "depth": 3,
  "max_documents": 50
}
```

**Parameters:**
- **`topic`** *(required)*: Analysis topic or theme
- **`depth`** *(optional)*: Analysis detail level 1-5 (default: 3)
  - `1` - High-level overview
  - `2` - Main themes identification  
  - `3` - Detailed analysis with examples
  - `4` - Comprehensive with citations
  - `5` - Exhaustive academic-level analysis
- **`max_documents`** *(optional)*: Document limit (default: 50)

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

### 3. Note Synthesis

#### `POST /synthesize_notes`

Create intelligent synthesis from multiple complete notes.

**Request:**
```json
{
  "note_paths": ["note1.md", "note2.md"],
  "synthesis_type": "summary | outline | connections"
}
```

**Parameters:**
- **`note_paths`** *(required)*: Array of note file paths
- **`synthesis_type`** *(optional)*: Synthesis approach (default: "summary")
  - `"summary"` - Comprehensive summary
  - `"outline"` - Structured hierarchical outline
  - `"connections"` - Relationship and link mapping

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

### 4. Context Retrieval

#### `GET /get_context`

Retrieve optimized context for any query without generation.

**Query Parameters:**
- **`query`** *(required)*: Search query string
- **`strategy`** *(optional)*: Context strategy (default: "smart_chunks")
- **`max_tokens`** *(optional)*: Token limit (default: 100000)

**Response:**
```json
{
  "chunks": [
    {
      "title": "Document Title",
      "content": "Content preview...",
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

### 5. System Health & Monitoring

#### `GET /health`

Check comprehensive service health status.

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

#### `GET /metrics`

Retrieve service performance metrics (if enabled).

**Response:**
```json
{
  "total_requests": 1000,
  "average_generation_time": 8.5,
  "average_context_size": 75000,
  "cache_hit_rate": 0.65
}
```

---

## Context Strategies Deep Dive

### Strategy Comparison Matrix

| Strategy | Token Usage | Processing Time | Best Use Cases |
|----------|-------------|-----------------|----------------|
| **`full_docs`** | High (100K-200K) | 15-30s | Deep research, comprehensive analysis |
| **`smart_chunks`** | Medium (50K-100K) | 5-15s | Daily writing, balanced performance |
| **`hierarchical`** | Optimized (varies) | 10-20s | Large vaults (>1000 notes) |

### Selection Guide

```python
# Deep research and analysis
context_strategy = "full_docs"
max_context_tokens = 150000

# Daily note writing and drafting  
context_strategy = "smart_chunks"
max_context_tokens = 80000

# Large knowledge bases (>1000 notes)
context_strategy = "hierarchical" 
max_context_tokens = 100000
```

### Performance Characteristics

**`full_docs` Strategy:**
- Includes complete documents in context
- Maximum semantic understanding
- Best for complex, multi-faceted queries
- Higher token usage and processing time

**`smart_chunks` Strategy:**
- Intelligent document segmentation
- Balanced performance vs. quality
- Recommended for most use cases
- Moderate resource usage

**`hierarchical` Strategy:**
- Combines summaries with detailed sections
- Scales well with vault size  
- Optimizes token allocation
- Best for information discovery

---

## Error Handling

### Standard Error Response
```json
{
  "detail": "Descriptive error message",
  "status_code": 500,
  "timestamp": "2024-01-18T10:30:00Z",
  "error_type": "internal_server_error"
}
```

### Error Code Reference

| HTTP Code | Error Type | Common Causes | Resolution |
|-----------|------------|---------------|------------|
| **400** | Bad Request | Invalid parameters, malformed JSON | Validate request format and parameters |
| **404** | Not Found | Invalid note paths, missing endpoints | Verify file paths and endpoint URLs |
| **422** | Validation Error | Missing required fields | Check required parameters |
| **500** | Internal Server Error | Claude CLI issues, system errors | Check logs, verify Claude CLI installation |
| **504** | Generation Timeout | Context too large, processing timeout | Reduce context size or max_tokens |

### Error Response Examples

**Invalid Context Strategy:**
```json
{
  "detail": "Invalid context_strategy. Must be one of: full_docs, smart_chunks, hierarchical",
  "status_code": 400,
  "timestamp": "2024-01-18T10:30:00Z"
}
```

**Note Not Found:**
```json
{
  "detail": "Note path 'nonexistent.md' not found in vault",
  "status_code": 404,
  "timestamp": "2024-01-18T10:30:00Z"
}
```

**Context Too Large:**
```json
{
  "detail": "Context size 250000 tokens exceeds maximum of 200000",
  "status_code": 400,
  "timestamp": "2024-01-18T10:30:00Z"
}
```

---

## Performance Guidelines

### Response Time Expectations

| Context Size | Expected Time | Optimization Notes |
|--------------|---------------|-------------------|
| **< 10K tokens** | 2-5 seconds | Fast responses, minimal context |
| **10K-50K tokens** | 5-10 seconds | Standard usage, balanced performance |
| **50K-100K tokens** | 10-15 seconds | Large contexts, detailed analysis |
| **100K-200K tokens** | 15-30 seconds | Maximum context, comprehensive research |

### Token Usage Guidelines

**Recommended Token Allocation:**
```python
# Quick queries
max_context_tokens = 20000
max_tokens = 2000

# Standard content generation  
max_context_tokens = 80000
max_tokens = 4000

# Research and analysis
max_context_tokens = 150000
max_tokens = 8000

# Maximum context (use sparingly)
max_context_tokens = 200000
max_tokens = 4000
```

### Performance Optimization

1. **Context Strategy Selection**
   ```python
   # Start with smart_chunks for most use cases
   context_strategy = "smart_chunks"
   
   # Use full_docs only when semantic completeness is critical
   if complex_analysis_needed:
       context_strategy = "full_docs"
   ```

2. **Caching Strategy**
   ```python
   # Enable Redis caching for frequent queries
   ENABLE_CACHING = True
   CACHE_TTL = 3600  # 1 hour
   ```

3. **Batch Processing**
   ```python
   # Group related queries to reuse context
   related_queries = [
       "What is machine learning?",
       "How does deep learning work?", 
       "What are neural networks?"
   ]
   ```

---

## Rate Limits & Resource Management

### Local Deployment Limits
- **No built-in API rate limits** (local processing)
- **Limited by system resources:**
  - CPU processing power
  - Available RAM 
  - Claude CLI processing speed
  - Context size (larger contexts = slower processing)

### Resource Management
```python
# Monitor system resources
import psutil

def check_resources():
    cpu_percent = psutil.cpu_percent()
    memory_percent = psutil.virtual_memory().percent
    
    if cpu_percent > 80 or memory_percent > 85:
        # Consider reducing context size or queue requests
        return False
    return True
```

---

## Testing Examples

### Unit Testing with Python

```python
import requests
import json

class TestObsidianCopilotAPI:
    def __init__(self):
        self.base_url = "http://localhost:8000"
        
    def test_health_endpoint(self):
        """Test service health check"""
        response = requests.get(f"{self.base_url}/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
        assert "claude_available" in data
        
    def test_context_retrieval(self):
        """Test context retrieval"""
        params = {
            "query": "machine learning basics",
            "strategy": "smart_chunks",
            "max_tokens": 50000
        }
        
        response = requests.get(f"{self.base_url}/get_context", params=params)
        assert response.status_code == 200
        
        data = response.json()
        assert "chunks" in data
        assert "metadata" in data
        
    def test_content_generation(self):
        """Test content generation"""
        payload = {
            "query": "Explain the benefits of retrieval-augmented generation",
            "system_prompt": "You are a helpful AI assistant",
            "context_strategy": "smart_chunks",
            "max_context_tokens": 80000
        }
        
        response = requests.post(f"{self.base_url}/generate", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        assert "response" in data
        assert "tokens_used" in data
        assert "generation_time" in data
        
    def test_vault_analysis(self):
        """Test vault analysis"""
        payload = {
            "topic": "artificial intelligence trends",
            "depth": 3,
            "max_documents": 20
        }
        
        response = requests.post(f"{self.base_url}/analyze_vault", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        assert "analysis" in data
        assert "documents_analyzed" in data

# Run tests
if __name__ == "__main__":
    tester = TestObsidianCopilotAPI()
    tester.test_health_endpoint()
    tester.test_context_retrieval()
    tester.test_content_generation()
    tester.test_vault_analysis()
    print("All tests passed!")
```

### Integration Testing with cURL

```bash
#!/bin/bash

# Obsidian Copilot API Integration Tests
BASE_URL="http://localhost:8000"

echo "=== Testing Obsidian Copilot API ==="

# Test 1: Health Check
echo "1. Testing health endpoint..."
curl -s "$BASE_URL/health" | jq '.status' || exit 1

# Test 2: Context Retrieval
echo "2. Testing context retrieval..."
curl -s "$BASE_URL/get_context?query=test&strategy=smart_chunks" | jq '.chunks | length' || exit 1

# Test 3: Content Generation
echo "3. Testing content generation..."
curl -s -X POST "$BASE_URL/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is artificial intelligence?",
    "system_prompt": "You are a helpful assistant",
    "context_strategy": "smart_chunks"
  }' | jq '.response' || exit 1

# Test 4: Vault Analysis  
echo "4. Testing vault analysis..."
curl -s -X POST "$BASE_URL/analyze_vault" \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "technology trends",
    "depth": 2,
    "max_documents": 10
  }' | jq '.analysis' || exit 1

echo "✅ All API tests passed!"
```

---

## Advanced Usage Patterns

### Research Workflow Example

```python
import requests

class ResearchWorkflow:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
    
    def comprehensive_research(self, topic):
        """Perform multi-step research analysis"""
        
        # Step 1: Get initial context
        context_response = requests.get(f"{self.base_url}/get_context", params={
            "query": topic,
            "strategy": "hierarchical",
            "max_tokens": 100000
        })
        
        # Step 2: Analyze vault for patterns
        analysis_response = requests.post(f"{self.base_url}/analyze_vault", json={
            "topic": topic,
            "depth": 4,
            "max_documents": 50
        })
        
        # Step 3: Generate comprehensive summary
        generation_response = requests.post(f"{self.base_url}/generate", json={
            "query": f"Based on all available information, provide a comprehensive analysis of {topic}",
            "system_prompt": "You are an expert researcher. Provide detailed, well-sourced analysis.",
            "context_strategy": "full_docs",
            "max_context_tokens": 180000,
            "max_tokens": 8000
        })
        
        return {
            "context": context_response.json(),
            "analysis": analysis_response.json(), 
            "summary": generation_response.json()
        }

# Usage
researcher = ResearchWorkflow()
results = researcher.comprehensive_research("quantum computing applications")
```

### Weekly Review Automation

```python
import requests
from datetime import datetime, timedelta

class WeeklyReviewGenerator:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
    
    def generate_weekly_review(self):
        """Generate automated weekly review"""
        
        # Get recent notes (last 7 days)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)
        
        note_paths = self._get_weekly_notes(start_date, end_date)
        
        # Synthesize weekly notes
        synthesis_response = requests.post(f"{self.base_url}/synthesize_notes", json={
            "note_paths": note_paths,
            "synthesis_type": "summary"
        })
        
        # Generate insights and action items
        insights_response = requests.post(f"{self.base_url}/generate", json={
            "query": "Based on this week's notes, identify key insights, patterns, and action items",
            "system_prompt": "You are a productivity coach. Analyze weekly notes for insights and actionable recommendations.",
            "context_strategy": "smart_chunks",
            "max_context_tokens": 100000
        })
        
        return {
            "synthesis": synthesis_response.json(),
            "insights": insights_response.json(),
            "period": f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}"
        }
```

---

## Troubleshooting Guide

### Common Issues & Solutions

#### Issue: "Claude Code CLI not found"
```bash
# Diagnosis
which claude

# Solutions
# 1. Install Claude Code CLI
curl -fsSL https://claude.ai/install.sh | sh

# 2. Update PATH
export PATH="$HOME/.claude/bin:$PATH"

# 3. Set environment variable
export CLAUDE_CODE_PATH=/path/to/claude
```

#### Issue: "Context too large" errors
```python
# Problem: Context exceeds token limits
# Solution 1: Reduce context size
{
  "max_context_tokens": 50000  # Reduce from 100000+
}

# Solution 2: Use different strategy
{
  "context_strategy": "smart_chunks"  # Instead of "full_docs"
}

# Solution 3: Limit documents
{
  "max_documents": 20  # Reduce document count
}
```

#### Issue: Slow generation times
```python
# Optimization strategies
{
  "context_strategy": "hierarchical",  # More efficient
  "max_context_tokens": 80000,         # Reasonable limit
  "max_tokens": 4000                   # Appropriate response size
}
```

#### Issue: Empty or irrelevant context
```python
# Debug context retrieval
context = requests.get(f"{base_url}/get_context", params={
    "query": "your query here",
    "strategy": "smart_chunks"
}).json()

print(f"Found {len(context['chunks'])} chunks")
for chunk in context['chunks'][:3]:
    print(f"- {chunk['title']}: {chunk['content'][:100]}...")
```

### Debugging Workflow

1. **Check Service Health**
   ```bash
   curl http://localhost:8000/health
   ```

2. **Test Context Retrieval**
   ```bash
   curl "http://localhost:8000/get_context?query=test&strategy=smart_chunks"
   ```

3. **Validate Generation**
   ```bash
   curl -X POST http://localhost:8000/generate \
     -H "Content-Type: application/json" \
     -d '{"query": "test", "system_prompt": "Test prompt"}'
   ```

4. **Check Logs**
   ```bash
   # Docker deployment
   docker logs obsidian-copilot
   
   # Local deployment
   tail -f app.log
   ```

---

## Future Enhancements

### Planned Features

#### WebSocket Support
```javascript
// Real-time streaming (planned)
const ws = new WebSocket('ws://localhost:8000/ws/generate');

ws.send(JSON.stringify({
  query: "Explain quantum computing",
  context_strategy: "smart_chunks"
}));

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  if (data.content) {
    console.log(data.content);
  }
};
```

#### Batch Processing
```json
POST /batch_generate
{
  "queries": [
    {
      "query": "Query 1",
      "context_strategy": "smart_chunks"
    },
    {
      "query": "Query 2", 
      "context_strategy": "full_docs"
    }
  ]
}
```

#### Advanced Analytics
```json
GET /analytics/usage
{
  "period": "last_30_days",
  "breakdown": {
    "total_requests": 2500,
    "context_strategies": {
      "smart_chunks": 1800,
      "full_docs": 500,
      "hierarchical": 200
    },
    "average_tokens_per_request": 75000
  }
}
```

---

## Support & Resources

### Getting Help

1. **API Issues**
   - Check service logs: `docker logs obsidian-copilot`
   - Verify Claude CLI: `claude --version`
   - Test individual endpoints
   - Review error responses and status codes

2. **Performance Issues**
   - Monitor system resources (CPU, RAM)
   - Optimize context strategies
   - Reduce token limits if needed
   - Enable caching for frequent queries

3. **Integration Support**
   - Review example code in this documentation
   - Test with minimal payloads first
   - Validate JSON request formats
   - Check HTTP headers and methods

### Documentation Links

- [Setup Guide](../setup/installation.md) - Installation and configuration
- [Usage Guide](../usage/basic-usage.md) - Getting started with the API
- [Agent Overview](../agents/overview.md) - Understanding the agent system
- [Troubleshooting](../troubleshooting/) - Common issues and solutions

---

**API Version**: 2.0.0-claude  
**Documentation Last Updated**: 2025-08-18  
**Status**: Production Ready

---

## Appendix: Complete cURL Examples

### Comprehensive Test Suite
```bash
#!/bin/bash
# Complete API test suite

BASE_URL="http://localhost:8000"

echo "🚀 Obsidian Copilot API Test Suite"
echo "=================================="

# Health Check
echo "📊 Testing health endpoint..."
curl -s "$BASE_URL/health" | jq '.'

# Context Retrieval
echo -e "\n🔍 Testing context retrieval..."
curl -s "$BASE_URL/get_context?query=artificial%20intelligence&strategy=smart_chunks&max_tokens=50000" | jq '.metadata'

# Content Generation
echo -e "\n✍️  Testing content generation..."
curl -s -X POST "$BASE_URL/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What are the key benefits of using AI in knowledge management?",
    "system_prompt": "You are an expert in knowledge management and AI systems. Provide comprehensive, practical insights.",
    "context_strategy": "smart_chunks",
    "max_context_tokens": 80000,
    "temperature": 0.7
  }' | jq '{response: .response[0:200], tokens_used: .tokens_used, generation_time: .generation_time}'

# Vault Analysis
echo -e "\n📚 Testing vault analysis..."
curl -s -X POST "$BASE_URL/analyze_vault" \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "productivity and knowledge management",
    "depth": 3,
    "max_documents": 25
  }' | jq '{documents_analyzed: .documents_analyzed, tokens_used: .tokens_used}'

# Note Synthesis
echo -e "\n🔗 Testing note synthesis..."
curl -s -X POST "$BASE_URL/synthesize_notes" \
  -H "Content-Type: application/json" \
  -d '{
    "note_paths": ["daily/2024-01-15.md", "daily/2024-01-16.md"],
    "synthesis_type": "summary"
  }' | jq '{type: .type, notes_synthesized: .notes_synthesized}'

echo -e "\n✅ API test suite completed!"
```

This comprehensive API reference provides complete technical documentation for the Obsidian Copilot API, preserving all original content while enhancing organization, usability, and depth of coverage.