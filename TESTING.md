# Testing Quick Start Guide

## 🚀 Running Tests

### TypeScript/Jest Tests (Plugin)
```bash
cd plugin

# Run all tests
npm test

# Run with coverage
npm test -- --coverage

# Run specific test
npm test -- --testPathPattern="settings"

# Watch mode
npm test -- --watch
```

### Python/Pytest Tests (Backend)
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src

# Run by marker
pytest -m unit
pytest -m "not slow"

# Run in parallel
pytest -n auto
```

## 📊 Coverage Requirements

- **TypeScript**: 90% lines, 90% functions, 85% branches
- **Python**: 80% minimum coverage
- **Critical files**: 95% all metrics

## 🏗️ Test Structure

```
tests/
├── unit/         # Isolated component tests
├── integration/  # Component interaction tests
├── e2e/         # Full workflow tests
├── performance/ # Response time tests
├── security/    # Authentication tests
├── fixtures/    # Test data factories
├── mocks/       # Mock implementations
└── helpers/     # Test utilities
```

## 🎯 Test Markers (Python)

- `@pytest.mark.unit` - Unit tests
- `@pytest.mark.integration` - Integration tests
- `@pytest.mark.slow` - Slow tests (>1s)
- `@pytest.mark.claude` - Claude API tests
- `@pytest.mark.agent` - Agent system tests
- `@pytest.mark.benchmark` - Performance tests
- `@pytest.mark.security` - Security tests

## 🔧 Key Testing Features

### TypeScript (Jest)
- ✅ MSW v2 for API mocking
- ✅ Obsidian API mocks
- ✅ Custom matchers for domain assertions
- ✅ Parallel test execution
- ✅ Global setup/teardown
- ✅ Coverage reporting

### Python (pytest)
- ✅ Advanced fixtures for all services
- ✅ Parallel execution with pytest-xdist
- ✅ Performance benchmarking
- ✅ Security testing patterns
- ✅ 20+ test markers
- ✅ Comprehensive mocking

## 📝 Writing Tests

### TDD Workflow
1. **Red**: Write failing test
2. **Green**: Implement minimal code
3. **Refactor**: Improve quality

### Example Test (TypeScript)
```typescript
describe('Plugin Settings', () => {
  it('should validate API key', () => {
    const settings = new Settings();
    expect(settings.validateApiKey('sk-test')).toBe(true);
  });
});
```

### Example Test (Python)
```python
@pytest.mark.unit
def test_query_endpoint(test_client):
    response = test_client.post('/query', json={
        'query': 'test query',
        'system_prompt': 'test prompt'
    })
    assert response.status_code == 200
    assert 'response' in response.json()
```

## 🐛 Debugging Tests

```bash
# Jest debugging
npm test -- --detectOpenHandles

# Pytest debugging
pytest -vv --tb=long --capture=no

# List discovered tests
jest --listTests
pytest --collect-only
```

## 📈 Performance Testing

```bash
# Run benchmarks
pytest --benchmark-only

# Profile tests
pytest --profile
```

## 🔗 Resources

- [Full TDD Documentation](docs/TDD-IMPLEMENTATION.md)
- [Jest Documentation](https://jestjs.io/)
- [Pytest Documentation](https://docs.pytest.org/)
- [MSW Documentation](https://mswjs.io/)

---

*For detailed documentation, see [docs/TDD-IMPLEMENTATION.md](docs/TDD-IMPLEMENTATION.md)*