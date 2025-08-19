"""
Unit tests for OpenSearch integration functionality.
Tests connection handling, error recovery, and search operations.
"""

import pytest
from unittest.mock import patch, MagicMock
from opensearchpy import ConnectionError, RequestError, TransportError

from src.prep.build_opensearch_index import (
    get_opensearch, 
    create_index, 
    index_vault, 
    query_opensearch,
    INDEX_NAME
)


class TestOpenSearchConnection:
    """Test OpenSearch connection and error handling."""
    
    def test_get_opensearch_successful_connection(self):
        """Test successful OpenSearch connection."""
        client = get_opensearch("localhost")
        assert client is not None
        assert hasattr(client, 'info')
        assert hasattr(client, 'search')
    
    @patch('src.prep.build_opensearch_index.OpenSearch')
    def test_get_opensearch_connection_error_handling(self, mock_opensearch):
        """Test OpenSearch connection error handling."""
        # Simulate connection failure
        mock_opensearch.side_effect = ConnectionError("Connection failed")
        
        with pytest.raises(ConnectionError):
            get_opensearch("invalid-host")
    
    def test_get_opensearch_with_different_hosts(self):
        """Test OpenSearch client creation with different hosts."""
        # Test with opensearch host
        client1 = get_opensearch("opensearch")
        assert client1 is not None
        
        # Test with localhost
        client2 = get_opensearch("localhost")
        assert client2 is not None
        
        # Both should have same interface but different host configs
        assert hasattr(client1, 'info')
        assert hasattr(client2, 'info')


class TestIndexOperations:
    """Test index creation, deletion, and management."""
    
    def test_create_index_success(self, mock_opensearch_client):
        """Test successful index creation."""
        mock_opensearch_client.indices.exists.return_value = False
        mock_opensearch_client.indices.create.return_value = {"acknowledged": True}
        
        # Should not raise exception
        create_index(mock_opensearch_client, INDEX_NAME)
        
        # Verify index creation was called
        mock_opensearch_client.indices.create.assert_called_once()
    
    def test_create_index_already_exists(self, mock_opensearch_client):
        """Test index creation when index already exists."""
        mock_opensearch_client.indices.exists.return_value = True
        
        # Should handle existing index gracefully
        create_index(mock_opensearch_client, INDEX_NAME)
        
        # Should not attempt to create
        mock_opensearch_client.indices.create.assert_not_called()
    
    def test_create_index_error_handling(self, mock_opensearch_client):
        """Test index creation error handling."""
        mock_opensearch_client.indices.exists.return_value = False
        mock_opensearch_client.indices.create.side_effect = RequestError("Index creation failed")
        
        with pytest.raises(RequestError):
            create_index(mock_opensearch_client, INDEX_NAME)


class TestDocumentIndexing:
    """Test document indexing operations."""
    
    def test_index_vault_success(self, mock_opensearch_client, mock_vault_dict):
        """Test successful document indexing."""
        from opensearchpy.helpers import bulk
        
        with patch('src.prep.build_opensearch_index.bulk') as mock_bulk:
            mock_bulk.return_value = (2, [])  # 2 successful, 0 errors
            
            # Should not raise exception
            index_vault(mock_opensearch_client, mock_vault_dict)
            
            # Verify bulk indexing was called
            mock_bulk.assert_called_once()
    
    def test_index_vault_partial_failure(self, mock_opensearch_client, mock_vault_dict):
        """Test document indexing with partial failures."""
        from opensearchpy.helpers import bulk, BulkIndexError
        
        with patch('src.prep.build_opensearch_index.bulk') as mock_bulk:
            # Simulate partial failure
            mock_bulk.side_effect = BulkIndexError("Some documents failed", [])
            
            with pytest.raises(BulkIndexError):
                index_vault(mock_opensearch_client, mock_vault_dict)
    
    def test_index_vault_empty_vault(self, mock_opensearch_client):
        """Test indexing with empty vault."""
        empty_vault = {}
        
        # Should handle empty vault gracefully
        with patch('src.prep.build_opensearch_index.bulk') as mock_bulk:
            index_vault(mock_opensearch_client, empty_vault)
            
            # Should still call bulk but with empty docs
            mock_bulk.assert_called_once()


class TestSearchOperations:
    """Test search functionality and error handling."""
    
    def test_query_opensearch_success(self, mock_opensearch_client):
        """Test successful OpenSearch query."""
        query = "machine learning"
        
        result = query_opensearch(query, mock_opensearch_client, INDEX_NAME)
        
        # Should return search results
        assert "hits" in result
        assert len(result["hits"]["hits"]) > 0
        
        # Verify search was called with correct parameters
        mock_opensearch_client.search.assert_called_once()
        search_call = mock_opensearch_client.search.call_args
        assert search_call[1]["index"] == INDEX_NAME
    
    def test_query_opensearch_empty_query(self, mock_opensearch_client):
        """Test OpenSearch query with empty query string."""
        query = ""
        
        result = query_opensearch(query, mock_opensearch_client, INDEX_NAME)
        
        # Should still execute search
        assert result is not None
        mock_opensearch_client.search.assert_called_once()
    
    def test_query_opensearch_connection_error(self, mock_opensearch_client):
        """Test OpenSearch query with connection error."""
        mock_opensearch_client.search.side_effect = ConnectionError("Connection lost")
        
        with pytest.raises(ConnectionError):
            query_opensearch("test query", mock_opensearch_client, INDEX_NAME)
    
    def test_query_opensearch_transport_error(self, mock_opensearch_client):
        """Test OpenSearch query with transport error."""
        mock_opensearch_client.search.side_effect = TransportError("Transport failed")
        
        with pytest.raises(TransportError):
            query_opensearch("test query", mock_opensearch_client, INDEX_NAME)
    
    def test_query_opensearch_request_error(self, mock_opensearch_client):
        """Test OpenSearch query with request error."""
        mock_opensearch_client.search.side_effect = RequestError("Bad request")
        
        with pytest.raises(RequestError):
            query_opensearch("test query", mock_opensearch_client, INDEX_NAME)
    
    def test_query_opensearch_large_query(self, mock_opensearch_client):
        """Test OpenSearch query with very large query string."""
        # Create a large query (simulate edge case)
        large_query = "machine learning " * 1000
        
        result = query_opensearch(large_query, mock_opensearch_client, INDEX_NAME)
        
        # Should handle large queries
        assert result is not None
        mock_opensearch_client.search.assert_called_once()


class TestErrorRecoveryPatterns:
    """Test error recovery and resilience patterns."""
    
    @pytest.mark.integration
    def test_opensearch_fallback_mechanism(self):
        """Test fallback from opensearch to localhost."""
        # This tests the actual fallback logic in app.py
        with patch('src.prep.build_opensearch_index.get_opensearch') as mock_get:
            # First call (opensearch) fails
            mock_get.side_effect = [ConnectionError("Connection refused"), MagicMock()]
            
            from src.app import os_client
            
            # Should have attempted both connections
            assert mock_get.call_count >= 1
    
    def test_opensearch_retry_logic(self, mock_opensearch_client):
        """Test retry logic for transient failures."""
        # This would test retry mechanisms once implemented
        mock_opensearch_client.search.side_effect = [
            TransportError("Temporary failure"),
            TransportError("Still failing"),
            {"hits": {"hits": []}}  # Success on third try
        ]
        
        # TODO: Implement retry logic in the actual code
        # For now, test that we can detect the pattern
        with pytest.raises(TransportError):
            query_opensearch("test", mock_opensearch_client, INDEX_NAME)


@pytest.mark.slow
class TestPerformanceScenarios:
    """Test performance-related scenarios."""
    
    def test_large_document_indexing(self, mock_opensearch_client):
        """Test indexing performance with large documents."""
        # Create large document set
        large_vault = {}
        for i in range(1000):
            large_vault[f"doc_{i}"] = {
                "content": f"Large document {i} content " * 100,
                "title": f"Doc {i}",
                "chunks": [f"Chunk {j} for doc {i}" for j in range(10)]
            }
        
        with patch('src.prep.build_opensearch_index.bulk') as mock_bulk:
            mock_bulk.return_value = (1000, [])
            
            # Should handle large document sets
            index_vault(mock_opensearch_client, large_vault)
            
            mock_bulk.assert_called_once()
    
    def test_concurrent_search_operations(self, mock_opensearch_client):
        """Test multiple concurrent search operations."""
        import asyncio
        
        async def concurrent_searches():
            tasks = []
            for i in range(10):
                # Create async version of query_opensearch
                task = asyncio.create_task(
                    asyncio.to_thread(
                        query_opensearch, 
                        f"query {i}", 
                        mock_opensearch_client, 
                        INDEX_NAME
                    )
                )
                tasks.append(task)
            
            results = await asyncio.gather(*tasks)
            return results
        
        # Run concurrent searches
        results = asyncio.run(concurrent_searches())
        
        # All searches should complete
        assert len(results) == 10
        assert all(result is not None for result in results)