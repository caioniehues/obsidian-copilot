/**
 * Claude CLI Service - Interface for local Claude Code integration
 * Provides subprocess management and streaming response parsing
 */

import { spawn, ChildProcess } from 'child_process';
import { EventEmitter } from 'events';

export interface CLIOptions {
  message: string;
  sessionId?: string;
  vaultPath?: string;
  streaming?: boolean;
  allowedTools?: string[];
  timeout?: number;
}

export interface StreamResponse {
  type: 'content' | 'error' | 'end' | 'tool_use' | 'metadata';
  content?: string;
  error?: string;
  metadata?: any;
}

export interface CLICommand {
  command: string;
  args: string[];
}

export interface PerformanceMetrics {
  lastResponseTime: number;
  successCount: number;
  errorCount: number;
  averageResponseTime: number;
}

export class ClaudeCLIService extends EventEmitter {
  private currentProcess: ChildProcess | null = null;
  private isProcessing = false;
  private partialData = '';
  private performanceMetrics: PerformanceMetrics = {
    lastResponseTime: 0,
    successCount: 0,
    errorCount: 0,
    averageResponseTime: 0
  };
  private responseTimes: number[] = [];

  constructor() {
    super();
  }

  /**
   * Check if Claude CLI is available on the system
   */
  async checkCLIAvailability(): Promise<boolean> {
    return new Promise((resolve) => {
      const process = spawn('claude', ['--version']);
      
      process.on('close', (code) => {
        resolve(code === 0);
      });
      
      process.on('error', () => {
        resolve(false);
      });
      
      // Timeout after 5 seconds
      setTimeout(() => {
        process.kill();
        resolve(false);
      }, 5000);
    });
  }

  /**
   * Build Claude CLI command with options
   */
  buildCLICommand(options: CLIOptions): CLICommand {
    const isWindows = process.platform === 'win32';
    const command = isWindows ? 'claude.exe' : 'claude';
    const args: string[] = [];

    // Add session ID if provided
    if (options.sessionId) {
      args.push('--session-id', options.sessionId);
    }

    // Add vault directory if provided
    if (options.vaultPath) {
      args.push('--add-dir', options.vaultPath);
    }

    // Configure streaming output
    if (options.streaming !== false) {
      args.push('--output-format', 'stream-json');
    }

    // Add tool permissions
    if (options.allowedTools && options.allowedTools.length > 0) {
      args.push('--allowedTools', options.allowedTools.join(','));
    }

    // Add the message last
    args.push(options.message);

    return { command, args };
  }

  /**
   * Parse streaming JSON response from Claude CLI
   */
  parseStreamResponse(data: string): StreamResponse[] {
    const lines = data.split('\n').filter(line => line.trim());
    const responses: StreamResponse[] = [];

    for (const line of lines) {
      try {
        const parsed = JSON.parse(line);
        responses.push(parsed);
      } catch (error) {
        // Skip malformed JSON lines
        continue;
      }
    }

    return responses;
  }

  /**
   * Handle partial stream chunks and return parsed responses
   */
  handleStreamChunk(chunk: string): StreamResponse[] {
    this.partialData += chunk;
    const lines = this.partialData.split('\n');
    
    // Keep the last incomplete line for next chunk
    this.partialData = lines.pop() || '';
    
    const responses: StreamResponse[] = [];
    for (const line of lines) {
      if (line.trim()) {
        try {
          const parsed = JSON.parse(line);
          responses.push(parsed);
        } catch (error) {
          // Skip malformed JSON
          continue;
        }
      }
    }

    return responses;
  }

  /**
   * Start chat session with Claude CLI
   */
  async startChat(
    options: CLIOptions,
    onResponse: (response: StreamResponse) => void
  ): Promise<void> {
    if (this.isProcessing) {
      throw new Error('Claude CLI is currently busy');
    }

    this.isProcessing = true;
    const startTime = Date.now();

    return new Promise((resolve, reject) => {
      const command = this.buildCLICommand(options);
      
      try {
        this.currentProcess = spawn(command.command, command.args);
      } catch (error) {
        this.isProcessing = false;
        reject(error);
        return;
      }

      let hasEnded = false;
      let errorOutput = '';

      // Set up timeout
      const timeout = options.timeout || 30000; // 30 second default
      const timeoutId = setTimeout(() => {
        if (this.currentProcess && !hasEnded) {
          this.currentProcess.kill('SIGTERM');
          this.cleanup();
          reject(new Error('Claude CLI process timed out'));
        }
      }, timeout);

      // Handle stdout (streaming responses)
      this.currentProcess.stdout?.on('data', (data: Buffer) => {
        const chunk = data.toString();
        const responses = this.handleStreamChunk(chunk);
        
        responses.forEach(response => {
          onResponse(response);
          if (response.type === 'end') {
            hasEnded = true;
          }
        });
      });

      // Handle stderr (errors)
      this.currentProcess.stderr?.on('data', (data: Buffer) => {
        errorOutput += data.toString();
      });

      // Handle process completion
      this.currentProcess.on('close', (code) => {
        clearTimeout(timeoutId);
        const responseTime = Date.now() - startTime;
        
        this.updatePerformanceMetrics(responseTime, code === 0);
        this.cleanup();

        if (code === 0) {
          resolve();
        } else {
          reject(new Error(`Claude CLI process failed with exit code: ${code}${errorOutput ? '\n' + errorOutput : ''}`));
        }
      });

      // Handle process errors
      this.currentProcess.on('error', (error) => {
        clearTimeout(timeoutId);
        this.updatePerformanceMetrics(Date.now() - startTime, false);
        this.cleanup();
        reject(error);
      });
    });
  }

  /**
   * Update performance metrics
   */
  private updatePerformanceMetrics(responseTime: number, success: boolean): void {
    this.performanceMetrics.lastResponseTime = responseTime;
    
    if (success) {
      this.performanceMetrics.successCount++;
    } else {
      this.performanceMetrics.errorCount++;
    }

    this.responseTimes.push(responseTime);
    
    // Keep only last 100 response times for average calculation
    if (this.responseTimes.length > 100) {
      this.responseTimes.shift();
    }

    this.performanceMetrics.averageResponseTime = 
      this.responseTimes.reduce((sum, time) => sum + time, 0) / this.responseTimes.length;
  }

  /**
   * Get performance metrics
   */
  getPerformanceMetrics(): PerformanceMetrics {
    return { ...this.performanceMetrics };
  }

  /**
   * Cleanup resources
   */
  cleanup(): void {
    if (this.currentProcess) {
      this.currentProcess.removeAllListeners();
      if (!this.currentProcess.killed) {
        this.currentProcess.kill();
      }
      this.currentProcess = null;
    }
    
    this.isProcessing = false;
    this.partialData = '';
  }

  /**
   * Terminate current session
   */
  terminate(): void {
    if (this.currentProcess && !this.currentProcess.killed) {
      this.currentProcess.kill('SIGTERM');
    }
    this.cleanup();
  }
}