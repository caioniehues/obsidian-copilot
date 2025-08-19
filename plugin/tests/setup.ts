/**
 * Enhanced Jest setup file for Obsidian Copilot plugin testing.
 * Configures test environment, global mocks, and advanced testing utilities.
 */

import '@testing-library/jest-dom';
import { server } from './global-setup';
import TestDataFactory from './fixtures/test-data-factory';

// Start MSW server for HTTP mocking
beforeAll(() => {
  server.listen({ onUnhandledRequest: 'error' });
});

afterAll(() => {
  server.close();
});

afterEach(() => {
  server.resetHandlers();
});

// Enhanced global fetch mock with request tracking
const fetchCalls: Array<{ url: string; options?: any; timestamp: number }> = [];
global.fetch = jest.fn().mockImplementation((url: string, options?: any) => {
  fetchCalls.push({ url, options, timestamp: Date.now() });
  return Promise.resolve({
    ok: true,
    status: 200,
    json: () => Promise.resolve({ mock: true }),
    text: () => Promise.resolve('mock response'),
    headers: new Headers(),
    statusText: 'OK'
  });
});

// Mock console methods with categorization
const originalConsole = { ...console };
const consoleLogs: Array<{ level: string; args: any[]; timestamp: number }> = [];

beforeEach(() => {
  // Reset all mocks and tracking arrays
  jest.clearAllMocks();
  fetchCalls.length = 0;
  consoleLogs.length = 0;
  
  // Enhanced console mocking with tracking
  ['log', 'info', 'debug', 'warn', 'error'].forEach(level => {
    (console as any)[level] = jest.fn((...args: any[]) => {
      consoleLogs.push({ level, args, timestamp: Date.now() });
      // Still call original for errors and warnings to aid debugging
      if (level === 'error' || level === 'warn') {
        (originalConsole as any)[level](...args);
      }
    });
  });
});

afterEach(() => {
  // Restore console after each test
  Object.assign(console, originalConsole);
});

// Advanced global test utilities
declare global {
  namespace jest {
    interface Matchers<R> {
      toBeValidApiResponse(): R;
      toHaveValidSettings(): R;
      toHaveBeenCalledWithApiKey(): R;
      toBeWithinPerformanceThreshold(maxMs: number): R;
      toHaveValidMarkdownStructure(): R;
      toMatchVaultDocument(): R;
      toBeStreamingResponse(): R;
    }
  }
  
  // Global test utilities available in all tests
  var testUtils: {
    getConsoleLogs: (level?: string) => any[];
    getFetchCalls: (urlPattern?: string) => any[];
    clearTestData: () => void;
    createTestVault: () => any;
    simulateUserTyping: (element: Element, text: string) => Promise<void>;
    waitForAsyncOperations: () => Promise<void>;
    measurePerformance: <T>(fn: () => T | Promise<T>) => Promise<{ result: T; duration: number }>;
  };
}

// Enhanced custom Jest matchers
expect.extend({
  toBeValidApiResponse(received) {
    const isValid = received && 
                   typeof received === 'object' && 
                   ('status' in received || 'ok' in received || 'data' in received);
    
    return {
      message: () => isValid 
        ? `expected ${JSON.stringify(received)} not to be a valid API response`
        : `expected ${JSON.stringify(received)} to be a valid API response with status, ok, or data field`,
      pass: isValid,
    };
  },
  
  toHaveValidSettings(received) {
    const requiredFields = ['mode', 'apiProvider', 'backendUrl'];
    const missingFields = requiredFields.filter(field => !(field in received));
    
    return {
      message: () => missingFields.length === 0
        ? `expected ${JSON.stringify(received)} not to have valid settings`
        : `expected ${JSON.stringify(received)} to have valid settings. Missing fields: ${missingFields.join(', ')}`,
      pass: missingFields.length === 0,
    };
  },

  toHaveBeenCalledWithApiKey(received) {
    const calls = received.mock.calls;
    const hasApiKey = calls.some((call: any[]) => {
      const options = call[1];
      return options && 
             options.headers && 
             (options.headers['x-api-key'] || 
              options.headers['Authorization'] || 
              options.headers['anthropic-version']);
    });

    return {
      message: () => hasApiKey
        ? `expected fetch not to be called with API key`
        : `expected fetch to be called with API key in headers`,
      pass: hasApiKey,
    };
  },

  toBeWithinPerformanceThreshold(received, maxMs) {
    const duration = typeof received === 'number' ? received : received.duration;
    const withinThreshold = duration <= maxMs;

    return {
      message: () => withinThreshold
        ? `expected ${duration}ms to exceed performance threshold of ${maxMs}ms`
        : `expected ${duration}ms to be within performance threshold of ${maxMs}ms`,
      pass: withinThreshold,
    };
  },

  toHaveValidMarkdownStructure(received) {
    if (typeof received !== 'string') {
      return {
        message: () => `expected string, received ${typeof received}`,
        pass: false,
      };
    }

    const hasTitle = /^#\s+.+$/m.test(received);
    const hasContent = received.trim().length > 10;
    const validStructure = hasTitle && hasContent;

    return {
      message: () => validStructure
        ? `expected markdown not to have valid structure`
        : `expected markdown to have valid structure (title and content)`,
      pass: validStructure,
    };
  },

  toMatchVaultDocument(received) {
    const requiredProps = ['path', 'title', 'content'];
    const hasProps = requiredProps.every(prop => prop in received);
    const hasValidPath = typeof received.path === 'string' && received.path.endsWith('.md');

    return {
      message: () => hasProps && hasValidPath
        ? `expected object not to match vault document structure`
        : `expected object to match vault document structure with ${requiredProps.join(', ')} and valid .md path`,
      pass: hasProps && hasValidPath,
    };
  },

  toBeStreamingResponse(received) {
    const isAsync = received && typeof received[Symbol.asyncIterator] === 'function';

    return {
      message: () => isAsync
        ? `expected object not to be a streaming response`
        : `expected object to be a streaming response (async iterable)`,
      pass: isAsync,
    };
  }
});

// Global test utilities
global.testUtils = {
  getConsoleLogs: (level?: string) => {
    return level 
      ? consoleLogs.filter(log => log.level === level)
      : consoleLogs;
  },

  getFetchCalls: (urlPattern?: string) => {
    return urlPattern
      ? fetchCalls.filter(call => call.url.includes(urlPattern))
      : fetchCalls;
  },

  clearTestData: () => {
    fetchCalls.length = 0;
    consoleLogs.length = 0;
    jest.clearAllMocks();
  },

  createTestVault: () => {
    const files = TestDataFactory.createVaultStructure();
    const vault = new Map();
    files.forEach(file => vault.set(file.path, file));
    return vault;
  },

  simulateUserTyping: async (element: Element, text: string) => {
    for (const char of text) {
      const event = new KeyboardEvent('keydown', { key: char });
      element.dispatchEvent(event);
      await new Promise(resolve => setTimeout(resolve, 10));
    }
  },

  waitForAsyncOperations: async () => {
    await new Promise(resolve => setImmediate(resolve));
    await jest.runAllTimersAsync();
  },

  measurePerformance: async <T>(fn: () => T | Promise<T>) => {
    const start = performance.now();
    const result = await fn();
    const duration = performance.now() - start;
    return { result, duration };
  }
};

// Configure fake timers for consistent testing
jest.useFakeTimers({
  advanceTimers: true,
  doNotFake: ['performance', 'hrtime']
});

// Enhanced global test timeout
jest.setTimeout(15000);

// Performance monitoring setup
const originalSetTimeout = global.setTimeout;
global.setTimeout = jest.fn().mockImplementation((callback, delay) => {
  // Track long timeouts that might indicate performance issues
  if (delay && delay > 5000) {
    console.warn(`Long timeout detected: ${delay}ms`);
  }
  return originalSetTimeout(callback, delay);
});

// Memory leak detection in tests
let initialMemoryUsage: NodeJS.MemoryUsage;

beforeEach(() => {
  if (global.gc) {
    global.gc();
  }
  initialMemoryUsage = process.memoryUsage();
});

afterEach(() => {
  if (global.gc) {
    global.gc();
  }
  
  const currentMemoryUsage = process.memoryUsage();
  const memoryIncrease = currentMemoryUsage.heapUsed - initialMemoryUsage.heapUsed;
  
  // Warn about potential memory leaks in individual tests
  if (memoryIncrease > 50 * 1024 * 1024) { // 50MB threshold
    console.warn(`Potential memory leak detected: ${Math.round(memoryIncrease / 1024 / 1024)}MB increase`);
  }
});

// Export commonly used test utilities
export { TestDataFactory };
export { server } from './global-setup';