/**
 * Comprehensive tests for Claude CLI Service
 * Following TDD approach - tests written before implementation
 */

import { ClaudeCLIService, CLIOptions, StreamResponse } from '../../src/claude-cli-service';
import { spawn, ChildProcess } from 'child_process';
import { EventEmitter } from 'events';

// Mock child_process
jest.mock('child_process');
const mockSpawn = spawn as jest.MockedFunction<typeof spawn>;

// Mock EventEmitter for process simulation
class MockChildProcess extends EventEmitter {
  stdout = new EventEmitter();
  stderr = new EventEmitter();
  stdin = {
    write: jest.fn(),
    end: jest.fn()
  };
  kill = jest.fn();
  pid = 12345;
}

describe('ClaudeCLIService', () => {
  let service: ClaudeCLIService;
  let mockProcess: MockChildProcess;

  beforeEach(() => {
    service = new ClaudeCLIService();
    mockProcess = new MockChildProcess();
    mockSpawn.mockReturnValue(mockProcess as any);
    jest.clearAllMocks();
  });

  afterEach(() => {
    service.cleanup();
  });

  describe('CLI Health Check', () => {
    it('should detect Claude CLI availability', async () => {
      // Simulate successful claude --version command
      setTimeout(() => {
        mockProcess.stdout.emit('data', 'claude version 1.2.3\n');
        mockProcess.emit('close', 0);
      }, 10);

      const isAvailable = await service.checkCLIAvailability();
      
      expect(mockSpawn).toHaveBeenCalledWith('claude', ['--version']);
      expect(isAvailable).toBe(true);
    });

    it('should handle missing Claude CLI', async () => {
      setTimeout(() => {
        mockProcess.emit('error', new Error('ENOENT: command not found'));
      }, 10);

      const isAvailable = await service.checkCLIAvailability();
      
      expect(isAvailable).toBe(false);
    });

    it('should handle Claude CLI with non-zero exit code', async () => {
      setTimeout(() => {
        mockProcess.stderr.emit('data', 'command not recognized\n');
        mockProcess.emit('close', 1);
      }, 10);

      const isAvailable = await service.checkCLIAvailability();
      
      expect(isAvailable).toBe(false);
    });
  });

  describe('Command Construction', () => {
    it('should build basic chat command', () => {
      const options: CLIOptions = {
        message: 'Hello Claude!',
        sessionId: 'test-session'
      };

      const command = service.buildCLICommand(options);
      
      expect(command.args).toContain('--session-id');
      expect(command.args).toContain('test-session');
    });

    it('should include vault directory when provided', () => {
      const options: CLIOptions = {
        message: 'Analyze my notes',
        vaultPath: '/path/to/vault'
      };

      const command = service.buildCLICommand(options);
      
      expect(command.args).toContain('--add-dir');
      expect(command.args).toContain('/path/to/vault');
    });

    it('should configure streaming output format', () => {
      const options: CLIOptions = {
        message: 'Stream response please',
        streaming: true
      };

      const command = service.buildCLICommand(options);
      
      expect(command.args).toContain('--output-format');
      expect(command.args).toContain('stream-json');
    });

    it('should handle tool permissions', () => {
      const options: CLIOptions = {
        message: 'Help with coding',
        allowedTools: ['bash', 'edit']
      };

      const command = service.buildCLICommand(options);
      
      expect(command.args).toContain('--allowedTools');
      expect(command.args).toContain('bash,edit');
    });
  });

  describe('Streaming Response Parsing', () => {
    it('should parse stream-json format correctly', () => {
      const streamData = `{"type":"content","content":"Hello "}\n{"type":"content","content":"world!"}\n{"type":"end"}`;
      
      const parsed = service.parseStreamResponse(streamData);
      
      expect(parsed.length).toBe(3);
      expect(parsed[0]).toEqual({ type: 'content', content: 'Hello ' });
      expect(parsed[1]).toEqual({ type: 'content', content: 'world!' });
      expect(parsed[2]).toEqual({ type: 'end' });
    });

    it('should handle malformed JSON gracefully', () => {
      const streamData = `{"type":"content","content":"Valid"}\n{invalid json}\n{"type":"end"}`;
      
      const parsed = service.parseStreamResponse(streamData);
      
      expect(parsed.length).toBe(2);
      expect(parsed[0]).toEqual({ type: 'content', content: 'Valid' });
      expect(parsed[1]).toEqual({ type: 'end' });
    });

    it('should accumulate partial JSON lines', () => {
      const chunk1 = `{"type":"content","con`;
      const chunk2 = `tent":"Hello world"}\n`;
      
      // Simulate partial data chunks
      service.handleStreamChunk(chunk1);
      const parsed = service.handleStreamChunk(chunk2);
      
      expect(parsed.length).toBe(1);
      expect(parsed[0]).toEqual({ type: 'content', content: 'Hello world' });
    });
  });

  describe('Chat Session Management', () => {
    it('should start new chat session successfully', async () => {
      const options: CLIOptions = {
        message: 'Start new conversation',
        sessionId: 'new-session'
      };

      setTimeout(() => {
        mockProcess.stdout.emit('data', '{"type":"content","content":"Hello! How can I help?"}\n');
        mockProcess.stdout.emit('data', '{"type":"end"}\n');
        mockProcess.emit('close', 0);
      }, 10);

      const responses: StreamResponse[] = [];
      await service.startChat(options, (response) => {
        responses.push(response);
      });

      expect(responses.length).toBe(2);
      expect(responses[0].content).toBe('Hello! How can I help?');
      expect(responses[1].type).toBe('end');
    });

    it('should handle chat session errors', async () => {
      const options: CLIOptions = {
        message: 'This will fail',
        sessionId: 'error-session'
      };

      setTimeout(() => {
        mockProcess.stderr.emit('data', 'Error: Invalid API key\n');
        mockProcess.emit('close', 1);
      }, 10);

      await expect(service.startChat(options, () => {}))
        .rejects.toThrow('Claude CLI process failed with exit code: 1');
    });

    it('should terminate long-running sessions', async () => {
      const options: CLIOptions = {
        message: 'Long conversation',
        timeout: 100 // 100ms timeout for test
      };

      setTimeout(() => {
        // Don't emit close event to simulate hanging process
        mockProcess.stdout.emit('data', '{"type":"content","content":"Starting..."}\n');
      }, 10);

      await expect(service.startChat(options, () => {}))
        .rejects.toThrow('Claude CLI process timed out');
      
      expect(mockProcess.kill).toHaveBeenCalledWith('SIGTERM');
    });
  });

  describe('Cross-Platform Compatibility', () => {
    it('should use correct command on Windows', () => {
      Object.defineProperty(process, 'platform', {
        value: 'win32',
        configurable: true
      });

      const options: CLIOptions = { message: 'Test Windows' };
      const command = service.buildCLICommand(options);
      
      expect(command.command).toBe('claude.exe');
    });

    it('should use correct command on Unix systems', () => {
      Object.defineProperty(process, 'platform', {
        value: 'darwin',
        configurable: true
      });

      const options: CLIOptions = { message: 'Test macOS' };
      const command = service.buildCLICommand(options);
      
      expect(command.command).toBe('claude');
    });
  });

  describe('Error Handling', () => {
    it('should handle process spawn errors', async () => {
      mockSpawn.mockImplementation(() => {
        const proc = new MockChildProcess();
        setTimeout(() => proc.emit('error', new Error('Spawn failed')), 10);
        return proc as any;
      });

      const options: CLIOptions = { message: 'This will spawn error' };
      
      await expect(service.startChat(options, () => {}))
        .rejects.toThrow('Spawn failed');
    });

    it('should cleanup resources on error', async () => {
      const cleanupSpy = jest.spyOn(service, 'cleanup');
      
      setTimeout(() => {
        mockProcess.emit('error', new Error('Process error'));
      }, 10);

      const options: CLIOptions = { message: 'Error test' };
      
      try {
        await service.startChat(options, () => {});
      } catch (error) {
        // Expected to throw
      }

      expect(cleanupSpy).toHaveBeenCalled();
    });

    it('should handle multiple simultaneous requests', async () => {
      const options1: CLIOptions = { message: 'Request 1' };
      const options2: CLIOptions = { message: 'Request 2' };

      // Second request should be queued/rejected since CLI is busy
      const promise1 = service.startChat(options1, () => {});
      
      await expect(service.startChat(options2, () => {}))
        .rejects.toThrow('Claude CLI is currently busy');
    });
  });

  describe('Performance Monitoring', () => {
    it('should track response time metrics', async () => {
      const options: CLIOptions = { message: 'Performance test' };
      
      setTimeout(() => {
        mockProcess.stdout.emit('data', '{"type":"content","content":"Response"}\n');
        mockProcess.stdout.emit('data', '{"type":"end"}\n');
        mockProcess.emit('close', 0);
      }, 50); // 50ms delay

      const startTime = Date.now();
      await service.startChat(options, () => {});
      const endTime = Date.now();

      const metrics = service.getPerformanceMetrics();
      expect(metrics.lastResponseTime).toBeGreaterThan(40);
      expect(metrics.lastResponseTime).toBeLessThan(100);
    });

    it('should track success/failure rates', async () => {
      // Simulate successful request
      setTimeout(() => {
        mockProcess.emit('close', 0);
      }, 10);

      await service.startChat({ message: 'Success test' }, () => {});

      const metrics = service.getPerformanceMetrics();
      expect(metrics.successCount).toBe(1);
      expect(metrics.errorCount).toBe(0);
    });
  });
});

// Interface definitions for type safety
interface CLICommand {
  command: string;
  args: string[];
}

interface PerformanceMetrics {
  lastResponseTime: number;
  successCount: number;
  errorCount: number;
}