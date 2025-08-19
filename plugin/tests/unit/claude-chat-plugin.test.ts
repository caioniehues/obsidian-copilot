/**
 * Tests for simplified Claude Chat Plugin
 * Tests the main plugin class without backend/API complexity
 */

import { App, Editor, MarkdownView, Plugin, TFile } from 'obsidian';
import { ClaudeChatPlugin } from '../../main';
import { ClaudeCLIService } from '../../src/claude-cli-service';

// Mock Obsidian API
jest.mock('obsidian');

// Mock ClaudeCLIService
jest.mock('../../src/claude-cli-service');

describe('ClaudeChatPlugin', () => {
  let app: App;
  let plugin: ClaudeChatPlugin;
  let mockCLIService: jest.Mocked<ClaudeCLIService>;

  beforeEach(() => {
    // Create mock app
    app = {
      vault: {
        getAbstractFileByPath: jest.fn(),
        modify: jest.fn(),
        create: jest.fn(),
        adapter: {
          path: { resolve: jest.fn().mockReturnValue('/mock/vault/path') }
        }
      },
      workspace: {
        getLeavesOfType: jest.fn().mockReturnValue([]),
        getLeaf: jest.fn().mockReturnValue({
          openFile: jest.fn()
        })
      }
    } as any;

    // Mock CLI service
    mockCLIService = {
      checkCLIAvailability: jest.fn(),
      startChat: jest.fn(),
      cleanup: jest.fn(),
      getPerformanceMetrics: jest.fn().mockReturnValue({
        lastResponseTime: 100,
        successCount: 1,
        errorCount: 0,
        averageResponseTime: 100
      })
    } as any;

    (ClaudeCLIService as any as jest.Mock).mockImplementation(() => mockCLIService);

    // Create plugin instance
    plugin = new ClaudeChatPlugin(app, {
      id: 'claude-chat-plugin',
      name: 'Claude Chat',
      version: '1.0.0',
      minAppVersion: '0.15.0',
      description: 'Chat with local Claude CLI',
      author: 'Test Author',
      isDesktopOnly: false
    });
    
    // Ensure app property is properly set
    (plugin as any).app = app;
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  describe('Plugin Initialization', () => {
    it('should initialize with default settings', async () => {
      await plugin.onload();

      expect(plugin.settings).toEqual({
        sessionTimeout: 30000,
        maxHistorySize: 100,
        showPerformanceMetrics: true,
        vaultIntegration: true,
        allowedTools: ['read', 'search'],
        autoDetectCLI: true
      });
    });

    it('should check Claude CLI availability on load', async () => {
      mockCLIService.checkCLIAvailability.mockResolvedValue(true);

      await plugin.onload();

      expect(mockCLIService.checkCLIAvailability).toHaveBeenCalled();
      expect(plugin.cliAvailable).toBe(true);
    });

    it('should handle missing Claude CLI gracefully', async () => {
      mockCLIService.checkCLIAvailability.mockResolvedValue(false);

      await plugin.onload();

      expect(plugin.cliAvailable).toBe(false);
    });
  });

  describe('Chat Commands', () => {
    beforeEach(async () => {
      mockCLIService.checkCLIAvailability.mockResolvedValue(true);
      await plugin.onload();
    });

    it('should register chat commands on load', async () => {
      const addCommandSpy = jest.spyOn(plugin, 'addCommand');

      await plugin.onload();

      expect(addCommandSpy).toHaveBeenCalledWith({
        id: 'open-chat',
        name: 'Open Chat Panel',
        callback: expect.any(Function)
      });

      expect(addCommandSpy).toHaveBeenCalledWith({
        id: 'new-chat-session',
        name: 'Start New Chat Session',
        callback: expect.any(Function)
      });
    });

    it('should open chat panel when command executed', async () => {
      const openChatPanelSpy = jest.spyOn(plugin, 'openChatPanel');

      await plugin.executeCommand('open-chat');

      expect(openChatPanelSpy).toHaveBeenCalled();
    });

    it('should start new chat session when command executed', async () => {
      const startNewSessionSpy = jest.spyOn(plugin, 'startNewSession');

      await plugin.executeCommand('new-chat-session');

      expect(startNewSessionSpy).toHaveBeenCalled();
    });
  });

  describe('Chat Panel Management', () => {
    beforeEach(async () => {
      mockCLIService.checkCLIAvailability.mockResolvedValue(true);
      await plugin.onload();
    });

    it('should create chat panel if not exists', async () => {
      const mockLeaf = {
        setViewState: jest.fn(),
        view: null
      };
      app.workspace.getLeavesOfType = jest.fn().mockReturnValue([]);
      app.workspace.getLeaf = jest.fn().mockReturnValue(mockLeaf);

      await plugin.openChatPanel();

      expect(app.workspace.getLeaf).toHaveBeenCalledWith('split', 'vertical');
      expect(mockLeaf.setViewState).toHaveBeenCalledWith({
        type: 'claude-chat',
        active: true
      });
    });

    it('should activate existing chat panel', async () => {
      const mockView = { focus: jest.fn() };
      const mockLeaf = { view: mockView };
      app.workspace.getLeavesOfType = jest.fn().mockReturnValue([mockLeaf]);

      await plugin.openChatPanel();

      expect(mockView.focus).toHaveBeenCalled();
    });
  });

  describe('Chat Session Management', () => {
    beforeEach(async () => {
      mockCLIService.checkCLIAvailability.mockResolvedValue(true);
      await plugin.onload();
    });

    it('should generate unique session IDs', () => {
      const sessionId1 = plugin.generateSessionId();
      const sessionId2 = plugin.generateSessionId();

      expect(sessionId1).not.toBe(sessionId2);
      expect(sessionId1).toMatch(/^chat-\d+-/);
      expect(sessionId2).toMatch(/^chat-\d+-/);
    });

    it('should start new session and reset history', () => {
      plugin.chatHistory = ['previous', 'messages'];

      plugin.startNewSession();

      expect(plugin.currentSessionId).toMatch(/^chat-\d+-/);
      expect(plugin.chatHistory).toEqual([]);
    });

    it('should maintain session state across messages', async () => {
      const sessionId = plugin.generateSessionId();
      plugin.currentSessionId = sessionId;

      mockCLIService.startChat.mockResolvedValue(undefined);

      await plugin.sendMessage('Hello Claude');

      expect(mockCLIService.startChat).toHaveBeenCalledWith(
        expect.objectContaining({
          sessionId: sessionId,
          message: 'Hello Claude'
        }),
        expect.any(Function)
      );
    });
  });

  describe('Vault Integration', () => {
    beforeEach(async () => {
      mockCLIService.checkCLIAvailability.mockResolvedValue(true);
      await plugin.onload();
    });

    it('should include vault path when vault integration enabled', async () => {
      plugin.settings.vaultIntegration = true;
      mockCLIService.startChat.mockResolvedValue(undefined);

      await plugin.sendMessage('Analyze my notes');

      expect(mockCLIService.startChat).toHaveBeenCalledWith(
        expect.objectContaining({
          vaultPath: '/mock/vault/path',
          allowedTools: ['read', 'search']
        }),
        expect.any(Function)
      );
    });

    it('should exclude vault path when vault integration disabled', async () => {
      plugin.settings.vaultIntegration = false;
      mockCLIService.startChat.mockResolvedValue(undefined);

      await plugin.sendMessage('General question');

      expect(mockCLIService.startChat).toHaveBeenCalledWith(
        expect.objectContaining({
          message: 'General question'
        }),
        expect.any(Function)
      );

      const callArgs = mockCLIService.startChat.mock.calls[0][0];
      expect(callArgs).not.toHaveProperty('vaultPath');
    });
  });

  describe('Message History', () => {
    beforeEach(async () => {
      mockCLIService.checkCLIAvailability.mockResolvedValue(true);
      await plugin.onload();
    });

    it('should add messages to history', async () => {
      mockCLIService.startChat.mockImplementation((options, callback) => {
        callback({ type: 'content', content: 'Hello!' });
        callback({ type: 'end' });
        return Promise.resolve();
      });

      await plugin.sendMessage('Hello Claude');

      expect(plugin.chatHistory).toHaveLength(2);
      expect(plugin.chatHistory[0]).toEqual({
        type: 'user',
        content: 'Hello Claude',
        timestamp: expect.any(Date)
      });
      expect(plugin.chatHistory[1]).toEqual({
        type: 'assistant',
        content: 'Hello!',
        timestamp: expect.any(Date)
      });
    });

    it('should limit history size based on settings', async () => {
      plugin.settings.maxHistorySize = 2;
      
      // Fill history beyond limit
      plugin.chatHistory = [
        { type: 'user', content: 'Message 1', timestamp: new Date() } as any,
        { type: 'assistant', content: 'Response 1', timestamp: new Date() } as any,
        { type: 'user', content: 'Message 2', timestamp: new Date() } as any
      ];

      mockCLIService.startChat.mockImplementation((options, callback) => {
        callback({ type: 'content', content: 'Response 2' });
        callback({ type: 'end' });
        return Promise.resolve();
      });

      await plugin.sendMessage('Message 3');

      expect(plugin.chatHistory).toHaveLength(2);
      expect(plugin.chatHistory[0].content).toBe('Message 3');
      expect(plugin.chatHistory[1].content).toBe('Response 2');
    });
  });

  describe('Error Handling', () => {
    beforeEach(async () => {
      mockCLIService.checkCLIAvailability.mockResolvedValue(true);
      await plugin.onload();
    });

    it('should handle CLI service errors gracefully', async () => {
      const errorSpy = jest.spyOn(console, 'error').mockImplementation();
      mockCLIService.startChat.mockRejectedValue(new Error('CLI failed'));

      await plugin.sendMessage('This will fail');

      expect(errorSpy).toHaveBeenCalledWith(
        'Failed to send message:',
        expect.any(Error)
      );
      
      errorSpy.mockRestore();
    });

    it('should show user-friendly error messages', async () => {
      const noticeSpy = jest.fn();
      (plugin as any).createNotice = noticeSpy;

      mockCLIService.startChat.mockRejectedValue(new Error('Claude CLI not found'));

      await plugin.sendMessage('Test message');

      expect(noticeSpy).toHaveBeenCalledWith(
        'Failed to communicate with Claude CLI. Please ensure Claude Code is installed.',
        'error'
      );
    });

    it('should handle missing CLI gracefully', async () => {
      plugin.cliAvailable = false;
      const noticeSpy = jest.fn();
      (plugin as any).createNotice = noticeSpy;

      await plugin.sendMessage('Test message');

      expect(noticeSpy).toHaveBeenCalledWith(
        'Claude CLI is not available. Please install Claude Code.',
        'error'
      );
    });
  });

  describe('Performance Monitoring', () => {
    beforeEach(async () => {
      mockCLIService.checkCLIAvailability.mockResolvedValue(true);
      plugin.settings.showPerformanceMetrics = true;
      await plugin.onload();
    });

    it('should track message timing when enabled', async () => {
      mockCLIService.startChat.mockImplementation((options, callback) => {
        setTimeout(() => {
          callback({ type: 'content', content: 'Response' });
          callback({ type: 'end' });
        }, 100);
        return Promise.resolve();
      });

      const startTime = Date.now();
      await plugin.sendMessage('Test timing');
      const endTime = Date.now();

      const metrics = plugin.getPerformanceMetrics();
      expect(metrics.lastResponseTime).toBeGreaterThan(0);
      expect(metrics.lastResponseTime).toBeLessThan(endTime - startTime + 50);
    });

    it('should not track timing when disabled', async () => {
      plugin.settings.showPerformanceMetrics = false;
      mockCLIService.startChat.mockResolvedValue(undefined);

      await plugin.sendMessage('Test message');

      expect(mockCLIService.getPerformanceMetrics).not.toHaveBeenCalled();
    });
  });

  describe('Cleanup', () => {
    it('should cleanup CLI service on unload', async () => {
      await plugin.onload();
      await plugin.onunload();

      expect(mockCLIService.cleanup).toHaveBeenCalled();
    });
  });
});

// Type definitions for the simplified plugin interface
interface ChatMessage {
  type: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: Date;
}

interface SimplifiedSettings {
  sessionTimeout: number;
  maxHistorySize: number;
  showPerformanceMetrics: boolean;
  vaultIntegration: boolean;
  allowedTools: string[];
  autoDetectCLI: boolean;
}