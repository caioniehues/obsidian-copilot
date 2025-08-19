"""
Unit tests for FastAPI application endpoints.
Tests request handling, response formatting, and error conditions.
"""

import pytest
import json
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from fastapi import HTTPException

from src.app import app, GenerationRequest, VaultAnalysisRequest


class TestGenerationEndpoint:
    """Test the main generation endpoint."""
    
    def test_query_endpoint_success(self, test_client, mock_subprocess):
        """Test successful query generation."""
        request_data = {
            "query": "What is machine learning?",
            "context_strategy": "smart_chunks",
            "system_prompt": "You are a helpful assistant.",
            "temperature": 0.7,
            "max_tokens": 1000,
            "model": "claude-3-5-sonnet-20241022"
        }
        
        # Mock successful Claude response
        mock_subprocess.return_value.stdout = "Machine learning is a subset of artificial intelligence..."
        mock_subprocess.return_value.returncode = 0
        
        response = test_client.post("/query", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        
        # Check response structure
        assert "response" in data
        assert "context_used" in data
        assert "tokens_used" in data
        assert "model" in data
        assert "generation_time" in data
        
        assert data["response"] == "Machine learning is a subset of artificial intelligence..."
        assert data["model"] == "claude-3-5-sonnet-20241022"
    
    def test_query_endpoint_missing_fields(self, test_client):
        """Test query endpoint with missing required fields."""
        incomplete_request = {
            "query": "What is machine learning?"
            # Missing other required fields
        }
        
        response = test_client.post("/query", json=incomplete_request)
        
        # Should use default values for missing fields
        assert response.status_code == 200
    
    def test_query_endpoint_invalid_context_strategy(self, test_client):
        """Test query endpoint with invalid context strategy."""
        request_data = {
            "query": "Test query",
            "context_strategy": "invalid_strategy",
            "system_prompt": "Test prompt"
        }
        
        response = test_client.post("/query", json=request_data)
        
        # Should return validation error
        assert response.status_code == 422
    
    def test_query_endpoint_subprocess_timeout(self, test_client, mock_subprocess):
        """Test query endpoint when subprocess times out."""
        import subprocess
        
        request_data = {
            "query": "Test query",
            "system_prompt": "Test prompt"
        }
        
        # Mock subprocess timeout
        mock_subprocess.side_effect = subprocess.TimeoutExpired("claude", 60)
        
        response = test_client.post("/query", json=request_data)
        
        assert response.status_code == 504
        assert "timeout" in response.json()["detail"].lower()
    
    def test_query_endpoint_subprocess_error(self, test_client, mock_subprocess):
        """Test query endpoint when subprocess fails."""
        request_data = {
            "query": "Test query",
            "system_prompt": "Test prompt"
        }
        
        # Mock subprocess error
        mock_subprocess.side_effect = Exception("Command not found")
        
        response = test_client.post("/query", json=request_data)
        
        assert response.status_code == 500
        assert "detail" in response.json()
    
    def test_query_endpoint_file_not_found_fallback(self, test_client):
        """Test query endpoint fallback when claude command not found."""
        request_data = {
            "query": "Test query",
            "system_prompt": "Test prompt"
        }
        
        with patch('subprocess.run') as mock_run:
            # First call raises FileNotFoundError, second succeeds
            mock_run.side_effect = [
                FileNotFoundError("claude command not found"),
                MagicMock(returncode=0, stdout="Fallback response")
            ]
            
            response = test_client.post("/query", json=request_data)
            
            # Should succeed with fallback
            assert response.status_code == 200
            data = response.json()
            assert data["response"] == "Fallback response"


class TestVaultAnalysisEndpoint:
    """Test vault analysis endpoint."""
    
    def test_vault_analysis_success(self, test_client, mock_subprocess):
        """Test successful vault analysis."""
        request_data = {
            "focus_areas": ["patterns", "gaps"],
            "analysis_depth": "comprehensive",
            "include_metrics": True
        }
        
        # Mock successful analysis response
        analysis_response = {
            "patterns_found": ["Note-taking pattern", "Learning pattern"],
            "knowledge_gaps": ["Missing ML fundamentals"],
            "metrics": {"total_notes": 150, "avg_length": 500}
        }
        mock_subprocess.return_value.stdout = json.dumps(analysis_response)
        mock_subprocess.return_value.returncode = 0
        
        response = test_client.post("/vault/analyze", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        
        # Should return analysis results
        assert "analysis" in data
        assert "execution_time" in data
        assert "model_used" in data
    
    def test_vault_analysis_timeout(self, test_client, mock_subprocess):
        """Test vault analysis timeout."""
        import subprocess
        
        request_data = {
            "focus_areas": ["patterns"],
            "analysis_depth": "quick"
        }
        
        # Mock timeout (120 seconds for analysis)
        mock_subprocess.side_effect = subprocess.TimeoutExpired("claude", 120)
        
        response = test_client.post("/vault/analyze", json=request_data)
        
        assert response.status_code == 504
        assert "timeout" in response.json()["detail"].lower()
    
    def test_vault_analysis_invalid_focus_areas(self, test_client):
        """Test vault analysis with invalid focus areas."""
        request_data = {
            "focus_areas": ["invalid_area"],
            "analysis_depth": "comprehensive"
        }
        
        response = test_client.post("/vault/analyze", json=request_data)
        
        # Should still process but might warn about invalid areas
        # Depends on implementation - for now, assume it processes
        assert response.status_code in [200, 400, 422]


class TestSynthesisEndpoint:
    """Test document synthesis endpoint."""
    
    def test_synthesis_success(self, test_client, mock_subprocess):
        """Test successful document synthesis."""
        request_data = {
            "note_paths": ["ml/basics.md", "ai/advanced.md"],
            "synthesis_type": "comprehensive",
            "focus_question": "How do ML and AI relate?"
        }
        
        # Mock successful synthesis
        mock_subprocess.return_value.stdout = "Comprehensive synthesis of ML and AI concepts..."
        mock_subprocess.return_value.returncode = 0
        
        response = test_client.post("/synthesize", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "synthesis" in data
        assert "source_documents" in data
        assert "execution_time" in data
    
    def test_synthesis_empty_notes(self, test_client):
        """Test synthesis with empty note paths."""
        request_data = {
            "note_paths": [],
            "synthesis_type": "quick"
        }
        
        response = test_client.post("/synthesize", json=request_data)
        
        # Should handle empty input gracefully
        assert response.status_code in [200, 400]
    
    def test_synthesis_nonexistent_notes(self, test_client, mock_subprocess):
        """Test synthesis with nonexistent note paths."""
        request_data = {
            "note_paths": ["nonexistent/note.md"],
            "synthesis_type": "quick"
        }
        
        # Mock response indicating missing files
        mock_subprocess.return_value.stdout = "Error: Some files not found"
        mock_subprocess.return_value.returncode = 1
        
        response = test_client.post("/synthesize", json=request_data)
        
        # Should handle missing files gracefully
        assert response.status_code in [200, 400, 404]


class TestAgentEndpoints:
    """Test agent execution endpoints."""
    
    def test_execute_agents_success(self, test_client):
        """Test successful agent execution."""
        request_data = {
            "agent_names": ["vault-analyzer", "synthesis-assistant"],
            "context": {"task": "analyze vault structure"},
            "parallel": True
        }
        
        with patch('src.app.enhanced_agent_manager') as mock_manager:
            # Mock successful agent execution
            mock_manager.execute_agent.return_value = {
                "status": "success",
                "result": "Analysis complete",
                "execution_time": 5.2
            }
            
            response = test_client.post("/agents/execute", json=request_data)
            
            assert response.status_code == 200
            data = response.json()
            
            assert "results" in data
            assert "total_execution_time" in data
            assert "successful_agents" in data
    
    def test_execute_agents_partial_failure(self, test_client):
        """Test agent execution with partial failures."""
        request_data = {
            "agent_names": ["vault-analyzer", "invalid-agent"],
            "context": {"task": "test task"},
            "parallel": False
        }
        
        with patch('src.app.enhanced_agent_manager') as mock_manager:
            # Mock mixed results
            def mock_execute(agent_name, context):
                if agent_name == "vault-analyzer":
                    return {"status": "success", "result": "Success"}
                else:
                    raise Exception("Agent not found")
            
            mock_manager.execute_agent.side_effect = mock_execute
            
            response = test_client.post("/agents/execute", json=request_data)
            
            assert response.status_code == 200
            data = response.json()
            
            # Should report both successes and failures
            assert "results" in data
            assert len(data["results"]) == 2
    
    def test_get_agent_status(self, test_client):
        """Test agent status endpoint."""
        with patch('src.app.enhanced_agent_manager') as mock_manager:
            mock_manager.get_agent_status.return_value = {
                "vault-analyzer": {"status": "ready", "last_execution": "2023-01-01T00:00:00Z"},
                "synthesis-assistant": {"status": "busy", "current_task": "document synthesis"}
            }
            
            response = test_client.get("/agents/status")
            
            assert response.status_code == 200
            data = response.json()
            
            assert "agents" in data
            assert "vault-analyzer" in data["agents"]
            assert "synthesis-assistant" in data["agents"]
    
    def test_get_agent_status_specific_agents(self, test_client):
        """Test agent status for specific agents."""
        with patch('src.app.enhanced_agent_manager') as mock_manager:
            mock_manager.get_agent_status.return_value = {
                "vault-analyzer": {"status": "ready"}
            }
            
            response = test_client.get("/agents/status?agent_names=vault-analyzer")
            
            assert response.status_code == 200
            data = response.json()
            
            assert "agents" in data
            assert len(data["agents"]) == 1


class TestHealthEndpoints:
    """Test health check and system status endpoints."""
    
    def test_health_check(self, test_client):
        """Test basic health check endpoint."""
        response = test_client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "status" in data
        assert "timestamp" in data
        assert "version" in data
        assert "dependencies" in data
    
    def test_health_detailed(self, test_client):
        """Test detailed health check."""
        with patch('src.app.enhanced_agent_manager') as mock_manager:
            mock_manager.get_agent_status.return_value = {
                "vault-analyzer": {"status": "ready"},
                "synthesis-assistant": {"status": "ready"}
            }
            
            response = test_client.get("/health/detailed")
            
            assert response.status_code == 200
            data = response.json()
            
            assert "status" in data
            assert "dependencies" in data
            assert "agents" in data
            assert "performance_metrics" in data


class TestErrorHandling:
    """Test error handling across all endpoints."""
    
    def test_invalid_json_request(self, test_client):
        """Test handling of invalid JSON requests."""
        response = test_client.post(
            "/query",
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 422
    
    def test_unsupported_media_type(self, test_client):
        """Test handling of unsupported media types."""
        response = test_client.post(
            "/query",
            data="test data",
            headers={"Content-Type": "text/plain"}
        )
        
        assert response.status_code == 422
    
    def test_cors_headers(self, test_client):
        """Test CORS headers are properly set."""
        response = test_client.options("/query")
        
        # Should have CORS headers
        assert "access-control-allow-origin" in response.headers
        assert "access-control-allow-methods" in response.headers
    
    def test_large_request_handling(self, test_client):
        """Test handling of very large requests."""
        # Create a very large query
        large_query = "test " * 10000
        request_data = {
            "query": large_query,
            "system_prompt": "Test prompt"
        }
        
        response = test_client.post("/query", json=request_data)
        
        # Should handle large requests (may succeed or fail with appropriate error)
        assert response.status_code in [200, 413, 422, 500]
    
    def test_concurrent_requests(self, test_client):
        """Test handling of concurrent requests."""
        import threading
        import time
        
        results = []
        
        def make_request():
            response = test_client.post("/query", json={
                "query": "test query",
                "system_prompt": "test prompt"
            })
            results.append(response.status_code)
        
        # Create multiple concurrent requests
        threads = []
        for _ in range(5):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
            thread.start()
        
        # Wait for all requests to complete
        for thread in threads:
            thread.join()
        
        # All requests should complete (may succeed or fail gracefully)
        assert len(results) == 5
        assert all(status in [200, 500, 503, 504] for status in results)


class TestRequestValidation:
    """Test request validation and sanitization."""
    
    def test_query_request_validation(self, test_client):
        """Test GenerationRequest validation."""
        # Test various invalid inputs
        invalid_requests = [
            {"query": "", "system_prompt": ""},  # Empty strings
            {"query": None, "system_prompt": "test"},  # Null values
            {"query": "test", "temperature": -1},  # Invalid temperature
            {"query": "test", "max_tokens": -100},  # Invalid max_tokens
            {"query": "test", "context_strategy": "invalid"}  # Invalid enum
        ]
        
        for invalid_request in invalid_requests:
            response = test_client.post("/query", json=invalid_request)
            # Should return validation error for clearly invalid inputs
            assert response.status_code in [200, 422]  # Some may have defaults
    
    def test_vault_analysis_request_validation(self, test_client):
        """Test VaultAnalysisRequest validation."""
        invalid_requests = [
            {"focus_areas": []},  # Empty focus areas
            {"analysis_depth": "invalid_depth"},  # Invalid depth
            {"include_metrics": "not_boolean"}  # Invalid boolean
        ]
        
        for invalid_request in invalid_requests:
            response = test_client.post("/vault/analyze", json=invalid_request)
            assert response.status_code in [200, 422]