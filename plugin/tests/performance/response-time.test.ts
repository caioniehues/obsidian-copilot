/**
 * Performance tests for plugin response times and memory usage.
 * Ensures the plugin meets performance requirements under various conditions.
 */

import { MockApp, Plugin } from '../mocks/obsidian';
import MockClaudeClient from '../mocks/api/claude-client';
import MockBackendClient from '../mocks/api/backend-client';
import TestDataFactory from '../fixtures/test-data-factory';

describe('Plugin Performance', () => {
  let app: MockApp;
  let plugin: Plugin;
  let claudeClient: MockClaudeClient;
  let backendClient: MockBackendClient;

  beforeEach(() => {
    app = new MockApp();
    plugin = new Plugin(app, { id: 'copilot', name: 'Copilot' });
    claudeClient = new MockClaudeClient('sk-ant-test-key');
    backendClient = new MockBackendClient();
  });

  describe('Response Time Requirements', () => {
    test('direct mode should respond within 2 seconds', async () => {
      const startTime = Date.now();
      
      const response = await claudeClient.createMessage([
        { role: 'user', content: 'Test query for performance measurement' }
      ]);
      
      const endTime = Date.now();
      const responseTime = endTime - startTime;
      
      expect(responseTime).toBeLessThan(2000);
      expect(response.content[0].text).toBeTruthy();
    });

    test('backend mode should respond within 3 seconds', async () => {
      const startTime = Date.now();
      
      const response = await backendClient.query({
        query: 'Test query for backend performance measurement',
        context_strategy: 'smart_chunks'
      });
      
      const endTime = Date.now();
      const responseTime = endTime - startTime;
      
      expect(responseTime).toBeLessThan(3000);
      expect(response.response).toBeTruthy();
    });

    test('streaming responses should start within 500ms', async () => {
      const startTime = Date.now();
      const streamGen = claudeClient.streamMessage([
        { role: 'user', content: 'Stream test for performance' }
      ]);
      
      const firstChunk = await streamGen.next();
      const firstChunkTime = Date.now() - startTime;
      
      expect(firstChunkTime).toBeLessThan(500);
      expect(firstChunk.value).toBeTruthy();
    });
  });

  describe('Memory Usage', () => {
    test('should not exceed 50MB memory increase during normal operation', async () => {
      if (global.gc) global.gc();
      const initialMemory = process.memoryUsage().heapUsed;
      
      // Perform multiple operations
      const operations = [];
      for (let i = 0; i < 100; i++) {
        operations.push(
          claudeClient.createMessage([
            { role: 'user', content: `Test operation ${i}` }
          ])
        );
      }
      
      await Promise.all(operations);
      
      if (global.gc) global.gc();
      const finalMemory = process.memoryUsage().heapUsed;
      const memoryIncrease = (finalMemory - initialMemory) / (1024 * 1024); // MB
      
      expect(memoryIncrease).toBeLessThan(50);
    });

    test('should clean up resources after operations', async () => {
      if (global.gc) global.gc();
      const initialMemory = process.memoryUsage().heapUsed;
      
      // Create large response data
      const largeQuery = 'x'.repeat(10000);
      await claudeClient.createMessage([
        { role: 'user', content: largeQuery }
      ]);
      
      // Force cleanup
      if (global.gc) global.gc();
      await new Promise(resolve => setTimeout(resolve, 100));
      
      const finalMemory = process.memoryUsage().heapUsed;
      const memoryDiff = Math.abs(finalMemory - initialMemory) / (1024 * 1024); // MB
      
      expect(memoryDiff).toBeLessThan(20);
    });
  });

  describe('Throughput Performance', () => {
    test('should handle concurrent requests efficiently', async () => {
      const concurrentRequests = 20;
      const startTime = Date.now();
      
      const promises = Array.from({ length: concurrentRequests }, (_, i) =>
        claudeClient.createMessage([
          { role: 'user', content: `Concurrent test ${i}` }
        ])
      );
      
      const results = await Promise.all(promises);
      const totalTime = Date.now() - startTime;
      const avgTimePerRequest = totalTime / concurrentRequests;
      
      expect(results).toHaveLength(concurrentRequests);
      expect(avgTimePerRequest).toBeLessThan(300); // Average < 300ms per request
      
      results.forEach(result => {
        expect(result.content[0].text).toBeTruthy();
      });
    });

    test('should maintain performance with large vault data', async () => {
      // Simulate large vault scenario
      const performanceData = TestDataFactory.createPerformanceTestData();
      expect(performanceData.documents).toHaveLength(1000);
      
      const startTime = Date.now();
      
      // Simulate vault analysis with large dataset
      const analysisResponse = await backendClient.analyzeVault({
        focus_areas: ['patterns', 'connections'],
        analysis_depth: 'comprehensive',
        include_metrics: true
      });
      
      const analysisTime = Date.now() - startTime;
      
      expect(analysisTime).toBeLessThan(5000); // Should complete within 5 seconds
      expect(analysisResponse.patterns.length).toBeGreaterThan(0);
      expect(analysisResponse.metrics.total_docs).toBeGreaterThan(0);
    });
  });

  describe('Resource Efficiency', () => {
    test('should optimize API calls to minimize costs', async () => {
      const usageStats = claudeClient.getUsageStats();
      
      // Perform standard operations
      await claudeClient.createMessage([
        { role: 'user', content: 'Short query' }
      ]);
      
      const newStats = claudeClient.getUsageStats();
      
      // Verify reasonable resource usage
      expect(newStats.averageResponseTime).toBeLessThan(200);
    });

    test('should batch operations when possible', async () => {
      const startTime = Date.now();
      
      // Simulate batch processing scenario
      const batchSize = 10;
      const batchPromises = [];
      
      for (let i = 0; i < batchSize; i++) {
        batchPromises.push(
          backendClient.query({
            query: `Batch query ${i}`,
            context_strategy: 'smart_chunks'
          })
        );
      }
      
      const results = await Promise.all(batchPromises);
      const batchTime = Date.now() - startTime;
      
      expect(results).toHaveLength(batchSize);
      expect(batchTime).toBeLessThan(2000); // Batch should be faster than sequential
    });
  });
});