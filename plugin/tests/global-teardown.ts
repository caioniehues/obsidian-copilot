/**
 * Global Jest teardown for Obsidian Copilot plugin testing.
 * Cleans up resources, stops mock servers, and performs final cleanup.
 */

import { server } from './global-setup';

export default async function globalTeardown() {
  console.log('🧹 Starting global test teardown...');

  // Stop MSW server
  if (server) {
    server.close();
    console.log('📡 MSW server stopped');
  }

  // Clean up any global mocks
  if (global.localStorage) {
    // @ts-ignore
    delete global.localStorage;
  }

  if (global.sessionStorage) {
    // @ts-ignore
    delete global.sessionStorage;
  }

  if (global.performance) {
    // @ts-ignore
    delete global.performance;
  }

  if (global.ResizeObserver) {
    // @ts-ignore
    delete global.ResizeObserver;
  }

  if (global.IntersectionObserver) {
    // @ts-ignore
    delete global.IntersectionObserver;
  }

  if (global.crypto) {
    // @ts-ignore
    delete global.crypto;
  }

  // Clean up test environment variables
  delete process.env.TEST_TIMEOUT;

  // Force garbage collection if available
  if (global.gc) {
    global.gc();
  }

  console.log('✅ Global test teardown completed');
}