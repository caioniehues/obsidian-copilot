"""
Pytest configuration and shared fixtures for Obsidian Copilot testing.
Provides comprehensive mocking and test utilities following TDD best practices.
"""

import asyncio
import os
import pickle
import tempfile
from typing import Dict, List, Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import numpy as np
from fastapi.testclient import TestClient
from httpx import AsyncClient
import fakeredis.aioredis

from src.app import app
from src.prep.build_opensearch_index import get_opensearch


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


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
def mock_vault_dict():
    """Mock vault dictionary with test documents."""
    return {
        "doc1": {
            "content": "# Test Document 1\nThis is a test document about machine learning.",
            "title": "ML Basics",
            "path": "ml/basics.md",
            "chunks": [
                "This is a test document about machine learning.",
                "Machine learning is a subset of AI."
            ]
        },
        "doc2": {
            "content": "# Test Document 2\nThis covers advanced topics in AI.",
            "title": "AI Advanced",
            "path": "ai/advanced.md", 
            "chunks": [
                "This covers advanced topics in AI.",
                "Advanced AI includes neural networks."
            ]
        }
    }


@pytest.fixture
def mock_embeddings():
    """Mock embeddings array for semantic search testing."""
    # 2 documents, 384-dimensional embeddings (E5-small-v2 size)
    return np.random.rand(2, 384).astype(np.float32)


@pytest.fixture
def mock_embedding_index():
    """Mock embedding index mapping."""
    return {
        0: "doc1",
        1: "doc2"
    }


@pytest.fixture
def temp_data_dir(mock_vault_dict, mock_embeddings, mock_embedding_index):
    """Create temporary data directory with mock files."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create mock pickle files
        vault_path = os.path.join(temp_dir, "vault_dict.pickle")
        with open(vault_path, "wb") as f:
            pickle.dump(mock_vault_dict, f)
        
        embeddings_path = os.path.join(temp_dir, "doc_embeddings_array.npy")
        np.save(embeddings_path, mock_embeddings)
        
        index_path = os.path.join(temp_dir, "embedding_index.pickle")
        with open(index_path, "wb") as f:
            pickle.dump(mock_embedding_index, f)
        
        # Patch the data directory
        with patch.dict(os.environ, {"DATA_DIR": temp_dir}):
            yield temp_dir


@pytest.fixture
def mock_opensearch_client():
    """Mock OpenSearch client for testing."""
    mock_client = MagicMock()
    
    # Mock successful connection
    mock_client.info.return_value = {"version": {"number": "2.7.0"}}
    
    # Mock search responses
    mock_client.search.return_value = {
        "hits": {
            "hits": [
                {
                    "_source": {"content": "Test content 1", "title": "Test 1"},
                    "_score": 0.95
                },
                {
                    "_source": {"content": "Test content 2", "title": "Test 2"},
                    "_score": 0.87
                }
            ]
        }
    }
    
    # Mock index operations
    mock_client.indices.exists.return_value = True
    mock_client.indices.create.return_value = {"acknowledged": True}
    mock_client.indices.delete.return_value = {"acknowledged": True}
    
    return mock_client


@pytest.fixture
def mock_redis_client():
    """Mock Redis client using fakeredis."""
    return fakeredis.aioredis.FakeRedis()


@pytest.fixture
def mock_transformers():
    """Mock transformers components for testing."""
    mock_tokenizer = MagicMock()
    mock_tokenizer.return_value = {
        "input_ids": [[1, 2, 3, 4, 5]],
        "attention_mask": [[1, 1, 1, 1, 1]]
    }
    
    mock_model = MagicMock()
    mock_model.return_value.last_hidden_state = np.random.rand(1, 5, 384)
    
    return {
        "tokenizer": mock_tokenizer,
        "model": mock_model
    }


@pytest.fixture
def mock_subprocess():
    """Mock subprocess calls for Claude CLI testing."""
    with patch("subprocess.run") as mock_run:
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = "Mocked Claude response"
        mock_run.return_value.stderr = ""
        yield mock_run


@pytest.fixture
def mock_agent_config():
    """Mock agent configuration for testing."""
    return {
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
            },
            "context-optimizer": {
                "role": "Context Optimization Specialist",
                "capabilities": ["context_optimization", "relevance_scoring"],
                "max_parallel_tasks": 4
            }
        }
    }


@pytest.fixture(autouse=True)
def setup_test_environment(
    mock_opensearch_client,
    mock_redis_client, 
    mock_transformers,
    temp_data_dir
):
    """Automatically setup test environment for all tests."""
    with patch("src.app.get_opensearch", return_value=mock_opensearch_client), \
         patch("src.app.vault", mock_vault_dict), \
         patch("src.app.doc_embeddings_array", mock_embeddings), \
         patch("src.app.embedding_index", mock_embedding_index), \
         patch("transformers.AutoTokenizer.from_pretrained", return_value=mock_transformers["tokenizer"]), \
         patch("transformers.AutoModel.from_pretrained", return_value=mock_transformers["model"]):
        yield


class MockAsyncContext:
    """Helper for mocking async context managers."""
    
    def __init__(self, return_value):
        self.return_value = return_value
    
    async def __aenter__(self):
        return self.return_value
    
    async def __aexit__(self, *args):
        pass


@pytest.fixture
def mock_file_operations():
    """Mock file system operations for testing."""
    with patch("builtins.open"), \
         patch("pickle.load"), \
         patch("pickle.dump"), \
         patch("numpy.load"), \
         patch("numpy.save"), \
         patch("os.path.exists", return_value=True):
        yield


# Utility functions for test assertions

def assert_response_structure(response: Dict[str, Any], required_fields: List[str]):
    """Assert that response contains all required fields."""
    for field in required_fields:
        assert field in response, f"Missing required field: {field}"


def assert_error_response(response: Dict[str, Any], expected_status: int):
    """Assert error response structure."""
    assert "detail" in response
    assert response.get("status_code") == expected_status


# Test data factories

class TestDataFactory:
    """Factory for generating test data."""
    
    @staticmethod
    def create_generation_request(**kwargs):
        """Create a GenerationRequest for testing."""
        defaults = {
            "query": "Test query about machine learning",
            "context_strategy": "smart_chunks",
            "system_prompt": "You are a helpful assistant.",
            "temperature": 0.7,
            "max_tokens": 1000,
            "model": "claude-3-5-sonnet-20241022"
        }
        defaults.update(kwargs)
        return defaults
    
    @staticmethod
    def create_vault_analysis_request(**kwargs):
        """Create a VaultAnalysisRequest for testing."""
        defaults = {
            "focus_areas": ["patterns", "gaps", "connections"],
            "analysis_depth": "comprehensive",
            "include_metrics": True
        }
        defaults.update(kwargs)
        return defaults