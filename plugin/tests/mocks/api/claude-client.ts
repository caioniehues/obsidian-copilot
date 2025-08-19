/**
 * Mock Claude API client for testing.
 * Provides predictable responses for Claude API interactions.
 */

export interface ClaudeMessage {
  role: 'user' | 'assistant';
  content: string;
}

export interface ClaudeResponse {
  id: string;
  type: 'message';
  role: 'assistant';
  content: Array<{
    type: 'text';
    text: string;
  }>;
  model: string;
  stop_reason: string;
  stop_sequence: null;
  usage: {
    input_tokens: number;
    output_tokens: number;
  };
}

export class MockClaudeClient {
  private apiKey: string;
  private model: string;
  private responses: Map<string, ClaudeResponse> = new Map();

  constructor(apiKey: string, model = 'claude-3-5-sonnet-20241022') {
    this.apiKey = apiKey;
    this.model = model;
    this.setupDefaultResponses();
  }

  private setupDefaultResponses() {
    // Default response for general queries
    this.responses.set('default', {
      id: 'msg_test_default',
      type: 'message',
      role: 'assistant',
      content: [
        {
          type: 'text',
          text: 'This is a default mocked response from Claude for testing purposes.'
        }
      ],
      model: this.model,
      stop_reason: 'end_turn',
      stop_sequence: null,
      usage: {
        input_tokens: 10,
        output_tokens: 15
      }
    });

    // Response for document synthesis
    this.responses.set('synthesis', {
      id: 'msg_test_synthesis',
      type: 'message',
      role: 'assistant',
      content: [
        {
          type: 'text',
          text: '## Synthesized Content\n\nBased on the provided documents, here is a comprehensive synthesis:\n\n- Key insight 1\n- Key insight 2\n- Key insight 3\n\nThis synthesis demonstrates the integration of multiple sources to create coherent content.'
        }
      ],
      model: this.model,
      stop_reason: 'end_turn',
      stop_sequence: null,
      usage: {
        input_tokens: 150,
        output_tokens: 75
      }
    });

    // Response for analysis tasks
    this.responses.set('analysis', {
      id: 'msg_test_analysis',
      type: 'message',
      role: 'assistant',
      content: [
        {
          type: 'text',
          text: '## Analysis Results\n\n### Patterns Identified\n1. Pattern A: Description\n2. Pattern B: Description\n\n### Recommendations\n- Recommendation 1\n- Recommendation 2\n\n### Conclusion\nThe analysis reveals significant insights that can guide future decisions.'
        }
      ],
      model: this.model,
      stop_reason: 'end_turn',
      stop_sequence: null,
      usage: {
        input_tokens: 200,
        output_tokens: 100
      }
    });
  }

  async createMessage(
    messages: ClaudeMessage[],
    options: {
      max_tokens?: number;
      temperature?: number;
      system?: string;
      stream?: boolean;
    } = {}
  ): Promise<ClaudeResponse> {
    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 100));

    // Determine response type based on content
    const lastMessage = messages[messages.length - 1];
    let responseType = 'default';

    if (lastMessage.content.toLowerCase().includes('synthesis') || 
        lastMessage.content.toLowerCase().includes('synthesize')) {
      responseType = 'synthesis';
    } else if (lastMessage.content.toLowerCase().includes('analysis') || 
               lastMessage.content.toLowerCase().includes('analyze')) {
      responseType = 'analysis';
    }

    const response = this.responses.get(responseType) || this.responses.get('default')!;

    // Simulate token usage based on input
    const inputTokens = messages.reduce((total, msg) => total + Math.floor(msg.content.length / 4), 0);
    const outputTokens = Math.floor(response.content[0].text.length / 4);

    return {
      ...response,
      id: `msg_test_${Date.now()}`,
      usage: {
        input_tokens: inputTokens,
        output_tokens: outputTokens
      }
    };
  }

  async *streamMessage(
    messages: ClaudeMessage[],
    options: {
      max_tokens?: number;
      temperature?: number;
      system?: string;
    } = {}
  ): AsyncGenerator<Partial<ClaudeResponse>, void, unknown> {
    const response = await this.createMessage(messages, options);
    const text = response.content[0].text;
    const words = text.split(' ');

    // Simulate streaming by yielding words progressively
    for (let i = 0; i < words.length; i++) {
      await new Promise(resolve => setTimeout(resolve, 50)); // Simulate network delay
      
      yield {
        id: response.id,
        type: 'message',
        role: 'assistant',
        content: [
          {
            type: 'text',
            text: words.slice(0, i + 1).join(' ')
          }
        ]
      };
    }

    // Final complete response
    yield response;
  }

  // Add custom response for specific test scenarios
  addCustomResponse(trigger: string, response: ClaudeResponse) {
    this.responses.set(trigger, response);
  }

  // Simulate API errors
  simulateError(errorType: 'rate_limit' | 'invalid_key' | 'server_error' = 'server_error') {
    const errors = {
      rate_limit: { status: 429, message: 'Rate limit exceeded' },
      invalid_key: { status: 401, message: 'Invalid API key' },
      server_error: { status: 500, message: 'Internal server error' }
    };

    const error = errors[errorType];
    throw new Error(`Claude API Error ${error.status}: ${error.message}`);
  }

  // Helper to validate API key format
  static isValidApiKey(key: string): boolean {
    return key.startsWith('sk-ant-') && key.length >= 20;
  }

  // Get usage statistics
  getUsageStats() {
    return {
      totalRequests: 0,
      totalTokensUsed: 0,
      averageResponseTime: 100
    };
  }
}

// Default export for easy mocking
export default MockClaudeClient;