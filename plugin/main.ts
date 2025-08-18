import { App, Editor, MarkdownView, Plugin, PluginSettingTab, Setting, TFile } from 'obsidian';

// Claude-optimized Copilot settings
interface CopilotPluginSettings {
	backendUrl: string;
	claudeModel: string;
	contextStrategy: 'full_docs' | 'smart_chunks' | 'hierarchical';
	maxContextTokens: number;
	showGenerationTime: boolean;
	systemContentDraftSection: string;
	systemContentDraftSectionNoContext: string;
	systemContentReflectWeek: string;
	enableVaultAnalysis: boolean;
	enableSynthesis: boolean;
}

const DEFAULT_SETTINGS: CopilotPluginSettings = {
	backendUrl: 'http://localhost:8000',
	claudeModel: 'claude-3-5-sonnet-20241022',
	contextStrategy: 'smart_chunks',
	maxContextTokens: 100000,
	showGenerationTime: true,
	systemContentDraftSection: "You are Claude-powered Obsidian Copilot, an advanced AI assistant that helps writers craft drafts based on their notes.\n\nWith access to a 200K token context window, you can understand entire documents and their relationships. When you reference content from a document, append the sentence with a markdown reference that links to the document's title. For example, if a sentence references context from 'Augmented Language Models.md', it should end with ([source](Augmented%20Language%20Models.md)).",
	systemContentDraftSectionNoContext: "You are Claude-powered Obsidian Copilot, an advanced AI assistant that helps writers craft drafts.\n\nGenerate comprehensive content based on the given section heading, leveraging your extensive knowledge and reasoning capabilities.",
	systemContentReflectWeek: "You are a thoughtful AI companion powered by Claude, helping users reflect on their week with deep insight and empathy. Given their journal entries, provide a thoughtful analysis for each of the following:\n\n* Celebrate what went well\n* Reflect on areas for growth\n* Suggest goals for next week",
	enableVaultAnalysis: true,
	enableSynthesis: true
}

export default class CopilotPlugin extends Plugin {
	settings: CopilotPluginSettings;
	processing = false;

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


	// Removed OpenAI API method - now using Claude exclusively via backend

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
		statusBarItemEl.setText('Copilot loaded');

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

		// Backend Selection
		containerEl.createEl('h3', { text: 'Backend Configuration' });
		
		new Setting(containerEl)
			.setName('Use Claude Backend')
			.setDesc('Use Claude Code CLI instead of OpenAI API for generation. Requires Claude Code installed on backend server.')
			.addToggle(toggle => toggle
				.setValue(this.plugin.settings.useClaudeBackend)
				.onChange(async (value) => {
					this.plugin.settings.useClaudeBackend = value;
					await this.plugin.saveSettings();
					// Refresh display to show/hide relevant settings
					this.display();
				}));

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