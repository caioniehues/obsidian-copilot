"""
Test utilities and helper functions for Python tests.
Provides common functionality used across test files.
"""

import json
import time
import asyncio
from typing import Dict, List, Any, Optional, Callable
from unittest.mock import MagicMock, AsyncMock
import numpy as np


class TestTimer:
    """Timer for measuring test execution time."""
    
    def __init__(self):
        self.start_time = None
        self.end_time = None
    
    def start(self):
        """Start the timer."""
        self.start_time = time.time()
    
    def stop(self) -> float:
        """Stop the timer and return elapsed time."""
        self.end_time = time.time()
        return self.elapsed
    
    @property
    def elapsed(self) -> float:
        """Get elapsed time in seconds."""
        if self.start_time is None:
            return 0.0
        end = self.end_time or time.time()
        return end - self.start_time


class PerformanceMonitor:
    """Monitor for tracking performance metrics during tests."""
    
    def __init__(self):
        self.metrics: Dict[str, Dict[str, Any]] = {}
        self.active_timers: Dict[str, TestTimer] = {}
    
    def start(self, operation: str):
        """Start monitoring an operation."""
        timer = TestTimer()
        timer.start()
        self.active_timers[operation] = timer
    
    def end(self, operation: str) -> float:
        """End monitoring and return elapsed time."""
        if operation not in self.active_timers:
            return 0.0
        
        timer = self.active_timers.pop(operation)
        elapsed = timer.stop()
        
        if operation not in self.metrics:
            self.metrics[operation] = {
                'times': [],
                'min_time': elapsed,
                'max_time': elapsed,
                'avg_time': elapsed,
                'count': 0
            }
        
        metric = self.metrics[operation]
        metric['times'].append(elapsed)
        metric['min_time'] = min(metric['min_time'], elapsed)
        metric['max_time'] = max(metric['max_time'], elapsed)
        metric['count'] += 1
        metric['avg_time'] = sum(metric['times']) / len(metric['times'])
        
        return elapsed
    
    def get_metrics(self, operation: str) -> Dict[str, Any]:
        """Get performance metrics for an operation."""
        return self.metrics.get(operation, {})
    
    def reset(self):
        """Reset all metrics."""
        self.metrics.clear()
        self.active_timers.clear()


class MockApiResponse:
    """Mock API response for testing."""
    
    def __init__(self, data: Any, status_code: int = 200, headers: Optional[Dict] = None):
        self.data = data
        self.status_code = status_code
        self.headers = headers or {}
        self.text = json.dumps(data) if isinstance(data, (dict, list)) else str(data)
    
    def json(self):
        """Return JSON data."""
        return self.data
    
    def raise_for_status(self):
        """Raise exception if status indicates error."""
        if self.status_code >= 400:
            raise Exception(f"HTTP {self.status_code}: {self.text}")


class DataGenerator:
    """Generate test data for various scenarios."""
    
    @staticmethod
    def create_vault_dict(doc_count: int = 10) -> Dict[str, Dict]:
        """Create a mock vault dictionary with specified number of documents."""
        vault = {}
        
        for i in range(doc_count):
            doc_id = f"doc_{i}"
            vault[doc_id] = {
                "content": f"# Document {i}\n\nThis is test document {i} with sample content about topic {i % 3}.",
                "title": f"Test Document {i}",
                "path": f"test/document_{i}.md",
                "chunks": [
                    f"This is test document {i} with sample content.",
                    f"Document {i} covers topic {i % 3}.",
                    f"Additional content for document {i}."
                ],
                "tags": [f"tag_{i % 5}", "test", "sample"],
                "created": "2024-01-01T00:00:00Z",
                "modified": "2024-01-01T00:00:00Z"
            }
        
        return vault
    
    @staticmethod
    def create_embeddings(doc_count: int = 10, dimensions: int = 384) -> np.ndarray:
        """Create mock embeddings array."""
        np.random.seed(42)  # For reproducible tests
        return np.random.rand(doc_count, dimensions).astype(np.float32)
    
    @staticmethod
    def create_embedding_index(doc_count: int = 10) -> Dict[int, str]:
        """Create mock embedding index."""
        return {i: f"doc_{i}" for i in range(doc_count)}
    
    @staticmethod
    def create_opensearch_response(query: str, doc_count: int = 3) -> Dict:
        """Create mock OpenSearch response."""
        hits = []
        for i in range(doc_count):
            hits.append({
                "_source": {
                    "content": f"Content for {query} in document {i}",
                    "title": f"Result {i}",
                    "path": f"results/result_{i}.md"
                },
                "_score": 1.0 - (i * 0.1)
            })
        
        return {
            "hits": {
                "hits": hits,
                "total": {"value": doc_count}
            }
        }
    
    @staticmethod
    def create_claude_response(content: str = "Test response") -> Dict:
        """Create mock Claude API response."""
        return {
            "id": "msg_test_123",
            "type": "message",
            "role": "assistant",
            "content": [{"type": "text", "text": content}],
            "model": "claude-3-5-sonnet-20241022",
            "stop_reason": "end_turn",
            "usage": {
                "input_tokens": 10,
                "output_tokens": len(content.split())
            }
        }


class AsyncTestHelper:
    """Helper for async test operations."""
    
    @staticmethod
    async def run_with_timeout(coro, timeout: float = 5.0):
        """Run coroutine with timeout."""
        try:
            return await asyncio.wait_for(coro, timeout=timeout)
        except asyncio.TimeoutError:
            raise TimeoutError(f"Operation timed out after {timeout} seconds")
    
    @staticmethod
    async def collect_stream(async_iter, max_items: int = 100):
        """Collect items from async iterator."""
        items = []
        count = 0
        
        async for item in async_iter:
            items.append(item)
            count += 1
            if count >= max_items:
                break
        
        return items
    
    @staticmethod
    def create_mock_stream(items: List[Any], delay: float = 0.01):
        """Create mock async stream."""
        async def mock_stream():
            for item in items:
                if delay > 0:
                    await asyncio.sleep(delay)
                yield item
        
        return mock_stream()


class MockGenerator:
    """Generate various types of mocks for testing."""
    
    @staticmethod
    def create_mock_opensearch_client():
        """Create mock OpenSearch client."""
        mock_client = MagicMock()
        
        # Mock successful connection
        mock_client.info.return_value = {"version": {"number": "2.7.0"}}
        
        # Mock search responses
        mock_client.search.return_value = DataGenerator.create_opensearch_response("test query")
        
        # Mock index operations
        mock_client.indices.exists.return_value = True
        mock_client.indices.create.return_value = {"acknowledged": True}
        mock_client.indices.delete.return_value = {"acknowledged": True}
        
        # Mock bulk operations
        mock_client.bulk.return_value = {"errors": False, "items": []}
        
        return mock_client
    
    @staticmethod
    def create_mock_redis_client():
        """Create mock Redis client."""
        mock_client = AsyncMock()
        
        # Mock basic operations
        mock_client.get.return_value = None
        mock_client.set.return_value = True
        mock_client.delete.return_value = 1
        mock_client.exists.return_value = False
        
        # Mock connection
        mock_client.ping.return_value = True
        
        return mock_client
    
    @staticmethod
    def create_mock_transformers():
        """Create mock transformers components."""
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


class TestAssertions:
    """Custom assertions for testing."""
    
    @staticmethod
    def assert_response_structure(response: Dict, required_fields: List[str]):
        """Assert response has required structure."""
        assert isinstance(response, dict), "Response should be a dictionary"
        
        for field in required_fields:
            assert field in response, f"Missing required field: {field}"
    
    @staticmethod
    def assert_performance_threshold(duration: float, max_seconds: float, operation: str = "operation"):
        """Assert operation completed within performance threshold."""
        assert duration <= max_seconds, \
            f"{operation} took {duration:.3f}s, expected <= {max_seconds}s"
    
    @staticmethod
    def assert_valid_embeddings(embeddings: np.ndarray, expected_shape: Optional[tuple] = None):
        """Assert embeddings have valid structure."""
        assert isinstance(embeddings, np.ndarray), "Embeddings should be numpy array"
        assert embeddings.dtype == np.float32, "Embeddings should be float32"
        assert len(embeddings.shape) == 2, "Embeddings should be 2D array"
        
        if expected_shape:
            assert embeddings.shape == expected_shape, \
                f"Expected shape {expected_shape}, got {embeddings.shape}"
        
        # Check for valid values
        assert not np.isnan(embeddings).any(), "Embeddings should not contain NaN"
        assert np.all(np.abs(embeddings) < 100), "Embedding values should be reasonable"
    
    @staticmethod
    def assert_search_results(results: List[Dict], min_count: int = 1, max_count: int = 10):
        """Assert search results are valid."""
        assert isinstance(results, list), "Results should be a list"
        assert min_count <= len(results) <= max_count, \
            f"Expected {min_count}-{max_count} results, got {len(results)}"
        
        for i, result in enumerate(results):
            assert isinstance(result, dict), f"Result {i} should be a dictionary"
            assert "title" in result, f"Result {i} missing title"
            assert "content" in result, f"Result {i} missing content"


class ConfigManager:
    """Manage test configuration and environment."""
    
    def __init__(self):
        self.original_env = {}
        self.test_config = {}
    
    def set_test_env(self, **env_vars):
        """Set test environment variables."""
        import os
        
        for key, value in env_vars.items():
            self.original_env[key] = os.environ.get(key)
            os.environ[key] = str(value)
    
    def restore_env(self):
        """Restore original environment variables."""
        import os
        
        for key, original_value in self.original_env.items():
            if original_value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = original_value
        
        self.original_env.clear()
    
    def get_test_config(self) -> Dict:
        """Get test configuration."""
        return {
            "test_mode": True,
            "mock_apis": True,
            "disable_cache": True,
            "log_level": "DEBUG",
            **self.test_config
        }


# Utility functions for common test operations
def wait_for_condition(condition: Callable[[], bool], timeout: float = 5.0, interval: float = 0.1):
    """Wait for a condition to become true."""
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        if condition():
            return True
        time.sleep(interval)
    
    return False


def create_temp_file(content: str, suffix: str = ".md") -> str:
    """Create temporary file with content."""
    import tempfile
    
    with tempfile.NamedTemporaryFile(mode='w', suffix=suffix, delete=False) as f:
        f.write(content)
        return f.name


def cleanup_temp_files(file_paths: List[str]):
    """Clean up temporary files."""
    import os
    
    for path in file_paths:
        try:
            os.unlink(path)
        except (OSError, FileNotFoundError):
            pass


# Export commonly used classes and functions
__all__ = [
    'TestTimer',
    'PerformanceMonitor', 
    'MockApiResponse',
    'DataGenerator',
    'AsyncTestHelper',
    'MockGenerator',
    'TestAssertions',
    'ConfigManager',
    'wait_for_condition',
    'create_temp_file',
    'cleanup_temp_files'
]