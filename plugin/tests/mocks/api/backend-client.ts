/**
 * Mock backend client for testing plugin-backend communication.
 * Simulates the FastAPI backend responses and behaviors.
 */

export interface QueryRequest {
  query: string;
  context_strategy?: 'full_docs' | 'smart_chunks' | 'hierarchical';
  system_prompt?: string;
  temperature?: number;
  max_tokens?: number;
  model?: string;
}

export interface QueryResponse {
  response: string;
  retrieved_docs: Array<{
    title: string;
    content: string;
    score: number;
    path: string;
  }>;
  processing_time: number;
  model_used: string;
  mode: 'direct' | 'backend';
}

export interface HealthResponse {
  status: 'healthy' | 'unhealthy';
  timestamp: string;
  version: string;
  services: {
    opensearch: boolean;
    redis: boolean;
    agents: boolean;
  };
}

export interface VaultAnalysisRequest {
  focus_areas: string[];
  analysis_depth: 'quick' | 'comprehensive';
  include_metrics: boolean;
}

export interface VaultAnalysisResponse {
  patterns: Array<{
    type: string;
    description: string;
    confidence: number;
    examples: string[];
  }>;
  gaps: Array<{
    area: string;
    description: string;
    suggestions: string[];
  }>;
  connections: Array<{
    from: string;
    to: string;
    strength: number;
    type: string;
  }>;
  metrics: {
    total_docs: number;
    avg_doc_length: number;
    topic_diversity: number;
    connection_density: number;
  };
  processing_time: number;
}

export class MockBackendClient {
  private baseUrl: string;
  private isAvailable: boolean = true;
  private latency: number = 100; // ms

  constructor(baseUrl = 'http://localhost:8000') {
    this.baseUrl = baseUrl;
  }

  // Health check endpoint
  async checkHealth(): Promise<HealthResponse> {
    await this.simulateLatency();
    
    if (!this.isAvailable) {
      throw new Error('Backend service unavailable');
    }

    return {
      status: 'healthy',
      timestamp: new Date().toISOString(),
      version: '1.0.0',
      services: {
        opensearch: true,
        redis: true,
        agents: true
      }
    };
  }

  // Main query endpoint
  async query(request: QueryRequest): Promise<QueryResponse> {
    await this.simulateLatency(200); // Queries take longer

    if (!this.isAvailable) {
      throw new Error('Backend service unavailable');
    }

    // Simulate different responses based on query content
    const response = this.generateResponse(request);
    
    return {
      response: response.text,
      retrieved_docs: response.docs,
      processing_time: this.latency / 1000,
      model_used: request.model || 'claude-3-5-sonnet-20241022',
      mode: 'backend'
    };
  }

  // Vault analysis endpoint
  async analyzeVault(request: VaultAnalysisRequest): Promise<VaultAnalysisResponse> {
    await this.simulateLatency(1000); // Analysis takes longer

    if (!this.isAvailable) {
      throw new Error('Backend service unavailable');
    }

    return {
      patterns: [
        {
          type: 'recurring_themes',
          description: 'Machine learning and AI concepts appear frequently',
          confidence: 0.89,
          examples: ['neural networks', 'deep learning', 'AI applications']
        },
        {
          type: 'documentation_style',
          description: 'Consistent use of markdown headers and code blocks',
          confidence: 0.95,
          examples: ['## Headers', '```code blocks```', '- List items']
        }
      ],
      gaps: [
        {
          area: 'practical_examples',
          description: 'Theoretical concepts lack practical implementation examples',
          suggestions: [
            'Add code examples for each concept',
            'Include real-world use cases',
            'Create tutorial-style documentation'
          ]
        }
      ],
      connections: [
        {
          from: 'Machine Learning Basics',
          to: 'Neural Networks',
          strength: 0.87,
          type: 'conceptual'
        },
        {
          from: 'Python Programming',
          to: 'Data Science',
          strength: 0.73,
          type: 'tooling'
        }
      ],
      metrics: {
        total_docs: 42,
        avg_doc_length: 1250,
        topic_diversity: 0.76,
        connection_density: 0.34
      },
      processing_time: this.latency / 1000
    };
  }

  // Weekly reflection endpoint
  async generateWeeklyReflection(): Promise<QueryResponse> {
    await this.simulateLatency(500);

    if (!this.isAvailable) {
      throw new Error('Backend service unavailable');
    }

    return {
      response: `## Weekly Reflection\n\n### Key Themes This Week\n- Learning and growth in AI/ML concepts\n- Documentation and knowledge organization\n- Tool integration and workflow optimization\n\n### Notable Insights\n- The importance of structured note-taking\n- Connections between theoretical and practical knowledge\n- Progress in understanding complex topics\n\n### Looking Forward\n- Continue building on established patterns\n- Explore new connections between ideas\n- Focus on practical application of concepts`,
      retrieved_docs: [
        {
          title: 'This Week in Learning',
          content: 'Summary of weekly learning activities and insights',
          score: 0.95,
          path: 'reflections/weekly/current.md'
        }
      ],
      processing_time: this.latency / 1000,
      model_used: 'claude-3-5-sonnet-20241022',
      mode: 'backend'
    };
  }

  // Agent management endpoints
  async getAgentStatus() {
    await this.simulateLatency();
    
    return {
      agents: [
        {
          id: 'vault-analyzer',
          status: 'active',
          current_tasks: 2,
          max_tasks: 5,
          last_activity: new Date().toISOString()
        },
        {
          id: 'synthesis-assistant',
          status: 'active',
          current_tasks: 1,
          max_tasks: 3,
          last_activity: new Date().toISOString()
        },
        {
          id: 'context-optimizer',
          status: 'active',
          current_tasks: 0,
          max_tasks: 4,
          last_activity: new Date().toISOString()
        }
      ],
      total_active_tasks: 3,
      system_load: 0.45
    };
  }

  // Utility methods for testing
  setAvailability(available: boolean) {
    this.isAvailable = available;
  }

  setLatency(ms: number) {
    this.latency = ms;
  }

  private async simulateLatency(customLatency?: number) {
    const delay = customLatency || this.latency;
    await new Promise(resolve => setTimeout(resolve, delay));
  }

  private generateResponse(request: QueryRequest) {
    const query = request.query.toLowerCase();
    
    // Generate contextual responses based on query content
    if (query.includes('machine learning') || query.includes('ml')) {
      return {
        text: `## Machine Learning Overview\n\nMachine learning is a subset of artificial intelligence that enables computers to learn and improve from experience without being explicitly programmed. Key concepts include:\n\n- **Supervised Learning**: Training with labeled data\n- **Unsupervised Learning**: Finding patterns in unlabeled data\n- **Reinforcement Learning**: Learning through interaction and feedback\n\nBased on your notes, you've been exploring neural networks and deep learning applications.`,
        docs: [
          {
            title: 'ML Fundamentals',
            content: 'Introduction to machine learning concepts and applications',
            score: 0.92,
            path: 'ml/fundamentals.md'
          },
          {
            title: 'Neural Networks Basics',
            content: 'Understanding the building blocks of neural networks',
            score: 0.88,
            path: 'ml/neural-networks.md'
          }
        ]
      };
    } 
    
    if (query.includes('programming') || query.includes('code')) {
      return {
        text: `## Programming Best Practices\n\nBased on your vault content, here are key programming insights:\n\n- **Clean Code**: Write code that is easy to read and maintain\n- **Testing**: Implement comprehensive test coverage\n- **Documentation**: Keep code well-documented\n- **Version Control**: Use Git effectively for collaboration\n\nYour notes show consistent focus on code quality and best practices.`,
        docs: [
          {
            title: 'Clean Code Principles',
            content: 'Guidelines for writing maintainable code',
            score: 0.89,
            path: 'programming/clean-code.md'
          },
          {
            title: 'Testing Strategies',
            content: 'Approaches to comprehensive software testing',
            score: 0.85,
            path: 'programming/testing.md'
          }
        ]
      };
    }

    // Default response for general queries
    return {
      text: `Based on your vault content, here's a synthesized response to your query about "${request.query}":\n\nI've analyzed your notes and found relevant connections that can help provide context for this topic. The information suggests several key insights that align with your learning patterns and knowledge base.\n\nWould you like me to elaborate on any specific aspect or explore related concepts from your notes?`,
      docs: [
        {
          title: 'General Knowledge Base',
          content: 'Relevant content from your vault related to the query',
          score: 0.75,
          path: 'general/knowledge-base.md'
        }
      ]
    };
  }
}

export default MockBackendClient;