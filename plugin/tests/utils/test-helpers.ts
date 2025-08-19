/**
 * Test utility functions and helpers for plugin testing.
 * Provides common functionality used across multiple test files.
 */

import { MockTFile } from '../mocks/obsidian';
import TestDataFactory from '../fixtures/test-data-factory';

export interface TestEnvironment {
  cleanup: () => void;
  reset: () => void;
  getMetrics: () => TestMetrics;
}

export interface TestMetrics {
  memoryUsage: NodeJS.MemoryUsage;
  timeElapsed: number;
  apiCalls: number;
  errors: number;
}

export class TestTimer {
  private startTime: number = 0;
  private endTime: number = 0;

  start(): void {
    this.startTime = performance.now();
  }

  stop(): number {
    this.endTime = performance.now();
    return this.endTime - this.startTime;
  }

  get duration(): number {
    return this.endTime - this.startTime;
  }

  static async measure<T>(fn: () => Promise<T>): Promise<{ result: T; duration: number }> {
    const timer = new TestTimer();
    timer.start();
    const result = await fn();
    const duration = timer.stop();
    return { result, duration };
  }
}

export class MemoryTracker {
  private initialMemory: NodeJS.MemoryUsage;
  private snapshots: NodeJS.MemoryUsage[] = [];

  constructor() {
    this.forceGC();
    this.initialMemory = process.memoryUsage();
  }

  takeSnapshot(): NodeJS.MemoryUsage {
    this.forceGC();
    const snapshot = process.memoryUsage();
    this.snapshots.push(snapshot);
    return snapshot;
  }

  getMemoryIncrease(): number {
    const current = this.takeSnapshot();
    return (current.heapUsed - this.initialMemory.heapUsed) / 1024 / 1024; // MB
  }

  private forceGC(): void {
    if (global.gc) {
      global.gc();
    }
  }

  reset(): void {
    this.forceGC();
    this.initialMemory = process.memoryUsage();
    this.snapshots = [];
  }
}

export class ApiCallTracker {
  private calls: Array<{
    url: string;
    method: string;
    timestamp: number;
    duration?: number;
    success: boolean;
  }> = [];

  trackCall(url: string, method: string = 'POST'): {
    start: () => void;
    success: () => void;
    error: () => void;
  } {
    const call = {
      url,
      method,
      timestamp: Date.now(),
      success: false
    };

    this.calls.push(call);
    const startTime = performance.now();

    return {
      start: () => {
        // Call already tracked on creation
      },
      success: () => {
        call.success = true;
        call.duration = performance.now() - startTime;
      },
      error: () => {
        call.success = false;
        call.duration = performance.now() - startTime;
      }
    };
  }

  getCalls(): typeof this.calls {
    return [...this.calls];
  }

  getCallCount(): number {
    return this.calls.length;
  }

  getSuccessRate(): number {
    if (this.calls.length === 0) return 0;
    const successCount = this.calls.filter(call => call.success).length;
    return successCount / this.calls.length;
  }

  getAverageResponseTime(): number {
    const completedCalls = this.calls.filter(call => call.duration !== undefined);
    if (completedCalls.length === 0) return 0;
    
    const totalTime = completedCalls.reduce((sum, call) => sum + (call.duration || 0), 0);
    return totalTime / completedCalls.length;
  }

  reset(): void {
    this.calls = [];
  }
}

export function createTestEnvironment(): TestEnvironment {
  const memoryTracker = new MemoryTracker();
  const apiTracker = new ApiCallTracker();
  const timer = new TestTimer();
  
  timer.start();

  return {
    cleanup: () => {
      memoryTracker.reset();
      apiTracker.reset();
      // Clean up any global test state
      if (global.testUtils) {
        global.testUtils.clearTestData();
      }
    },

    reset: () => {
      memoryTracker.reset();
      apiTracker.reset();
      timer.start();
    },

    getMetrics: (): TestMetrics => ({
      memoryUsage: process.memoryUsage(),
      timeElapsed: timer.duration,
      apiCalls: apiTracker.getCallCount(),
      errors: 0 // Would track errors in real implementation
    })
  };
}

export async function waitForCondition(
  condition: () => boolean | Promise<boolean>,
  timeout: number = 5000,
  interval: number = 100
): Promise<void> {
  const startTime = Date.now();
  
  while (Date.now() - startTime < timeout) {
    if (await condition()) {
      return;
    }
    await new Promise(resolve => setTimeout(resolve, interval));
  }
  
  throw new Error(`Condition not met within ${timeout}ms`);
}

export function createMockVault(fileCount: number = 10): Map<string, MockTFile> {
  const vault = new Map<string, MockTFile>();
  
  // Add default test files
  const defaultFiles = TestDataFactory.createVaultStructure();
  defaultFiles.forEach(file => {
    vault.set(file.path, file);
  });

  // Add additional generated files if requested
  if (fileCount > defaultFiles.length) {
    const additionalDocs = TestDataFactory.createMultipleDocuments(fileCount - defaultFiles.length);
    additionalDocs.forEach(doc => {
      const file = TestDataFactory.createTFile(doc.path, doc.content);
      vault.set(doc.path, file);
    });
  }

  return vault;
}

export function assertValidResponse(response: any, requiredFields: string[] = []): void {
  expect(response).toBeTruthy();
  expect(typeof response === 'object').toBe(true);
  
  requiredFields.forEach(field => {
    expect(response).toHaveProperty(field);
  });
}

export function assertPerformanceThreshold(duration: number, maxMs: number, operation: string = 'operation'): void {
  expect(duration).toBeLessThan(maxMs);
  
  if (duration > maxMs * 0.8) {
    console.warn(`${operation} took ${duration}ms, approaching threshold of ${maxMs}ms`);
  }
}

export function generateRandomString(length: number): string {
  const chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789';
  let result = '';
  for (let i = 0; i < length; i++) {
    result += chars.charAt(Math.floor(Math.random() * chars.length));
  }
  return result;
}

export function simulateUserDelay(minMs: number = 100, maxMs: number = 300): Promise<void> {
  const delay = Math.random() * (maxMs - minMs) + minMs;
  return new Promise(resolve => setTimeout(resolve, delay));
}

export class EventCollector<T = any> {
  private events: T[] = [];

  collect(event: T): void {
    this.events.push(event);
  }

  getEvents(): T[] {
    return [...this.events];
  }

  getEventCount(): number {
    return this.events.length;
  }

  clear(): void {
    this.events = [];
  }

  waitForEvents(count: number, timeout: number = 5000): Promise<T[]> {
    return new Promise((resolve, reject) => {
      const startTime = Date.now();
      
      const checkEvents = () => {
        if (this.events.length >= count) {
          resolve([...this.events]);
        } else if (Date.now() - startTime > timeout) {
          reject(new Error(`Expected ${count} events, got ${this.events.length} within ${timeout}ms`));
        } else {
          setTimeout(checkEvents, 10);
        }
      };
      
      checkEvents();
    });
  }
}

export function createStressTestData(): {
  largeText: string;
  deeplyNestedObject: any;
  manyFiles: MockTFile[];
} {
  return {
    largeText: 'Lorem ipsum '.repeat(10000), // ~110KB of text
    deeplyNestedObject: createDeepObject(100),
    manyFiles: TestDataFactory.createVaultStructure().concat(
      TestDataFactory.createMultipleDocuments(500)
    ).map(doc => TestDataFactory.createTFile(doc.path, doc.content))
  };
}

function createDeepObject(depth: number): any {
  if (depth <= 0) return { value: 'bottom' };
  return { 
    level: depth, 
    child: createDeepObject(depth - 1),
    data: `Level ${depth} data`
  };
}

export const TestHelpers = {
  TestTimer,
  MemoryTracker,
  ApiCallTracker,
  EventCollector,
  createTestEnvironment,
  waitForCondition,
  createMockVault,
  assertValidResponse,
  assertPerformanceThreshold,
  generateRandomString,
  simulateUserDelay,
  createStressTestData
};