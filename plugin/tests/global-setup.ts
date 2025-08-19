/**
 * Global Jest setup for Obsidian Copilot plugin testing.
 * Configures test environment, starts mock servers, and initializes shared resources.
 */

import { setupServer } from 'msw/node';
import { http, HttpResponse } from 'msw';

// Mock Service Worker handlers for API testing
const handlers = [
  // Claude API mock
  http.post('https://api.anthropic.com/v1/messages', () => {
    return HttpResponse.json({
      id: 'msg_test_123',
      type: 'message',
      role: 'assistant',
      content: [
        {
          type: 'text',
          text: 'This is a mocked Claude response for testing.'
        }
      ],
      model: 'claude-3-5-sonnet-20241022',
      stop_reason: 'end_turn',
      stop_sequence: null,
      usage: {
        input_tokens: 10,
        output_tokens: 25
      }
    });
  }),

  // OpenAI API mock
  http.post('https://api.openai.com/v1/chat/completions', () => {
    return HttpResponse.json({
      id: 'chatcmpl-test123',
      object: 'chat.completion',
      created: Date.now(),
      model: 'gpt-4-turbo-preview',
      choices: [
        {
          index: 0,
          message: {
            role: 'assistant',
            content: 'This is a mocked OpenAI response for testing.'
          },
          finish_reason: 'stop'
        }
      ],
      usage: {
        prompt_tokens: 10,
        completion_tokens: 25,
        total_tokens: 35
      }
    });
  }),

  // Backend API health check mock
  http.get('http://localhost:8000/health', () => {
    return HttpResponse.json({
        status: 'healthy',
        timestamp: new Date().toISOString(),
        version: '1.0.0'
      });
  }),

  // Backend query endpoint mock
  http.post('http://localhost:8000/query', () => {
    return HttpResponse.json({
        response: 'This is a mocked backend response for testing.',
        retrieved_docs: [
          {
            title: 'Test Document 1',
            content: 'Test content for retrieval testing.',
            score: 0.95,
            path: 'test/doc1.md'
          }
        ],
        processing_time: 0.123,
        model_used: 'claude-3-5-sonnet-20241022'
      });
  }),

  // Error simulation endpoints
  http.get('http://localhost:8000/error/500', () => {
    return new HttpResponse(
      JSON.stringify({ error: 'Internal server error for testing' }),
      { status: 500, headers: { 'Content-Type': 'application/json' } }
    );
  }),

  http.get('http://localhost:8000/error/timeout', async () => {
    // Simulate timeout with delay
    await new Promise(resolve => setTimeout(resolve, 1000));
    return HttpResponse.json({ message: 'This should timeout' });
  })
];

// Create MSW server instance
export const server = setupServer(...handlers);

// Global setup function
export default async function globalSetup() {
  console.log('🚀 Starting global test setup...');

  // Start MSW server
  server.listen({
    onUnhandledRequest: 'warn' // Warn about unhandled requests during development
  });

  // Set up global test environment variables
  process.env.NODE_ENV = 'test';
  process.env.TEST_TIMEOUT = '15000';
  
  // Mock localStorage for browser environment simulation
  const localStorageMock = {
    getItem: () => null,
    setItem: () => {},
    removeItem: () => {},
    clear: () => {},
    length: 0,
    key: () => null
  };
  
  // @ts-ignore
  global.localStorage = localStorageMock;
  
  // Mock sessionStorage
  // @ts-ignore
  global.sessionStorage = localStorageMock;

  // Set up global performance mocks for testing
  const performanceMock = {
    now: () => Date.now(),
    mark: () => {},
    measure: () => {},
    getEntriesByName: () => [],
    getEntriesByType: () => [],
    clearMarks: () => {},
    clearMeasures: () => {}
  };
  
  // @ts-ignore
  global.performance = performanceMock;

  // Mock ResizeObserver for DOM testing
  const ResizeObserverMock = function() {
    return {
      observe: () => {},
      unobserve: () => {},
      disconnect: () => {}
    };
  };
  
  // @ts-ignore
  global.ResizeObserver = ResizeObserverMock;

  // Mock IntersectionObserver for DOM testing
  const IntersectionObserverMock = function() {
    return {
      observe: () => {},
      unobserve: () => {},
      disconnect: () => {}
    };
  };
  
  // @ts-ignore
  global.IntersectionObserver = IntersectionObserverMock;

  // Mock crypto for security-related testing
  const cryptoMock = {
    getRandomValues: (arr) => {
      for (let i = 0; i < arr.length; i++) {
        arr[i] = Math.floor(Math.random() * 256);
      }
      return arr;
    },
    randomUUID: () => '12345678-1234-1234-1234-123456789012'
  };
  
  // Use Object.defineProperty for crypto mock since it's read-only
  Object.defineProperty(global, 'crypto', {
    value: cryptoMock,
    writable: true,
    configurable: true
  });

  // Set up test database/cache if needed
  console.log('✅ Global test setup completed');
}