"""
Performance tests for search functionality.
Benchmarks semantic search, keyword search, and combined retrieval performance.
"""

import pytest
import time
import asyncio
from typing import List, Dict, Any

from src.prep.build_opensearch_index import query_opensearch
from src.prep.build_semantic_index import query_semantic


@pytest.mark.performance
@pytest.mark.requires_opensearch
class TestSearchPerformance:
    """Performance tests for search operations."""

    @pytest.mark.benchmark(group="search", min_rounds=10)
    def test_opensearch_query_performance(self, benchmark, mock_opensearch_client):
        """Benchmark OpenSearch query performance."""
        query = "machine learning neural networks"
        
        def search_operation():
            return query_opensearch(mock_opensearch_client, query, size=10)
        
        result = benchmark(search_operation)
        
        # Assert reasonable response structure
        assert "hits" in result
        assert isinstance(result["hits"], list)
        
        # Performance assertion
        assert benchmark.stats.mean < 0.2  # Average < 200ms

    @pytest.mark.benchmark(group="search", min_rounds=10)
    def test_semantic_search_performance(self, benchmark, mock_embeddings, mock_transformers):
        """Benchmark semantic search performance."""
        query = "deep learning algorithms"
        
        def semantic_search_operation():
            return query_semantic(query, mock_transformers["tokenizer"], mock_transformers["model"], mock_embeddings, n_results=5)
        
        result = benchmark(semantic_search_operation)
        
        # Assert reasonable response structure
        assert isinstance(result, list)
        assert len(result) <= 5
        
        # Performance assertion
        assert benchmark.stats.mean < 0.15  # Average < 150ms

    @pytest.mark.benchmark(group="search", min_rounds=5)
    async def test_concurrent_search_performance(self, benchmark, mock_opensearch_client, mock_embeddings, mock_transformers):
        """Benchmark concurrent search operations."""
        queries = [
            "machine learning",
            "neural networks", 
            "artificial intelligence",
            "deep learning",
            "data science"
        ]
        
        async def concurrent_searches():
            tasks = []
            for query in queries:
                task1 = asyncio.create_task(
                    asyncio.to_thread(query_opensearch, mock_opensearch_client, query)
                )
                task2 = asyncio.create_task(
                    asyncio.to_thread(query_semantic, query, mock_transformers["tokenizer"], mock_transformers["model"], mock_embeddings, 3)
                )
                tasks.extend([task1, task2])
            
            results = await asyncio.gather(*tasks)
            return results
        
        results = await benchmark.pedantic(concurrent_searches, rounds=5)
        
        # Assert all searches completed
        assert len(results) == len(queries) * 2
        
        # Performance assertion for concurrent execution
        assert benchmark.stats.mean < 1.0  # All searches < 1 second

    @pytest.mark.performance
    def test_search_scalability(self, performance_monitor, mock_opensearch_client):
        """Test search performance with increasing data volumes."""
        document_counts = [100, 500, 1000, 2000]
        query = "machine learning performance"
        
        performance_results = {}
        
        for doc_count in document_counts:
            # Simulate index with doc_count documents
            mock_opensearch_client.count.return_value = {"count": doc_count}
            
            performance_monitor.start(f"search_{doc_count}_docs")
            
            # Perform search
            result = query_opensearch(mock_opensearch_client, query, size=10)
            
            duration = performance_monitor.end(f"search_{doc_count}_docs")
            performance_results[doc_count] = duration
            
            # Assert search completed
            assert "hits" in result
        
        # Performance should scale reasonably
        # Allow some degradation but not exponential
        max_acceptable_duration = 0.5  # 500ms for largest dataset
        assert performance_results[max(document_counts)] < max_acceptable_duration

    @pytest.mark.performance
    @pytest.mark.slow
    def test_search_memory_usage(self, mock_embeddings, mock_transformers):
        """Test memory usage during search operations."""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Perform multiple searches to test memory accumulation
        for i in range(100):
            query = f"test query {i}"
            result = query_semantic(query, mock_transformers["tokenizer"], mock_transformers["model"], mock_embeddings, n_results=5)
            assert isinstance(result, list)
        
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        # Memory increase should be reasonable (< 50MB for 100 searches)
        assert memory_increase < 50, f"Memory increased by {memory_increase:.2f}MB"

    @pytest.mark.performance
    def test_embedding_generation_performance(self, benchmark, mock_transformers):
        """Benchmark embedding generation performance."""
        texts = [
            "Machine learning is a subset of artificial intelligence.",
            "Neural networks are inspired by biological neural networks.",
            "Deep learning uses multiple layers to learn representations.",
            "Natural language processing enables computers to understand text.",
            "Computer vision allows machines to interpret visual information."
        ]
        
        def generate_embeddings():
            embeddings = []
            for text in texts:
                # Simulate embedding generation
                tokens = mock_transformers["tokenizer"](text)
                embedding = mock_transformers["model"](tokens)
                embeddings.append(embedding.last_hidden_state)
            return embeddings
        
        result = benchmark(generate_embeddings)
        
        # Assert embeddings generated
        assert len(result) == len(texts)
        
        # Performance assertion
        assert benchmark.stats.mean < 0.3  # Average < 300ms for 5 texts

    @pytest.mark.performance
    def test_search_result_relevance_performance(self, mock_opensearch_client):
        """Test performance of relevance scoring and ranking."""
        query = "machine learning neural networks"
        result_sizes = [10, 50, 100, 200]
        
        performance_times = {}
        
        for size in result_sizes:
            start_time = time.time()
            
            # Mock search with specified result size
            mock_results = {
                "hits": [
                    {
                        "_source": {"content": f"Document {i}", "title": f"Doc {i}"},
                        "_score": 1.0 - (i * 0.01)
                    }
                    for i in range(size)
                ]
            }
            mock_opensearch_client.search.return_value = mock_results
            
            result = query_opensearch(mock_opensearch_client, query, size=size)
            
            end_time = time.time()
            performance_times[size] = end_time - start_time
            
            # Assert correct number of results
            assert len(result["hits"]) == size
        
        # Performance should not degrade significantly with result size
        max_time = max(performance_times.values())
        assert max_time < 0.1, f"Maximum search time {max_time:.3f}s exceeds threshold"

    @pytest.mark.performance
    @pytest.mark.parametrize("query_length", [5, 20, 50, 100])
    def test_query_length_performance(self, query_length, performance_monitor, mock_opensearch_client):
        """Test search performance with varying query lengths."""
        # Generate query of specified length
        words = ["machine", "learning", "neural", "network", "artificial", "intelligence", "deep", "data"]
        query = " ".join(words * (query_length // len(words) + 1))[:query_length * 7]  # Approximate words
        
        performance_monitor.start(f"query_length_{query_length}")
        
        result = query_opensearch(mock_opensearch_client, query, size=10)
        
        duration = performance_monitor.end(f"query_length_{query_length}")
        
        # Assert search completed
        assert "hits" in result
        
        # Performance should not degrade significantly with query length
        max_acceptable_time = 0.3  # 300ms regardless of query length
        assert duration < max_acceptable_time

    @pytest.mark.performance
    def test_cache_performance_impact(self, mock_redis_client, mock_opensearch_client):
        """Test performance impact of caching layer."""
        query = "cached search performance test"
        
        # First search (cache miss)
        start_time = time.time()
        result1 = query_opensearch(mock_opensearch_client, query, size=10)
        first_search_time = time.time() - start_time
        
        # Simulate cache store
        import json
        cache_key = f"search:{hash(query)}"
        mock_redis_client.set(cache_key, json.dumps(result1))
        
        # Second search (cache hit simulation)
        start_time = time.time()
        cached_result = mock_redis_client.get(cache_key)
        if cached_result:
            result2 = json.loads(cached_result)
        else:
            result2 = query_opensearch(mock_opensearch_client, query, size=10)
        second_search_time = time.time() - start_time
        
        # Cache hit should be significantly faster
        assert second_search_time < first_search_time * 0.5  # At least 50% faster
        assert result1 == result2  # Results should be identical


@pytest.mark.performance
class TestSearchThroughput:
    """Tests for search throughput and concurrent performance."""

    @pytest.mark.slow
    async def test_sustained_search_throughput(self, mock_opensearch_client):
        """Test sustained search throughput over time."""
        duration_seconds = 10
        queries_per_second_target = 50
        
        queries = [f"test query {i}" for i in range(1000)]
        start_time = time.time()
        completed_searches = 0
        
        async def search_worker(query):
            nonlocal completed_searches
            result = await asyncio.to_thread(query_opensearch, mock_opensearch_client, query)
            completed_searches += 1
            return result
        
        # Start search workers
        tasks = []
        query_index = 0
        
        while time.time() - start_time < duration_seconds:
            if len(tasks) < 100:  # Limit concurrent tasks
                task = asyncio.create_task(search_worker(queries[query_index % len(queries)]))
                tasks.append(task)
                query_index += 1
            
            # Clean up completed tasks
            completed_tasks = [task for task in tasks if task.done()]
            for task in completed_tasks:
                tasks.remove(task)
            
            await asyncio.sleep(0.01)  # Small delay to prevent tight loop
        
        # Wait for remaining tasks
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
        
        total_time = time.time() - start_time
        throughput = completed_searches / total_time
        
        assert throughput >= queries_per_second_target, \
            f"Throughput {throughput:.1f} qps below target {queries_per_second_target} qps"