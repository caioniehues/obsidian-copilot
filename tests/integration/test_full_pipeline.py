"""
Integration tests for the complete Obsidian Copilot pipeline.
Tests end-to-end functionality from query to response.
"""

import pytest
import asyncio
from fastapi.testclient import TestClient
from unittest.mock import patch

from src.app import app


@pytest.mark.integration
class TestFullPipeline:
    """Test complete query processing pipeline."""

    def test_complete_query_flow(self, test_client, mock_vault_dict, mock_embeddings):
        """Test the complete flow from query to response."""
        request_data = {
            "query": "Explain machine learning concepts",
            "context_strategy": "smart_chunks",
            "temperature": 0.7,
            "max_tokens": 1000,
            "model": "claude-3-5-sonnet-20241022"
        }

        with patch('src.app.vault', mock_vault_dict), \
             patch('src.app.doc_embeddings_array', mock_embeddings):
            
            response = test_client.post("/query", json=request_data)

        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert "response" in data
        assert "retrieved_docs" in data
        assert "processing_time" in data
        assert "model_used" in data
        
        # Verify content quality
        assert len(data["response"]) > 10
        assert isinstance(data["retrieved_docs"], list)
        assert data["processing_time"] > 0

    def test_vault_analysis_integration(self, test_client, comprehensive_vault_dict):
        """Test vault analysis with comprehensive dataset."""
        request_data = {
            "focus_areas": ["patterns", "gaps", "connections"],
            "analysis_depth": "comprehensive",
            "include_metrics": True
        }

        with patch('src.app.vault', comprehensive_vault_dict):
            response = test_client.post("/vault-analysis", json=request_data)

        assert response.status_code == 200
        data = response.json()
        
        # Verify analysis components
        assert "patterns" in data
        assert "gaps" in data
        assert "connections" in data
        assert "metrics" in data
        
        # Verify pattern detection
        assert len(data["patterns"]) > 0
        for pattern in data["patterns"]:
            assert "type" in pattern
            assert "description" in pattern
            assert "confidence" in pattern

    @pytest.mark.slow
    def test_streaming_response_integration(self, test_client, mock_vault_dict):
        """Test streaming response functionality."""
        request_data = {
            "query": "Generate a comprehensive overview",
            "context_strategy": "full_docs",
            "temperature": 0.5,
            "max_tokens": 2000,
            "stream": True
        }

        with patch('src.app.vault', mock_vault_dict):
            response = test_client.post("/generate-streaming", json=request_data)

        assert response.status_code == 200
        
        # Verify streaming headers
        assert response.headers.get("content-type") == "text/plain; charset=utf-8"
        
        # Collect streaming chunks
        chunks = []
        for chunk in response.iter_lines():
            if chunk:
                chunks.append(chunk.decode())
        
        assert len(chunks) > 0
        full_response = "".join(chunks)
        assert len(full_response) > 50

    def test_error_handling_integration(self, test_client):
        """Test error handling across the pipeline."""
        # Test invalid request
        invalid_request = {
            "query": "",  # Empty query
            "context_strategy": "invalid_strategy"
        }

        response = test_client.post("/query", json=invalid_request)
        assert response.status_code == 422  # Validation error

        # Test missing required fields
        incomplete_request = {"temperature": 0.5}
        response = test_client.post("/query", json=incomplete_request)
        assert response.status_code == 422

    @pytest.mark.requires_opensearch
    def test_search_integration(self, test_client, mock_opensearch_client, mock_vault_dict):
        """Test search functionality integration."""
        # Test query that should trigger search
        request_data = {
            "query": "machine learning neural networks",
            "context_strategy": "smart_chunks",
            "max_tokens": 500
        }

        with patch('src.app.get_opensearch', return_value=mock_opensearch_client), \
             patch('src.app.vault', mock_vault_dict):
            
            response = test_client.post("/query", json=request_data)

        assert response.status_code == 200
        data = response.json()
        
        # Verify search was performed
        assert len(data["retrieved_docs"]) > 0
        
        # Verify document relevance
        for doc in data["retrieved_docs"]:
            assert "title" in doc
            assert "content" in doc
            assert "score" in doc
            assert doc["score"] > 0


@pytest.mark.integration
@pytest.mark.performance
class TestPipelinePerformance:
    """Test performance characteristics of the pipeline."""

    def test_query_response_time(self, test_client, performance_monitor, mock_vault_dict):
        """Test that queries complete within acceptable time."""
        request_data = {
            "query": "Quick test query for performance",
            "context_strategy": "smart_chunks",
            "max_tokens": 100
        }

        performance_monitor.start("query_performance")
        
        with patch('src.app.vault', mock_vault_dict):
            response = test_client.post("/query", json=request_data)
        
        duration = performance_monitor.end("query_performance")

        assert response.status_code == 200
        assert duration < 2.0  # Should complete within 2 seconds

    def test_concurrent_queries(self, test_client, mock_vault_dict):
        """Test handling of concurrent queries."""
        import concurrent.futures
        import threading

        def make_query(query_id):
            request_data = {
                "query": f"Concurrent test query {query_id}",
                "context_strategy": "smart_chunks",
                "max_tokens": 100
            }
            
            with patch('src.app.vault', mock_vault_dict):
                response = test_client.post("/query", json=request_data)
            
            return response.status_code, query_id

        # Run 5 concurrent queries
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(make_query, i) for i in range(5)]
            results = [future.result() for future in futures]

        # All queries should succeed
        for status_code, query_id in results:
            assert status_code == 200

    @pytest.mark.slow
    def test_large_vault_performance(self, test_client, large_vault_dict):
        """Test performance with large vault data."""
        request_data = {
            "query": "Analyze patterns in large dataset",
            "context_strategy": "hierarchical",
            "max_tokens": 500
        }

        performance_monitor = performance_monitor
        performance_monitor.start("large_vault_query")
        
        with patch('src.app.vault', large_vault_dict):
            response = test_client.post("/query", json=request_data)
        
        duration = performance_monitor.end("large_vault_query")

        assert response.status_code == 200
        assert duration < 5.0  # Should complete within 5 seconds even with large data

    def test_memory_usage_during_processing(self, test_client, mock_vault_dict):
        """Test memory usage remains reasonable during processing."""
        import psutil
        import os

        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB

        # Perform multiple queries
        for i in range(10):
            request_data = {
                "query": f"Memory test query {i}",
                "context_strategy": "smart_chunks",
                "max_tokens": 200
            }
            
            with patch('src.app.vault', mock_vault_dict):
                response = test_client.post("/query", json=request_data)
            
            assert response.status_code == 200

        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory

        # Memory increase should be reasonable (< 100MB for 10 queries)
        assert memory_increase < 100