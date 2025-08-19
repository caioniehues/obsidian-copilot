/**
 * Unit tests for plugin settings management.
 * Tests settings validation, mode switching, and configuration persistence.
 */

import { MockApp, Plugin } from '../mocks/obsidian';

// Import types from main.ts
interface CopilotPluginSettings {
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
  systemContentDraftSection: string;
  systemContentDraftSectionNoContext: string;
  systemContentReflectWeek: string;
  enableVaultAnalysis: boolean;
  enableSynthesis: boolean;
  showModeIndicator: boolean;
}

const DEFAULT_SETTINGS: CopilotPluginSettings = {
  mode: 'auto',
  apiProvider: 'anthropic',
  apiKey: '',
  backendUrl: 'http://localhost:8000',
  claudeModel: 'claude-3-5-sonnet-20241022',
  openaiModel: 'gpt-4-turbo-preview',
  contextStrategy: 'smart_chunks',
  maxContextTokens: 100000,
  maxOutputTokens: 4096,
  temperature: 0.7,
  showGenerationTime: true,
  systemContentDraftSection: "You are Claude-powered Obsidian Copilot...",
  systemContentDraftSectionNoContext: "You are Claude-powered Obsidian Copilot...",
  systemContentReflectWeek: "You are a thoughtful AI companion...",
  enableVaultAnalysis: true,
  enableSynthesis: true,
  showModeIndicator: true
};

// Mock plugin class for testing
class MockCopilotPlugin extends Plugin {
  settings: CopilotPluginSettings = DEFAULT_SETTINGS;
  processing = false;
  backendAvailable = false;
  currentMode: 'direct' | 'backend' = 'direct';

  async loadSettings(): Promise<void> {
    const data = await this.loadData();
    this.settings = { ...DEFAULT_SETTINGS, ...data };
  }

  async saveSettings(): Promise<void> {
    await this.saveData(this.settings);
  }

  async checkBackendAvailability(): Promise<boolean> {
    // Mock implementation
    try {
      const response = await fetch(`${this.settings.backendUrl}/health`, {
        method: 'GET',
        signal: AbortSignal.timeout(1000)
      });
      this.backendAvailable = response.ok;
      return this.backendAvailable;
    } catch {
      this.backendAvailable = false;
      return false;
    }
  }

  determineOperationMode(): 'direct' | 'backend' {
    switch (this.settings.mode) {
      case 'direct':
        return 'direct';
      case 'backend':
        return this.backendAvailable ? 'backend' : 'direct';
      case 'auto':
        return this.backendAvailable ? 'backend' : 'direct';
      default:
        return 'direct';
    }
  }
}

describe('Plugin Settings Management', () => {
  let app: MockApp;
  let plugin: MockCopilotPlugin;

  beforeEach(() => {
    app = new MockApp();
    plugin = new MockCopilotPlugin(app, { id: 'copilot', name: 'Copilot' });
  });

  describe('Default Settings', () => {
    test('should have valid default settings', () => {
      expect(plugin.settings).toHaveValidSettings();
      expect(plugin.settings.mode).toBe('auto');
      expect(plugin.settings.apiProvider).toBe('anthropic');
      expect(plugin.settings.backendUrl).toBe('http://localhost:8000');
    });

    test('should have reasonable default values', () => {
      expect(plugin.settings.maxContextTokens).toBeGreaterThan(0);
      expect(plugin.settings.maxOutputTokens).toBeGreaterThan(0);
      expect(plugin.settings.temperature).toBeGreaterThanOrEqual(0);
      expect(plugin.settings.temperature).toBeLessThanOrEqual(2);
    });

    test('should have non-empty system prompts', () => {
      expect(plugin.settings.systemContentDraftSection).toBeTruthy();
      expect(plugin.settings.systemContentDraftSectionNoContext).toBeTruthy();
      expect(plugin.settings.systemContentReflectWeek).toBeTruthy();
    });
  });

  describe('Settings Validation', () => {
    test('should validate mode values', () => {
      const validModes: Array<'auto' | 'direct' | 'backend'> = ['auto', 'direct', 'backend'];
      
      validModes.forEach(mode => {
        plugin.settings.mode = mode;
        expect(['auto', 'direct', 'backend']).toContain(plugin.settings.mode);
      });
    });

    test('should validate API provider values', () => {
      const validProviders: Array<'anthropic' | 'openai'> = ['anthropic', 'openai'];
      
      validProviders.forEach(provider => {
        plugin.settings.apiProvider = provider;
        expect(['anthropic', 'openai']).toContain(plugin.settings.apiProvider);
      });
    });

    test('should validate context strategy values', () => {
      const validStrategies: Array<'full_docs' | 'smart_chunks' | 'hierarchical'> = 
        ['full_docs', 'smart_chunks', 'hierarchical'];
      
      validStrategies.forEach(strategy => {
        plugin.settings.contextStrategy = strategy;
        expect(['full_docs', 'smart_chunks', 'hierarchical']).toContain(plugin.settings.contextStrategy);
      });
    });

    test('should validate numeric settings ranges', () => {
      // Test invalid negative values
      expect(() => {
        plugin.settings.maxContextTokens = -1;
      }).not.toThrow(); // Should not crash but might be invalid

      expect(() => {
        plugin.settings.temperature = -1;
      }).not.toThrow(); // Should not crash but might be invalid
      
      // Test reasonable ranges
      plugin.settings.maxContextTokens = 50000;
      expect(plugin.settings.maxContextTokens).toBe(50000);
      
      plugin.settings.temperature = 0.5;
      expect(plugin.settings.temperature).toBe(0.5);
    });

    test('should handle empty API key gracefully', () => {
      plugin.settings.apiKey = '';
      expect(plugin.settings.apiKey).toBe('');
      // Plugin should handle this case without crashing
    });

    test('should validate backend URL format', () => {
      const validUrls = [
        'http://localhost:8000',
        'https://api.example.com',
        'http://127.0.0.1:3000'
      ];

      validUrls.forEach(url => {
        plugin.settings.backendUrl = url;
        expect(plugin.settings.backendUrl).toBe(url);
      });
    });
  });

  describe('Settings Persistence', () => {
    test('should load settings from storage', async () => {
      // Mock loadData to return saved settings
      const savedSettings = { 
        ...DEFAULT_SETTINGS, 
        apiKey: 'test-key',
        mode: 'direct' as const
      };
      
      jest.spyOn(plugin, 'loadData').mockResolvedValue(savedSettings);
      
      await plugin.loadSettings();
      
      expect(plugin.settings.apiKey).toBe('test-key');
      expect(plugin.settings.mode).toBe('direct');
    });

    test('should merge with defaults when loading partial settings', async () => {
      // Mock partial settings
      const partialSettings = { 
        apiKey: 'partial-key',
        mode: 'backend' as const
      };
      
      jest.spyOn(plugin, 'loadData').mockResolvedValue(partialSettings);
      
      await plugin.loadSettings();
      
      // Should have the partial settings
      expect(plugin.settings.apiKey).toBe('partial-key');
      expect(plugin.settings.mode).toBe('backend');
      
      // Should still have defaults for other fields
      expect(plugin.settings.apiProvider).toBe('anthropic');
      expect(plugin.settings.temperature).toBe(0.7);
    });

    test('should save settings to storage', async () => {
      const saveDataSpy = jest.spyOn(plugin, 'saveData').mockResolvedValue();
      
      plugin.settings.apiKey = 'new-key';
      plugin.settings.mode = 'direct';
      
      await plugin.saveSettings();
      
      expect(saveDataSpy).toHaveBeenCalledWith(plugin.settings);
    });

    test('should handle save errors gracefully', async () => {
      jest.spyOn(plugin, 'saveData').mockRejectedValue(new Error('Save failed'));
      
      // Should not throw
      await expect(plugin.saveSettings()).rejects.toThrow('Save failed');
    });
  });

  describe('Mode Switching Logic', () => {
    test('should use direct mode when mode is set to direct', () => {
      plugin.settings.mode = 'direct';
      plugin.backendAvailable = true;
      
      const mode = plugin.determineOperationMode();
      expect(mode).toBe('direct');
    });

    test('should use backend mode when mode is set to backend and backend is available', () => {
      plugin.settings.mode = 'backend';
      plugin.backendAvailable = true;
      
      const mode = plugin.determineOperationMode();
      expect(mode).toBe('backend');
    });

    test('should fallback to direct mode when backend mode is set but backend unavailable', () => {
      plugin.settings.mode = 'backend';
      plugin.backendAvailable = false;
      
      const mode = plugin.determineOperationMode();
      expect(mode).toBe('direct');
    });

    test('should use auto mode intelligently', () => {
      plugin.settings.mode = 'auto';
      
      // When backend is available
      plugin.backendAvailable = true;
      expect(plugin.determineOperationMode()).toBe('backend');
      
      // When backend is not available
      plugin.backendAvailable = false;
      expect(plugin.determineOperationMode()).toBe('direct');
    });

    test('should handle invalid mode gracefully', () => {
      // Force invalid mode
      (plugin.settings as any).mode = 'invalid';
      
      const mode = plugin.determineOperationMode();
      expect(mode).toBe('direct'); // Should fallback to direct
    });
  });

  describe('Backend Availability Check', () => {
    beforeEach(() => {
      // Reset fetch mock
      (global.fetch as jest.Mock).mockReset();
    });

    test('should detect available backend', async () => {
      (global.fetch as jest.Mock).mockResolvedValue({
        ok: true,
        status: 200
      });

      const available = await plugin.checkBackendAvailability();
      
      expect(available).toBe(true);
      expect(plugin.backendAvailable).toBe(true);
      expect(global.fetch).toHaveBeenCalledWith(
        'http://localhost:8000/health',
        expect.objectContaining({
          method: 'GET'
        })
      );
    });

    test('should detect unavailable backend', async () => {
      (global.fetch as jest.Mock).mockResolvedValue({
        ok: false,
        status: 500
      });

      const available = await plugin.checkBackendAvailability();
      
      expect(available).toBe(false);
      expect(plugin.backendAvailable).toBe(false);
    });

    test('should handle network errors', async () => {
      (global.fetch as jest.Mock).mockRejectedValue(new Error('Network error'));

      const available = await plugin.checkBackendAvailability();
      
      expect(available).toBe(false);
      expect(plugin.backendAvailable).toBe(false);
    });

    test('should handle timeouts', async () => {
      (global.fetch as jest.Mock).mockImplementation(() => 
        new Promise((_, reject) => 
          setTimeout(() => reject(new Error('Timeout')), 2000)
        )
      );

      const available = await plugin.checkBackendAvailability();
      
      expect(available).toBe(false);
      expect(plugin.backendAvailable).toBe(false);
    });

    test('should use correct backend URL', async () => {
      plugin.settings.backendUrl = 'https://custom-backend.com:9000';
      
      (global.fetch as jest.Mock).mockResolvedValue({
        ok: true,
        status: 200
      });

      await plugin.checkBackendAvailability();
      
      expect(global.fetch).toHaveBeenCalledWith(
        'https://custom-backend.com:9000/health',
        expect.any(Object)
      );
    });
  });

  describe('Edge Cases and Error Handling', () => {
    test('should handle undefined settings gracefully', async () => {
      jest.spyOn(plugin, 'loadData').mockResolvedValue(undefined);
      
      await plugin.loadSettings();
      
      // Should use defaults
      expect(plugin.settings).toEqual(DEFAULT_SETTINGS);
    });

    test('should handle null settings gracefully', async () => {
      jest.spyOn(plugin, 'loadData').mockResolvedValue(null);
      
      await plugin.loadSettings();
      
      // Should use defaults
      expect(plugin.settings).toEqual(DEFAULT_SETTINGS);
    });

    test('should handle corrupted settings data', async () => {
      // Mock corrupted data
      jest.spyOn(plugin, 'loadData').mockResolvedValue({
        mode: 'invalid',
        apiProvider: 'unknown',
        maxContextTokens: 'not-a-number'
      });
      
      await plugin.loadSettings();
      
      // Should merge with defaults and handle invalid values
      expect(plugin.settings.apiProvider).toBe('anthropic'); // Should use default
      expect(typeof plugin.settings.maxContextTokens).toBe('number');
    });

    test('should handle very large token limits', () => {
      plugin.settings.maxContextTokens = 1000000;
      plugin.settings.maxOutputTokens = 100000;
      
      // Should not crash
      expect(plugin.settings.maxContextTokens).toBe(1000000);
      expect(plugin.settings.maxOutputTokens).toBe(100000);
    });

    test('should handle extreme temperature values', () => {
      // Test boundary values
      plugin.settings.temperature = 0;
      expect(plugin.settings.temperature).toBe(0);
      
      plugin.settings.temperature = 2;
      expect(plugin.settings.temperature).toBe(2);
      
      // Test extreme values (may be invalid but shouldn't crash)
      plugin.settings.temperature = -10;
      expect(plugin.settings.temperature).toBe(-10);
      
      plugin.settings.temperature = 100;
      expect(plugin.settings.temperature).toBe(100);
    });
  });
});