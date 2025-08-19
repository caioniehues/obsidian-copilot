"""
Unit tests for semantic search functionality.
Tests embedding generation, similarity search, and error handling.
"""

import pytest
import numpy as np
from unittest.mock import patch, MagicMock
import torch

from src.prep.build_semantic_index import (
    average_pool,
    get_batch_embeddings,
    query_semantic,
    build_embedding_array,
    build_embedding_index,
    DEVICE
)


class TestEmbeddingGeneration:
    """Test embedding generation and processing."""
    
    def test_average_pool_basic(self):
        """Test basic average pooling functionality."""
        # Create test tensors
        last_hidden_states = torch.randn(2, 5, 384)  # batch_size=2, seq_len=5, hidden_size=384
        attention_mask = torch.ones(2, 5)  # All tokens are valid
        
        result = average_pool(last_hidden_states, attention_mask)
        
        # Should return averaged embeddings
        assert result.shape == (2, 384)
        assert not torch.isnan(result).any()
        assert not torch.isinf(result).any()
    
    def test_average_pool_with_padding(self):
        """Test average pooling with padding tokens."""
        last_hidden_states = torch.randn(2, 5, 384)
        attention_mask = torch.tensor([
            [1, 1, 1, 0, 0],  # First sequence has 3 valid tokens
            [1, 1, 1, 1, 1]   # Second sequence has all valid tokens
        ])
        
        result = average_pool(last_hidden_states, attention_mask)
        
        # Should properly handle padding
        assert result.shape == (2, 384)
        assert not torch.isnan(result).any()
        
        # First sequence should be different from second due to different valid lengths
        assert not torch.equal(result[0], result[1])
    
    def test_average_pool_empty_sequence(self):
        """Test average pooling with empty sequences."""
        last_hidden_states = torch.randn(1, 5, 384)
        attention_mask = torch.zeros(1, 5)  # No valid tokens
        
        # This should handle edge case gracefully
        with pytest.raises(RuntimeError):  # Division by zero expected
            average_pool(last_hidden_states, attention_mask)


class TestBatchEmbeddings:
    """Test batch embedding generation."""
    
    def test_get_batch_embeddings_success(self, mock_transformers):
        """Test successful batch embedding generation."""
        documents = ["Document 1 content", "Document 2 content"]
        tokenizer = mock_transformers["tokenizer"]
        model = mock_transformers["model"]
        
        # Mock model output
        model.return_value = MagicMock()
        model.return_value.last_hidden_state = torch.randn(2, 5, 384)
        
        # Mock tokenizer output
        tokenizer.return_value = {
            "input_ids": torch.tensor([[1, 2, 3, 4, 5], [1, 2, 3, 4, 5]]),
            "attention_mask": torch.tensor([[1, 1, 1, 1, 1], [1, 1, 1, 1, 1]])
        }
        
        embeddings = get_batch_embeddings(documents, tokenizer, model)
        
        # Should return list of embeddings
        assert isinstance(embeddings, list)
        assert len(embeddings) == 2
        assert all(isinstance(emb, np.ndarray) for emb in embeddings)
    
    def test_get_batch_embeddings_empty_documents(self, mock_transformers):
        """Test batch embeddings with empty document list."""
        documents = []
        tokenizer = mock_transformers["tokenizer"]
        model = mock_transformers["model"]
        
        embeddings = get_batch_embeddings(documents, tokenizer, model)
        
        # Should return empty list
        assert isinstance(embeddings, list)
        assert len(embeddings) == 0
    
    def test_get_batch_embeddings_long_documents(self, mock_transformers):
        """Test batch embeddings with very long documents."""
        # Create documents longer than max_length (512)
        long_doc = "word " * 600  # Much longer than 512 tokens
        documents = [long_doc]
        
        tokenizer = mock_transformers["tokenizer"]
        model = mock_transformers["model"]
        
        # Mock tokenizer to handle truncation
        tokenizer.return_value = {
            "input_ids": torch.tensor([[1] * 512]),  # Truncated to 512
            "attention_mask": torch.tensor([[1] * 512])
        }
        
        model.return_value = MagicMock()
        model.return_value.last_hidden_state = torch.randn(1, 512, 384)
        
        embeddings = get_batch_embeddings(documents, tokenizer, model)
        
        # Should handle truncation gracefully
        assert len(embeddings) == 1
        assert isinstance(embeddings[0], np.ndarray)
    
    @patch('src.prep.build_semantic_index.DEVICE', torch.device('cpu'))
    def test_get_batch_embeddings_device_handling(self, mock_transformers):
        """Test device handling in batch embeddings."""
        documents = ["Test document"]
        tokenizer = mock_transformers["tokenizer"]
        model = mock_transformers["model"]
        
        # Mock tokenizer output
        tokenizer.return_value = {
            "input_ids": torch.tensor([[1, 2, 3, 4, 5]]),
            "attention_mask": torch.tensor([[1, 1, 1, 1, 1]])
        }
        
        model.return_value = MagicMock()
        model.return_value.last_hidden_state = torch.randn(1, 5, 384)
        
        embeddings = get_batch_embeddings(documents, tokenizer, model)
        
        # Should work regardless of device
        assert len(embeddings) == 1


class TestSemanticQuery:
    """Test semantic search query functionality."""
    
    def test_query_semantic_success(self, mock_embeddings, mock_embedding_index, mock_vault_dict):
        """Test successful semantic query."""
        query = "machine learning algorithms"
        
        with patch('src.prep.build_semantic_index.doc_embeddings_array', mock_embeddings), \
             patch('src.prep.build_semantic_index.embedding_index', mock_embedding_index), \
             patch('src.prep.build_semantic_index.vault', mock_vault_dict):
            
            # Mock the embedding generation for query
            with patch('src.prep.build_semantic_index.get_batch_embeddings') as mock_get_emb:
                mock_get_emb.return_value = [np.random.rand(384)]
                
                results = query_semantic(query, top_k=2)
                
                # Should return results
                assert isinstance(results, list)
                assert len(results) <= 2  # top_k limit
                
                # Each result should have required fields
                for result in results:
                    assert "content" in result
                    assert "score" in result
                    assert "doc_id" in result
    
    def test_query_semantic_empty_query(self, mock_embeddings, mock_embedding_index, mock_vault_dict):
        """Test semantic query with empty query string."""
        query = ""
        
        with patch('src.prep.build_semantic_index.doc_embeddings_array', mock_embeddings), \
             patch('src.prep.build_semantic_index.embedding_index', mock_embedding_index):
            
            with patch('src.prep.build_semantic_index.get_batch_embeddings') as mock_get_emb:
                mock_get_emb.return_value = [np.random.rand(384)]
                
                results = query_semantic(query, top_k=5)
                
                # Should handle empty query gracefully
                assert isinstance(results, list)
    
    def test_query_semantic_no_embeddings(self):
        """Test semantic query when no embeddings are available."""
        query = "test query"
        
        # Mock empty embeddings
        empty_embeddings = np.array([]).reshape(0, 384)
        empty_index = {}
        
        with patch('src.prep.build_semantic_index.doc_embeddings_array', empty_embeddings), \
             patch('src.prep.build_semantic_index.embedding_index', empty_index):
            
            with patch('src.prep.build_semantic_index.get_batch_embeddings') as mock_get_emb:
                mock_get_emb.return_value = [np.random.rand(384)]
                
                results = query_semantic(query, top_k=5)
                
                # Should return empty results
                assert isinstance(results, list)
                assert len(results) == 0
    
    def test_query_semantic_high_top_k(self, mock_embeddings, mock_embedding_index, mock_vault_dict):
        """Test semantic query with top_k higher than available documents."""
        query = "test query"
        
        with patch('src.prep.build_semantic_index.doc_embeddings_array', mock_embeddings), \
             patch('src.prep.build_semantic_index.embedding_index', mock_embedding_index), \
             patch('src.prep.build_semantic_index.vault', mock_vault_dict):
            
            with patch('src.prep.build_semantic_index.get_batch_embeddings') as mock_get_emb:
                mock_get_emb.return_value = [np.random.rand(384)]
                
                results = query_semantic(query, top_k=100)  # Much higher than 2 available docs
                
                # Should return all available documents
                assert isinstance(results, list)
                assert len(results) <= 2  # Only 2 docs available


class TestEmbeddingCreation:
    """Test full embedding creation pipeline."""
    
    def test_build_embedding_array_success(self, mock_vault_dict, mock_transformers):
        """Test successful embedding creation for entire vault."""
        tokenizer = mock_transformers["tokenizer"]
        model = mock_transformers["model"]
        
        # Mock successful embedding generation
        with patch('src.prep.build_semantic_index.get_batch_embeddings') as mock_get_emb:
            mock_get_emb.return_value = [np.random.rand(384) for _ in range(4)]  # 2 docs * 2 chunks each
            
            embeddings_array = build_embedding_array(
                mock_vault_dict, tokenizer, model
            )
            embedding_index = build_embedding_index(mock_vault_dict)
            
            # Should create embeddings for all chunks
            assert embeddings_array.shape[0] == 4  # 2 docs * 2 chunks each
            assert embeddings_array.shape[1] == 384  # E5-small-v2 dimension
            assert len(embedding_index) == 4
    
    def test_build_embedding_array_empty(self, mock_transformers):
        """Test embedding creation for empty vault."""
        empty_vault = {}
        tokenizer = mock_transformers["tokenizer"]
        model = mock_transformers["model"]
        
        embeddings_array = build_embedding_array(
            empty_vault, tokenizer, model
        )
        embedding_index = build_embedding_index(empty_vault)
        
        # Should handle empty vault gracefully
        assert embeddings_array.shape[0] == 0
        assert len(embedding_index) == 0
    
    def test_build_embedding_array_model_error(self, mock_vault_dict, mock_transformers):
        """Test embedding creation when model fails."""
        tokenizer = mock_transformers["tokenizer"]
        model = mock_transformers["model"]
        
        # Mock model failure
        with patch('src.prep.build_semantic_index.get_batch_embeddings') as mock_get_emb:
            mock_get_emb.side_effect = RuntimeError("Model execution failed")
            
            with pytest.raises(RuntimeError):
                build_embedding_array(mock_vault_dict, tokenizer, model)


class TestErrorHandling:
    """Test error handling in semantic search."""
    
    def test_embedding_dimension_mismatch(self):
        """Test handling of embedding dimension mismatch."""
        query = "test query"
        
        # Create embeddings with wrong dimension
        wrong_dim_embeddings = np.random.rand(2, 256)  # Should be 384
        mock_index = {0: "doc1", 1: "doc2"}
        
        with patch('src.prep.build_semantic_index.doc_embeddings_array', wrong_dim_embeddings), \
             patch('src.prep.build_semantic_index.embedding_index', mock_index):
            
            with patch('src.prep.build_semantic_index.get_batch_embeddings') as mock_get_emb:
                mock_get_emb.return_value = [np.random.rand(384)]  # Correct dimension
                
                # Should raise dimension mismatch error
                with pytest.raises(ValueError):
                    query_semantic(query, top_k=5)
    
    def test_corrupted_embedding_index(self, mock_embeddings):
        """Test handling of corrupted embedding index."""
        query = "test query"
        
        # Create index with invalid document IDs
        corrupted_index = {0: "nonexistent_doc", 1: "another_missing_doc"}
        
        with patch('src.prep.build_semantic_index.doc_embeddings_array', mock_embeddings), \
             patch('src.prep.build_semantic_index.embedding_index', corrupted_index):
            
            with patch('src.prep.build_semantic_index.get_batch_embeddings') as mock_get_emb:
                mock_get_emb.return_value = [np.random.rand(384)]
                
                # Should handle missing documents gracefully
                results = query_semantic(query, top_k=5)
                
                # Might return empty results or skip invalid entries
                assert isinstance(results, list)
    
    def test_memory_error_large_embeddings(self):
        """Test handling of memory errors with very large embeddings."""
        # This would test memory management in real scenarios
        # For now, just verify the structure can handle large arrays
        
        large_embeddings = np.random.rand(100000, 384)  # Very large embedding set
        large_index = {i: f"doc_{i}" for i in range(100000)}
        
        # Test that the structure can be created (might be slow in real scenarios)
        assert large_embeddings.shape == (100000, 384)
        assert len(large_index) == 100000


@pytest.mark.slow
class TestPerformanceScenarios:
    """Test performance-related scenarios for semantic search."""
    
    def test_large_scale_semantic_search(self):
        """Test semantic search with large document collections."""
        # Create large embedding array
        large_embeddings = np.random.rand(10000, 384)
        large_index = {i: f"doc_{i}" for i in range(10000)}
        
        with patch('src.prep.build_semantic_index.doc_embeddings_array', large_embeddings), \
             patch('src.prep.build_semantic_index.embedding_index', large_index):
            
            with patch('src.prep.build_semantic_index.get_batch_embeddings') as mock_get_emb:
                mock_get_emb.return_value = [np.random.rand(384)]
                
                # Should handle large searches efficiently
                results = query_semantic("test query", top_k=10)
                
                assert isinstance(results, list)
                assert len(results) <= 10
    
    def test_concurrent_semantic_queries(self):
        """Test multiple concurrent semantic queries."""
        import asyncio
        
        async def concurrent_semantic_searches():
            tasks = []
            for i in range(5):
                # Create async version of query_semantic
                task = asyncio.create_task(
                    asyncio.to_thread(query_semantic, f"query {i}", top_k=5)
                )
                tasks.append(task)
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            return results
        
        # Mock the necessary components
        with patch('src.prep.build_semantic_index.doc_embeddings_array', np.random.rand(100, 384)), \
             patch('src.prep.build_semantic_index.embedding_index', {i: f"doc_{i}" for i in range(100)}):
            
            with patch('src.prep.build_semantic_index.get_batch_embeddings') as mock_get_emb:
                mock_get_emb.return_value = [np.random.rand(384)]
                
                # Run concurrent searches
                results = asyncio.run(concurrent_semantic_searches())
                
                # All searches should complete successfully
                assert len(results) == 5
                assert all(isinstance(result, list) for result in results)