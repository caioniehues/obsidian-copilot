/**
 * Mock Obsidian API for testing.
 * Provides comprehensive mocks for all Obsidian components used by the plugin.
 */

// Mock App interface
export class MockApp {
  workspace = new MockWorkspace();
  vault = new MockVault();
  
  constructor() {
    // Initialize with default state
  }
}

// Mock Workspace interface
export class MockWorkspace {
  private leaves: MockWorkspaceLeaf[] = [];
  
  getLeaf(split?: string, direction?: string): MockWorkspaceLeaf {
    const leaf = new MockWorkspaceLeaf();
    this.leaves.push(leaf);
    return leaf;
  }
  
  getLeavesOfType(type: string): MockWorkspaceLeaf[] {
    return this.leaves.filter(leaf => leaf.view?.getViewType() === type);
  }
  
  getActiveViewOfType<T>(type: any): T | null {
    const leaf = this.leaves.find(leaf => leaf.view?.getViewType() === type.name);
    return leaf?.view as T || null;
  }
  
  revealLeaf(leaf: MockWorkspaceLeaf): void {
    // Mock reveal leaf functionality
  }
}

// Mock WorkspaceLeaf interface
export class MockWorkspaceLeaf {
  view: MockView | null = null;
  
  async openFile(file: MockTFile): Promise<void> {
    this.view = new MockMarkdownView(file);
  }
  
  setViewState(state: any): Promise<void> {
    return Promise.resolve();
  }
}

// Mock base View interface
export class MockView {
  getViewType(): string {
    return 'unknown';
  }
}

// Mock MarkdownView interface
export class MockMarkdownView extends MockView {
  editor = new MockEditor();
  file: MockTFile;
  
  constructor(file: MockTFile) {
    super();
    this.file = file;
  }
  
  getViewType(): string {
    return 'markdown';
  }
}

// Mock Editor interface
export class MockEditor {
  private content = '';
  private cursor = { line: 0, ch: 0 };
  
  getValue(): string {
    return this.content;
  }
  
  setValue(content: string): void {
    this.content = content;
  }
  
  getCursor(): { line: number; ch: number } {
    return this.cursor;
  }
  
  setCursor(pos: { line: number; ch: number }): void {
    this.cursor = pos;
  }
  
  getLine(line: number): string {
    const lines = this.content.split('\n');
    return lines[line] || '';
  }
  
  replaceRange(replacement: string, from: any, to?: any): void {
    // Simple mock implementation
    this.content = replacement;
  }
  
  on(event: string, callback: Function): void {
    // Mock event listener
  }
  
  off(event: string, callback: Function): void {
    // Mock event listener removal
  }
}

// Mock Vault interface
export class MockVault {
  private files: Map<string, MockTFile> = new Map();
  adapter = {
    path: {
      resolve: (path: string) => `/mock/vault${path === '.' ? '' : '/' + path}`
    }
  };
  
  getAbstractFileByPath(path: string): MockTFile | null {
    return this.files.get(path) || null;
  }
  
  async create(path: string, content: string): Promise<MockTFile> {
    const file = new MockTFile(path, content);
    this.files.set(path, file);
    return file;
  }
  
  async modify(file: MockTFile, content: string): Promise<void> {
    file.content = content;
  }
  
  async read(file: MockTFile): Promise<string> {
    return file.content;
  }
  
  async delete(file: MockTFile): Promise<void> {
    this.files.delete(file.path);
  }
}

// Mock TFile interface
export class MockTFile {
  path: string;
  name: string;
  content: string;
  
  constructor(path: string, content = '') {
    this.path = path;
    this.name = path.split('/').pop() || path;
    this.content = content;
  }
}

// Mock Plugin base class
export class Plugin {
  app: MockApp;
  manifest: any;
  
  constructor(app: MockApp, manifest: any) {
    this.app = app;
    this.manifest = manifest;
  }
  
  async loadData(): Promise<any> {
    return {};
  }
  
  async saveData(data: any): Promise<void> {
    // Mock save
  }
  
  addCommand(command: any): void {
    // Mock command registration
  }
  
  addRibbonIcon(icon: string, title: string, callback: Function): HTMLElement {
    const element = document.createElement('div');
    element.setAttribute('aria-label', title);
    return element;
  }
  
  addSettingTab(tab: any): void {
    // Mock settings tab
  }
  
  registerView(type: string, viewCreator: any): void {
    // Mock view registration
  }
  
  registerEvent(event: any): void {
    // Mock event registration
  }
  
  async onload(): Promise<void> {
    // Override in subclasses
  }
  
  onunload(): void {
    // Override in subclasses
  }
}

// Mock PluginSettingTab
export class PluginSettingTab {
  app: MockApp;
  plugin: Plugin;
  containerEl: HTMLElement;
  
  constructor(app: MockApp, plugin: Plugin) {
    this.app = app;
    this.plugin = plugin;
    this.containerEl = document.createElement('div');
  }
  
  display(): void {
    // Override in subclasses
  }
  
  hide(): void {
    // Override in subclasses
  }
}

// Mock Setting class
export class Setting {
  settingEl: HTMLElement;
  
  constructor(containerEl: HTMLElement) {
    this.settingEl = document.createElement('div');
    containerEl.appendChild(this.settingEl);
  }
  
  setName(name: string): Setting {
    const nameEl = document.createElement('span');
    nameEl.textContent = name;
    this.settingEl.appendChild(nameEl);
    return this;
  }
  
  setDesc(desc: string): Setting {
    const descEl = document.createElement('span');
    descEl.textContent = desc;
    this.settingEl.appendChild(descEl);
    return this;
  }
  
  addText(callback: (text: any) => any): Setting {
    const input = document.createElement('input');
    input.type = 'text';
    const textComponent = {
      setPlaceholder: (placeholder: string) => {
        input.placeholder = placeholder;
        return textComponent;
      },
      setValue: (value: string) => {
        input.value = value;
        return textComponent;
      },
      onChange: (callback: (value: string) => void) => {
        input.addEventListener('input', (e) => {
          callback((e.target as HTMLInputElement).value);
        });
        return textComponent;
      }
    };
    callback(textComponent);
    this.settingEl.appendChild(input);
    return this;
  }
  
  addDropdown(callback: (dropdown: any) => any): Setting {
    const select = document.createElement('select');
    const dropdownComponent = {
      addOption: (value: string, text: string) => {
        const option = document.createElement('option');
        option.value = value;
        option.textContent = text;
        select.appendChild(option);
        return dropdownComponent;
      },
      setValue: (value: string) => {
        select.value = value;
        return dropdownComponent;
      },
      onChange: (callback: (value: string) => void) => {
        select.addEventListener('change', (e) => {
          callback((e.target as HTMLSelectElement).value);
        });
        return dropdownComponent;
      }
    };
    callback(dropdownComponent);
    this.settingEl.appendChild(select);
    return this;
  }
  
  addToggle(callback: (toggle: any) => any): Setting {
    const input = document.createElement('input');
    input.type = 'checkbox';
    const toggleComponent = {
      setValue: (value: boolean) => {
        input.checked = value;
        return toggleComponent;
      },
      onChange: (callback: (value: boolean) => void) => {
        input.addEventListener('change', (e) => {
          callback((e.target as HTMLInputElement).checked);
        });
        return toggleComponent;
      }
    };
    callback(toggleComponent);
    this.settingEl.appendChild(input);
    return this;
  }
}

// Mock Modal class
export class Modal {
  app: MockApp;
  contentEl: HTMLElement;
  
  constructor(app: MockApp) {
    this.app = app;
    this.contentEl = document.createElement('div');
  }
  
  open(): void {
    // Mock modal opening
  }
  
  close(): void {
    // Mock modal closing
  }
  
  onOpen(): void {
    // Override in subclasses
  }
  
  onClose(): void {
    // Override in subclasses
  }
}

// Mock Notice class
export class Notice {
  message: string;
  timeout: number;
  
  constructor(message: string, timeout = 5000) {
    this.message = message;
    this.timeout = timeout;
  }
  
  setMessage(message: string): void {
    this.message = message;
  }
  
  hide(): void {
    // Mock notice hiding
  }
}

// Default exports matching Obsidian API
export const App = MockApp;
export const Workspace = MockWorkspace;
export const WorkspaceLeaf = MockWorkspaceLeaf;
export const MarkdownView = MockMarkdownView;
export const Editor = MockEditor;
export const Vault = MockVault;
export const TFile = MockTFile;