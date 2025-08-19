/** @type {import('jest').Config} */
module.exports = {
  preset: 'ts-jest/presets/default',
  testEnvironment: 'jsdom',
  extensionsToTreatAsEsm: ['.ts'],
  roots: ['<rootDir>/tests', '<rootDir>'],
  testMatch: [
    '**/tests/**/*.test.ts',
    '**/tests/**/*.test.js',
    '**/__tests__/**/*.test.ts',
    '**/__tests__/**/*.test.js'
  ],
  
  // Enhanced transform configuration
  transform: {
    '^.+\\.ts$': ['ts-jest', {
      tsconfig: 'tsconfig.json',
      isolatedModules: true,
      useESM: false
    }]
  },
  
  // Comprehensive coverage collection
  collectCoverageFrom: [
    'main.ts',
    'spinner.ts',
    'src/**/*.ts',
    '!**/node_modules/**',
    '!**/tests/**',
    '!**/mocks/**',
    '!**/fixtures/**',
    '!**/*.d.ts',
    '!**/*.config.ts',
    '!**/types/**'
  ],
  
  // Coverage thresholds for quality gates
  coverageThreshold: {
    global: {
      branches: 85,
      functions: 90,
      lines: 90,
      statements: 90
    },
    './main.ts': {
      branches: 95,
      functions: 95,
      lines: 95,
      statements: 95
    }
  },
  
  coverageDirectory: 'coverage',
  coverageReporters: ['text', 'text-summary', 'lcov', 'html', 'json', 'clover'],
  
  // Setup and teardown
  globalSetup: '<rootDir>/tests/global-setup.ts',
  globalTeardown: '<rootDir>/tests/global-teardown.ts',
  
  moduleFileExtensions: ['ts', 'js', 'json', 'node'],
  
  // Enhanced test configuration
  testTimeout: 15000,
  clearMocks: true,
  restoreMocks: true,
  resetMocks: true,
  
  // Parallel execution for performance
  maxWorkers: '50%',
  
  // Module mapping for comprehensive mocking
  moduleNameMapper: {
    // Obsidian API mock
    '^obsidian$': '<rootDir>/tests/mocks/obsidian.ts',
    
    // Style imports
    '\\.(css|less|scss|sass)$': 'identity-obj-proxy',
    
    // Asset imports
    '\\.(jpg|jpeg|png|gif|svg)$': '<rootDir>/tests/mocks/file-mock.ts',
    
    // API client mocks - adjusted for actual structure
    '^@/api/(.*)$': '<rootDir>/tests/mocks/api/$1',
    
    // Main plugin files
    '^@/(.*)$': '<rootDir>/$1'
  },
  
  // Test environment options
  testEnvironmentOptions: {
    url: 'http://localhost:3000'
  },
  
  // Watch configuration for development
  watchPathIgnorePatterns: [
    '<rootDir>/node_modules/',
    '<rootDir>/coverage/',
    '<rootDir>/dist/',
    '<rootDir>/build/'
  ],
  
  // Performance and memory management
  workerIdleMemoryLimit: '1GB',
  
  
  // Reporter configuration
  reporters: [
    'default',
    ['jest-html-reporters', {
      publicPath: './coverage/html-report',
      filename: 'report.html',
      expand: true
    }],
    ['jest-junit', {
      outputDirectory: './coverage',
      outputName: 'junit.xml'
    }]
  ],
  
  // Error handling
  bail: false,
  verbose: true,
  
  // Transform ignore patterns for node_modules
  transformIgnorePatterns: [
    'node_modules/(?!(.*\\.mjs$|@testing-library|msw))'
  ]
};