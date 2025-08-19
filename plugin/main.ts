/**
 * Claude Chat Plugin - Simplified Local CLI Integration
 * Provides chat interface with local Claude Code CLI
 */

import { App, Plugin, PluginSettingTab, Setting, Notice, WorkspaceLeaf, ItemView } from 'obsidian';
import { ClaudeCLIService, CLIOptions, StreamResponse } from './src/claude-cli-service';

// Simplified settings interface for local Claude CLI only
interface ClaudeChatSettings {
	sessionTimeout: number;
	maxHistorySize: number;
	showPerformanceMetrics: boolean;
	vaultIntegration: boolean;
	allowedTools: string[];
	autoDetectCLI: boolean;
}

const DEFAULT_SETTINGS: ClaudeChatSettings = {
	sessionTimeout: 30000,
	maxHistorySize: 100,
	showPerformanceMetrics: true,
	vaultIntegration: true,
	allowedTools: ['read', 'search'],
	autoDetectCLI: true
};

interface ChatMessage {
	type: 'user' | 'assistant' | 'system';
	content: string;
	timestamp: Date;
}

export class ClaudeChatPlugin extends Plugin {
	settings: ClaudeChatSettings;
	private cliService: ClaudeCLIService;
	cliAvailable = false;
	chatHistory: ChatMessage[] = [];
	currentSessionId: string | null = null;

	async onload() {
		// Load settings
		await this.loadSettings();

		// Initialize Claude CLI service
		this.cliService = new ClaudeCLIService();

		// Check CLI availability
		if (this.settings.autoDetectCLI) {
			this.cliAvailable = await this.cliService.checkCLIAvailability();
			
			if (!this.cliAvailable) {
				new Notice('Claude CLI not found. Please install Claude Code for full functionality.');
			}
		}

		// Register commands
		this.addCommand({
			id: 'open-chat',
			name: 'Open Chat Panel',
			callback: () => this.openChatPanel()
		});

		this.addCommand({
			id: 'new-chat-session',
			name: 'Start New Chat Session',
			callback: () => this.startNewSession()
		});

		this.addCommand({
			id: 'export-chat',
			name: 'Export Chat to Note',
			callback: () => this.exportChatToNote()
		});

		// Add settings tab
		this.addSettingTab(new ClaudeChatSettingTab(this.app, this));

		// Register chat view
		this.registerView('claude-chat', (leaf) => new ChatView(leaf, this));

		// Start with new session
		this.startNewSession();
	}

	async onunload() {
		// Cleanup CLI service
		if (this.cliService) {
			this.cliService.cleanup();
		}
	}

	async loadSettings() {
		this.settings = Object.assign({}, DEFAULT_SETTINGS, await this.loadData());
	}

	async saveSettings() {
		await this.saveData(this.settings);
	}

	// Session Management
	generateSessionId(): string {
		return `chat-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
	}

	startNewSession() {
		this.currentSessionId = this.generateSessionId();
		this.chatHistory = [];
		
		// Notify active chat views
		this.app.workspace.getLeavesOfType('claude-chat').forEach(leaf => {
			(leaf.view as ChatView).onNewSession();
		});
	}

	// Chat Panel Management
	async openChatPanel() {
		const existingLeaf = this.app.workspace.getLeavesOfType('claude-chat')[0];
		
		if (existingLeaf) {
			this.app.workspace.revealLeaf(existingLeaf);
			(existingLeaf.view as ChatView).focus();
		} else {
			const leaf = this.app.workspace.getLeaf('split', 'vertical');
			await leaf.setViewState({
				type: 'claude-chat',
				active: true
			});
		}
	}

	// Message Handling
	async sendMessage(message: string): Promise<void> {
		if (!this.cliAvailable) {
			this.createNotice('Claude CLI is not available. Please install Claude Code.', 'error');
			return;
		}

		try {
			// Add user message to history
			const userMessage: ChatMessage = {
				type: 'user',
				content: message,
				timestamp: new Date()
			};
			this.addToHistory(userMessage);

			// Prepare CLI options
			const options: CLIOptions = {
				message: message,
				sessionId: this.currentSessionId || undefined,
				streaming: true,
				timeout: this.settings.sessionTimeout
			};

			// Add vault integration if enabled
			if (this.settings.vaultIntegration) {
				options.vaultPath = (this.app.vault.adapter as any).path?.resolve?.('.') || '/mock/vault';
				options.allowedTools = this.settings.allowedTools;
			}

			let assistantContent = '';
			const startTime = Date.now();

			// Start chat with streaming response
			await this.cliService.startChat(options, (response: StreamResponse) => {
				this.handleStreamResponse(response, (content) => {
					assistantContent += content;
				});
			});

			// Add complete assistant response to history
			if (assistantContent) {
				const assistantMessage: ChatMessage = {
					type: 'assistant',
					content: assistantContent,
					timestamp: new Date()
				};
				this.addToHistory(assistantMessage);
			}

			// Track performance if enabled
			if (this.settings.showPerformanceMetrics) {
				const responseTime = Date.now() - startTime;
				console.log(`Claude response time: ${responseTime}ms`);
			}

		} catch (error) {
			console.error('Failed to send message:', error);
			this.createNotice(
				'Failed to communicate with Claude CLI. Please ensure Claude Code is installed.',
				'error'
			);
		}
	}

	private handleStreamResponse(response: StreamResponse, onContent: (content: string) => void) {
		switch (response.type) {
			case 'content':
				if (response.content) {
					onContent(response.content);
					
					// Update active chat views in real-time
					this.app.workspace.getLeavesOfType('claude-chat').forEach(leaf => {
						(leaf.view as ChatView).appendStreamingContent(response.content!);
					});
				}
				break;
			
			case 'end':
				// Update active chat views that streaming is complete
				this.app.workspace.getLeavesOfType('claude-chat').forEach(leaf => {
					(leaf.view as ChatView).onStreamingComplete();
				});
				break;
			
			case 'error':
				console.error('Claude CLI error:', response.error);
				this.createNotice(`Claude error: ${response.error}`, 'error');
				break;
		}
	}

	private addToHistory(message: ChatMessage) {
		this.chatHistory.push(message);
		
		// Limit history size
		if (this.chatHistory.length > this.settings.maxHistorySize) {
			this.chatHistory = this.chatHistory.slice(-this.settings.maxHistorySize);
		}

		// Update active chat views
		this.app.workspace.getLeavesOfType('claude-chat').forEach(leaf => {
			(leaf.view as ChatView).updateHistory(this.chatHistory);
		});
	}

	// Export functionality
	async exportChatToNote() {
		if (this.chatHistory.length === 0) {
			this.createNotice('No chat history to export.', 'warning');
			return;
		}

		const timestamp = new Date().toISOString().split('T')[0];
		const filename = `Chat Export ${timestamp}.md`;
		
		let content = `# Chat Export - ${new Date().toLocaleString()}\n\n`;
		
		this.chatHistory.forEach((message, index) => {
			const role = message.type === 'user' ? '👤 User' : '🤖 Claude';
			content += `## ${role} (${message.timestamp.toLocaleTimeString()})\n\n${message.content}\n\n`;
		});

		try {
			const file = await this.app.vault.create(filename, content);
			this.createNotice(`Chat exported to ${filename}`, 'success');
			
			// Open the exported file
			const leaf = this.app.workspace.getLeaf();
			await leaf.openFile(file);
		} catch (error) {
			console.error('Failed to export chat:', error);
			this.createNotice('Failed to export chat.', 'error');
		}
	}

	// Utility methods
	createNotice(message: string, type: 'info' | 'success' | 'warning' | 'error' = 'info') {
		new Notice(message);
	}

	getPerformanceMetrics() {
		return this.cliService.getPerformanceMetrics();
	}

	// Test helper methods
	async executeCommand(commandId: string) {
		const command = (this as any).commands[commandId];
		if (command && command.callback) {
			await command.callback();
		}
	}
}

// Chat View Component
class ChatView extends ItemView {
	private plugin: ClaudeChatPlugin;

	constructor(leaf: WorkspaceLeaf, plugin: ClaudeChatPlugin) {
		super(leaf);
		this.plugin = plugin;
	}

	getViewType(): string {
		return 'claude-chat';
	}

	getDisplayText(): string {
		return 'Claude Chat';
	}

	async onOpen() {
		// Initialize chat UI when view opens
		const container = this.containerEl.children[1];
		container.empty();
		
		// Create basic chat interface
		const chatContainer = container.createEl('div', { cls: 'claude-chat-container' });
		chatContainer.createEl('h3', { text: 'Claude Chat', cls: 'chat-header' });
		
		// Messages area
		const messagesArea = chatContainer.createEl('div', { cls: 'chat-messages' });
		messagesArea.createEl('p', { text: 'Chat interface will be implemented here', cls: 'placeholder' });
		
		// Input area
		const inputArea = chatContainer.createEl('div', { cls: 'chat-input' });
		const input = inputArea.createEl('input', { type: 'text', placeholder: 'Type a message...', cls: 'message-input' });
		const sendButton = inputArea.createEl('button', { text: 'Send', cls: 'send-button' });
		
		sendButton.addEventListener('click', () => {
			const message = input.value.trim();
			if (message) {
				this.plugin.sendMessage(message);
				input.value = '';
			}
		});

		input.addEventListener('keypress', (e) => {
			if (e.key === 'Enter') {
				sendButton.click();
			}
		});
	}

	async onClose() {
		// Cleanup when view closes
	}

	focus() {
		// Focus the input field
		const input = this.containerEl.querySelector('.message-input') as HTMLInputElement;
		if (input) {
			input.focus();
		}
	}

	onNewSession() {
		// Handle new session in UI
		const messagesArea = this.containerEl.querySelector('.chat-messages');
		if (messagesArea) {
			messagesArea.empty();
			messagesArea.createEl('p', { text: 'New chat session started', cls: 'session-notice' });
		}
	}

	appendStreamingContent(content: string) {
		// Append streaming content to UI
		const messagesArea = this.containerEl.querySelector('.chat-messages');
		if (messagesArea) {
			const lastMessage = messagesArea.querySelector('.message.assistant:last-child .content') as HTMLElement;
			if (lastMessage) {
				lastMessage.textContent += content;
			} else {
				// Create new assistant message
				const messageDiv = messagesArea.createEl('div', { cls: 'message assistant' });
				messageDiv.createEl('span', { cls: 'role', text: '🤖 Claude: ' });
				messageDiv.createEl('span', { cls: 'content', text: content });
			}
		}
	}

	onStreamingComplete() {
		// Handle streaming completion in UI
		const messagesArea = this.containerEl.querySelector('.chat-messages');
		if (messagesArea) {
			messagesArea.scrollTop = messagesArea.scrollHeight;
		}
	}

	updateHistory(history: ChatMessage[]) {
		// Update chat history in UI
		const messagesArea = this.containerEl.querySelector('.chat-messages');
		if (messagesArea) {
			messagesArea.empty();
			
			history.forEach(message => {
				const messageDiv = messagesArea.createEl('div', { cls: `message ${message.type}` });
				const roleIcon = message.type === 'user' ? '👤' : '🤖';
				messageDiv.createEl('span', { cls: 'role', text: `${roleIcon} ${message.type === 'user' ? 'You' : 'Claude'}: ` });
				messageDiv.createEl('span', { cls: 'content', text: message.content });
				messageDiv.createEl('span', { cls: 'timestamp', text: message.timestamp.toLocaleTimeString() });
			});
			
			messagesArea.scrollTop = messagesArea.scrollHeight;
		}
	}
}

// Settings Tab
class ClaudeChatSettingTab extends PluginSettingTab {
	plugin: ClaudeChatPlugin;

	constructor(app: App, plugin: ClaudeChatPlugin) {
		super(app, plugin);
		this.plugin = plugin;
	}

	display(): void {
		const { containerEl } = this;
		containerEl.empty();
		containerEl.createEl('h2', { text: 'Claude Chat Settings' });

		// CLI Settings
		containerEl.createEl('h3', { text: 'Claude CLI Configuration' });

		new Setting(containerEl)
			.setName('Auto-detect Claude CLI')
			.setDesc('Automatically check if Claude CLI is available on startup')
			.addToggle(toggle => toggle
				.setValue(this.plugin.settings.autoDetectCLI)
				.onChange(async (value) => {
					this.plugin.settings.autoDetectCLI = value;
					await this.plugin.saveSettings();
				}));

		new Setting(containerEl)
			.setName('Session timeout')
			.setDesc('Maximum time to wait for Claude CLI response (milliseconds)')
			.addText(text => text
				.setPlaceholder('30000')
				.setValue(this.plugin.settings.sessionTimeout.toString())
				.onChange(async (value) => {
					const timeout = parseInt(value);
					if (!isNaN(timeout) && timeout > 0) {
						this.plugin.settings.sessionTimeout = timeout;
						await this.plugin.saveSettings();
					}
				}));

		// Vault Integration
		containerEl.createEl('h3', { text: 'Vault Integration' });

		new Setting(containerEl)
			.setName('Enable vault integration')
			.setDesc('Allow Claude to access and analyze your vault content')
			.addToggle(toggle => toggle
				.setValue(this.plugin.settings.vaultIntegration)
				.onChange(async (value) => {
					this.plugin.settings.vaultIntegration = value;
					await this.plugin.saveSettings();
				}));

		new Setting(containerEl)
			.setName('Allowed tools')
			.setDesc('Comma-separated list of tools Claude can use (e.g., read,search,write)')
			.addText(text => text
				.setPlaceholder('read,search')
				.setValue(this.plugin.settings.allowedTools.join(','))
				.onChange(async (value) => {
					this.plugin.settings.allowedTools = value.split(',').map(tool => tool.trim());
					await this.plugin.saveSettings();
				}));

		// Chat Settings
		containerEl.createEl('h3', { text: 'Chat Configuration' });

		new Setting(containerEl)
			.setName('Max history size')
			.setDesc('Maximum number of messages to keep in chat history')
			.addText(text => text
				.setPlaceholder('100')
				.setValue(this.plugin.settings.maxHistorySize.toString())
				.onChange(async (value) => {
					const size = parseInt(value);
					if (!isNaN(size) && size > 0) {
						this.plugin.settings.maxHistorySize = size;
						await this.plugin.saveSettings();
					}
				}));

		new Setting(containerEl)
			.setName('Show performance metrics')
			.setDesc('Display response times and performance information in console')
			.addToggle(toggle => toggle
				.setValue(this.plugin.settings.showPerformanceMetrics)
				.onChange(async (value) => {
					this.plugin.settings.showPerformanceMetrics = value;
					await this.plugin.saveSettings();
				}));

		// Status Information
		containerEl.createEl('h3', { text: 'Status' });

		const statusEl = containerEl.createEl('div', { cls: 'claude-chat-status' });
		const cliStatus = this.plugin.cliAvailable ? '✅ Available' : '❌ Not Found';
		statusEl.createEl('p', { text: `Claude CLI: ${cliStatus}` });

		if (this.plugin.settings.showPerformanceMetrics && this.plugin.cliAvailable) {
			const metrics = this.plugin.getPerformanceMetrics();
			statusEl.createEl('p', { text: `Last Response Time: ${metrics.lastResponseTime}ms` });
			statusEl.createEl('p', { text: `Success Rate: ${metrics.successCount}/${metrics.successCount + metrics.errorCount}` });
		}
	}
}

export default ClaudeChatPlugin;