/**
 * Test data factory for generating consistent test data across all tests.
 * Provides builders for creating complex test scenarios and edge cases.
 */

import { MockTFile } from '../mocks/obsidian';

export interface TestVaultDocument {
  path: string;
  title: string;
  content: string;
  tags: string[];
  created: Date;
  modified: Date;
}

export interface TestSettings {
  mode: 'auto' | 'direct' | 'backend';
  apiProvider: 'anthropic' | 'openai';
  apiKey: string;
  backendUrl: string;
  claudeModel: string;
  openaiModel: string;
  contextStrategy: 'full_docs' | 'smart_chunks' | 'hierarchical';
  maxContextTokens: number;
  maxOutputTokens: number;
  temperature: number;
  showGenerationTime: boolean;
  enableVaultAnalysis: boolean;
  enableSynthesis: boolean;
  showModeIndicator: boolean;
}

export interface TestApiResponse {
  success: boolean;
  data?: any;
  error?: string;
  processingTime?: number;
}

export class TestDataFactory {
  
  // Vault document builders
  static createDocument(overrides: Partial<TestVaultDocument> = {}): TestVaultDocument {
    const defaults: TestVaultDocument = {
      path: 'test/document.md',
      title: 'Test Document',
      content: '# Test Document\n\nThis is a test document for unit testing.',
      tags: ['test', 'sample'],
      created: new Date('2024-01-01T00:00:00Z'),
      modified: new Date('2024-01-01T00:00:00Z')
    };

    return { ...defaults, ...overrides };
  }

  static createMachineLearningDocument(): TestVaultDocument {
    return this.createDocument({
      path: 'ml/neural-networks.md',
      title: 'Neural Networks Fundamentals',
      content: `# Neural Networks Fundamentals

## Overview
Neural networks are computing systems inspired by biological neural networks. They consist of interconnected nodes (neurons) that process information.

## Key Concepts
- **Perceptron**: Basic building block
- **Layers**: Input, hidden, and output layers
- **Weights and Biases**: Parameters that control learning
- **Activation Functions**: Determine neuron output

## Applications
- Image recognition
- Natural language processing
- Predictive modeling
- Game playing (e.g., chess, Go)

## Mathematical Foundation
The output of a neuron can be calculated as:
\`\`\`
output = activation_function(sum(weights * inputs) + bias)
\`\`\`

## Training Process
1. Forward propagation
2. Loss calculation
3. Backpropagation
4. Weight updates

## Common Architectures
- Feedforward networks
- Convolutional Neural Networks (CNNs)
- Recurrent Neural Networks (RNNs)
- Transformer networks`,
      tags: ['ml', 'ai', 'neural-networks', 'deep-learning'],
      created: new Date('2024-01-15T10:30:00Z'),
      modified: new Date('2024-01-20T14:45:00Z')
    });
  }

  static createProgrammingDocument(): TestVaultDocument {
    return this.createDocument({
      path: 'programming/clean-code.md',
      title: 'Clean Code Principles',
      content: `# Clean Code Principles

## What is Clean Code?
Clean code is code that is easy to read, understand, and maintain. It follows consistent patterns and expresses intent clearly.

## Core Principles

### 1. Meaningful Names
- Use descriptive and unambiguous names
- Make meaningful distinctions
- Use pronounceable names
- Use searchable names

### 2. Functions
- Functions should be small
- Functions should do one thing
- Use descriptive names
- Prefer fewer arguments

### 3. Comments
- Comments should explain why, not what
- Good code mostly documents itself
- Update comments when code changes
- Remove outdated comments

### 4. Formatting
- Consistent indentation
- Logical grouping of related code
- Reasonable line length
- Vertical spacing for readability

### 5. Error Handling
- Use exceptions rather than return codes
- Write your try-catch-finally statement first
- Provide context with exceptions
- Don't return null

## Code Examples

\`\`\`typescript
// Bad: unclear naming
function calc(x: number, y: number): number {
  return x * y * 0.1;
}

// Good: clear intent
function calculateDiscountAmount(price: number, discountRate: number): number {
  return price * discountRate * 0.1;
}
\`\`\`

## Benefits
- Easier to understand and modify
- Fewer bugs and defects  
- Faster development velocity
- Better team collaboration
- Reduced technical debt`,
      tags: ['programming', 'clean-code', 'best-practices', 'software-engineering'],
      created: new Date('2024-01-10T09:15:00Z'),
      modified: new Date('2024-01-25T16:20:00Z')
    });
  }

  static createProjectDocument(): TestVaultDocument {
    return this.createDocument({
      path: 'projects/obsidian-copilot.md',
      title: 'Obsidian Copilot Project',
      content: `# Obsidian Copilot Project

## Overview
An AI-powered writing assistant for Obsidian that provides contextual suggestions based on vault content.

## Architecture
- **Plugin**: TypeScript-based Obsidian plugin
- **Backend**: Python FastAPI service
- **AI Integration**: Claude and OpenAI APIs
- **Search**: Semantic and keyword search capabilities

## Features
- Contextual content generation
- Vault analysis and insights
- Multiple operation modes (direct, backend, auto)
- Streaming responses
- Agent-based processing

## Technical Stack
- Frontend: TypeScript, Obsidian API
- Backend: Python, FastAPI, OpenSearch
- AI: Claude 3.5 Sonnet, GPT-4
- Testing: Jest, pytest

## Current Status
- ✅ Basic plugin structure
- ✅ Claude API integration  
- ✅ Backend service architecture
- 🚧 Advanced agent features
- 📋 Comprehensive testing suite

## Next Steps
1. Complete agent implementation
2. Add performance monitoring
3. Implement caching layer
4. Create user documentation`,
      tags: ['project', 'obsidian', 'ai', 'copilot', 'development'],
      created: new Date('2024-01-05T08:00:00Z'),
      modified: new Date('2024-01-26T11:30:00Z')
    });
  }

  // Settings builders
  static createSettings(overrides: Partial<TestSettings> = {}): TestSettings {
    const defaults: TestSettings = {
      mode: 'auto',
      apiProvider: 'anthropic',
      apiKey: 'sk-ant-test-key-1234567890abcdef',
      backendUrl: 'http://localhost:8000',
      claudeModel: 'claude-3-5-sonnet-20241022',
      openaiModel: 'gpt-4-turbo-preview',
      contextStrategy: 'smart_chunks',
      maxContextTokens: 100000,
      maxOutputTokens: 4096,
      temperature: 0.7,
      showGenerationTime: true,
      enableVaultAnalysis: true,
      enableSynthesis: true,
      showModeIndicator: true
    };

    return { ...defaults, ...overrides };
  }

  static createDirectModeSettings(): TestSettings {
    return this.createSettings({
      mode: 'direct',
      apiProvider: 'anthropic',
      apiKey: 'sk-ant-direct-test-key'
    });
  }

  static createBackendModeSettings(): TestSettings {
    return this.createSettings({
      mode: 'backend',
      backendUrl: 'https://api.example.com:8000'
    });
  }

  static createOpenAISettings(): TestSettings {
    return this.createSettings({
      apiProvider: 'openai',
      apiKey: 'sk-openai-test-key-1234567890',
      openaiModel: 'gpt-4-turbo-preview'
    });
  }

  // API response builders
  static createApiResponse(overrides: Partial<TestApiResponse> = {}): TestApiResponse {
    const defaults: TestApiResponse = {
      success: true,
      data: { message: 'Test response' },
      processingTime: 0.123
    };

    return { ...defaults, ...overrides };
  }

  static createErrorResponse(message = 'Test error'): TestApiResponse {
    return this.createApiResponse({
      success: false,
      error: message,
      data: undefined
    });
  }

  static createStreamingResponse(): AsyncGenerator<string, void, unknown> {
    const chunks = [
      'This is a',
      ' streaming response',
      ' that simulates',
      ' real-time generation',
      ' from the AI model.'
    ];

    return this.createAsyncGenerator(chunks);
  }

  // File system builders
  static createTFile(path: string, content: string): MockTFile {
    return new MockTFile(path, content);
  }

  static createVaultStructure(): MockTFile[] {
    return [
      this.createTFile('index.md', '# My Vault\n\nWelcome to my knowledge base.'),
      this.createTFile('ml/neural-networks.md', this.createMachineLearningDocument().content),
      this.createTFile('programming/clean-code.md', this.createProgrammingDocument().content),
      this.createTFile('projects/obsidian-copilot.md', this.createProjectDocument().content),
      this.createTFile('daily/2024-01-26.md', '# 2024-01-26\n\n## Daily Notes\n- Working on test infrastructure\n- Implementing TDD practices'),
      this.createTFile('templates/meeting-notes.md', '# Meeting Notes Template\n\n**Date**: \n**Attendees**: \n**Agenda**: \n\n## Discussion\n\n## Action Items\n'),
      this.createTFile('inbox/quick-note.md', 'Random thought about AI applications in education')
    ];
  }

  // Edge case builders
  static createLargeDocument(): TestVaultDocument {
    const longContent = `# Large Document\n\n${'## Section\n\nLorem ipsum dolor sit amet, consectetur adipiscing elit. '.repeat(100)}`;
    
    return this.createDocument({
      path: 'large/big-document.md',
      title: 'Large Test Document',
      content: longContent,
      tags: ['large', 'performance-test']
    });
  }

  static createEmptyDocument(): TestVaultDocument {
    return this.createDocument({
      path: 'empty/empty-document.md',
      title: 'Empty Document',
      content: '',
      tags: []
    });
  }

  static createDocumentWithSpecialCharacters(): TestVaultDocument {
    return this.createDocument({
      path: 'special/special-chars.md',
      title: 'Document with Special Characters',
      content: `# Special Characters Test

This document contains various special characters:
- Unicode: 🚀 💡 🎯
- Mathematical: α β γ Σ ∑ ∫ ∆
- Symbols: © ® ™ § ¶ † ‡
- Accented: café naïve résumé
- Code: \`const x = "hello"; // comment\`
- HTML entities: &lt; &gt; &amp; &quot;
- Markdown: **bold** *italic* ~~strikethrough~~

\`\`\`javascript
// Code block with special chars
const regex = /[^\w\s]/g;
const emoji = "🎉";
\`\`\``,
      tags: ['special', 'unicode', 'testing']
    });
  }

  static createInvalidSettings(): TestSettings {
    return this.createSettings({
      mode: 'invalid' as any,
      apiProvider: 'unknown' as any,
      apiKey: '',
      maxContextTokens: -1,
      temperature: 10
    });
  }

  // Utility methods
  private static async *createAsyncGenerator<T>(items: T[]): AsyncGenerator<T, void, unknown> {
    for (const item of items) {
      await new Promise(resolve => setTimeout(resolve, 50)); // Simulate delay
      yield item;
    }
  }

  // Bulk data generation
  static createMultipleDocuments(count: number): TestVaultDocument[] {
    return Array.from({ length: count }, (_, i) => 
      this.createDocument({
        path: `generated/document-${i + 1}.md`,
        title: `Generated Document ${i + 1}`,
        content: `# Generated Document ${i + 1}\n\nThis is automatically generated test content.`,
        tags: ['generated', `doc-${i + 1}`]
      })
    );
  }

  static createPerformanceTestData() {
    return {
      documents: this.createMultipleDocuments(1000),
      largeDocument: this.createLargeDocument(),
      settings: this.createSettings(),
      apiResponses: Array.from({ length: 100 }, (_, i) => 
        this.createApiResponse({ 
          data: { id: i, message: `Response ${i}` },
          processingTime: Math.random() * 0.5
        })
      )
    };
  }
}

export default TestDataFactory;