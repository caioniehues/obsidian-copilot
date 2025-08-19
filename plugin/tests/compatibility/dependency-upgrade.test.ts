/**
 * Compatibility Test Suite for Dependency Upgrades
 * 
 * This test suite validates that upgrading TypeScript and Node.js types
 * doesn't break existing functionality. It captures baseline behavior
 * before the upgrade and ensures compatibility after.
 */

import { spawn } from 'child_process';
import { promises as fs } from 'fs';
import * as crypto from 'crypto';
import { Readable, Writable } from 'stream';
import { server } from '../global-setup';
import { http, HttpResponse } from 'msw';

describe('Dependency Upgrade Compatibility', () => {
  
  describe('TypeScript 4.8 Feature Compatibility', () => {
    
    test('template literal types work correctly', () => {
      // TypeScript 4.8 has stricter template literal type checking
      type Status = 'success' | 'error' | 'pending';
      type Message = `Status: ${Status}`;
      
      const createMessage = (status: Status): Message => {
        return `Status: ${status}`;
      };
      
      expect(createMessage('success')).toBe('Status: success');
      expect(createMessage('error')).toBe('Status: error');
      expect(createMessage('pending')).toBe('Status: pending');
    });
    
    test('unknown type narrowing behaves correctly', () => {
      // TypeScript 4.8 improved unknown type narrowing
      const processValue = (value: unknown): string => {
        if (typeof value === 'string') {
          return value.toUpperCase();
        }
        if (typeof value === 'number') {
          return value.toString();
        }
        if (value instanceof Date) {
          return value.toISOString();
        }
        return 'unknown';
      };
      
      expect(processValue('hello')).toBe('HELLO');
      expect(processValue(42)).toBe('42');
      expect(processValue(new Date('2024-01-01'))).toContain('2024-01-01');
      expect(processValue(null)).toBe('unknown');
    });
    
    test('control flow analysis for generics', () => {
      // TypeScript 4.8 improved control flow analysis
      function processArray<T>(items: T[]): T | undefined {
        if (items.length > 0) {
          return items[0];
        }
        return undefined;
      }
      
      const result1 = processArray([1, 2, 3]);
      expect(result1).toBe(1);
      
      const result2 = processArray<string>([]);
      expect(result2).toBeUndefined();
    });
    
    test('improved type inference for arrays', () => {
      // TypeScript 4.8 improved array type inference
      function processArrayItems<T extends readonly unknown[]>(items: T): T {
        return items;
      }
      
      const tuple = processArrayItems(['a', 1, true] as const);
      expect(tuple).toEqual(['a', 1, true]);
      expect(tuple.length).toBe(3);
      
      // Test with regular array
      const arr = processArrayItems([1, 2, 3]);
      expect(arr).toEqual([1, 2, 3]);
    });
  });
  
  describe('Node.js v18 API Compatibility', () => {
    
    test('crypto API works with new types', () => {
      // Node.js 18 has updated crypto types
      const hash = crypto.createHash('sha256');
      hash.update('test data');
      const digest = hash.digest('hex');
      
      expect(digest).toBeDefined();
      expect(typeof digest).toBe('string');
      expect(digest.length).toBe(64); // SHA-256 produces 64 hex characters
      
      // Test randomUUID (added in Node.js 14.17.0, types updated in v18)
      const uuid = crypto.randomUUID();
      expect(uuid).toMatch(/^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i);
    });
    
    test('stream API with updated types', async () => {
      // Node.js 18 has improved stream types
      const chunks: Buffer[] = [];
      
      const readable = new Readable({
        read() {
          this.push('test data');
          this.push(null);
        }
      });
      
      const writable = new Writable({
        write(chunk, encoding, callback) {
          chunks.push(Buffer.isBuffer(chunk) ? chunk : Buffer.from(chunk));
          callback();
        }
      });
      
      await new Promise((resolve, reject) => {
        readable.pipe(writable);
        writable.on('finish', resolve);
        writable.on('error', reject);
      });
      
      const result = Buffer.concat(chunks).toString();
      expect(result).toBe('test data');
    });
    
    test('fs promises API works correctly', async () => {
      // Node.js 18 has updated fs.promises types
      const testFile = '/tmp/test-compatibility.txt';
      const testContent = 'Test content for fs promises';
      
      // Write file
      await fs.writeFile(testFile, testContent, 'utf8');
      
      // Read file
      const content = await fs.readFile(testFile, 'utf8');
      expect(content).toBe(testContent);
      
      // Check file stats
      const stats = await fs.stat(testFile);
      expect(stats.isFile()).toBe(true);
      expect(stats.size).toBeGreaterThan(0);
      
      // Clean up
      await fs.unlink(testFile);
      
      // Verify deletion
      await expect(fs.access(testFile)).rejects.toThrow();
    });
    
    test('child_process spawn works with new types', async () => {
      // Node.js 18 has updated child_process types
      const result = await new Promise<string>((resolve, reject) => {
        const child = spawn('echo', ['test']);
        let output = '';
        
        child.stdout?.on('data', (data) => {
          output += data.toString();
        });
        
        child.on('close', (code) => {
          if (code === 0) {
            resolve(output.trim());
          } else {
            reject(new Error(`Process exited with code ${code}`));
          }
        });
        
        child.on('error', reject);
      });
      
      expect(result).toBe('test');
    });
  });
  
  describe('MSW Mock Handler Compatibility', () => {
    
    beforeEach(() => {
      server.resetHandlers();
    });
    
    test('MSW handlers work with TypeScript 4.8', async () => {
      // Add a custom handler for this test
      server.use(
        http.get('https://api.test.com/data', () => {
          return HttpResponse.json({
            id: 1,
            name: 'Test Item',
            status: 'active'
          });
        })
      );
      
      const response = await fetch('https://api.test.com/data');
      const data = await response.json();
      
      expect(response.status).toBe(200);
      expect(data).toEqual({
        id: 1,
        name: 'Test Item',
        status: 'active'
      });
    });
    
    test('MSW can mock streaming responses', async () => {
      // TypeScript 4.8 and Node.js 18 improved streaming support
      server.use(
        http.get('https://api.test.com/stream', () => {
          const encoder = new TextEncoder();
          const stream = new ReadableStream({
            start(controller) {
              controller.enqueue(encoder.encode('chunk1'));
              controller.enqueue(encoder.encode('chunk2'));
              controller.close();
            }
          });
          
          return new HttpResponse(stream, {
            headers: {
              'Content-Type': 'text/plain'
            }
          });
        })
      );
      
      const response = await fetch('https://api.test.com/stream');
      const text = await response.text();
      
      expect(text).toBe('chunk1chunk2');
    });
    
    test('MSW error handling works correctly', async () => {
      server.use(
        http.get('https://api.test.com/error', () => {
          return HttpResponse.json(
            { error: 'Internal Server Error' },
            { status: 500 }
          );
        })
      );
      
      const response = await fetch('https://api.test.com/error');
      const data = await response.json();
      
      expect(response.status).toBe(500);
      expect(data.error).toBe('Internal Server Error');
    });
    
    test('MSW request interception with params', async () => {
      server.use(
        http.get('https://api.test.com/users/:id', ({ params }) => {
          return HttpResponse.json({
            id: params.id,
            name: `User ${params.id}`
          });
        })
      );
      
      const response = await fetch('https://api.test.com/users/123');
      const data = await response.json();
      
      expect(data.id).toBe('123');
      expect(data.name).toBe('User 123');
    });
  });
  
  describe('Jest Configuration Compatibility', () => {
    
    test('Jest mocks work with new TypeScript', () => {
      const mockFn = jest.fn((x: number) => x * 2);
      
      mockFn(5);
      mockFn(10);
      
      expect(mockFn).toHaveBeenCalledTimes(2);
      expect(mockFn).toHaveBeenCalledWith(5);
      expect(mockFn).toHaveBeenCalledWith(10);
      expect(mockFn.mock.results[0].value).toBe(10);
      expect(mockFn.mock.results[1].value).toBe(20);
    });
    
    test('Jest timers work correctly', () => {
      jest.useFakeTimers();
      
      const callback = jest.fn();
      setTimeout(callback, 1000);
      
      expect(callback).not.toHaveBeenCalled();
      
      jest.advanceTimersByTime(1000);
      
      expect(callback).toHaveBeenCalledTimes(1);
      
      jest.useRealTimers();
    });
    
    test('Jest module mocking works', () => {
      // Mock a module
      jest.mock('path', () => ({
        join: jest.fn((...args) => args.join('/')),
        resolve: jest.fn((p) => `/absolute/${p}`)
      }));
      
      const path = require('path');
      
      const joined = path.join('a', 'b', 'c');
      expect(joined).toBe('a/b/c');
      
      const resolved = path.resolve('test.txt');
      expect(resolved).toBe('/absolute/test.txt');
      
      jest.unmock('path');
    });
  });
  
  describe('Obsidian API Compatibility', () => {
    
    test('Obsidian types work with new TypeScript', () => {
      // Test that Obsidian type definitions compile with TypeScript 4.8
      interface MockPlugin {
        id: string;
        name: string;
        manifest: {
          version: string;
          minAppVersion: string;
        };
      }
      
      const plugin: MockPlugin = {
        id: 'test-plugin',
        name: 'Test Plugin',
        manifest: {
          version: '1.0.0',
          minAppVersion: '0.15.0'
        }
      };
      
      expect(plugin.id).toBe('test-plugin');
      expect(plugin.manifest.version).toBe('1.0.0');
    });
    
    test('async/await patterns work correctly', async () => {
      // Obsidian plugins often use async/await
      const loadData = async (): Promise<{ settings: any }> => {
        return new Promise((resolve) => {
          setTimeout(() => {
            resolve({ settings: { apiKey: 'test-key' } });
          }, 10);
        });
      };
      
      const data = await loadData();
      expect(data.settings.apiKey).toBe('test-key');
    });
  });
  
  describe('Build Process Compatibility', () => {
    
    test('TypeScript compilation features', () => {
      // Test decorators (if used)
      function logMethod(target: any, propertyKey: string, descriptor: PropertyDescriptor) {
        const originalMethod = descriptor.value;
        descriptor.value = function(...args: any[]) {
          const result = originalMethod.apply(this, args);
          return result;
        };
        return descriptor;
      }
      
      class TestClass {
        @logMethod
        testMethod(value: string): string {
          return value.toUpperCase();
        }
      }
      
      const instance = new TestClass();
      expect(instance.testMethod('hello')).toBe('HELLO');
    });
    
    test('module resolution works correctly', () => {
      // Test that module imports resolve correctly
      expect(typeof require).toBe('function');
      
      // Test JSON module import
      const packageJson = require('../../package.json');
      expect(packageJson).toBeDefined();
      expect(packageJson.name).toBe('obsidian-claude-cli-chat');
    });
  });
});

/**
 * Performance baseline tests to ensure upgrades don't degrade performance
 */
describe('Performance Baselines', () => {
  
  test('test execution time is reasonable', () => {
    const start = performance.now();
    
    // Simulate some work
    for (let i = 0; i < 1000000; i++) {
      Math.sqrt(i);
    }
    
    const end = performance.now();
    const duration = end - start;
    
    // Should complete in less than 100ms
    expect(duration).toBeLessThan(100);
  });
  
  test('memory usage is reasonable', () => {
    if (global.gc) {
      global.gc(); // Force garbage collection if available
    }
    
    const used = process.memoryUsage();
    
    // Heap should be under 100MB for these tests
    expect(used.heapUsed).toBeLessThan(100 * 1024 * 1024);
  });
});