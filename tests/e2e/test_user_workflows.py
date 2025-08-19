"""
End-to-end tests for complete user workflows.
Tests realistic user scenarios from start to finish.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch

from src.app import app


@pytest.mark.e2e
class TestUserWorkflows:
    """Test complete user workflows and scenarios."""

    def test_new_user_onboarding_workflow(self, test_client, mock_vault_dict):
        """Test the workflow for a new user setting up the system."""
        # 1. Check health endpoint
        health_response = test_client.get("/health")
        assert health_response.status_code == 200
        
        # 2. First query with empty context
        first_query = {
            "query": "Hello, I'm new to this system",
            "context_strategy": "smart_chunks",
            "max_tokens": 500
        }
        
        with patch('src.app.vault', {}):  # Empty vault for new user
            response = test_client.post("/query", json=first_query)
        
        assert response.status_code == 200
        data = response.json()
        assert "response" in data
        assert len(data["retrieved_docs"]) == 0  # No docs for empty vault

    def test_content_creation_workflow(self, test_client, mock_vault_dict):
        """Test workflow for creating content with AI assistance."""
        # 1. Initial query for topic exploration
        exploration_query = {
            "query": "I want to learn about machine learning. What should I focus on?",
            "context_strategy": "smart_chunks",
            "max_tokens": 800
        }
        
        with patch('src.app.vault', mock_vault_dict):
            response = test_client.post("/query", json=exploration_query)
        
        assert response.status_code == 200
        exploration_data = response.json()
        assert len(exploration_data["response"]) > 100
        assert len(exploration_data["retrieved_docs"]) > 0

        # 2. Follow-up query for specific details
        detail_query = {
            "query": "Can you explain neural networks in more detail?",
            "context_strategy": "hierarchical",
            "max_tokens": 1000
        }
        
        with patch('src.app.vault', mock_vault_dict):
            response = test_client.post("/query", json=detail_query)
        
        assert response.status_code == 200
        detail_data = response.json()
        assert len(detail_data["response"]) > 200

        # 3. Request for practical examples
        example_query = {
            "query": "Show me some practical examples of neural network applications",
            "context_strategy": "full_docs",
            "max_tokens": 1200
        }
        
        with patch('src.app.vault', mock_vault_dict):
            response = test_client.post("/query", json=example_query)
        
        assert response.status_code == 200
        example_data = response.json()
        assert "example" in example_data["response"].lower()

    def test_research_workflow(self, test_client, comprehensive_vault_dict):
        """Test workflow for research and analysis tasks."""
        # 1. Vault analysis to understand current knowledge
        analysis_request = {
            "focus_areas": ["patterns", "gaps", "connections"],
            "analysis_depth": "comprehensive",
            "include_metrics": True
        }
        
        with patch('src.app.vault', comprehensive_vault_dict):
            response = test_client.post("/vault-analysis", json=analysis_request)
        
        assert response.status_code == 200
        analysis_data = response.json()
        assert len(analysis_data["patterns"]) > 0
        assert len(analysis_data["connections"]) > 0

        # 2. Query based on identified gaps
        gap_query = {
            "query": "Based on my knowledge gaps, what should I research next?",
            "context_strategy": "smart_chunks",
            "max_tokens": 600
        }
        
        with patch('src.app.vault', comprehensive_vault_dict):
            response = test_client.post("/query", json=gap_query)
        
        assert response.status_code == 200
        gap_data = response.json()
        assert "research" in gap_data["response"].lower()

        # 3. Synthesis of existing knowledge
        synthesis_request = {
            "notes": ["ml/basics.md", "programming/clean-code.md"],
            "synthesis_type": "connections",
            "max_tokens": 800
        }
        
        with patch('src.app.vault', comprehensive_vault_dict):
            response = test_client.post("/synthesize-notes", json=synthesis_request)
        
        assert response.status_code == 200
        synthesis_data = response.json()
        assert "synthesis" in synthesis_data or "connection" in synthesis_data

    def test_weekly_reflection_workflow(self, test_client, comprehensive_vault_dict):
        """Test workflow for weekly reflection and review."""
        # 1. Generate weekly reflection
        with patch('src.app.vault', comprehensive_vault_dict):
            response = test_client.post("/reflect-week")
        
        assert response.status_code == 200
        reflection_data = response.json()
        assert "reflection" in reflection_data or "week" in reflection_data

        # 2. Follow-up questions based on reflection
        followup_query = {
            "query": "What are the key themes from this week's work?",
            "context_strategy": "hierarchical",
            "max_tokens": 500
        }
        
        with patch('src.app.vault', comprehensive_vault_dict):
            response = test_client.post("/query", json=followup_query)
        
        assert response.status_code == 200
        followup_data = response.json()
        assert len(followup_data["response"]) > 50

    @pytest.mark.slow
    def test_collaborative_workflow(self, test_client, mock_vault_dict):
        """Test workflow simulating multiple users or sessions."""
        session_queries = [
            "What are the fundamentals of machine learning?",
            "How do neural networks work?",
            "What are some practical applications?",
            "How can I implement a simple neural network?",
            "What are common pitfalls to avoid?"
        ]

        responses = []
        for i, query_text in enumerate(session_queries):
            query = {
                "query": query_text,
                "context_strategy": "smart_chunks",
                "max_tokens": 400,
                "session_id": f"session_{i}"  # Simulate different sessions
            }
            
            with patch('src.app.vault', mock_vault_dict):
                response = test_client.post("/query", json=query)
            
            assert response.status_code == 200
            responses.append(response.json())

        # Verify all queries were processed successfully
        assert len(responses) == len(session_queries)
        for response_data in responses:
            assert len(response_data["response"]) > 20
            assert "processing_time" in response_data

    def test_error_recovery_workflow(self, test_client, mock_vault_dict):
        """Test how the system handles and recovers from errors."""
        # 1. Send malformed request
        malformed_request = {
            "query": "",  # Empty query
            "invalid_field": "should_be_ignored"
        }
        
        response = test_client.post("/query", json=malformed_request)
        assert response.status_code == 422

        # 2. Recover with valid request
        valid_request = {
            "query": "This is a valid query after error",
            "context_strategy": "smart_chunks",
            "max_tokens": 300
        }
        
        with patch('src.app.vault', mock_vault_dict):
            response = test_client.post("/query", json=valid_request)
        
        assert response.status_code == 200
        recovery_data = response.json()
        assert len(recovery_data["response"]) > 10

        # 3. Test with edge case inputs
        edge_cases = [
            {"query": "a", "max_tokens": 1},  # Minimal query
            {"query": "x" * 1000, "max_tokens": 2000},  # Very long query
            {"query": "🚀🎯💡", "max_tokens": 100}  # Unicode characters
        ]

        for edge_case in edge_cases:
            edge_case["context_strategy"] = "smart_chunks"
            
            with patch('src.app.vault', mock_vault_dict):
                response = test_client.post("/query", json=edge_case)
            
            # Should handle gracefully (either succeed or fail predictably)
            assert response.status_code in [200, 422]

    @pytest.mark.requires_agents
    def test_agent_workflow(self, test_client, mock_agent_config, comprehensive_vault_dict):
        """Test workflows involving Agent OS functionality."""
        # 1. Check agent status
        with patch('src.app.agent_config', mock_agent_config):
            response = test_client.get("/agents/status")
        
        assert response.status_code == 200
        status_data = response.json()
        assert "agents" in status_data

        # 2. Execute agent-based task
        agent_request = {
            "agent_type": "vault-analyzer",
            "task": "analyze_patterns",
            "parameters": {"depth": "comprehensive"}
        }
        
        with patch('src.app.vault', comprehensive_vault_dict), \
             patch('src.app.agent_config', mock_agent_config):
            response = test_client.post("/agents/execute", json=agent_request)
        
        assert response.status_code == 200
        agent_data = response.json()
        assert "result" in agent_data or "analysis" in agent_data

        # 3. Query with agent assistance
        agent_query = {
            "query": "Use agents to provide a comprehensive analysis",
            "context_strategy": "smart_chunks",
            "use_agents": True,
            "max_tokens": 1000
        }
        
        with patch('src.app.vault', comprehensive_vault_dict), \
             patch('src.app.agent_config', mock_agent_config):
            response = test_client.post("/query", json=agent_query)
        
        assert response.status_code == 200
        query_data = response.json()
        assert len(query_data["response"]) > 100