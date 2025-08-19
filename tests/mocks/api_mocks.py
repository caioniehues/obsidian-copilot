"""
Mock implementations for external APIs and services.
Provides realistic mock responses for testing without actual API calls.
"""

import json
import time
import asyncio
from typing import Dict, List, Any, Optional, AsyncGenerator
from unittest.mock import MagicMock, AsyncMock
import numpy as np


class MockClaudeAPI:
    """Mock implementation of Claude API."""
    
    def __init__(self, api_key: str = "sk-ant-test-key"):
        self.api_key = api_key
        self.call_count = 0
        self.response_delay = 0.1
        self.should_fail = False
        self.failure_rate = 0.0
    
    async def create_message(self, messages: List[Dict], **kwargs) -> Dict:
        """Mock message creation."""
        await asyncio.sleep(self.response_delay)
        self.call_count += 1
        
        if self.should_fail or (self.failure_rate > 0 and np.random.random() < self.failure_rate):
            raise Exception("Mock API failure")
        
        # Generate response based on input
        user_message = messages[-1]["content"] if messages else "default query"
        response_text = self._generate_response(user_message)
        
        return {
            "id": f"msg_test_{self.call_count}",
            "type": "message",
            "role": "assistant",
            "content": [{"type": "text", "text": response_text}],
            "model": kwargs.get("model", "claude-3-5-sonnet-20241022"),
            "stop_reason": "end_turn",
            "usage": {
                "input_tokens": len(user_message.split()),
                "output_tokens": len(response_text.split())
            }
        }
    
    async def stream_message(self, messages: List[Dict], **kwargs) -> AsyncGenerator[Dict, None]:
        """Mock streaming message creation."""
        response = await self.create_message(messages, **kwargs)
        text = response["content"][0]["text"]
        words = text.split()
        
        # Stream words progressively
        for i, word in enumerate(words):
            await asyncio.sleep(0.05)  # Simulate streaming delay
            
            partial_text = " ".join(words[:i+1])
            yield {
                "id": response["id"],
                "type": "message",
                "role": "assistant",
                "content": [{"type": "text", "text": partial_text}]
            }
        
        # Final complete response
        yield response
    
    def _generate_response(self, user_message: str) -> str:
        """Generate contextual response based on user message."""
        message_lower = user_message.lower()
        
        if "machine learning" in message_lower or "ml" in message_lower:
            return """Machine learning is a powerful subset of artificial intelligence that enables systems to learn and improve from experience. Key concepts include:

- **Supervised Learning**: Training with labeled data
- **Unsupervised Learning**: Finding patterns in unlabeled data  
- **Neural Networks**: Interconnected nodes that process information
- **Deep Learning**: Multi-layered neural networks for complex patterns

Applications span from image recognition to natural language processing."""
        
        elif "neural network" in message_lower:
            return """Neural networks are computing systems inspired by biological neural networks. They consist of:

1. **Input Layer**: Receives data
2. **Hidden Layers**: Process and transform information
3. **Output Layer**: Produces final results

Key components:
- Neurons (nodes) that process information
- Weights that determine connection strength
- Activation functions that introduce non-linearity
- Backpropagation for training and optimization"""
        
        elif "programming" in message_lower or "code" in message_lower:
            return """Programming best practices focus on writing clean, maintainable code:

**Clean Code Principles:**
- Use meaningful variable and function names
- Keep functions small and focused
- Write self-documenting code
- Implement comprehensive error handling

**Testing Strategies:**
- Unit tests for individual components
- Integration tests for system interactions
- Test-driven development (TDD)
- Continuous integration and deployment"""
        
        elif "analysis" in message_lower or "analyze" in message_lower:
            return """Based on the available information, here's a comprehensive analysis:

**Key Patterns Identified:**
- Consistent focus on technical learning
- Strong emphasis on best practices
- Integration of theory with practical application

**Recommendations:**
- Continue building practical examples
- Expand documentation with real-world use cases
- Create connections between different technical domains

**Next Steps:**
- Identify knowledge gaps for focused learning
- Develop hands-on projects to reinforce concepts"""
        
        else:
            return f"""Thank you for your query about "{user_message}". Based on the available context and information, I can provide insights and guidance on this topic.

This response demonstrates the system's ability to process queries and provide relevant, contextual information. The system draws from available knowledge to offer comprehensive answers that address your specific needs.

Would you like me to elaborate on any particular aspect or explore related topics?"""
    
    def set_failure_mode(self, should_fail: bool = True, failure_rate: float = 0.0):
        """Configure failure behavior for testing."""
        self.should_fail = should_fail
        self.failure_rate = failure_rate
    
    def set_response_delay(self, delay: float):
        """Set response delay for performance testing."""
        self.response_delay = delay
    
    def reset_stats(self):
        """Reset call statistics."""
        self.call_count = 0


class MockOpenSearchClient:
    """Mock OpenSearch client for testing."""
    
    def __init__(self):
        self.indices = MockIndicesClient()
        self.call_count = 0
        self.search_responses = {}
        self.should_fail = False
    
    def info(self) -> Dict:
        """Mock cluster info."""
        return {
            "version": {"number": "2.7.0"},
            "cluster_name": "test-cluster"
        }
    
    def search(self, index: str, body: Dict, **kwargs) -> Dict:
        """Mock search operation."""
        self.call_count += 1
        
        if self.should_fail:
            raise Exception("Mock OpenSearch failure")
        
        query = body.get("query", {})
        size = body.get("size", 10)
        
        # Generate mock hits based on query
        hits = self._generate_search_hits(query, size)
        
        return {
            "hits": {
                "total": {"value": len(hits)},
                "hits": hits
            }
        }
    
    def bulk(self, body: List[Dict], **kwargs) -> Dict:
        """Mock bulk operation."""
        self.call_count += 1
        
        if self.should_fail:
            return {"errors": True, "items": [{"index": {"error": "Mock failure"}}]}
        
        items = []
        for item in body:
            if "index" in item:
                items.append({"index": {"_id": f"doc_{len(items)}", "status": 201}})
        
        return {"errors": False, "items": items}
    
    def _generate_search_hits(self, query: Dict, size: int) -> List[Dict]:
        """Generate mock search hits."""
        hits = []
        
        # Extract query terms for relevance
        query_text = ""
        if "multi_match" in query:
            query_text = query["multi_match"].get("query", "")
        elif "match" in query:
            query_text = list(query["match"].values())[0] if query["match"] else ""
        
        for i in range(min(size, 5)):  # Return up to 5 hits
            score = 1.0 - (i * 0.1)
            
            hits.append({
                "_index": "test-index",
                "_id": f"doc_{i}",
                "_score": score,
                "_source": {
                    "title": f"Test Document {i}",
                    "content": f"This is test content for document {i} related to {query_text}",
                    "path": f"test/document_{i}.md",
                    "tags": ["test", "mock"],
                    "created": "2024-01-01T00:00:00Z"
                }
            })
        
        return hits
    
    def add_search_response(self, query_pattern: str, response: Dict):
        """Add custom search response for specific queries."""
        self.search_responses[query_pattern] = response
    
    def set_failure_mode(self, should_fail: bool = True):
        """Configure failure behavior."""
        self.should_fail = should_fail


class MockIndicesClient:
    """Mock indices client for OpenSearch."""
    
    def __init__(self):
        self.existing_indices = set()
    
    def exists(self, index: str) -> bool:
        """Check if index exists."""
        return index in self.existing_indices
    
    def create(self, index: str, body: Optional[Dict] = None) -> Dict:
        """Create index."""
        self.existing_indices.add(index)
        return {"acknowledged": True}
    
    def delete(self, index: str) -> Dict:
        """Delete index."""
        self.existing_indices.discard(index)
        return {"acknowledged": True}


class MockRedisClient:
    """Mock Redis client for testing."""
    
    def __init__(self):
        self.data = {}
        self.call_count = 0
        self.should_fail = False
    
    async def get(self, key: str) -> Optional[str]:
        """Mock get operation."""
        self.call_count += 1
        
        if self.should_fail:
            raise Exception("Mock Redis failure")
        
        return self.data.get(key)
    
    async def set(self, key: str, value: str, ex: Optional[int] = None) -> bool:
        """Mock set operation."""
        self.call_count += 1
        
        if self.should_fail:
            raise Exception("Mock Redis failure")
        
        self.data[key] = value
        return True
    
    async def delete(self, key: str) -> int:
        """Mock delete operation."""
        self.call_count += 1
        
        if self.should_fail:
            raise Exception("Mock Redis failure")
        
        if key in self.data:
            del self.data[key]
            return 1
        return 0
    
    async def exists(self, key: str) -> bool:
        """Mock exists operation."""
        self.call_count += 1
        return key in self.data
    
    async def ping(self) -> bool:
        """Mock ping operation."""
        return not self.should_fail
    
    def set_failure_mode(self, should_fail: bool = True):
        """Configure failure behavior."""
        self.should_fail = should_fail
    
    def clear_data(self):
        """Clear all stored data."""
        self.data.clear()


class MockTransformersModel:
    """Mock transformer model for embeddings."""
    
    def __init__(self, model_name: str = "intfloat/e5-small-v2"):
        self.model_name = model_name
        self.dimensions = 384
        self.call_count = 0
        self.should_fail = False
    
    def encode(self, texts: List[str], **kwargs) -> np.ndarray:
        """Mock text encoding to embeddings."""
        self.call_count += 1
        
        if self.should_fail:
            raise Exception("Mock model failure")
        
        # Generate deterministic embeddings for testing
        np.random.seed(42)
        embeddings = []
        
        for text in texts:
            # Simple hash-based embedding for consistency
            text_hash = hash(text) % 1000000
            np.random.seed(text_hash)
            embedding = np.random.rand(self.dimensions).astype(np.float32)
            embeddings.append(embedding)
        
        return np.array(embeddings)
    
    def set_failure_mode(self, should_fail: bool = True):
        """Configure failure behavior."""
        self.should_fail = should_fail


class MockVaultProcessor:
    """Mock vault processing for testing."""
    
    def __init__(self):
        self.processed_docs = {}
        self.processing_time = 0.1
    
    def process_vault(self, vault: Dict[str, Dict]) -> Dict[str, Any]:
        """Mock vault processing."""
        time.sleep(self.processing_time)
        
        processed = {
            "total_docs": len(vault),
            "total_chunks": sum(len(doc.get("chunks", [])) for doc in vault.values()),
            "avg_doc_length": np.mean([len(doc.get("content", "")) for doc in vault.values()]),
            "topics": ["machine learning", "programming", "documentation"],
            "connections": [
                {"from": "ML Basics", "to": "Neural Networks", "strength": 0.8},
                {"from": "Programming", "to": "Clean Code", "strength": 0.9}
            ]
        }
        
        self.processed_docs = processed
        return processed
    
    def analyze_patterns(self, vault: Dict[str, Dict]) -> List[Dict]:
        """Mock pattern analysis."""
        return [
            {
                "type": "recurring_themes",
                "description": "Machine learning concepts appear frequently",
                "confidence": 0.85,
                "examples": ["neural networks", "deep learning", "AI"]
            },
            {
                "type": "documentation_style", 
                "description": "Consistent markdown structure",
                "confidence": 0.92,
                "examples": ["# Headers", "## Subheaders", "- Lists"]
            }
        ]


# Factory functions for creating mocks
def create_mock_claude_api(**kwargs) -> MockClaudeAPI:
    """Create configured Claude API mock."""
    return MockClaudeAPI(**kwargs)


def create_mock_opensearch_client(**kwargs) -> MockOpenSearchClient:
    """Create configured OpenSearch client mock."""
    return MockOpenSearchClient(**kwargs)


def create_mock_redis_client(**kwargs) -> MockRedisClient:
    """Create configured Redis client mock."""
    return MockRedisClient(**kwargs)


def create_mock_transformers_model(**kwargs) -> MockTransformersModel:
    """Create configured transformers model mock."""
    return MockTransformersModel(**kwargs)


def create_mock_vault_processor(**kwargs) -> MockVaultProcessor:
    """Create configured vault processor mock."""
    return MockVaultProcessor(**kwargs)


# Export all mock classes and factory functions
__all__ = [
    'MockClaudeAPI',
    'MockOpenSearchClient', 
    'MockRedisClient',
    'MockTransformersModel',
    'MockVaultProcessor',
    'create_mock_claude_api',
    'create_mock_opensearch_client',
    'create_mock_redis_client',
    'create_mock_transformers_model',
    'create_mock_vault_processor'
]