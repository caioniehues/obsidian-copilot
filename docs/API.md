# Claude CLI Chat Plugin - API Reference

This document provides comprehensive API reference documentation for the Claude CLI Chat plugin, covering all public interfaces, methods, and integration points.

## Core Plugin API

### ClaudeChatPlugin

Main plugin class extending Obsidian's `Plugin` base class.

#### Public Properties

```typescript
class ClaudeChatPlugin extends Plugin {
  settings: ClaudeChatSettings;           // Current plugin configuration
  cliAvailable: boolean;                  // Claude CLI availability status
  chatHistory: ChatMessage[];             // Current session chat history
  currentSessionId: string | null;        // Active session identifier
}
```

#### Public Methods

##### Plugin Lifecycle

```typescript
async onload(): Promise<void>
```
Initializes the plugin, loads settings, checks CLI availability, and registers components.

**Behavior:**
- Loads plugin settings from storage
- Initializes `ClaudeCLIService` instance
- Checks Claude CLI availability if `autoDetectCLI` is enabled
- Registers commands, views, and settings tab
- Starts initial chat session

```typescript
async onunload(): Promise<void>
```
Cleans up plugin resources and terminates active processes.

**Behavior:**
- Calls `cliService.cleanup()` to terminate subprocess
- Removes event listeners and cleanup resources

##### Settings Management

```typescript
async loadSettings(): Promise<void>
```
Loads plugin settings from Obsidian's data storage, merging with defaults.

```typescript
async saveSettings(): Promise<void>
```
Persists current settings to Obsidian's data storage.

##### Session Management

```typescript
generateSessionId(): string
```
Generates unique session identifier for Claude CLI interaction.

**Returns:** String in format `chat-{timestamp}-{randomString}`

**Example:**
```typescript
const sessionId = plugin.generateSessionId();
// Returns: "chat-1703123456789-kx7m9qp2w"
```

```typescript
startNewSession(): void
```
Initiates new chat session, clearing history and notifying active views.

**Behavior:**
- Generates new session ID
- Clears `chatHistory` array
- Notifies all active `claude-chat` views via `onNewSession()`

##### Chat Panel Management

```typescript
async openChatPanel(): Promise<void>
```
Opens or activates Claude chat panel in Obsidian workspace.

**Behavior:**
- If chat panel exists: reveals and focuses existing panel
- If no panel exists: creates new panel with vertical split layout

##### Message Handling

```typescript
async sendMessage(message: string): Promise<void>
```
Sends message to Claude CLI and handles streaming response.

**Parameters:**
- `message` (string): User message to send to Claude

**Behavior:**
- Validates CLI availability
- Adds user message to chat history
- Constructs `CLIOptions` with current session and settings
- Calls `cliService.startChat()` with streaming callback
- Handles streaming responses via `handleStreamResponse()`
- Adds complete assistant response to chat history
- Tracks performance metrics if enabled

**Error Handling:**
- Shows error notice if CLI unavailable
- Catches and logs CLI service errors
- Provides user-friendly error messages

##### Export Functionality

```typescript
async exportChatToNote(): Promise<void>
```
Exports current chat history to new Obsidian note.

**Behavior:**
- Validates chat history exists
- Generates timestamped filename
- Creates markdown content with formatted messages
- Creates new vault file and opens in workspace

**Generated Format:**
```markdown
# Chat Export - {date}

## 👤 User ({timestamp})

{user message}

## 🤖 Claude ({timestamp})

{assistant response}
```

##### Utility Methods

```typescript
createNotice(message: string, type: 'info' | 'success' | 'warning' | 'error' = 'info'): void
```
Creates user notification with specified type.

```typescript
getPerformanceMetrics(): PerformanceMetrics
```
Returns current performance metrics from CLI service.

```typescript
async executeCommand(commandId: string): Promise<void>
```
Executes registered plugin command by ID. Used primarily for testing.

## ClaudeCLIService API

Core service class handling Claude CLI subprocess communication.

### Interface Definitions

#### CLIOptions

Configuration options for Claude CLI interaction:

```typescript
interface CLIOptions {
  message: string;              // Message to send to Claude
  sessionId?: string;           // Session identifier for context
  vaultPath?: string;           // Obsidian vault path for integration
  streaming?: boolean;          // Enable streaming responses (default: true)
  allowedTools?: string[];      // Permitted CLI tools
  timeout?: number;             // Process timeout in milliseconds
}
```

#### StreamResponse

Streaming response format from Claude CLI:

```typescript
interface StreamResponse {
  type: 'content' | 'error' | 'end' | 'tool_use' | 'metadata';
  content?: string;             // Incremental text content
  error?: string;               // Error message
  metadata?: any;               // Additional context data
}
```

#### CLICommand

Internal command representation:

```typescript
interface CLICommand {
  command: string;              // Executable name/path
  args: string[];               // Command arguments array
}
```

#### PerformanceMetrics

Performance tracking data:

```typescript
interface PerformanceMetrics {
  lastResponseTime: number;     // Most recent response time (ms)
  successCount: number;         // Successful requests count
  errorCount: number;           // Failed requests count
  averageResponseTime: number;  // Average response time (ms)
}
```

### Public Methods

#### Health Check

```typescript
async checkCLIAvailability(): Promise<boolean>
```
Verifies Claude CLI is installed and accessible.

**Returns:** Promise resolving to availability status

**Implementation Details:**
- Spawns `claude --version` process
- Monitors exit code and error events
- Times out after 5 seconds to prevent hanging
- Returns `false` for any error condition

**Example:**
```typescript
const service = new ClaudeCLIService();
const available = await service.checkCLIAvailability();
if (!available) {
  console.log('Claude CLI not found');
}
```

#### Command Construction

```typescript
buildCLICommand(options: CLIOptions): CLICommand
```
Constructs platform-appropriate Claude CLI command.

**Parameters:**
- `options` (CLIOptions): Configuration for CLI invocation

**Returns:** CLICommand object with executable and arguments

**Cross-Platform Handling:**
- Windows: Uses `claude.exe` executable
- Unix systems: Uses `claude` executable
- Handles path normalization across platforms

**Generated Arguments:**
```bash
claude [--session-id {id}] [--add-dir {vaultPath}] [--output-format stream-json] [--allowedTools {tools}] {message}
```

#### Stream Processing

```typescript
parseStreamResponse(data: string): StreamResponse[]
```
Parses complete stream-json data into response objects.

**Parameters:**
- `data` (string): Complete JSON stream data

**Returns:** Array of parsed StreamResponse objects

**Error Handling:**
- Skips malformed JSON lines silently
- Continues processing valid lines
- Returns empty array for invalid input

```typescript
handleStreamChunk(chunk: string): StreamResponse[]
```
Processes partial stream chunks, accumulating incomplete lines.

**Parameters:**
- `chunk` (string): Partial stream data

**Returns:** Array of complete StreamResponse objects from chunk

**Implementation:**
- Accumulates partial data across chunks
- Splits on newlines, preserving incomplete lines
- Parses complete lines as JSON
- Maintains state for next chunk processing

#### Chat Session

```typescript
async startChat(
  options: CLIOptions,
  onResponse: (response: StreamResponse) => void
): Promise<void>
```
Initiates chat session with Claude CLI subprocess.

**Parameters:**
- `options` (CLIOptions): CLI configuration
- `onResponse` (Function): Callback for streaming responses

**Returns:** Promise resolving when chat completes

**Process Management:**
- Enforces single concurrent process
- Sets up process timeout protection
- Handles stdout/stderr streams
- Manages process lifecycle events

**Event Sequence:**
1. Validates no concurrent process running
2. Constructs CLI command from options
3. Spawns subprocess with error handling
4. Sets up timeout protection
5. Processes stdout chunks via `handleStreamChunk()`
6. Calls `onResponse` for each parsed response
7. Handles process completion and cleanup

**Error Conditions:**
- Throws if already processing request
- Rejects on process spawn failure
- Rejects on process timeout
- Rejects on non-zero exit code

#### Performance Monitoring

```typescript
getPerformanceMetrics(): PerformanceMetrics
```
Returns current performance statistics.

**Returns:** Copy of current performance metrics

**Metrics Tracked:**
- Response time for each request
- Success/failure counts
- Rolling average of last 100 requests

#### Resource Management

```typescript
cleanup(): void
```
Cleans up subprocess and resets service state.

**Behavior:**
- Removes all process event listeners
- Terminates subprocess if running
- Resets processing flags
- Clears partial data buffer

```typescript
terminate(): void
```
Forcibly terminates current subprocess.

**Behavior:**
- Sends SIGTERM to running process
- Calls `cleanup()` for complete resource cleanup

## Chat UI Components

### ChatView

Obsidian ItemView implementation for chat interface.

#### Public Methods

```typescript
getViewType(): string
```
Returns unique view type identifier: `'claude-chat'`

```typescript
getDisplayText(): string
```
Returns display name for workspace tab: `'Claude Chat'`

```typescript
async onOpen(): Promise<void>
```
Initializes chat interface when view opens.

**UI Components Created:**
- Chat container with header
- Messages display area
- Message input field
- Send button with keyboard support

```typescript
async onClose(): Promise<void>
```
Cleanup when view closes.

```typescript
focus(): void
```
Focuses the message input field.

#### Event Handlers

```typescript
onNewSession(): void
```
Updates UI when new chat session starts.

**Behavior:**
- Clears message area
- Shows "New chat session started" notice

```typescript
appendStreamingContent(content: string): void
```
Appends streaming content to current assistant message.

**Behavior:**
- Finds last assistant message element
- Appends content to existing message or creates new message
- Updates UI in real-time during streaming

```typescript
onStreamingComplete(): void
```
Handles streaming completion.

**Behavior:**
- Scrolls message area to bottom
- Finalizes message display state

```typescript
updateHistory(history: ChatMessage[]): void
```
Updates complete chat history display.

**Parameters:**
- `history` (ChatMessage[]): Complete message history

**Behavior:**
- Clears existing messages
- Renders all messages with role icons
- Scrolls to bottom of message area

## Settings API

### ClaudeChatSettings

Plugin configuration interface:

```typescript
interface ClaudeChatSettings {
  sessionTimeout: number;        // CLI timeout (ms, default: 30000)
  maxHistorySize: number;        // History limit (default: 100)
  showPerformanceMetrics: boolean; // Debug info (default: true)
  vaultIntegration: boolean;     // Vault access (default: true)
  allowedTools: string[];        // CLI tools (default: ['read', 'search'])
  autoDetectCLI: boolean;        // Startup detection (default: true)
}
```

### ClaudeChatSettingTab

Settings UI implementation extending `PluginSettingTab`.

#### Public Methods

```typescript
display(): void
```
Renders complete settings interface.

**Settings Sections:**
1. **Claude CLI Configuration**
   - Auto-detect toggle
   - Session timeout input
   
2. **Vault Integration**
   - Enable/disable vault access
   - Allowed tools configuration
   
3. **Chat Configuration**
   - History size limit
   - Performance metrics toggle
   
4. **Status Information**
   - CLI availability status
   - Performance metrics display

## Event System

### Plugin Events

The plugin integrates with Obsidian's event system:

```typescript
// Command registration
this.addCommand({
  id: 'open-chat',
  name: 'Open Chat Panel',
  callback: () => this.openChatPanel()
});

// View registration
this.registerView('claude-chat', (leaf) => new ChatView(leaf, this));
```

### Custom Event Callbacks

#### Stream Response Handler

```typescript
type StreamResponseHandler = (response: StreamResponse) => void;
```
Callback function for processing streaming responses from Claude CLI.

**Usage Example:**
```typescript
await service.startChat(options, (response) => {
  switch (response.type) {
    case 'content':
      // Handle incremental content
      break;
    case 'end':
      // Handle completion
      break;
    case 'error':
      // Handle errors
      break;
  }
});
```

## Data Models

### ChatMessage

Internal message representation:

```typescript
interface ChatMessage {
  type: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: Date;
}
```

**Usage:**
- Stored in `plugin.chatHistory` array
- Used for message display and export functionality
- Automatically managed by plugin lifecycle

## Error Handling

### Exception Types

The plugin defines specific error conditions:

```typescript
// CLI service errors
throw new Error('Claude CLI is currently busy');
throw new Error('Claude CLI process timed out');
throw new Error('Claude CLI process failed with exit code: {code}');

// Plugin errors
this.createNotice('Claude CLI is not available. Please install Claude Code.', 'error');
this.createNotice('Failed to communicate with Claude CLI.', 'error');
```

### Error Recovery

The API provides multiple layers of error recovery:

1. **Graceful degradation**: Plugin functions with reduced capability when CLI unavailable
2. **User feedback**: Clear error messages via Obsidian's notice system
3. **Resource cleanup**: Automatic cleanup on error conditions
4. **Process recovery**: Ability to restart failed subprocess

## Integration Examples

### Basic Chat Implementation

```typescript
// Initialize plugin and send message
const plugin = new ClaudeChatPlugin(app, manifest);
await plugin.onload();

if (plugin.cliAvailable) {
  await plugin.sendMessage('Hello Claude!');
}
```

### Custom Settings Integration

```typescript
// Modify settings programmatically
plugin.settings.vaultIntegration = false;
plugin.settings.allowedTools = ['read'];
await plugin.saveSettings();
```

### Performance Monitoring

```typescript
// Track performance metrics
const metrics = plugin.getPerformanceMetrics();
console.log(`Average response time: ${metrics.averageResponseTime}ms`);
console.log(`Success rate: ${metrics.successCount}/${metrics.successCount + metrics.errorCount}`);
```

### Advanced CLI Service Usage

```typescript
// Direct CLI service usage
const service = new ClaudeCLIService();
await service.startChat({
  message: 'Analyze this code',
  vaultPath: '/path/to/vault',
  allowedTools: ['read', 'bash'],
  timeout: 45000
}, (response) => {
  console.log('Received:', response);
});
```

This API provides comprehensive access to the Claude CLI Chat plugin's functionality while maintaining simplicity and type safety for integration scenarios.