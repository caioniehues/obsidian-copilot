"""
Enhanced assertion utilities for comprehensive test validation.
Provides specialized assertions for API responses, performance, and security testing.
"""

from typing import Dict, List, Any, Optional, Union
import time
import json
import re


class ApiAssertions:
    """Assertions for API response validation."""
    
    @staticmethod
    def assert_valid_response_structure(
        response: Dict[str, Any], 
        required_fields: List[str],
        optional_fields: Optional[List[str]] = None
    ):
        """Assert that response has valid structure with required fields."""
        missing_fields = [field for field in required_fields if field not in response]
        assert not missing_fields, f"Missing required fields: {missing_fields}"
        
        # Validate field types if specified
        type_validators = {
            "status": (int, str),
            "data": (dict, list, str),
            "error": str,
            "message": str,
            "timestamp": str,
            "processing_time": (int, float),
            "version": str
        }
        
        for field, expected_types in type_validators.items():
            if field in response:
                assert isinstance(response[field], expected_types), \
                    f"Field '{field}' should be {expected_types}, got {type(response[field])}"
    
    @staticmethod
    def assert_error_response(
        response: Dict[str, Any], 
        expected_status: int,
        error_message_pattern: Optional[str] = None
    ):
        """Assert that response is a properly formatted error."""
        assert "detail" in response or "error" in response or "message" in response
        
        if "status_code" in response:
            assert response["status_code"] == expected_status
        
        if error_message_pattern:
            error_text = str(response.get("detail", response.get("error", response.get("message", ""))))
            assert re.search(error_message_pattern, error_text, re.IGNORECASE), \
                f"Error message '{error_text}' doesn't match pattern '{error_message_pattern}'"
    
    @staticmethod
    def assert_success_response(
        response: Dict[str, Any],
        expected_data_type: Optional[type] = None
    ):
        """Assert that response indicates success."""
        # Check for success indicators
        success_indicators = [
            response.get("status") == "success",
            response.get("status_code") in [200, 201, 202],
            "error" not in response,
            "data" in response
        ]
        
        assert any(success_indicators), "Response does not indicate success"
        
        if expected_data_type and "data" in response:
            assert isinstance(response["data"], expected_data_type), \
                f"Data should be {expected_data_type}, got {type(response['data'])}"
    
    @staticmethod
    def assert_pagination_response(
        response: Dict[str, Any],
        expected_page_size: Optional[int] = None,
        has_next: Optional[bool] = None
    ):
        """Assert that response has valid pagination structure."""
        pagination_fields = ["page", "page_size", "total", "has_next", "has_previous"]
        present_fields = [field for field in pagination_fields if field in response]
        
        assert len(present_fields) >= 3, "Response missing pagination fields"
        
        if expected_page_size and "page_size" in response:
            assert response["page_size"] == expected_page_size
        
        if has_next is not None and "has_next" in response:
            assert response["has_next"] == has_next
        
        # Validate pagination logic
        if "page" in response and "total" in response and "page_size" in response:
            page = response["page"]
            total = response["total"]
            page_size = response["page_size"]
            
            assert page >= 1, "Page number should be >= 1"
            assert page_size > 0, "Page size should be > 0"
            assert total >= 0, "Total should be >= 0"


class PerformanceAssertions:
    """Assertions for performance validation."""
    
    @staticmethod
    def assert_response_time(
        duration: float,
        max_seconds: float,
        operation: str = "operation"
    ):
        """Assert that operation completed within time threshold."""
        assert duration <= max_seconds, \
            f"{operation} took {duration:.3f}s, expected <= {max_seconds}s"
    
    @staticmethod
    def assert_throughput(
        completed_operations: int,
        duration_seconds: float,
        min_ops_per_second: float,
        operation: str = "operation"
    ):
        """Assert minimum throughput was achieved."""
        actual_throughput = completed_operations / duration_seconds
        assert actual_throughput >= min_ops_per_second, \
            f"{operation} throughput {actual_throughput:.2f} ops/s < {min_ops_per_second} ops/s"
    
    @staticmethod
    def assert_memory_usage(
        initial_memory_mb: float,
        final_memory_mb: float,
        max_increase_mb: float,
        operation: str = "operation"
    ):
        """Assert that memory increase is within acceptable limits."""
        memory_increase = final_memory_mb - initial_memory_mb
        assert memory_increase <= max_increase_mb, \
            f"{operation} memory increase {memory_increase:.2f}MB > {max_increase_mb}MB"
    
    @staticmethod
    def assert_cpu_usage(
        cpu_percent: float,
        max_cpu_percent: float,
        operation: str = "operation"
    ):
        """Assert that CPU usage is within acceptable limits."""
        assert cpu_percent <= max_cpu_percent, \
            f"{operation} CPU usage {cpu_percent:.1f}% > {max_cpu_percent}%"
    
    @staticmethod
    def assert_scalability(
        performance_data: Dict[int, float],
        max_degradation_factor: float = 2.0
    ):
        """Assert that performance scales reasonably with load."""
        if len(performance_data) < 2:
            return
        
        load_levels = sorted(performance_data.keys())
        baseline_load = load_levels[0]
        baseline_time = performance_data[baseline_load]
        
        for load in load_levels[1:]:
            current_time = performance_data[load]
            load_factor = load / baseline_load
            time_factor = current_time / baseline_time
            
            # Performance degradation should not exceed load increase by more than factor
            assert time_factor <= load_factor * max_degradation_factor, \
                f"Performance at load {load} degraded by {time_factor:.2f}x, " \
                f"expected <= {load_factor * max_degradation_factor:.2f}x"


class SecurityAssertions:
    """Assertions for security validation."""
    
    @staticmethod
    def assert_no_sensitive_data_exposure(
        response_text: str,
        sensitive_patterns: List[str]
    ):
        """Assert that response doesn't expose sensitive data."""
        for pattern in sensitive_patterns:
            assert pattern not in response_text, \
                f"Sensitive data pattern '{pattern}' found in response"
    
    @staticmethod
    def assert_api_key_not_logged(
        log_output: str,
        api_key: str,
        allow_partial: bool = True
    ):
        """Assert that API key is not present in logs."""
        assert api_key not in log_output, "Full API key found in logs"
        
        if not allow_partial:
            # Check for partial key exposure
            key_prefix = api_key[:8] if len(api_key) > 8 else api_key[:4]
            assert key_prefix not in log_output, f"Partial API key '{key_prefix}' found in logs"
    
    @staticmethod
    def assert_input_sanitization(
        input_value: str,
        output_value: str,
        malicious_patterns: List[str]
    ):
        """Assert that malicious input patterns are sanitized."""
        for pattern in malicious_patterns:
            if pattern in input_value:
                assert pattern not in output_value, \
                    f"Malicious pattern '{pattern}' not sanitized in output"
    
    @staticmethod
    def assert_secure_headers(
        response_headers: Dict[str, str],
        required_headers: Optional[List[str]] = None
    ):
        """Assert that security headers are present."""
        default_required = [
            "x-content-type-options",
            "x-frame-options", 
            "x-xss-protection"
        ]
        
        required_headers = required_headers or default_required
        headers_lower = {k.lower(): v for k, v in response_headers.items()}
        
        missing_headers = [
            header for header in required_headers 
            if header.lower() not in headers_lower
        ]
        
        assert not missing_headers, f"Missing security headers: {missing_headers}"
    
    @staticmethod
    def assert_rate_limiting(
        response_status_codes: List[int],
        expected_rate_limit_status: int = 429
    ):
        """Assert that rate limiting is functioning."""
        rate_limited_responses = [
            status for status in response_status_codes 
            if status == expected_rate_limit_status
        ]
        
        assert len(rate_limited_responses) > 0, \
            "No rate limiting detected in response sequence"


class DataAssertions:
    """Assertions for data validation."""
    
    @staticmethod
    def assert_valid_vault_document(
        document: Dict[str, Any],
        required_fields: Optional[List[str]] = None
    ):
        """Assert that document has valid vault structure."""
        default_required = ["path", "title", "content"]
        required_fields = required_fields or default_required
        
        missing_fields = [field for field in required_fields if field not in document]
        assert not missing_fields, f"Document missing required fields: {missing_fields}"
        
        # Validate specific field formats
        if "path" in document:
            assert document["path"].endswith(".md"), "Document path should end with .md"
            assert "/" in document["path"] or document["path"].count(".") == 1, \
                "Document path should be valid file path"
        
        if "content" in document:
            assert isinstance(document["content"], str), "Document content should be string"
        
        if "title" in document:
            assert isinstance(document["title"], str), "Document title should be string"
            assert len(document["title"]) > 0, "Document title should not be empty"
    
    @staticmethod
    def assert_valid_markdown_structure(
        markdown_content: str,
        require_title: bool = True,
        min_content_length: int = 10
    ):
        """Assert that content has valid markdown structure."""
        assert isinstance(markdown_content, str), "Markdown content should be string"
        assert len(markdown_content.strip()) >= min_content_length, \
            f"Markdown content too short: {len(markdown_content)} < {min_content_length}"
        
        if require_title:
            # Check for markdown title (starts with #)
            lines = markdown_content.split('\n')
            title_line = next((line for line in lines if line.strip().startswith('#')), None)
            assert title_line is not None, "Markdown should contain a title (line starting with #)"
    
    @staticmethod
    def assert_valid_embeddings(
        embeddings: Any,
        expected_dimensions: Optional[int] = None,
        expected_count: Optional[int] = None
    ):
        """Assert that embeddings have valid structure."""
        import numpy as np
        
        assert isinstance(embeddings, np.ndarray), "Embeddings should be numpy array"
        assert embeddings.dtype == np.float32, "Embeddings should be float32"
        assert len(embeddings.shape) == 2, "Embeddings should be 2D array"
        
        if expected_dimensions:
            assert embeddings.shape[1] == expected_dimensions, \
                f"Embeddings should have {expected_dimensions} dimensions, got {embeddings.shape[1]}"
        
        if expected_count:
            assert embeddings.shape[0] == expected_count, \
                f"Expected {expected_count} embeddings, got {embeddings.shape[0]}"
        
        # Check for valid values (no NaN, reasonable range)
        assert not np.isnan(embeddings).any(), "Embeddings should not contain NaN values"
        assert np.all(np.abs(embeddings) < 100), "Embedding values should be reasonable magnitude"
    
    @staticmethod
    def assert_valid_search_results(
        results: List[Dict[str, Any]],
        query: str,
        min_relevance_score: float = 0.0,
        max_results: Optional[int] = None
    ):
        """Assert that search results are valid and relevant."""
        assert isinstance(results, list), "Search results should be a list"
        
        if max_results:
            assert len(results) <= max_results, \
                f"Too many results: {len(results)} > {max_results}"
        
        for i, result in enumerate(results):
            assert isinstance(result, dict), f"Result {i} should be a dictionary"
            
            # Check for required fields
            required_fields = ["title", "content", "score"]
            missing_fields = [field for field in required_fields if field not in result]
            assert not missing_fields, f"Result {i} missing fields: {missing_fields}"
            
            # Validate score
            score = result["score"]
            assert isinstance(score, (int, float)), f"Result {i} score should be numeric"
            assert score >= min_relevance_score, \
                f"Result {i} score {score} below minimum {min_relevance_score}"
        
        # Results should be sorted by score (descending)
        if len(results) > 1:
            scores = [result["score"] for result in results]
            assert scores == sorted(scores, reverse=True), \
                "Search results should be sorted by score (descending)"


class StreamingAssertions:
    """Assertions for streaming response validation."""
    
    @staticmethod
    async def assert_valid_streaming_response(
        async_iterator,
        expected_chunks: Optional[int] = None,
        max_chunk_delay: float = 1.0,
        min_chunk_size: int = 1
    ):
        """Assert that streaming response is valid."""
        chunks = []
        chunk_times = []
        last_time = time.time()
        
        async for chunk in async_iterator:
            current_time = time.time()
            chunk_delay = current_time - last_time
            
            # Validate chunk timing
            if len(chunks) > 0:  # Skip first chunk timing
                assert chunk_delay <= max_chunk_delay, \
                    f"Chunk delay {chunk_delay:.3f}s > {max_chunk_delay}s"
            
            # Validate chunk content
            assert len(chunk) >= min_chunk_size, \
                f"Chunk too small: {len(chunk)} < {min_chunk_size}"
            
            chunks.append(chunk)
            chunk_times.append(chunk_delay)
            last_time = current_time
        
        # Validate overall streaming behavior
        assert len(chunks) > 0, "No chunks received from stream"
        
        if expected_chunks:
            assert len(chunks) == expected_chunks, \
                f"Expected {expected_chunks} chunks, got {len(chunks)}"
        
        # Combine chunks to validate final content
        full_content = "".join(str(chunk) for chunk in chunks)
        assert len(full_content) > 0, "Combined streaming content is empty"
        
        return {
            "chunks": chunks,
            "chunk_count": len(chunks),
            "total_content": full_content,
            "average_chunk_delay": sum(chunk_times[1:]) / max(1, len(chunk_times) - 1),
            "max_chunk_delay": max(chunk_times[1:]) if len(chunk_times) > 1 else 0
        }


# Convenience functions for common assertion patterns
def assert_api_success(response: Dict[str, Any], expected_data_type: type = dict):
    """Quick assertion for successful API response."""
    ApiAssertions.assert_success_response(response, expected_data_type)


def assert_api_error(response: Dict[str, Any], status: int, message_pattern: str = None):
    """Quick assertion for error API response."""
    ApiAssertions.assert_error_response(response, status, message_pattern)


def assert_fast_response(duration: float, operation: str = "operation"):
    """Quick assertion for fast response (< 500ms)."""
    PerformanceAssertions.assert_response_time(duration, 0.5, operation)


def assert_no_api_key_leak(text: str, api_key: str):
    """Quick assertion that API key is not exposed."""
    SecurityAssertions.assert_no_sensitive_data_exposure(text, [api_key])


def assert_valid_document(doc: Dict[str, Any]):
    """Quick assertion for valid vault document."""
    DataAssertions.assert_valid_vault_document(doc)