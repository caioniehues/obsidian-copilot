# Test Organization Structure

This document outlines the comprehensive test organization structure for the Obsidian Copilot project, designed to support advanced TDD practices and ensure high code quality.

## Directory Structure

```
tests/
├── unit/                    # Unit tests (fast, isolated)
│   ├── test_api_endpoints.py
│   ├── test_semantic_search.py
│   ├── test_opensearch_integration.py
│   └── agents/              # Agent-specific unit tests
├── integration/             # Integration tests (medium speed)
│   ├── test_plugin_backend_communication.py
│   ├── test_opensearch_semantic_integration.py
│   ├── test_agent_coordination.py
│   └── test_vault_analysis_pipeline.py
├── e2e/                    # End-to-end tests (slow, full system)
│   ├── test_complete_user_workflows.py
│   ├── test_dual_mode_switching.py
│   └── test_streaming_generation.py
├── performance/            # Performance and benchmark tests
│   ├── test_search_performance.py
│   ├── test_embedding_generation.py
│   ├── test_concurrent_requests.py
│   └── benchmarks/
│       ├── search_benchmarks.py
│       └── agent_performance.py
├── security/              # Security-focused tests
│   ├── test_api_key_handling.py
│   ├── test_input_validation.py
│   ├── test_injection_prevention.py
│   └── test_data_privacy.py
├── fixtures/              # Test data and fixtures
│   ├── __init__.py
│   ├── vault_samples.py
│   ├── api_responses.py
│   ├── embedding_data.py
│   └── factories/         # Factory classes for test data
│       ├── __init__.py
│       ├── vault_factory.py
│       ├── request_factory.py
│       └── response_factory.py
├── mocks/                 # Mock implementations
│   ├── __init__.py
│   ├── opensearch_mock.py
│   ├── redis_mock.py
│   ├── claude_api_mock.py
│   └── agent_mock.py
├── utils/                 # Testing utilities
│   ├── __init__.py
│   ├── assertions.py
│   ├── performance_helpers.py
│   ├── security_helpers.py
│   └── data_generators.py
├── helpers/               # Test helper functions
│   ├── __init__.py
│   ├── setup_helpers.py
│   ├── cleanup_helpers.py
│   └── mock_helpers.py
├── conftest.py           # Main pytest configuration
├── conftest_enhanced.py  # Enhanced fixtures (future replacement)
├── pytest.ini           # Pytest configuration
├── pytest.log           # Test execution logs
└── README.md            # This file
```

## Plugin Test Structure

```
plugin/tests/
├── unit/                    # TypeScript unit tests
│   ├── settings.test.ts
│   ├── editor-integration.test.ts
│   ├── api-client.test.ts
│   └── vault-operations.test.ts
├── integration/             # Plugin integration tests
│   ├── obsidian-api.test.ts
│   ├── backend-communication.test.ts
│   └── mode-switching.test.ts
├── e2e/                    # End-to-end plugin tests
│   ├── complete-workflow.test.ts
│   ├── user-interactions.test.ts
│   └── error-scenarios.test.ts
├── performance/            # Plugin performance tests
│   ├── rendering-performance.test.ts
│   ├── memory-usage.test.ts
│   └── startup-time.test.ts
├── security/              # Plugin security tests
│   ├── api-key-security.test.ts
│   ├── data-sanitization.test.ts
│   └── cross-frame-security.test.ts
├── fixtures/              # TypeScript test data
│   ├── test-data-factory.ts
│   ├── mock-vault-data.ts
│   └── api-response-mocks.ts
├── mocks/                 # TypeScript mocks
│   ├── obsidian.ts
│   ├── api/
│   │   ├── claude-client.ts
│   │   └── backend-client.ts
│   └── file-mock.ts
├── utils/                 # TypeScript test utilities
│   ├── test-helpers.ts
│   ├── performance-utils.ts
│   └── mock-factories.ts
├── jest.config.js         # Jest configuration
├── setup.ts              # Jest setup
├── global-setup.ts       # Global Jest setup
├── global-teardown.ts    # Global Jest teardown
└── tsconfig.json         # TypeScript config for tests
```

## Test Categories and Markers

### Test Type Markers
- `@pytest.mark.unit` - Fast, isolated unit tests
- `@pytest.mark.integration` - Tests with external dependencies
- `@pytest.mark.e2e` - Complete system tests
- `@pytest.mark.performance` - Performance benchmarks
- `@pytest.mark.security` - Security-focused tests

### Speed Markers
- `@pytest.mark.fast` - Tests completing in < 1 second
- `@pytest.mark.slow` - Tests taking > 5 seconds

### Dependency Markers
- `@pytest.mark.requires_opensearch` - Needs OpenSearch running
- `@pytest.mark.requires_redis` - Needs Redis running
- `@pytest.mark.requires_models` - Needs ML models loaded
- `@pytest.mark.requires_docker` - Needs Docker containers
- `@pytest.mark.requires_network` - Needs network access

### Feature Markers
- `@pytest.mark.agents` - Agent OS functionality
- `@pytest.mark.retrieval` - RAG retrieval system
- `@pytest.mark.api` - API endpoints
- `@pytest.mark.streaming` - Streaming responses
- `@pytest.mark.vault_analysis` - Vault analysis features

### Environment Markers
- `@pytest.mark.dev_only` - Development environment only
- `@pytest.mark.ci_only` - CI environment only
- `@pytest.mark.local_only` - Local environment only

## Test Execution Patterns

### Running Different Test Categories

```bash
# Fast tests only (development workflow)
pytest -m "fast and not slow"

# Unit tests only
pytest tests/unit/ -m unit

# Integration tests with OpenSearch
pytest tests/integration/ -m "integration and requires_opensearch"

# Performance benchmarks
pytest tests/performance/ -m performance --benchmark-only

# Security tests
pytest tests/security/ -m security

# All tests except slow ones
pytest -m "not slow"

# Parallel execution
pytest -n auto

# Coverage with parallel execution
pytest -n auto --cov=src --cov-report=html

# Specific feature tests
pytest -m "agents or retrieval"

# Environment-specific tests
pytest -m "not ci_only"  # Skip CI-only tests locally
```

### TypeScript Test Execution

```bash
# All plugin tests
npm test

# Unit tests only
npm run test:unit

# Integration tests
npm run test:integration

# Performance tests
npm run test:performance

# Watch mode for development
npm run test:watch

# Coverage report
npm run test:coverage

# Specific test categories
npx jest --testNamePattern="unit"
npx jest --testPathPattern="integration"
```

## Test Data Management

### Fixtures Organization
- **fixtures/vault_samples.py** - Sample vault documents and structures
- **fixtures/api_responses.py** - Mock API response data
- **fixtures/embedding_data.py** - Pre-computed embeddings for testing
- **fixtures/factories/** - Factory classes for generating test data

### Mock Strategy
- **Comprehensive Mocking** - All external dependencies mocked by default
- **Realistic Responses** - Mocks return realistic data structures
- **State Management** - Mocks maintain state across test execution
- **Performance Simulation** - Mocks simulate realistic latencies

### Test Data Factories
- **VaultDocumentFactory** - Creates realistic vault documents
- **ApiRequestFactory** - Generates API request objects
- **EmbeddingFactory** - Creates test embeddings
- **UserInteractionFactory** - Simulates user interactions

## Performance Testing Strategy

### Benchmarking
- **Response Time Targets** - API responses < 500ms
- **Search Performance** - Semantic search < 200ms
- **Memory Usage** - Monitor for memory leaks
- **Concurrent Load** - Test with multiple simultaneous requests

### Performance Monitoring
- **Automated Benchmarks** - Run with each test execution
- **Regression Detection** - Alert on performance degradation
- **Resource Monitoring** - Track CPU, memory, and I/O usage
- **Scalability Testing** - Test with increasing data volumes

## Security Testing Approach

### Input Validation
- **Injection Prevention** - SQL, NoSQL, and code injection tests
- **XSS Protection** - Cross-site scripting prevention
- **Path Traversal** - Directory traversal attack prevention
- **Data Sanitization** - Input sanitization validation

### API Security
- **Authentication Testing** - API key validation
- **Authorization Testing** - Access control verification
- **Rate Limiting** - Request throttling validation
- **Data Privacy** - Sensitive data handling

### Plugin Security
- **Cross-Frame Security** - Obsidian API boundary testing
- **Data Isolation** - Vault data access controls
- **Permission Validation** - Plugin permission enforcement
- **Secure Communication** - HTTPS and encryption testing

## Quality Gates and Thresholds

### Coverage Requirements
- **Unit Tests** - 90% minimum coverage
- **Integration Tests** - 80% minimum coverage
- **E2E Tests** - 100% critical path coverage
- **Security Tests** - 100% security-critical code coverage

### Performance Thresholds
- **API Response Time** - 95th percentile < 500ms
- **Search Latency** - Average < 200ms
- **Memory Usage** - No leaks > 50MB in test suite
- **Startup Time** - Plugin activation < 1s

### Quality Metrics
- **Test Execution Time** - Full suite < 5 minutes
- **Test Reliability** - < 1% flaky test rate
- **Bug Escape Rate** - < 5% of bugs reach production
- **Security Compliance** - Zero high-severity vulnerabilities

## Continuous Integration Integration

### CI Pipeline Stages
1. **Fast Tests** - Unit tests and quick validations
2. **Integration Tests** - Tests with external dependencies
3. **Security Scans** - Vulnerability and security testing
4. **Performance Tests** - Benchmark and load testing
5. **E2E Tests** - Complete workflow validation

### Reporting
- **JUnit XML** - For CI system integration
- **Coverage Reports** - HTML and XML formats
- **Performance Reports** - Benchmark results and trends
- **Security Reports** - Vulnerability scan results

## Best Practices

### Test Organization
- **Single Responsibility** - Each test tests one thing
- **Clear Naming** - Descriptive test names
- **Independent Tests** - No interdependencies
- **Fast Feedback** - Quick test execution

### Mock Management
- **Minimal Mocking** - Mock only external dependencies
- **Realistic Mocks** - Mocks behave like real services
- **State Cleanup** - Reset mocks between tests
- **Mock Verification** - Verify mock interactions

### Performance Testing
- **Baseline Measurements** - Establish performance baselines
- **Regression Detection** - Monitor for performance degradation
- **Resource Monitoring** - Track system resource usage
- **Load Testing** - Test under realistic load conditions

### Security Testing
- **Threat Modeling** - Identify potential security threats
- **Input Fuzzing** - Test with malicious inputs
- **Authentication Testing** - Verify access controls
- **Data Protection** - Ensure sensitive data security

This comprehensive test organization structure ensures thorough coverage, maintainability, and scalability of the test suite while supporting advanced TDD practices and quality assurance processes.