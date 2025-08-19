# Test-Driven Development (TDD) Implementation Guide

## Overview

This document describes the comprehensive Test-Driven Development infrastructure implemented for the Obsidian Copilot project. The TDD framework supports both TypeScript (plugin) and Python (backend) components with advanced testing capabilities.

## Table of Contents

1. [Architecture](#architecture)
2. [Jest Configuration (TypeScript)](#jest-configuration-typescript)
3. [Pytest Configuration (Python)](#pytest-configuration-python)
4. [Test Organization](#test-organization)
5. [Mocking Strategy](#mocking-strategy)
6. [Running Tests](#running-tests)
7. [Quality Gates](#quality-gates)
8. [Best Practices](#best-practices)

## Architecture

### Testing Framework Stack

```
┌─────────────────────────────────────────┐
│          Obsidian Copilot TDD           │
├─────────────┬───────────────────────────┤
│  TypeScript │         Python             │
│    (Jest)   │        (pytest)            │
├─────────────┼───────────────────────────┤
│     MSW     │      OpenSearch Mock       │
│   Obsidian  │       Redis Mock           │
│  Claude API │      Claude API Mock       │
│  OpenAI API │    Semantic Search Mock    │
└─────────────┴───────────────────────────┘
```

### Key Components

- **Jest**: TypeScript/JavaScript testing framework with DOM simulation
- **pytest**: Python testing framework with advanced fixtures
- **MSW (Mock Service Worker)**: API mocking for HTTP requests
- **Test Factories**: Consistent test data generation
- **Performance Benchmarking**: Response time and resource usage testing
- **Security Testing**: API key and authentication validation

## Jest Configuration (TypeScript)

### Configuration File: `plugin/jest.config.js`

```javascript
module.exports = {
  preset: 'ts-jest/presets/default',
  testEnvironment: 'jsdom',
  extensionsToTreatAsEsm: ['.ts'],
  
  // Coverage Requirements
  coverageThreshold: {
    global: {
      branches: 85,
      functions: 90,
      lines: 90,
      statements: 90
    }
  },
  
  // Parallel Execution
  maxWorkers: '50%',
  
  // Enhanced Mocking
  moduleNameMapper: {
    '^obsidian$': '<rootDir>/tests/mocks/obsidian.ts',
    '^@/api/(.*)$': '<rootDir>/tests/mocks/api/$1',
    '^@/(.*)$': '<rootDir>/$1'
  }
};
```

### Global Setup

The global setup (`plugin/tests/global-setup.ts`) initializes:

1. **MSW Server**: HTTP request interception and mocking
2. **Browser APIs**: localStorage, sessionStorage, performance, crypto
3. **DOM APIs**: ResizeObserver, IntersectionObserver
4. **Environment Variables**: Test-specific configuration

### Custom Matchers

Enhanced Jest matchers for domain-specific assertions:

- `toBeValidApiResponse()`: Validates API response structure
- `toHaveValidSettings()`: Checks plugin settings configuration
- `toHaveBeenCalledWithApiKey()`: Verifies API key usage
- `toBeWithinPerformanceThreshold(ms)`: Performance validation
- `toHaveValidMarkdownStructure()`: Markdown content validation
- `toMatchVaultDocument()`: Vault document structure validation
- `toBeStreamingResponse()`: Streaming response validation

### MSW v2 Integration

Mock Service Worker handlers for API simulation:

```typescript
import { http, HttpResponse } from 'msw';

const handlers = [
  // Claude API
  http.post('https://api.anthropic.com/v1/messages', () => {
    return HttpResponse.json({
      id: 'msg_test_123',
      type: 'message',
      role: 'assistant',
      content: [{ type: 'text', text: 'Mocked response' }]
    });
  }),
  
  // Backend API
  http.post('http://localhost:8000/query', () => {
    return HttpResponse.json({
      response: 'Mocked backend response',
      retrieved_docs: []
    });
  })
];
```

## Pytest Configuration (Python)

### Configuration File: `pytest.ini`

```ini
[pytest]
minversion = 7.0
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*

# Parallel Execution
addopts = 
    -ra
    --strict-markers
    --cov=src
    --cov-report=term-missing
    --cov-report=html
    --cov-report=xml
    --cov-fail-under=80
    -n auto
    --maxfail=3
    --tb=short
    --benchmark-only
    --benchmark-autosave

# Test Markers (20+ categories)
markers =
    unit: Unit tests
    integration: Integration tests
    e2e: End-to-end tests
    slow: Slow running tests
    agent: Agent-related tests
    memory: Memory system tests
    search: Search functionality tests
    claude: Claude API tests
    openai: OpenAI API tests
    benchmark: Performance benchmarks
    security: Security tests
    mock: Tests using mocks
    network: Network-dependent tests
    db: Database tests
    parallel: Parallel execution tests
    flaky: Flaky tests to retry
    critical: Critical path tests
    experimental: Experimental features
    deprecated: Deprecated functionality
    wip: Work in progress
```

### Advanced Fixtures

Comprehensive fixtures for testing (`tests/conftest.py`):

```python
@pytest.fixture
def mock_opensearch_client():
    """Mock OpenSearch client with search capabilities"""
    client = Mock()
    client.search.return_value = {
        'hits': {
            'hits': [
                {'_id': '1', '_source': {'content': 'Test content'}}
            ]
        }
    }
    return client

@pytest.fixture
def mock_vault_dict():
    """Sample vault dictionary for testing"""
    return {
        'doc1': {'title': 'Test Doc 1', 'chunk': 'Content 1'},
        'doc2': {'title': 'Test Doc 2', 'chunk': 'Content 2'}
    }

@pytest.fixture
async def mock_redis_client():
    """Mock Redis client for caching tests"""
    client = AsyncMock()
    client.get.return_value = None
    client.set.return_value = True
    return client
```

## Test Organization

### Directory Structure

```
tests/
├── unit/                    # Unit tests
│   ├── test_semantic_search.py
│   ├── test_opensearch_integration.py
│   ├── test_api_endpoints.py
│   └── test_agent_system.py
├── integration/             # Integration tests
│   ├── test_full_pipeline.py
│   ├── test_vault_analysis.py
│   └── test_agent_orchestration.py
├── e2e/                    # End-to-end tests
│   ├── test_user_workflows.py
│   └── test_system_integration.py
├── performance/            # Performance tests
│   ├── test_search_performance.py
│   └── test_response_times.py
├── security/               # Security tests
│   ├── test_api_security.py
│   └── test_authentication.py
├── fixtures/               # Test data and factories
│   ├── test-data-factory.ts
│   └── sample_data.py
├── mocks/                  # Mock implementations
│   ├── obsidian.ts
│   ├── claude-api.ts
│   └── api_mocks.py
├── helpers/                # Test utilities
│   ├── test-helpers.ts
│   └── test_utilities.py
├── conftest.py            # Pytest configuration
├── setup.ts               # Jest setup
├── global-setup.ts        # Global test setup
└── global-teardown.ts     # Global test cleanup
```

### Test Categories

1. **Unit Tests**: Isolated component testing
2. **Integration Tests**: Component interaction testing
3. **E2E Tests**: Full workflow validation
4. **Performance Tests**: Response time and throughput
5. **Security Tests**: Authentication and authorization
6. **Agent Tests**: Agent OS functionality
7. **Memory Tests**: Basic Memory integration

## Mocking Strategy

### External Service Mocks

1. **Claude API**: Response generation simulation
2. **OpenAI API**: GPT model response mocking
3. **OpenSearch**: Search result simulation
4. **Redis**: Cache operation mocking
5. **Obsidian API**: Vault and editor mocking
6. **File System**: Virtual file operations

### Mock Implementations

#### TypeScript Mock Example (Obsidian API)

```typescript
export class MockApp {
  vault = new MockVault();
  workspace = new MockWorkspace();
  
  async loadData() {
    return { settings: DEFAULT_SETTINGS };
  }
  
  async saveData(data: any) {
    this.data = data;
  }
}
```

#### Python Mock Example (Claude API)

```python
class MockClaudeClient:
    async def create_message(self, **kwargs):
        return {
            'id': 'msg_test',
            'content': [{'text': 'Mocked Claude response'}],
            'usage': {'input_tokens': 10, 'output_tokens': 20}
        }
```

## Running Tests

### Jest Tests (TypeScript)

```bash
# Run all tests
npm test

# Run with coverage
npm test -- --coverage

# Run specific test file
npm test -- --testPathPattern="settings.test.ts"

# Run in watch mode
npm test -- --watch

# Run with verbose output
npm test -- --verbose
```

### Pytest Tests (Python)

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific marker
pytest -m unit
pytest -m "not slow"

# Run in parallel
pytest -n auto

# Run with benchmark
pytest --benchmark-only

# Run specific test
pytest tests/unit/test_api_endpoints.py::TestGenerationEndpoint
```

## Quality Gates

### Coverage Requirements

- **Jest (TypeScript)**:
  - Global: 90% lines, 90% functions, 85% branches
  - Critical files (main.ts): 95% all metrics

- **Pytest (Python)**:
  - Global: 80% minimum coverage
  - HTML and XML reports generated

### Performance Thresholds

- API response time: < 2000ms
- Search operations: < 500ms
- Agent execution: < 5000ms
- Memory operations: < 100ms

### Test Execution Limits

- Maximum test duration: 15 seconds
- Parallel workers: 50% of CPU cores
- Maximum failures before stop: 3

## Best Practices

### TDD Workflow

1. **Red Phase**: Write failing test first
2. **Green Phase**: Implement minimal code to pass
3. **Refactor Phase**: Improve code quality

### Test Writing Guidelines

1. **Isolation**: Each test should be independent
2. **Clarity**: Test names should describe behavior
3. **Speed**: Prefer unit tests over integration tests
4. **Completeness**: Test edge cases and error conditions
5. **Maintenance**: Keep tests simple and readable

### Mock Usage

1. **Minimize Mocking**: Only mock external dependencies
2. **Realistic Data**: Use factory patterns for test data
3. **Verify Interactions**: Assert mock method calls
4. **Clean State**: Reset mocks between tests

### Performance Testing

1. **Benchmark Baselines**: Establish performance baselines
2. **Regular Monitoring**: Run performance tests in CI
3. **Resource Tracking**: Monitor memory and CPU usage
4. **Optimization**: Profile before optimizing

### Security Testing

1. **API Key Validation**: Test authentication flows
2. **Input Sanitization**: Test injection prevention
3. **Rate Limiting**: Verify throttling mechanisms
4. **Error Handling**: Ensure no sensitive data leaks

## Continuous Integration

### GitHub Actions Integration

```yaml
name: Test Suite

on: [push, pull_request]

jobs:
  test-typescript:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-node@v2
      - run: npm install
      - run: npm test -- --coverage
      
  test-python:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
      - run: pip install -r requirements-test.txt
      - run: pytest --cov
```

## Troubleshooting

### Common Issues

1. **MSW Not Starting**: Ensure global setup is configured
2. **Import Errors**: Check TypeScript configuration
3. **Mock Not Working**: Verify mock registration
4. **Slow Tests**: Use parallel execution
5. **Flaky Tests**: Add retry mechanisms

### Debug Commands

```bash
# Jest debug
npm test -- --detectOpenHandles --forceExit

# Pytest debug
pytest -vv --tb=long --capture=no

# Check test discovery
jest --listTests
pytest --collect-only
```

## Future Enhancements

1. **Mutation Testing**: Validate test effectiveness
2. **Contract Testing**: API contract validation
3. **Visual Regression**: UI snapshot testing
4. **Load Testing**: Scalability validation
5. **Chaos Engineering**: Resilience testing

## References

- [Jest Documentation](https://jestjs.io/docs/getting-started)
- [Pytest Documentation](https://docs.pytest.org/)
- [MSW Documentation](https://mswjs.io/)
- [Testing Best Practices](https://testingjavascript.com/)
- [TDD by Example](https://www.amazon.com/Test-Driven-Development-Kent-Beck/dp/0321146530)

---

*Last Updated: 2025-08-19*
*Version: 1.0.0*