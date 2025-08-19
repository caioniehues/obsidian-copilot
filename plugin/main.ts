import { App, Editor, MarkdownView, Plugin, PluginSettingTab, Setting, TFile, Modal, Notice } from 'obsidian';

// Claude-optimized Copilot settings with hybrid mode support
interface CopilotPluginSettings {
	// Mode settings
	mode: 'auto' | 'direct' | 'backend';
	apiProvider: 'anthropic' | 'openai';
	apiKey: string;
	
	// Backend settings
	backendUrl: string;
	
	// Model settings
	claudeModel: string;
	openaiModel: string;
	
	// Shared settings
	contextStrategy: 'full_docs' | 'smart_chunks' | 'hierarchical';
	maxContextTokens: number;
	maxOutputTokens: number;
	temperature: number;
	showGenerationTime: boolean;
	
	// System prompts
	systemContentDraftSection: string;
	systemContentDraftSectionNoContext: string;
	systemContentReflectWeek: string;
	
	// Feature flags
	enableVaultAnalysis: boolean;
	enableSynthesis: boolean;
	showModeIndicator: boolean;
}

const DEFAULT_SETTINGS: CopilotPluginSettings = {
	// Mode settings
	mode: 'auto',
	apiProvider: 'anthropic',
	apiKey: '',
	
	// Backend settings
	backendUrl: 'http://localhost:8000',
	
	// Model settings
	claudeModel: 'claude-3-5-sonnet-20241022',
	openaiModel: 'gpt-4-turbo-preview',
	
	// Shared settings
	contextStrategy: 'smart_chunks',
	maxContextTokens: 100000,
	maxOutputTokens: 4096,
	temperature: 0.7,
	showGenerationTime: true,
	
	// System prompts
	systemContentDraftSection: "You are Claude-powered Obsidian Copilot, an advanced AI assistant that helps writers craft drafts based on their notes.\n\nWith access to a 200K token context window, you can understand entire documents and their relationships. When you reference content from a document, append the sentence with a markdown reference that links to the document's title. For example, if a sentence references context from 'Augmented Language Models.md', it should end with ([source](Augmented%20Language%20Models.md)).",
	systemContentDraftSectionNoContext: "You are Claude-powered Obsidian Copilot, an advanced AI assistant that helps writers craft drafts.\n\nGenerate comprehensive content based on the given section heading, leveraging your extensive knowledge and reasoning capabilities.",
	systemContentReflectWeek: "You are a thoughtful AI companion powered by Claude, helping users reflect on their week with deep insight and empathy. Given their journal entries, provide a thoughtful analysis for each of the following:\n\n* Celebrate what went well\n* Reflect on areas for growth\n* Suggest goals for next week",
	
	// Feature flags
	enableVaultAnalysis: true,
	enableSynthesis: true,
	showModeIndicator: true
}

export default class CopilotPlugin extends Plugin {
	settings: CopilotPluginSettings;
	processing = false;
	backendAvailable = false;
	currentMode: 'direct' | 'backend' = 'direct';

	// Opens a new pane to display the retrieved docs
	async openNewPane(content: string) {
		const filename = 'Retrieved docs.md';
		let file = this.app.vault.getAbstractFileByPath(filename) as TFile;

		if (file) {
			await this.app.vault.modify(file, content);
		} else {
			file = await this.app.vault.create(filename, content);
		}

		// Check if there is already an open pane with the file
		const existingLeaf = this.app.workspace.getLeavesOfType('markdown').find(leaf => leaf.view.file && leaf.view.file.path === file.path);

		if (existingLeaf) {
			// If a pane with the file already exists, just set the content
			(existingLeaf.view as MarkdownView).editor.setValue(content);
		} else {
			// If no pane with the file exists, create a new one
			const leaf = this.app.workspace.getLeaf('split', 'vertical');
			leaf.openFile(file);
		}
	}

	// Backend health check
	async checkBackendAvailability(): Promise<boolean> {
		try {
			const controller = new AbortController();
			const timeoutId = setTimeout(() => controller.abort(), 1000);
			
			const response = await fetch(`${this.settings.backendUrl}/health`, {
				signal: controller.signal
			});
			
			clearTimeout(timeoutId);
			this.backendAvailable = response.ok;
			return response.ok;
		} catch (error) {
			this.backendAvailable = false;
			return false;
		}
	}

	// Determine which mode to use
	async determineMode(): Promise<'direct' | 'backend'> {
		if (this.settings.mode === 'direct') {
			this.currentMode = 'direct';
			return 'direct';
		}
		
		if (this.settings.mode === 'backend') {
			this.currentMode = 'backend';
			return 'backend';
		}
		
		// Auto mode - check backend availability
		const backendAvailable = await this.checkBackendAvailability();
		this.currentMode = backendAvailable ? 'backend' : 'direct';
		return this.currentMode;
	}

	// Direct API methods for standalone operation
	async queryLLM(messages: any[], model: string, temperature: number): Promise<Response> {
		if (this.settings.apiProvider === 'anthropic') {
			return await this.queryAnthropic(messages, model, temperature);
		} else {
			return await this.queryOpenAI(messages, model, temperature);
		}
	}

	async queryAnthropic(messages: any[], model: string, temperature: number): Promise<Response> {
		// Convert OpenAI format messages to Anthropic format
		const anthropicMessages = messages.filter(m => m.role !== 'system').map(m => ({
			role: m.role === 'user' ? 'user' : 'assistant',
			content: m.content
		}));
		
		const systemMessage = messages.find(m => m.role === 'system')?.content || '';
		
		const response = await fetch('https://api.anthropic.com/v1/messages', {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json',
				'x-api-key': this.settings.apiKey,
				'anthropic-version': '2023-06-01'
			},
			body: JSON.stringify({
				model: model || this.settings.claudeModel,
				messages: anthropicMessages,
				system: systemMessage,
				max_tokens: this.settings.maxOutputTokens,
				temperature: temperature || this.settings.temperature,
				stream: true
			})
		});
		
		return response;
	}

	async queryOpenAI(messages: any[], model: string, temperature: number): Promise<Response> {
		const response = await fetch('https://api.openai.com/v1/chat/completions', {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json',
				'Authorization': `Bearer ${this.settings.apiKey}`
			},
			body: JSON.stringify({
				model: model || this.settings.openaiModel,
				messages: messages,
				max_tokens: this.settings.maxOutputTokens,
				temperature: temperature || this.settings.temperature,
				stream: true
			})
		});
		
		return response;
	}

	// Claude generation method
	private async generateWithClaude(query: string, systemPrompt: string): Promise<any> {
		const response = await fetch(
			`${this.settings.backendUrl}/generate`,
			{
				method: 'POST',
				headers: {
					'Content-Type': 'application/json',
				},
				body: JSON.stringify({
					query,
					context_strategy: this.settings.contextStrategy,
					system_prompt: systemPrompt,
					temperature: 0.7,
					model: this.settings.claudeModel,
					max_tokens: 4000,
					max_context_tokens: this.settings.maxContextTokens,
					include_full_docs: this.settings.contextStrategy === 'full_docs'
				})
			}
		);
		
		if (!response.ok) {
			const errorText = await response.text();
			throw new Error(`Claude generation failed: ${response.statusText} - ${errorText}`);
		}
		
		const data = await response.json();
		
		// Show generation time and context info if enabled
		if (this.settings.showGenerationTime) {
			console.log(`Claude generation: ${data.generation_time?.toFixed(2)}s | Context: ${data.context_used} | Tokens: ${data.tokens_used}`);
		}
		
		return data;
	}

	private async generateWithClaudeStreaming(
		query: string,
		systemPrompt: string,
		editor: Editor,
		statusBarItemEl: HTMLElement
	): Promise<void> {
		const response = await fetch(
			`${this.settings.backendUrl}/generate_streaming`,
			{
				method: 'POST',
				headers: {
					'Content-Type': 'application/json',
				},
				body: JSON.stringify({
					query,
					context_strategy: this.settings.contextStrategy,
					system_prompt: systemPrompt,
					temperature: 0.7,
					model: this.settings.claudeModel,
					max_tokens: 4000,
					max_context_tokens: this.settings.maxContextTokens
				})
			}
		);
		
		if (!response.ok) {
			const errorText = await response.text();
			throw new Error(`Claude streaming failed: ${response.statusText} - ${errorText}`);
		}
		
		const reader = response.body?.getReader();
		if (!reader) {
			throw new Error('No response body reader available');
		}
		
		const decoder = new TextDecoder();
		let buffer = '';
		
		while (true) {
			const { value, done } = await reader.read();
			if (done) break;
			
			buffer += decoder.decode(value, { stream: true });
			const lines = buffer.split('\n');
			
			// Process all complete lines
			for (let i = 0; i < lines.length - 1; i++) {
				const line = lines[i].trim();
				if (line.startsWith('data: ')) {
					try {
						const data = JSON.parse(line.slice(6));
						if (data.content) {
							editor.replaceSelection(data.content);
						}
						if (data.done) {
							statusBarItemEl.setText('✅ Claude generation complete!');
						}
					} catch (e) {
						// Ignore parse errors for incomplete JSON
					}
				}
			}
			
			// Keep the last incomplete line in the buffer
			buffer = lines[lines.length - 1];
		}
	}

	async onload() {
		await this.loadSettings();
		
		// Check backend availability on startup
		await this.determineMode();
		console.log(`Obsidian Copilot starting in ${this.currentMode} mode`);

		async function parseStream(reader: any, editor: Editor): Promise<void> {
			let buffer = '';
			const { value, done } = await reader.read();

			if (done) {
				statusBarItemEl.setText('Done with Copilot task!');
				return;
			}

			const decoded = new TextDecoder().decode(value);
			buffer += decoded;
			let start = 0;
			let end = buffer.indexOf('\n');

			while (end !== -1) {
				const message = buffer.slice(start, end);
				start = end + 1;

				try {
					const messageWithoutPrefix = message.replace('data: ', '');
					const json = JSON.parse(messageWithoutPrefix);

					let lastToken = '';

					if (json.choices && json.choices.length > 0 && json.choices[0].delta && json.choices[0].delta.content) {
						let token = json.choices[0].delta.content;

						// If token is a space, append it to last token
						if (token === ' ') {
							lastToken += token;
							token = lastToken;
						} else {
							// Save the last non-space token
							lastToken = token;
						}

						// Replace in the editor
						editor.replaceSelection(token);
					}

				} catch (err) {
					// console.error('Failed to parse JSON: ', err);
				}
				end = buffer.indexOf('\n', start);
			}
			buffer = buffer.slice(start);
			requestAnimationFrame(() => parseStream(reader, editor));
		}

		// This adds a status bar item to the bottom of the app. Does not work on mobile apps.
		const statusBarItemEl = this.addStatusBarItem();
		
		// Update status bar based on current mode
		const updateStatusBar = () => {
			if (this.settings.showModeIndicator) {
				const modeIcon = this.currentMode === 'backend' ? '🚀' : '✨';
				const modeText = this.currentMode === 'backend' ? 'Enhanced' : 'Direct';
				statusBarItemEl.setText(`Copilot: ${modeIcon} ${modeText}`);
			} else {
				statusBarItemEl.setText('Copilot ready');
			}
		};
		
		updateStatusBar();
		
		// Periodically check backend availability in auto mode
		if (this.settings.mode === 'auto') {
			this.registerInterval(
				window.setInterval(async () => {
					const previousMode = this.currentMode;
					await this.determineMode();
					if (previousMode !== this.currentMode) {
						updateStatusBar();
						console.log(`Copilot switched to ${this.currentMode} mode`);
					}
				}, 30000) // Check every 30 seconds
			);
		}

		// Editor command that drafts a section given the section heading and context
		this.addCommand({
			id: 'copilot-draft-section',
			name: 'Draft Section',
			editorCallback: async (editor: Editor, view: MarkdownView) => {
				const selection = editor.getSelection();
				const query = selection.replace(/[^a-z0-9 ]/gi, '');
				statusBarItemEl.setText('🔍 Retrieving context with Claude...');

				try {
					// Retrieve optimized context from the server
					const contextResponse = await fetch(
						`${this.settings.backendUrl}/get_context?` + 
						`query=${encodeURIComponent(query)}&` +
						`strategy=${this.settings.contextStrategy}&` +
						`max_tokens=${this.settings.maxContextTokens}`
					);
					
					if (!contextResponse.ok) {
						console.error('Failed to fetch context', await contextResponse.text());
						statusBarItemEl.setText('❌ Failed to retrieve context');
						return;
					}

					const contextData = await contextResponse.json();
					const { chunks, metadata } = contextData;
					
					// Display retrieved docs
					const retrievedDocs = chunks.map((item: any) => {
						if (item.type === 'full_document') {
							return `📄 [[${item.title}]] (Full Document)\n\n${item.content.substring(0, 500)}...`;
						} else {
							return `[[${item.title}]]\n\n${item.content}`;
						}
					});
					const retrievedDocsDisplay = retrievedDocs.join('\n---\n');
					
					console.log(`Context: ${metadata.strategy} | ${metadata.documents_included.length} docs | ${metadata.tokens_used} tokens`);
					this.openNewPane(retrievedDocsDisplay);

					// Use Claude for generation
					statusBarItemEl.setText('🤖 Claude is thinking...');
					
					// Use simulated streaming for better UX
					editor.replaceSelection(selection + '\n\n');
					await this.generateWithClaudeStreaming(
						query,
						this.settings.systemContentDraftSection,
						editor,
						statusBarItemEl
					);
					
				} catch (error) {
					console.error('Generation error:', error);
					statusBarItemEl.setText('❌ Generation failed');
				}
			}
		});

		// Editor command that drafts a section given the section heading ONLY
		this.addCommand({
			id: 'copilot-draft-section-no-context',
			name: 'Draft Section (no context)',
			editorCallback: async (editor: Editor, view: MarkdownView) => {
				const selection = editor.getSelection();
				const query = selection.replace(/[^a-z0-9 ]/gi, '');
				statusBarItemEl.setText('Running Copilot...');

				// Create user content
				const user_content = `Section heading: ${query}\n\nDraft:`;
				console.log(`USER CONTENT:\n\n${user_content}`);

				// Send messages to OpenAI
				const messages = [
					{ 'role': 'system', 'content': this.settings.systemContentDraftSectionNoContext },
					{ 'role': 'user', 'content': user_content }
				]
				const response = await this.queryLLM(messages, this.settings.model, 0.7);

				if (!response.ok) {
					const errorData = await response.json();
					console.error('An error occurred', errorData);
					statusBarItemEl.setText('ERROR: No response from LLM API');
				} else {
					const reader = response.body?.getReader();
					editor.replaceSelection(selection + '\n\n');

					await parseStream(reader, editor);
				}
			}
		});

		this.addCommand({
			id: 'copilot-reflect-week',
			name: 'Reflect on the week',
			editorCallback: async (editor: Editor, view: MarkdownView) => {
				statusBarItemEl.setText('Running Copilot...');

				// Get the date from the note's title
				const titleDateStr = view.file.basename;
				const date = new Date(titleDateStr);
				console.log(`Date: ${date.toISOString().slice(0, 10)}`);

				let pastContent = '';
				for (let i = 0; i < 7; i++) {
					const dateStr = date.toISOString().slice(0, 10);
					const dailyNote = this.app.vault.getAbstractFileByPath(`daily/${dateStr}.md`);
					console.log(`dateStr: ${dateStr}, dailyNote: ${dailyNote}`);
					if (dailyNote && dailyNote instanceof TFile) {
						const noteContent = await this.app.vault.read(dailyNote);
						console.log(`dateStr: ${dateStr}, dailyNote: ${dailyNote}, noteContent:\n\n${noteContent}`);
						pastContent += `Date: ${dateStr}\n\nJournal entry:\n${noteContent}\n---\n`;
					}
					date.setDate(date.getDate() - 1);
				}
				console.log(`PAST JOURNAL ENTRIES: \n\n${pastContent}`);

				this.openNewPane(pastContent);

				// Create user content
				const user_content = `These are the journal entries for my week:\n${pastContent}\n\nReflection:`;
				console.log(`USER CONTENT:\n\n${user_content}`);

				// Send messages to OpenAI
				const messages = [
					{ 'role': 'system', 'content': this.settings.systemContentReflectWeek },
					{ 'role': 'user', 'content': user_content }
				]
				const response = await this.queryLLM(messages, this.settings.model, 0.7);

				if (!response.ok) {
					const errorData = await response.json();
					console.error('An error occurred', errorData);
					statusBarItemEl.setText('ERROR: No response from LLM API');
				} else {
					const reader = response.body?.getReader();
					editor.replaceSelection('\n');

					await parseStream(reader, editor);
				}
			}
		});

		// Agent OS Commands - Parallel Execution Support
		this.addCommand({
			id: 'agent-analyze-vault',
			name: '🤖 Agent: Analyze Vault',
			editorCallback: async (editor: Editor, view: MarkdownView) => {
				const statusBarItemEl = this.addStatusBarItem();
				statusBarItemEl.setText('🔍 Agent analyzing vault...');

				try {
					const response = await fetch(`${this.settings.backendUrl}/agents/vault-analyze`, {
						method: 'POST',
						headers: { 'Content-Type': 'application/json' }
					});

					if (!response.ok) {
						throw new Error(`Agent analysis failed: ${response.statusText}`);
					}

					const result = await response.json();
					
					// Create comprehensive analysis report
					const analysisReport = this.formatVaultAnalysis(result.analysis);
					editor.replaceSelection(`## 🤖 Vault Analysis Report\n\n${analysisReport}\n\n`);
					
					statusBarItemEl.setText('✅ Vault analysis complete!');
					setTimeout(() => statusBarItemEl.remove(), 3000);

				} catch (error) {
					console.error('Vault analysis error:', error);
					statusBarItemEl.setText('❌ Analysis failed');
					setTimeout(() => statusBarItemEl.remove(), 3000);
				}
			}
		});

		this.addCommand({
			id: 'agent-synthesize',
			name: '🧠 Agent: Synthesize Selection',
			editorCallback: async (editor: Editor, view: MarkdownView) => {
				const selection = editor.getSelection();
				if (!selection) {
					console.log('No text selected for synthesis');
					return;
				}

				const statusBarItemEl = this.addStatusBarItem();
				statusBarItemEl.setText('🧠 Agent synthesizing...');

				try {
					// Parse selected text for note references
					const noteRefs = this.extractNoteReferences(selection);
					
					const response = await fetch(`${this.settings.backendUrl}/agents/synthesize`, {
						method: 'POST',
						headers: { 'Content-Type': 'application/json' },
						body: JSON.stringify({
							note_paths: noteRefs,
							synthesis_type: 'thematic'
						})
					});

					if (!response.ok) {
						throw new Error(`Synthesis failed: ${response.statusText}`);
					}

					const result = await response.json();
					
					// Replace selection with synthesis
					const synthesis = `## 🧠 Agent Synthesis\n\n${result.synthesis_result.synthesis || 'Synthesis not available'}\n\n*Processed ${result.documents_processed} documents*\n\n`;
					editor.replaceSelection(synthesis);
					
					statusBarItemEl.setText('✅ Synthesis complete!');
					setTimeout(() => statusBarItemEl.remove(), 3000);

				} catch (error) {
					console.error('Synthesis error:', error);
					statusBarItemEl.setText('❌ Synthesis failed');
					setTimeout(() => statusBarItemEl.remove(), 3000);
				}
			}
		});

		this.addCommand({
			id: 'agent-optimize-context',
			name: '⚡ Agent: Optimize Performance',
			callback: async () => {
				const statusBarItemEl = this.addStatusBarItem();
				statusBarItemEl.setText('⚡ Agent optimizing...');

				try {
					const response = await fetch(`${this.settings.backendUrl}/agents/optimize-context`, {
						method: 'GET',
						headers: { 'Content-Type': 'application/json' }
					});

					if (!response.ok) {
						throw new Error(`Optimization failed: ${response.statusText}`);
					}

					const result = await response.json();
					
					// Show optimization results in notice
					const optimizationSummary = this.formatOptimizationResult(result.optimization_result);
					new Notice(`⚡ Performance optimized!\n${optimizationSummary}`, 5000);
					
					statusBarItemEl.setText('✅ Optimization complete!');
					setTimeout(() => statusBarItemEl.remove(), 3000);

				} catch (error) {
					console.error('Optimization error:', error);
					statusBarItemEl.setText('❌ Optimization failed');
					setTimeout(() => statusBarItemEl.remove(), 3000);
				}
			}
		});

		this.addCommand({
			id: 'agent-parallel-execute',
			name: '🚀 Agent: Execute Multiple Agents',
			editorCallback: async (editor: Editor, view: MarkdownView) => {
				const statusBarItemEl = this.addStatusBarItem();
				statusBarItemEl.setText('🚀 Executing agents in parallel...');

				try {
					// Execute multiple agents in parallel for maximum performance
					const response = await fetch(`${this.settings.backendUrl}/agents/execute`, {
						method: 'POST',
						headers: { 'Content-Type': 'application/json' },
						body: JSON.stringify({
							agent_names: ['vault-analyzer', 'context-optimizer', 'suggestion-engine'],
							parallel: true,
							context: {
								active_note: view.file?.path || '',
								execution_mode: 'comprehensive'
							}
						})
					});

					if (!response.ok) {
						throw new Error(`Parallel execution failed: ${response.statusText}`);
					}

					const result = await response.json();
					
					// Format results from all agents
					const agentReport = this.formatParallelAgentResults(result);
					editor.replaceSelection(`## 🚀 Multi-Agent Analysis\n\n${agentReport}\n\n`);
					
					statusBarItemEl.setText(`✅ ${result.agents_executed} agents completed in ${result.total_execution_time.toFixed(2)}s!`);
					setTimeout(() => statusBarItemEl.remove(), 5000);

				} catch (error) {
					console.error('Parallel execution error:', error);
					statusBarItemEl.setText('❌ Execution failed');
					setTimeout(() => statusBarItemEl.remove(), 3000);
				}
			}
		});

		this.addCommand({
			id: 'agent-status',
			name: '📊 Agent: Show Status',
			callback: async () => {
				const statusBarItemEl = this.addStatusBarItem();
				statusBarItemEl.setText('📊 Checking agent status...');

				try {
					const response = await fetch(`${this.settings.backendUrl}/agents/status`, {
						method: 'GET',
						headers: { 'Content-Type': 'application/json' }
					});

					if (!response.ok) {
						throw new Error(`Status check failed: ${response.statusText}`);
					}

					const result = await response.json();
					
					// Show agent status in modal
					this.showAgentStatusModal(result.agents);
					
					statusBarItemEl.setText('✅ Status retrieved!');
					setTimeout(() => statusBarItemEl.remove(), 2000);

				} catch (error) {
					console.error('Status check error:', error);
					new Notice('❌ Failed to get agent status', 3000);
					statusBarItemEl.remove();
				}
			}
		});


		// This adds a settings tab so the user can configure various aspects of the plugin
		this.addSettingTab(new CopilotSettingTab(this.app, this));

		// If the plugin hooks up any global DOM events (on parts of the app that doesn't belong to this plugin)
		// Using this function will automatically remove the event listener when this plugin is disabled.
		this.registerDomEvent(document, 'click', (evt: MouseEvent) => {
			console.log('click', evt);
		});

		// When registering intervals, this function will automatically clear the interval when the plugin is disabled.
		this.registerInterval(window.setInterval(() => console.log('setInterval'), 5 * 60 * 1000));
	}

	// Helper methods for agent command formatting

	formatVaultAnalysis(analysis: any): string {
		if (!analysis) return "Analysis data not available";

		const parts = [];
		
		// Basic statistics
		if (analysis.statistics) {
			const stats = analysis.statistics;
			parts.push(`### 📊 Vault Statistics
- **Total Notes**: ${stats.total_notes || 0}
- **Total Words**: ${stats.total_words || 0}  
- **Total Links**: ${stats.total_links || 0}
- **Average Note Length**: ${stats.avg_note_length || 0} words`);
		}

		// Quality metrics
		if (analysis.quality_metrics) {
			const metrics = analysis.quality_metrics;
			parts.push(`### ⭐ Quality Assessment
- **Completeness**: ${(metrics.completeness * 100).toFixed(1)}%
- **Connectivity**: ${(metrics.connectivity * 100).toFixed(1)}%
- **Organization**: ${(metrics.organization * 100).toFixed(1)}%
- **Consistency**: ${(metrics.consistency * 100).toFixed(1)}%`);
		}

		// Insights
		if (analysis.insights && analysis.insights.length > 0) {
			parts.push(`### 💡 Key Insights
${analysis.insights.map((insight: string) => `- ${insight}`).join('\n')}`);
		}

		// Suggestions
		if (analysis.suggestions && analysis.suggestions.length > 0) {
			parts.push(`### 🎯 Recommendations
${analysis.suggestions.map((suggestion: any) => `- **${suggestion.type}**: ${suggestion.suggestion} (${suggestion.priority} priority)`).join('\n')}`);
		}

		return parts.join('\n\n');
	}

	extractNoteReferences(text: string): string[] {
		// Extract [[note]] references from text
		const linkRegex = /\[\[([^\]]+)\]\]/g;
		const matches = [];
		let match;
		
		while ((match = linkRegex.exec(text)) !== null) {
			matches.push(match[1]);
		}
		
		// If no links found, return current file
		return matches.length > 0 ? matches : [this.app.workspace.getActiveFile()?.basename || 'current'];
	}

	formatOptimizationResult(result: any): string {
		if (!result) return "Optimization complete";
		
		return `Cache hit rate: ${(result.cache_hit_rate * 100).toFixed(1)}% | Avg latency: ${result.avg_latency_ms}ms`;
	}

	formatParallelAgentResults(result: any): string {
		if (!result.results) return "No results available";

		const parts = [`**Execution Mode**: ${result.execution_mode} | **Total Time**: ${result.total_execution_time.toFixed(2)}s\n`];

		result.results.forEach((agentResult: any) => {
			parts.push(`### 🤖 ${agentResult.agent_name}`);
			parts.push(`**Status**: ${agentResult.status} | **Time**: ${agentResult.execution_time?.toFixed(2)}s`);
			
			if (agentResult.status === 'success' && agentResult.result) {
				const res = agentResult.result;
				
				if (res.insights) {
					parts.push(`**Insights**: ${res.insights.slice(0, 2).join(', ')}`);
				}
				
				if (res.cache_hit_rate !== undefined) {
					parts.push(`**Performance**: ${(res.cache_hit_rate * 100).toFixed(1)}% cache hit rate`);
				}
				
				if (res.suggestions) {
					parts.push(`**Suggestions**: ${res.suggestions.length} recommendations`);
				}
			} else if (agentResult.error) {
				parts.push(`**Error**: ${agentResult.error}`);
			}
			
			parts.push('');
		});

		return parts.join('\n');
	}

	showAgentStatusModal(agents: any[]) {
		const modal = new Modal(this.app);
		modal.titleEl.setText('🤖 Agent OS Status');
		
		const content = modal.contentEl;
		content.empty();
		
		// Create status table
		const table = content.createEl('table');
		table.addClass('agent-status-table');
		
		// Header
		const headerRow = table.createEl('tr');
		['Agent', 'Status', 'Type', 'Description'].forEach(header => {
			const th = headerRow.createEl('th');
			th.setText(header);
		});
		
		// Agent rows
		agents.forEach(agent => {
			const row = table.createEl('tr');
			
			const nameCell = row.createEl('td');
			nameCell.setText(agent.name);
			
			const statusCell = row.createEl('td');
			statusCell.setText(agent.enabled ? '✅ Enabled' : '❌ Disabled');
			statusCell.addClass(agent.enabled ? 'status-enabled' : 'status-disabled');
			
			const typeCell = row.createEl('td');
			typeCell.setText(agent.type || 'unknown');
			
			const descCell = row.createEl('td');
			descCell.setText(agent.description || 'No description');
		});
		
		// Add CSS for table styling
		const style = content.createEl('style');
		style.textContent = `
			.agent-status-table {
				width: 100%;
				border-collapse: collapse;
				margin-top: 10px;
			}
			.agent-status-table th,
			.agent-status-table td {
				border: 1px solid var(--background-modifier-border);
				padding: 8px;
				text-align: left;
			}
			.agent-status-table th {
				background-color: var(--background-secondary);
				font-weight: bold;
			}
			.status-enabled {
				color: var(--text-success);
			}
			.status-disabled {
				color: var(--text-error);
			}
		`;
		
		modal.open();
	}

	async loadSettings() {
		this.settings = Object.assign({}, DEFAULT_SETTINGS, await this.loadData());
	}

	async saveSettings() {
		await this.saveData(this.settings);
	}
}

class CopilotSettingTab extends PluginSettingTab {
	plugin: CopilotPlugin;

	constructor(app: App, plugin: CopilotPlugin) {
		super(app, plugin);
		this.plugin = plugin;
	}

	display(): void {
		const { containerEl } = this;

		containerEl.empty();

		containerEl.createEl('h2', { text: 'Settings for Obsidian Copilot' });

		// Mode Selection
		containerEl.createEl('h3', { text: 'Operation Mode' });
		
		// Current Status
		new Setting(containerEl)
			.setName('Current Status')
			.setDesc(`Mode: ${this.plugin.currentMode === 'backend' ? '🚀 Enhanced (with backend)' : '✨ Direct API'} | Backend: ${this.plugin.backendAvailable ? '✅ Available' : '❌ Not available'}`)
			.addButton(button => button
				.setButtonText('Check Now')
				.onClick(async () => {
					await this.plugin.determineMode();
					this.display(); // Refresh display
				}));
		
		new Setting(containerEl)
			.setName('Mode')
			.setDesc('Auto: Use backend when available, fallback to direct API. Direct: Always use API keys. Backend: Always use backend.')
			.addDropdown(dropdown => dropdown
				.addOption('auto', 'Auto (Recommended)')
				.addOption('direct', 'Direct API Only')
				.addOption('backend', 'Backend Only')
				.setValue(this.plugin.settings.mode)
				.onChange(async (value: 'auto' | 'direct' | 'backend') => {
					this.plugin.settings.mode = value;
					await this.plugin.saveSettings();
					await this.plugin.determineMode();
					this.display();
				}));

		// API Configuration (for direct mode)
		if (this.plugin.settings.mode !== 'backend') {
			containerEl.createEl('h3', { text: 'API Configuration' });
			
			new Setting(containerEl)
				.setName('API Provider')
				.setDesc('Choose between Anthropic Claude or OpenAI')
				.addDropdown(dropdown => dropdown
					.addOption('anthropic', 'Anthropic Claude')
					.addOption('openai', 'OpenAI')
					.setValue(this.plugin.settings.apiProvider)
					.onChange(async (value: 'anthropic' | 'openai') => {
						this.plugin.settings.apiProvider = value;
						await this.plugin.saveSettings();
						this.display();
					}));
			
			new Setting(containerEl)
				.setName('API Key')
				.setDesc(`Enter your ${this.plugin.settings.apiProvider === 'anthropic' ? 'Anthropic' : 'OpenAI'} API key`)
				.addText(text => text
					.setPlaceholder(this.plugin.settings.apiProvider === 'anthropic' ? 'sk-ant-...' : 'sk-...')
					.setValue(this.plugin.settings.apiKey)
					.onChange(async (value) => {
						this.plugin.settings.apiKey = value;
						await this.plugin.saveSettings();
					}));
		}

		// Backend Configuration (for backend mode)
		if (this.plugin.settings.mode !== 'direct') {
			containerEl.createEl('h3', { text: 'Backend Configuration' });

		new Setting(containerEl)
			.setName('Backend URL')
			.setDesc('URL for the FastAPI backend server (e.g., http://localhost:8000)')
			.addText(text => text
				.setPlaceholder('http://localhost:8000')
				.setValue(this.plugin.settings.backendUrl)
				.onChange(async (value) => {
					this.plugin.settings.backendUrl = value;
					await this.plugin.saveSettings();
				}));

		// Claude-specific settings (only show if Claude backend is enabled)
		if (this.plugin.settings.useClaudeBackend) {
			containerEl.createEl('h3', { text: 'Claude Settings' });
			
			new Setting(containerEl)
				.setName('Claude Model')
				.setDesc('Claude model to use for generation')
				.addDropdown(dropdown => dropdown
					.addOption('claude-3-5-sonnet-20241022', 'Claude 3.5 Sonnet')
					.addOption('claude-3-opus-20240229', 'Claude 3 Opus')
					.addOption('claude-3-haiku-20240307', 'Claude 3 Haiku')
					.setValue(this.plugin.settings.claudeModel)
					.onChange(async (value) => {
						this.plugin.settings.claudeModel = value;
						await this.plugin.saveSettings();
					}));

			new Setting(containerEl)
				.setName('Max Context Tokens')
				.setDesc('Maximum number of tokens for Claude context (up to 200000)')
				.addText(text => text
					.setPlaceholder('100000')
					.setValue(String(this.plugin.settings.maxContextTokens))
					.onChange(async (value) => {
						const num = parseInt(value);
						if (!isNaN(num) && num > 0 && num <= 200000) {
							this.plugin.settings.maxContextTokens = num;
							await this.plugin.saveSettings();
						}
					}));

			new Setting(containerEl)
				.setName('Show Generation Time')
				.setDesc('Display how long Claude takes to generate responses in the console')
				.addToggle(toggle => toggle
					.setValue(this.plugin.settings.showGenerationTime)
					.onChange(async (value) => {
						this.plugin.settings.showGenerationTime = value;
						await this.plugin.saveSettings();
					}));
		}

		// OpenAI settings (only show if OpenAI backend is enabled)
		if (!this.plugin.settings.useClaudeBackend) {
			containerEl.createEl('h3', { text: 'OpenAI Settings' });
			
			new Setting(containerEl)
				.setName('OpenAI API Key')
				.setDesc('Enter your OpenAI API key')
				.addText(text => text
					.setPlaceholder('sk-...')
					.setValue(this.plugin.settings.apiKey)
					.onChange(async (value) => {
						this.plugin.settings.apiKey = value;
						await this.plugin.saveSettings();
					}));

			new Setting(containerEl)
				.setName('OpenAI Model')
				.setDesc('OpenAI model to use for generation')
				.addDropdown(dropdown => dropdown
					.addOption('gpt-3.5-turbo', 'GPT-3.5 Turbo')
					.addOption('gpt-4', 'GPT-4')
					.addOption('gpt-4-turbo-preview', 'GPT-4 Turbo')
					.setValue(this.plugin.settings.model)
					.onChange(async (value) => {
						this.plugin.settings.model = value;
						await this.plugin.saveSettings();
					}));
		}

		// System Prompts (shown for both backends)
		containerEl.createEl('h3', { text: 'System Prompts' });

		new Setting(containerEl)
			.setName('System Prompt: Draft Section')
			.setDesc('Define the prompt used for drafting a section with context')
			.addTextArea(text => text
				.setPlaceholder('Prompt to draft a section')
				.setValue(this.plugin.settings.systemContentDraftSection)
				.onChange(async (value) => {
					this.plugin.settings.systemContentDraftSection = value;
					await this.plugin.saveSettings();
				})
				.inputEl.rows = 4);

		new Setting(containerEl)
			.setName('System Prompt: Draft Section (without context)')
			.setDesc('Define the prompt used for drafting a section without context')
			.addTextArea(text => text
				.setPlaceholder('Prompt to draft a section (without context)')
				.setValue(this.plugin.settings.systemContentDraftSectionNoContext)
				.onChange(async (value) => {
					this.plugin.settings.systemContentDraftSectionNoContext = value;
					await this.plugin.saveSettings();
				})
				.inputEl.rows = 4);

		new Setting(containerEl)
			.setName('System Prompt: Reflect on the week')
			.setDesc('Define the prompt used to reflect on the week')
			.addTextArea(text => text
				.setPlaceholder('Prompt to reflect on the week')
				.setValue(this.plugin.settings.systemContentReflectWeek)
				.onChange(async (value) => {
					this.plugin.settings.systemContentReflectWeek = value;
					await this.plugin.saveSettings();
				})
				.inputEl.rows = 4);
	}
}