/**
 * Basic JavaScript test to verify Jest configuration works
 */

describe('Basic Jest Configuration (JS)', () => {
  it('should run JavaScript tests', () => {
    expect(true).toBe(true);
  });

  it('should handle global mocks', () => {
    expect(global.localStorage).toBeDefined();
    expect(global.performance).toBeDefined();
    expect(global.crypto).toBeDefined();
  });
});