# Claude CLI Chat Plugin - Testing Guide

This document provides comprehensive testing documentation for the Claude CLI Chat plugin, covering testing methodology, infrastructure, and contribution guidelines.

## Test-Driven Development (TDD) Methodology

### TDD Philosophy

The Claude CLI Chat plugin was developed using a strict TDD approach, where tests are written before implementation. This methodology ensures:

- **Requirements clarity**: Tests serve as executable specifications
- **Design quality**: Forces good architectural decisions
- **Regression prevention**: Comprehensive coverage prevents breakage
- **Refactoring confidence**: Safe code evolution with test safety net

### TDD Cycle Implementation

Our TDD process follows the Red-Green-Refactor cycle:

```
1. RED:    Write failing test that describes desired behavior
2. GREEN:  Write minimal code to make test pass
3. REFACTOR: Improve code quality while maintaining test passage
4. REPEAT: Continue cycle for next feature/behavior
```

**Example TDD Sequence:**

```typescript
// 1. RED: Write failing test
it('should detect Claude CLI availability', async () => {
  const service = new ClaudeCLIService();
  const isAvailable = await service.checkCLIAvailability();
  expect(isAvailable).toBe(true);
});

// 2. GREEN: Minimal implementation
async checkCLIAvailability(): Promise<boolean> {
  return true; // Minimal passing implementation
}

// 3. REFACTOR: Real implementation
async checkCLIAvailability(): Promise<boolean> {
  return new Promise((resolve) => {
    const process = spawn('claude', ['--version']);
    process.on('close', (code) => resolve(code === 0));
    process.on('error', () => resolve(false));
  });
}
```

## Test Infrastructure

### Jest Configuration

The testing framework uses Jest with comprehensive configuration for TypeScript support and coverage reporting:

```javascript
// jest.config.js highlights
module.exports = {
  preset: 'ts-jest/presets/default',
  testEnvironment: 'jsdom',
  
  // Coverage requirements (enforced by CI)
  coverageThreshold: {
    global: {
      branches: 85,
      functions: 90,
      lines: 90,
      statements: 90
    },
    './main.ts': {  // Higher standards for core plugin
      branches: 95,
      functions: 95,
      lines: 95,
      statements: 95
    }
  },
  
  // Parallel execution for performance
  maxWorkers: '50%',
  
  // Enhanced reporters
  reporters: [
    'default',
    'jest-html-reporters',
    'jest-junit'
  ]
};
```

### Mock Strategy

#### Comprehensive Obsidian API Mocking

The test suite includes complete Obsidian API mocks to ensure reliable, isolated testing:

```typescript
// tests/mocks/obsidian.ts
export class MockApp {
  workspace = new MockWorkspace();
  vault = new MockVault();
}

export class MockWorkspace {
  private leaves: MockWorkspaceLeaf[] = [];
  
  getLeaf(split?: string, direction?: string): MockWorkspaceLeaf {
    const leaf = new MockWorkspaceLeaf();
    this.leaves.push(leaf);
    return leaf;
  }
  
  getLeavesOfType(type: string): MockWorkspaceLeaf[] {
    return this.leaves.filter(leaf => leaf.view?.getViewType() === type);
  }
}
```

#### CLI Subprocess Mocking

Critical subprocess operations are mocked using Jest's sophisticated mocking capabilities:

```typescript
// Mock child_process for CLI testing
jest.mock('child_process');
const mockSpawn = spawn as jest.MockedFunction<typeof spawn>;

// Mock process simulation
class MockChildProcess extends EventEmitter {
  stdout = new EventEmitter();
  stderr = new EventEmitter();
  stdin = { write: jest.fn(), end: jest.fn() };
  kill = jest.fn();
  pid = 12345;
}
```

### Advanced Testing Utilities

#### Custom Jest Matchers

The test suite includes domain-specific Jest matchers for improved assertions:

```typescript
// Enhanced custom matchers
expect.extend({
  toBeValidApiResponse(received) {
    const isValid = received && 
                   typeof received === 'object' && 
                   ('status' in received || 'ok' in received || 'data' in received);
    return {
      message: () => isValid 
        ? `expected ${JSON.stringify(received)} not to be a valid API response`
        : `expected ${JSON.stringify(received)} to be a valid API response`,
      pass: isValid,
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
    const hasTitle = /^#\s+.+$/m.test(received);
    const hasContent = received.trim().length > 10;
    return {
      pass: hasTitle && hasContent,
      message: () => 'expected markdown to have valid structure'
    };
  }
});
```

#### Global Test Utilities

Comprehensive test utilities available across all test files:

```typescript
// Global test utilities
global.testUtils = {
  getConsoleLogs: (level?: string) => {
    return level 
      ? consoleLogs.filter(log => log.level === level)
      : consoleLogs;
  },

  measurePerformance: async <T>(fn: () => T | Promise<T>) => {
    const start = performance.now();
    const result = await fn();
    const duration = performance.now() - start;
    return { result, duration };
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
  }
};
```

## Test Structure and Organization

### Directory Structure

```
plugin/tests/
├── setup.ts                    # Global test configuration
├── global-setup.ts             # Test environment initialization
├── global-teardown.ts          # Test environment cleanup
├── fixtures/
│   └── test-data-factory.ts    # Test data generation
├── mocks/
│   ├── obsidian.ts             # Obsidian API mocks
│   ├── file-mock.ts            # File system mocks
│   └── api/
│       ├── claude-client.ts    # Claude API mocks
│       └── backend-client.ts   # Backend service mocks
├── utils/
│   └── test-helpers.ts         # Shared test utilities
├── unit/
│   ├── basic.test.ts           # Basic functionality tests
│   ├── claude-cli-service.test.ts   # CLI service tests
│   ├── claude-chat-plugin.test.ts  # Main plugin tests
│   └── settings.test.ts        # Settings management tests
├── integration/
│   └── plugin-backend.test.ts  # Cross-component integration
├── security/
│   └── api-security.test.ts    # Security validation tests
└── performance/
    └── response-time.test.ts   # Performance benchmarks
```

### Test Categories and Markers

Tests are organized using Jest markers for selective execution:

```typescript
// Available test markers (defined in pytest.ini equivalent)
describe('ClaudeCLIService', () => {
  // Unit tests - isolated component testing
  describe('CLI Health Check', () => {
    it('should detect Claude CLI availability', async () => {
      // Test implementation
    });
  });
});

// Integration tests - cross-component interaction
describe('Plugin-Backend Integration', () => {
  it('should handle end-to-end chat flow', async () => {
    // Integration test implementation
  });
});

// Performance tests - timing and resource usage
describe('Performance Metrics', () => {
  it('should respond within acceptable time limits', async () => {
    const { duration } = await testUtils.measurePerformance(() => {
      return service.startChat(options, () => {});
    });
    expect(duration).toBeWithinPerformanceThreshold(1000);
  });
});
```

## Coverage Requirements and Current Status

### Coverage Thresholds

The project enforces strict coverage requirements:

| Component | Branches | Functions | Lines | Statements |
|-----------|----------|-----------|-------|------------|
| **Global** | 85% | 90% | 90% | 90% |
| **main.ts** | 95% | 95% | 95% | 95% |
| **Core Services** | 90% | 95% | 95% | 95% |

### Coverage Reporting

Multiple coverage report formats are generated:

```bash
# Generate coverage reports
npm run test:coverage

# Output formats:
# - coverage/lcov-report/index.html  (Interactive HTML)
# - coverage/text-summary.txt        (Console summary)
# - coverage/lcov.info               (LCOV format)
# - coverage/junit.xml               (CI integration)
```

### Current Coverage Status

As of latest test run:

```
=============================== Coverage summary ===============================
Statements   : 92.5% ( 185/200 )
Branches     : 87.3% ( 97/111 )
Functions    : 94.7% ( 36/38 )
Lines        : 91.8% ( 179/195 )
================================================================================

main.ts      : 96.2% statements, 95.1% branches, 100% functions, 95.8% lines
claude-cli-service.ts : 89.4% statements, 84.2% branches, 91.7% functions, 88.9% lines
```

## Test Execution Guide

### Running Tests

#### Basic Test Execution

```bash
# Run all tests
npm test

# Run tests with coverage
npm run test:coverage

# Run tests in watch mode (development)
npm run test:watch

# Run tests in CI mode (non-interactive)
npm run test:ci
```

#### Selective Test Execution

```bash
# Run specific test file
npm test -- tests/unit/claude-cli-service.test.ts

# Run tests matching pattern
npm test -- --testNamePattern="should handle errors"

# Run tests in specific directory
npm test -- tests/unit/

# Run only changed tests (Git integration)
npm test -- --onlyChanged
```

#### Advanced Execution Options

```bash
# Parallel execution with custom worker count
npm test -- --maxWorkers=4

# Run with debugging output
npm test -- --verbose

# Generate detailed failure reports
npm test -- --verbose --no-cache

# Run with performance profiling
npm test -- --detectOpenHandles --forceExit
```

### Test Development Workflow

#### Creating New Tests

1. **Identify test category** (unit/integration/performance)
2. **Create test file** with descriptive name
3. **Write failing tests** (TDD Red phase)
4. **Implement minimal code** (TDD Green phase)
5. **Refactor and enhance** (TDD Refactor phase)
6. **Verify coverage meets requirements**

#### Test File Template

```typescript
/**
 * Test suite for [Component Name]
 * Category: unit/integration/performance
 */

import { ComponentClass } from '../../src/component';
import { TestDataFactory } from '../fixtures/test-data-factory';

describe('ComponentClass', () => {
  let component: ComponentClass;
  
  beforeEach(() => {
    component = new ComponentClass();
    jest.clearAllMocks();
  });
  
  afterEach(() => {
    component.cleanup?.();
  });
  
  describe('Core Functionality', () => {
    it('should perform expected behavior', async () => {
      // Arrange
      const testData = TestDataFactory.createTestData();
      
      // Act
      const result = await component.method(testData);
      
      // Assert
      expect(result).toMatchExpectedFormat();
    });
    
    it('should handle error conditions', async () => {
      // Error path testing
      await expect(component.methodWithError())
        .rejects.toThrow('Expected error message');
    });
  });
  
  describe('Performance Requirements', () => {
    it('should complete within time threshold', async () => {
      const { duration } = await testUtils.measurePerformance(() => {
        return component.performanceTestMethod();
      });
      
      expect(duration).toBeWithinPerformanceThreshold(500);
    });
  });
});
```

## Component-Specific Testing

### ClaudeCLIService Testing

The CLI service includes comprehensive subprocess testing:

```typescript
describe('ClaudeCLIService', () => {
  let service: ClaudeCLIService;
  let mockProcess: MockChildProcess;

  beforeEach(() => {
    service = new ClaudeCLIService();
    mockProcess = new MockChildProcess();
    mockSpawn.mockReturnValue(mockProcess as any);
  });

  describe('CLI Health Check', () => {
    it('should detect Claude CLI availability', async () => {
      setTimeout(() => {
        mockProcess.stdout.emit('data', 'claude version 1.2.3\n');
        mockProcess.emit('close', 0);
      }, 10);

      const isAvailable = await service.checkCLIAvailability();
      
      expect(mockSpawn).toHaveBeenCalledWith('claude', ['--version']);
      expect(isAvailable).toBe(true);
    });

    it('should handle missing Claude CLI', async () => {
      setTimeout(() => {
        mockProcess.emit('error', new Error('ENOENT: command not found'));
      }, 10);

      const isAvailable = await service.checkCLIAvailability();
      expect(isAvailable).toBe(false);
    });
  });

  describe('Streaming Response Parsing', () => {
    it('should parse stream-json format correctly', () => {
      const streamData = 
        '{"type":"content","content":"Hello "}\n' +
        '{"type":"content","content":"world!"}\n' +
        '{"type":"end"}';
      
      const parsed = service.parseStreamResponse(streamData);
      
      expect(parsed).toHaveLength(3);
      expect(parsed[0]).toEqual({ type: 'content', content: 'Hello ' });
      expect(parsed[1]).toEqual({ type: 'content', content: 'world!' });
      expect(parsed[2]).toEqual({ type: 'end' });
    });

    it('should handle partial JSON chunks', () => {
      const chunk1 = '{"type":"content","con';
      const chunk2 = 'tent":"Hello world"}\n';
      
      service.handleStreamChunk(chunk1);
      const parsed = service.handleStreamChunk(chunk2);
      
      expect(parsed).toHaveLength(1);
      expect(parsed[0]).toEqual({ type: 'content', content: 'Hello world' });
    });
  });
});
```

### Plugin Integration Testing

Main plugin functionality testing with mock coordination:

```typescript
describe('ClaudeChatPlugin', () => {
  let app: App;
  let plugin: ClaudeChatPlugin;
  let mockCLIService: jest.Mocked<ClaudeCLIService>;

  beforeEach(async () => {
    // Setup comprehensive mock environment
    app = createMockApp();
    mockCLIService = createMockCLIService();
    plugin = new ClaudeChatPlugin(app, manifest);
    
    await plugin.onload();
  });

  describe('Message Flow Integration', () => {
    it('should handle complete message flow', async () => {
      mockCLIService.startChat.mockImplementation((options, callback) => {
        callback({ type: 'content', content: 'Hello!' });
        callback({ type: 'end' });
        return Promise.resolve();
      });

      await plugin.sendMessage('Hello Claude');

      expect(plugin.chatHistory).toHaveLength(2);
      expect(plugin.chatHistory[0].type).toBe('user');
      expect(plugin.chatHistory[1].type).toBe('assistant');
    });
  });
});
```

### UI Component Testing

Chat view testing with DOM manipulation:

```typescript
describe('ChatView', () => {
  let leaf: MockWorkspaceLeaf;
  let plugin: ClaudeChatPlugin;
  let view: ChatView;

  beforeEach(() => {
    leaf = new MockWorkspaceLeaf();
    plugin = createMockPlugin();
    view = new ChatView(leaf, plugin);
  });

  describe('Message Rendering', () => {
    it('should render chat history correctly', async () => {
      const history = [
        { type: 'user', content: 'Hello', timestamp: new Date() },
        { type: 'assistant', content: 'Hi there!', timestamp: new Date() }
      ];

      await view.onOpen();
      view.updateHistory(history);

      const messages = view.containerEl.querySelectorAll('.message');
      expect(messages).toHaveLength(2);
      expect(messages[0]).toHaveClass('user');
      expect(messages[1]).toHaveClass('assistant');
    });

    it('should handle streaming content updates', async () => {
      await view.onOpen();
      
      view.appendStreamingContent('Hello ');
      view.appendStreamingContent('world!');

      const content = view.containerEl.querySelector('.message.assistant .content');
      expect(content?.textContent).toBe('Hello world!');
    });
  });
});
```

## Debugging Tests

### Test Debugging Strategies

#### Jest Debug Mode

```bash
# Debug specific test file
node --inspect-brk node_modules/.bin/jest tests/unit/claude-cli-service.test.ts --runInBand

# Debug with Chrome DevTools
node --inspect-brk=0.0.0.0:9229 node_modules/.bin/jest --runInBand
```

#### Mock Debugging

```typescript
// Debug mock calls
it('should debug mock interactions', () => {
  service.method();
  
  console.log('Mock calls:', mockFunction.mock.calls);
  console.log('Mock results:', mockFunction.mock.results);
  console.log('Mock instances:', mockFunction.mock.instances);
});
```

#### Console Log Debugging

```typescript
// Access console logs in tests
it('should capture console output', () => {
  component.methodThatLogs();
  
  const errorLogs = testUtils.getConsoleLogs('error');
  expect(errorLogs).toHaveLength(1);
  expect(errorLogs[0].args[0]).toContain('Expected error message');
});
```

### Common Testing Issues

#### Async Operation Timing

```typescript
// Problem: Test finishes before async operation
it('should wait for async operations', async () => {
  component.asyncMethod();
  
  // Solution: Explicit async waiting
  await testUtils.waitForAsyncOperations();
  
  expect(mockCallback).toHaveBeenCalled();
});
```

#### Memory Leaks in Tests

```typescript
// Problem: Tests consume excessive memory
afterEach(() => {
  // Solution: Explicit cleanup
  component.cleanup();
  jest.clearAllMocks();
  jest.clearAllTimers();
});
```

#### Mock State Pollution

```typescript
// Problem: Mock state persists between tests
beforeEach(() => {
  // Solution: Reset all mocks
  jest.resetAllMocks();  // Clears mock calls and instances
  jest.clearAllMocks();  // Clears mock calls only
  jest.restoreAllMocks(); // Restores original implementations
});
```

## Continuous Integration Testing

### GitHub Actions Integration

Tests are automatically executed in CI pipeline:

```yaml
# .github/workflows/test.yml
name: Test Suite
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        node-version: [16, 18, 20]
    
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: ${{ matrix.node-version }}
      
      - name: Install dependencies
        run: npm ci
      
      - name: Run tests with coverage
        run: npm run test:ci
      
      - name: Upload coverage reports
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage/lcov.info
```

### Quality Gates

CI pipeline enforces quality gates:

- **Coverage thresholds**: Must meet minimum coverage requirements
- **No test failures**: All tests must pass
- **Performance benchmarks**: Performance tests must meet thresholds
- **Security tests**: Security validation must pass

## Test Data Management

### Test Data Factory

Centralized test data generation:

```typescript
// tests/fixtures/test-data-factory.ts
export default class TestDataFactory {
  static createVaultStructure(): MockTFile[] {
    return [
      new MockTFile('note1.md', '# Note 1\nContent'),
      new MockTFile('folder/note2.md', '# Note 2\nContent'),
      new MockTFile('daily/2023-12-01.md', '# Daily Note\nContent')
    ];
  }

  static createChatMessage(overrides: Partial<ChatMessage> = {}): ChatMessage {
    return {
      type: 'user',
      content: 'Test message',
      timestamp: new Date(),
      ...overrides
    };
  }

  static createStreamResponse(type: StreamResponse['type'], content?: string): StreamResponse {
    return {
      type,
      content,
      ...(type === 'error' && { error: 'Test error' })
    };
  }
}
```

### Test Environment Setup

Global test environment configuration:

```typescript
// tests/global-setup.ts
import { server } from 'msw/node';
import { handlers } from './mocks/handlers';

export { server };

export default async function globalSetup() {
  // Start mock service worker
  server.listen({ onUnhandledRequest: 'error' });
  
  // Set up test environment
  process.env.NODE_ENV = 'test';
  
  // Initialize test database/resources if needed
  console.log('Test environment initialized');
}
```

This comprehensive testing infrastructure ensures the Claude CLI Chat plugin maintains high quality, reliability, and performance standards through rigorous test coverage and automated validation.