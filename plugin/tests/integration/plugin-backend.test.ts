/**
 * Integration tests for plugin-backend communication.
 * Tests end-to-end functionality between plugin and backend service.
 */

import { MockApp, Plugin } from '../mocks/obsidian';
import MockBackendClient from '../mocks/api/backend-client';
import TestDataFactory from '../fixtures/test-data-factory';

describe('Plugin-Backend Integration', () => {
  let app: MockApp;
  let plugin: Plugin;
  let backendClient: MockBackendClient;

  beforeEach(() => {
    app = new MockApp();
    plugin = new Plugin(app, { id: 'copilot', name: 'Copilot' });
    backendClient = new MockBackendClient();
  });

  describe('Backend Availability Detection', () => {
    test('should detect available backend service', async () => {
      backendClient.setAvailability(true);
      
      const healthResponse = await backendClient.checkHealth();
      
      expect(healthResponse.status).toBe('healthy');
      expect(healthResponse.services.opensearch).toBe(true);
      expect(healthResponse.services.redis).toBe(true);
      expect(healthResponse.services.agents).toBe(true);
    });

    test('should handle unavailable backend gracefully', async () => {
      backendClient.setAvailability(false);
      
      await expect(backendClient.checkHealth()).rejects.toThrow('Backend service unavailable');
    });
  });

  describe('Query Processing', () => {
    test('should process queries through backend', async () => {
      const queryRequest = {
        query: 'Explain machine learning concepts',
        context_strategy: 'smart_chunks' as const,
        temperature: 0.7,
        max_tokens: 1000
      };

      const response = await backendClient.query(queryRequest);

      expect(response.response).toBeTruthy();
      expect(response.retrieved_docs).toHaveLength(2);
      expect(response.mode).toBe('backend');
      expect(response.processing_time).toBeGreaterThan(0);
    });

    test('should handle vault analysis requests', async () => {
      const analysisRequest = {
        focus_areas: ['patterns', 'gaps', 'connections'],
        analysis_depth: 'comprehensive' as const,
        include_metrics: true
      };

      const response = await backendClient.analyzeVault(analysisRequest);

      expect(response.patterns).toHaveLength(2);
      expect(response.gaps).toHaveLength(1);
      expect(response.connections).toHaveLength(2);
      expect(response.metrics.total_docs).toBeGreaterThan(0);
    });
  });

  describe('Performance and Reliability', () => {
    test('should handle high latency gracefully', async () => {
      backendClient.setLatency(1000); // 1 second delay
      
      const startTime = Date.now();
      await backendClient.checkHealth();
      const endTime = Date.now();
      
      expect(endTime - startTime).toBeGreaterThan(950);
    });

    test('should maintain functionality under load', async () => {
      const promises = Array.from({ length: 10 }, (_, i) => 
        backendClient.query({
          query: `Test query ${i}`,
          context_strategy: 'smart_chunks'
        })
      );

      const results = await Promise.all(promises);
      
      expect(results).toHaveLength(10);
      results.forEach(result => {
        expect(result.response).toBeTruthy();
        expect(result.mode).toBe('backend');
      });
    });
  });
});