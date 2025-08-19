/**
 * Basic test to verify Jest configuration works
 */

describe('Basic Jest Configuration', () => {
  it('should run TypeScript tests', () => {
    expect(true).toBe(true);
  });

  it('should handle basic TypeScript syntax', () => {
    const obj: { value: number } = { value: 42 };
    expect(obj.value).toBe(42);
  });

  it('should handle mock service worker setup', () => {
    expect(global.localStorage).toBeDefined();
    expect(global.performance).toBeDefined();
  });
});