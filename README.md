# Obsidian Claude CLI Chat Plugin

[![Claude Code](https://img.shields.io/badge/Claude_Code-Local_Integration-blue)](https://claude.ai/code)
[![Privacy](https://img.shields.io/badge/Privacy-100%25_Local-green)](https://claude.ai/code)
[![Zero Config](https://img.shields.io/badge/Setup-Zero_Config-orange)](#installation)
[![License](https://img.shields.io/badge/License-MIT-yellow)](./LICENSE)

> **🚀 LOCAL CLAUDE CODE INTEGRATION**  
> Chat with Claude directly from Obsidian using your local Claude CLI installation.  
> **No API keys required. Complete privacy. Zero configuration.**

## 🌟 Overview

This plugin transforms your Obsidian workspace into a direct interface with Claude Code CLI, providing seamless local AI assistance without the complexity of external APIs or backend services. Built from the ground up for simplicity, privacy, and performance.

### Why Choose Local Claude CLI Integration?

- **🔐 Complete Privacy** - All processing happens locally on your machine
- **🚀 Zero Configuration** - Works instantly if Claude CLI is installed
- **💸 No API Costs** - Use your existing Claude Code subscription
- **⚡ Real-time Streaming** - Live responses as Claude types
- **🧠 Vault Awareness** - Optional integration with your Obsidian knowledge base
- **🎯 Simplified Architecture** - No complex RAG systems or backend services

## 🎯 Key Features

### 💬 **Seamless Chat Interface**
- **Integrated Chat Panel** - Native Obsidian sidebar chat experience
- **Streaming Responses** - Watch Claude's thoughts unfold in real-time
- **Message History** - Complete session management with export capabilities
- **Rich Formatting** - Full markdown support in both questions and responses

### 🏠 **Local-First Design**
- **Claude CLI Integration** - Direct communication with your local Claude installation
- **No Network Dependencies** - Works completely offline (except Claude API calls)
- **Privacy Guaranteed** - Your vault never leaves your machine unless you choose
- **Performance Optimized** - Minimal overhead, maximum responsiveness

### 📚 **Smart Vault Integration**
- **Configurable Permissions** - Choose exactly what Claude can access
- **Context-Aware Responses** - Optional vault integration for informed answers
- **Safe by Default** - Vault access requires explicit permission
- **Granular Controls** - File-level and folder-level access controls

### 🛠️ **Developer-Friendly**
- **Tool Permission System** - Control which Claude Code tools are available
- **Session Export** - Save conversations for documentation or sharing
- **Performance Monitoring** - Built-in metrics for response times and token usage
- **Debug Mode** - Detailed logging for troubleshooting

## 📋 Requirements

### Essential Requirements
- **Obsidian Desktop App** - Version 1.0.0 or higher
- **Claude Code CLI** - [Install from claude.ai/code](https://claude.ai/code)
- **Active Claude Subscription** - Pro or higher recommended for best performance

### System Requirements
- **Operating System** - Windows 10+, macOS 10.15+, or Linux (Ubuntu 18.04+)
- **Memory** - 4GB RAM minimum, 8GB recommended
- **Storage** - 50MB for plugin, additional space for chat history

### Network Requirements
- **Internet Connection** - Required only for Claude API calls
- **Corporate Networks** - Supports proxy configurations and corporate firewalls

## 🚀 Installation

### Method 1: Manual Installation (Recommended)

1. **Download the Plugin**
   ```bash
   # Clone the repository
   git clone https://github.com/caioniehues/obsidian-copilot.git
   cd obsidian-copilot/plugin
   
   # Build the plugin
   npm install
   npm run build
   ```

2. **Install to Obsidian**
   ```bash
   # Create plugin directory (replace with your vault path)
   mkdir -p "/path/to/your/vault/.obsidian/plugins/obsidian-claude-cli-chat"
   
   # Copy plugin files
   cp main.js manifest.json styles.css "/path/to/your/vault/.obsidian/plugins/obsidian-claude-cli-chat/"
   ```

3. **Enable the Plugin**
   - Open Obsidian
   - Go to Settings → Community plugins
   - Find "Obsidian Claude CLI Chat" and enable it

### Method 2: Development Setup

For developers who want to modify the plugin:

```bash
# Clone and setup development environment
git clone https://github.com/caioniehues/obsidian-copilot.git
cd obsidian-copilot/plugin

# Install dependencies
npm install

# Start development mode (auto-rebuild on changes)
npm run dev

# Link to your vault for live testing
ln -sf "$PWD" "/path/to/your/vault/.obsidian/plugins/obsidian-claude-cli-chat"
```

### Verify Installation

1. **Check Claude CLI** - Ensure `claude` command works in terminal
2. **Plugin Status** - Confirm plugin appears in Obsidian's Community plugins list
3. **Chat Panel** - Look for the Claude chat icon in the Obsidian sidebar

## 📖 Usage

### Opening the Chat Panel

**Multiple ways to start chatting:**
- **Sidebar Icon** - Click the Claude icon in the left sidebar
- **Command Palette** - `Ctrl/Cmd + P` → "Open Claude Chat"
- **Hotkey** - Default: `Ctrl/Cmd + Shift + C` (customizable in settings)
- **Right-click Menu** - Right-click any note → "Chat with Claude about this note"

### Basic Chat Workflow

1. **Start a Conversation**
   ```
   Hello Claude! Can you help me organize my thoughts about quantum computing?
   ```

2. **Include Vault Context** (optional)
   ```
   Based on my notes about machine learning, what should I study next?
   ```

3. **Use Specific Commands**
   - `/help` - Show available commands
   - `/clear` - Clear current chat session
   - `/export` - Export chat to markdown file
   - `/settings` - Quick access to plugin settings

### Advanced Usage Patterns

**📝 Note Analysis**
```
Analyze this note and suggest improvements:
[Include specific note content]
```

**🔗 Cross-Note Synthesis**
```
Create a summary connecting my notes on:
- Productivity systems
- Time management 
- Goal setting
```

**📊 Research Assistance**
```
I'm researching [topic]. Based on my existing notes, what gaps should I fill?
```

## ⚙️ Settings Configuration

### Basic Settings

**Claude CLI Configuration**
- **CLI Path** - Auto-detected or manual path to Claude executable
- **Model Selection** - Choose preferred Claude model (if available)
- **Response Timeout** - Maximum wait time for responses (default: 60s)

**Chat Interface**
- **Panel Position** - Left or right sidebar placement
- **Message Limit** - Maximum messages to keep in memory (default: 100)
- **Auto-scroll** - Automatically scroll to new messages
- **Font Size** - Customize chat text size

### Vault Integration Settings

**Access Permissions**
- **Vault Access Mode** - None, Read-only, or Full access
- **Allowed Folders** - Specific folders Claude can access
- **Excluded Patterns** - File patterns to always exclude (e.g., `.private/`)
- **Context Limit** - Maximum vault content to include (default: 50KB)

**Context Strategy**
- **Smart Context** - Automatically select relevant notes
- **Full Vault** - Include entire vault (use with caution)
- **Manual Selection** - User chooses which notes to include
- **No Context** - Pure chat mode without vault integration

### Tool Permission Controls

**Available Tools** - Control which Claude Code tools are accessible:
- **File Operations** - Read, write, search files
- **Web Browsing** - Access external websites
- **Code Execution** - Run code snippets
- **System Commands** - Execute terminal commands

### Performance Settings

**Streaming Configuration**
- **Enable Streaming** - Real-time response display (recommended: on)
- **Chunk Size** - Size of response chunks for streaming
- **Typing Animation** - Visual typing indicator

**Caching Options**
- **Session Persistence** - Remember chats between Obsidian sessions
- **Message Caching** - Cache messages for faster loading
- **Auto-cleanup** - Automatically remove old chat data

## ✨ Features Deep Dive

### 🧠 Intelligent Context Integration

The plugin offers three levels of vault integration:

**Level 1: No Context**
Pure chat experience without vault access. Perfect for general questions and brainstorming.

**Level 2: Smart Context**
Claude automatically identifies and includes relevant notes based on your conversation. Uses intelligent matching to find connected content.

**Level 3: Full Vault Access**
Complete integration with your knowledge base. Claude can read, analyze, and reference any content in your vault.

### 📊 Session Management

**Persistent Sessions**
- Chats automatically save and restore between Obsidian sessions
- Organize conversations by topics or projects
- Quick access to recent conversations

**Export Capabilities**
- Export individual chats to markdown files
- Bulk export all conversations
- Include metadata (timestamps, context used)
- Custom export templates

### 🔍 Performance Monitoring

**Built-in Analytics**
- Response time tracking
- Token usage monitoring
- Error rate analysis
- Success metrics

**Debug Information**
- Detailed logs for troubleshooting
- Claude CLI communication status
- Context processing metrics
- Performance bottleneck identification

### 🎨 Customization Options

**Theme Integration**
- Automatically matches your Obsidian theme
- Custom CSS support for chat styling
- Dark/light mode compatibility
- Font and spacing customization

**Hotkey Configuration**
- Fully customizable keyboard shortcuts
- Context-sensitive actions
- Quick command access
- Multi-key combinations

## 🔧 Troubleshooting

### Common Issues and Solutions

#### Claude CLI Not Found

**Problem**: Plugin can't locate Claude CLI installation

**Solutions**:
1. **Verify Installation**
   ```bash
   # Test Claude CLI in terminal
   claude --version
   ```

2. **Manual Path Configuration**
   - Go to Plugin Settings → Claude CLI Path
   - Browse and select the Claude executable
   - Common locations:
     - macOS: `/usr/local/bin/claude`
     - Windows: `C:\Program Files\Claude\claude.exe`
     - Linux: `/usr/bin/claude`

3. **Environment Variables**
   ```bash
   # Add to your shell profile
   export PATH="/path/to/claude:$PATH"
   ```

#### Connection Issues

**Problem**: Plugin shows "Connection Failed" or timeouts

**Solutions**:
1. **Check Network**
   - Verify internet connection
   - Test Claude CLI directly: `claude chat "Hello"`
   
2. **Firewall/Proxy Settings**
   - Configure corporate proxy if needed
   - Whitelist Claude domains in firewall
   - Check with IT if in corporate environment

3. **Resource Limits**
   - Close other resource-intensive applications
   - Increase timeout in plugin settings
   - Monitor system memory usage

#### Performance Issues

**Problem**: Slow responses or high resource usage

**Solutions**:
1. **Optimize Context**
   - Reduce vault context size in settings
   - Use Smart Context instead of Full Vault
   - Exclude large files from context

2. **Session Management**
   - Clear old conversations regularly
   - Reduce message history limit
   - Enable auto-cleanup features

3. **System Resources**
   - Close unnecessary browser tabs
   - Monitor RAM usage
   - Consider upgrading hardware for large vaults

#### Vault Integration Problems

**Problem**: Claude can't access or understand vault content

**Solutions**:
1. **Permission Check**
   - Verify vault access is enabled in settings
   - Check folder permissions
   - Review excluded patterns

2. **Content Issues**
   - Ensure files are valid markdown
   - Check for encoding issues (use UTF-8)
   - Remove corrupted or binary files from context

3. **Context Limits**
   - Increase context limit if too restrictive
   - Use selective folder access
   - Break large vaults into sections

### Advanced Debugging

#### Enable Debug Mode

1. Open Plugin Settings
2. Go to Advanced → Debug Options
3. Enable "Verbose Logging"
4. Check Obsidian Developer Console (Ctrl/Cmd+Shift+I)

#### Log Files Location

- **Windows**: `%APPDATA%\obsidian\logs\claude-cli-chat\`
- **macOS**: `~/Library/Logs/obsidian/claude-cli-chat/`
- **Linux**: `~/.config/obsidian/logs/claude-cli-chat/`

#### Community Support

- **GitHub Issues** - [Report bugs and request features](https://github.com/caioniehues/obsidian-copilot/issues)
- **Obsidian Forum** - Community discussions and help
- **Discord** - Real-time support in Obsidian community servers

## 🛠️ Development

### Building from Source

**Prerequisites**
- Node.js 16+ and npm
- Git
- Claude CLI installed locally

**Build Steps**
```bash
# Clone repository
git clone https://github.com/caioniehues/obsidian-copilot.git
cd obsidian-copilot/plugin

# Install dependencies
npm install

# Development build (with file watching)
npm run dev

# Production build
npm run build

# Run tests
npm run test

# Lint code
npm run lint
```

### Testing Setup

**Unit Tests**
```bash
# Run all tests
npm test

# Watch mode for development
npm run test:watch

# Coverage report
npm run test:coverage
```

**Integration Tests**
```bash
# Test with real Claude CLI (requires setup)
npm run test:integration

# Mock tests (safe for CI/CD)
npm run test:mock
```

**Manual Testing**
1. Link plugin to development vault
2. Enable Developer Mode in Obsidian
3. Use browser DevTools for debugging
4. Monitor console for errors and warnings

### Contributing Guidelines

**Code Style**
- Use TypeScript for all new code
- Follow existing formatting conventions
- Include JSDoc comments for functions
- Use descriptive variable and function names

**Pull Request Process**
1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request with detailed description

**Issue Reporting**
- Use provided issue templates
- Include reproduction steps
- Attach relevant logs and screenshots
- Specify Obsidian and Claude CLI versions

### Architecture Overview

**Plugin Structure**
```
plugin/
├── src/
│   ├── main.ts              # Plugin entry point
│   ├── chat-view.ts         # Chat interface
│   ├── claude-client.ts     # Claude CLI communication
│   ├── settings.ts          # Configuration management
│   ├── vault-integration.ts # Obsidian vault access
│   └── utils/              # Utility functions
├── styles/
│   ├── main.css            # Core styles
│   └── themes/             # Theme-specific styles
├── tests/                  # Test suite
└── manifest.json           # Plugin metadata
```

**Key Components**

1. **ChatView** - Main UI component for chat interface
2. **ClaudeClient** - Handles communication with Claude CLI
3. **VaultIntegration** - Manages Obsidian vault access and context
4. **SettingsTab** - Configuration interface
5. **MessageHistory** - Session management and persistence

## 📊 Comparison with Complex RAG Systems

### Before: Complex RAG Architecture
```
Obsidian → Plugin → FastAPI Backend → Vector DB → OpenSearch → Claude API
         ↓
   - Multiple Docker containers
   - Complex setup process
   - API key management
   - Backend maintenance
   - Resource intensive
```

### After: Simplified Claude CLI Integration
```
Obsidian → Plugin → Claude CLI → Claude API
         ↓
   - Single plugin installation  
   - Zero configuration
   - No API key management
   - No backend required
   - Lightweight and fast
```

### Benefits of Simplification

| Aspect | Complex RAG | Claude CLI Integration |
|--------|-------------|------------------------|
| **Setup Time** | 30-60 minutes | 2-5 minutes |
| **Dependencies** | Docker, Python, OpenSearch | Claude CLI only |
| **Resource Usage** | High (multiple services) | Low (single process) |
| **Maintenance** | Regular updates required | Self-updating with Claude CLI |
| **Privacy** | Data processed by multiple services | Direct local processing |
| **Reliability** | Multiple failure points | Single, robust connection |

## 🔒 Privacy & Security

### Local-First Philosophy

**Your Data Stays Local**
- All vault processing happens on your machine
- No data transmitted except direct Claude API calls
- Complete control over what information is shared
- Optional vault integration (disabled by default)

**Security Measures**
- No telemetry or usage tracking
- Secure Claude CLI communication
- Configurable access permissions
- Audit logs for all vault access

### Corporate Environment Compatibility

**Enterprise Features**
- Proxy server support
- Corporate firewall compatibility  
- Zscaler and similar network security tools
- Compliance with data governance policies

## 🎯 Use Cases

### Personal Knowledge Management
- **Daily Journaling** - Process thoughts and experiences with Claude
- **Research Notes** - Analyze and synthesize research findings
- **Learning** - Ask questions about your study materials
- **Creative Writing** - Brainstorm ideas and get feedback

### Professional Workflows
- **Meeting Notes** - Summarize and extract action items
- **Project Planning** - Break down complex projects with Claude's help
- **Documentation** - Generate and improve technical documentation
- **Code Review** - Discuss code snippets and architectural decisions

### Academic Research
- **Literature Review** - Synthesize multiple research papers
- **Thesis Writing** - Organize thoughts and arguments
- **Data Analysis** - Discuss findings and interpretations
- **Citation Management** - Get help with references and formatting

## 📈 Performance Optimization

### Response Time Optimization
- **Streaming Enabled** - See responses as they're generated
- **Context Caching** - Reuse vault context across conversations
- **Smart Batching** - Optimize multiple requests
- **Async Processing** - Non-blocking UI operations

### Memory Management
- **Efficient Storage** - Minimal memory footprint for chat history
- **Garbage Collection** - Automatic cleanup of old data
- **Context Limits** - Configurable limits to prevent memory issues
- **Lazy Loading** - Load vault content only when needed

### Network Optimization
- **Connection Pooling** - Reuse Claude CLI connections
- **Request Batching** - Combine multiple operations
- **Retry Logic** - Intelligent retry on network failures
- **Offline Support** - Basic functionality without internet

## 🚀 Future Roadmap

### Short Term (Next Release)
- **Voice Input** - Speak questions directly to Claude
- **Note Templates** - Generate structured notes from conversations
- **Export Improvements** - Better formatting and sharing options
- **Performance Dashboard** - Real-time metrics and insights

### Medium Term (3-6 months)
- **Multi-Vault Support** - Switch between different Obsidian vaults
- **Collaborative Features** - Share conversations with team members
- **Custom Commands** - User-defined shortcuts and macros
- **Integration APIs** - Connect with other productivity tools

### Long Term (6+ months)
- **Mobile Support** - Obsidian mobile app compatibility
- **Advanced Analytics** - Conversation insights and patterns
- **Plugin Ecosystem** - Third-party extensions and integrations
- **Enterprise Features** - Team management and administration

## 🤝 Community & Support

### Getting Help
- **Documentation** - Comprehensive guides and tutorials
- **GitHub Issues** - Bug reports and feature requests
- **Community Forum** - User discussions and tips
- **Discord Chat** - Real-time community support

### Contributing
We welcome contributions from the community:
- **Code Contributions** - Bug fixes and new features
- **Documentation** - Improve guides and tutorials
- **Testing** - Help test new features and report issues
- **Community Support** - Help other users in forums

### Feedback
Your feedback helps improve the plugin:
- **Feature Requests** - Suggest new capabilities
- **User Experience** - Share workflow improvements
- **Performance Reports** - Help optimize for different use cases
- **Bug Reports** - Help identify and fix issues

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

### Third-Party Licenses
- **Obsidian API** - Obsidian's plugin development terms
- **Claude CLI** - Anthropic's terms of service
- **Dependencies** - Various open-source licenses (see package.json)

## 🐛 Troubleshooting

### Dependency Installation Issues (Fixed in Latest Version)

If you encounter npm installation errors with older versions, the issue has been resolved by upgrading:
- **TypeScript**: 4.7.4 → 4.8.4 (fixes msw compatibility)
- **@types/node**: v16 → v18 (fixes peer dependency conflicts)

**Solution**: Pull the latest changes and run:
```bash
cd plugin
rm -rf node_modules package-lock.json
npm install
npm run build
```

### Common Issues

**Claude CLI Not Found**
- Ensure Claude Code CLI is installed: `claude --version`
- Add Claude to your PATH if needed
- Restart Obsidian after installation

**Build Failures**
- Use Node.js v16 or higher
- Clear npm cache: `npm cache clean --force`
- Try with legacy peer deps: `npm install --legacy-peer-deps`

**Plugin Not Loading**
- Check Obsidian console for errors (Ctrl+Shift+I / Cmd+Option+I)
- Verify plugin files are in `.obsidian/plugins/obsidian-copilot/`
- Enable the plugin in Settings → Community plugins

## 🙏 Acknowledgments

This plugin builds on the excellent work of:
- **Original Obsidian Copilot** - Logan Yang and contributors
- **Obsidian Team** - For the amazing note-taking platform
- **Anthropic** - For Claude and the Claude CLI
- **Community Contributors** - Everyone who helped test and improve

Special thanks to the Obsidian plugin development community for their excellent documentation and examples.

---

<div align="center">
  <h3>🎉 Ready to supercharge your Obsidian experience with Claude?</h3>
  <p>
    <a href="#installation"><strong>Get Started →</strong></a> |
    <a href="#usage"><strong>Learn Usage →</strong></a> |
    <a href="#troubleshooting"><strong>Get Help →</strong></a>
  </p>
  <p><small>Built with ❤️ for the Obsidian + Claude community</small></p>
</div>