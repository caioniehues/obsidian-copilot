# Installation Guide

> Complete installation guide for the Claude CLI Chat Plugin for Obsidian

## Prerequisites

Before installing the Claude CLI Chat Plugin, ensure you have the following requirements:

### Required Software

1. **Obsidian** (Version 1.4.0 or later)
   - Download from [obsidian.md](https://obsidian.md)
   - Verify version: Settings → About → Current version

2. **Claude Code CLI** (Latest stable version)
   - Install from [claude.ai/code](https://claude.ai/code)
   - Follow the official installation instructions for your platform
   - Ensure CLI is available in your system PATH

### System Requirements

| Platform | Minimum Version | Recommended |
|----------|----------------|-------------|
| Windows | 10 (64-bit) | Windows 11 |
| macOS | 10.15 Catalina | macOS 12+ |
| Linux | Ubuntu 18.04+ | Ubuntu 22.04+ |

### Node.js (Development Only)
- **Version**: 16.x or later
- **Purpose**: Only required for building from source
- **Download**: [nodejs.org](https://nodejs.org)

## Installation Methods

### Method 1: Obsidian Community Plugins (Recommended)

1. **Open Obsidian Settings**
   - Click the settings icon (⚙️) or press `Ctrl/Cmd + ,`

2. **Navigate to Community Plugins**
   - Go to `Settings → Community plugins`
   - If this is your first community plugin, click "Turn on community plugins"

3. **Browse Plugins**
   - Click "Browse" to open the community plugin browser
   - Search for "Claude CLI Chat" or "Claude Code Chat"

4. **Install Plugin**
   - Click "Install" on the Claude CLI Chat Plugin
   - After installation completes, click "Enable"

5. **Initial Configuration**
   - The plugin settings will open automatically
   - Configure Claude Code CLI path (see [Configuration](#initial-configuration) below)

### Method 2: Manual Installation

1. **Download Plugin Files**
   - Visit the [GitHub releases page](https://github.com/caioniehues/obsidian-copilot/releases)
   - Download the latest `claude-cli-chat-plugin.zip` file

2. **Extract to Plugin Directory**
   ```bash
   # Navigate to your vault's plugin directory
   cd /path/to/your/vault/.obsidian/plugins/
   
   # Create plugin directory
   mkdir claude-cli-chat
   cd claude-cli-chat
   
   # Extract downloaded zip file
   unzip /path/to/claude-cli-chat-plugin.zip
   ```

3. **Enable in Obsidian**
   - Restart Obsidian or refresh plugins (`Ctrl/Cmd + R`)
   - Go to `Settings → Community plugins`
   - Find "Claude CLI Chat" and toggle it on

### Method 3: Development Installation

For developers or users who want the latest features:

1. **Clone Repository**
   ```bash
   cd /path/to/your/vault/.obsidian/plugins/
   git clone https://github.com/caioniehues/obsidian-copilot.git claude-cli-chat
   cd claude-cli-chat
   ```

2. **Install Dependencies**
   ```bash
   cd plugin
   npm install
   ```

3. **Build Plugin**
   ```bash
   npm run build
   ```

4. **Enable in Obsidian**
   - Restart Obsidian
   - Enable plugin in Community plugins settings

## Initial Configuration

After installation, you need to configure the plugin to work with your Claude Code CLI installation.

### 1. Open Plugin Settings

- Go to `Settings → Community plugins`
- Find "Claude CLI Chat" and click the settings icon (⚙️)

### 2. Configure Claude Code Path

The plugin needs to know where your Claude Code CLI is installed:

#### Automatic Detection
1. Click "Auto-detect Claude CLI"
2. The plugin will search common installation paths
3. If found, the path will be automatically filled

#### Manual Configuration
If auto-detection fails, set the path manually:

**Windows:**
```
C:\Users\[username]\AppData\Local\Claude\claude.exe
```

**macOS:**
```
/usr/local/bin/claude
```

**Linux:**
```
/usr/local/bin/claude
```

#### Verify Installation
1. Click "Test Connection" in the settings
2. You should see: ✅ "Claude Code CLI detected successfully"
3. If you see an error, check the [Troubleshooting](#troubleshooting-installation-issues) section

### 3. Basic Settings Configuration

Configure basic settings to match your preferences:

| Setting | Default | Description |
|---------|---------|-------------|
| **Default Model** | claude-3-5-sonnet-20241022 | Claude model to use for conversations |
| **Temperature** | 0.7 | Response creativity (0.0-2.0) |
| **Context Mode** | Current Note | What content to include automatically |
| **Token Limit** | 4000 | Maximum tokens for context |
| **Auto-save Chat** | Yes | Save conversations automatically |

### 4. Keyboard Shortcuts

Set up keyboard shortcuts for quick access:

| Action | Default Shortcut | Customizable |
|--------|-----------------|-------------|
| **Open Chat** | `Ctrl/Cmd + Shift + C` | ✅ |
| **Send Message** | `Ctrl/Cmd + Enter` | ✅ |
| **Insert Response** | `Ctrl/Cmd + Shift + I` | ✅ |
| **New Session** | `Ctrl/Cmd + Shift + N` | ✅ |

## Verification Steps

After installation and configuration, verify everything works:

### 1. Open Chat Panel
- Press `Ctrl/Cmd + Shift + C` or click the chat icon in the ribbon
- The chat panel should open in the sidebar

### 2. Send Test Message
1. Type "Hello, can you help me test this plugin?"
2. Press `Ctrl/Cmd + Enter` or click Send
3. You should see a response from Claude within a few seconds

### 3. Test Context Integration
1. Open a note with some content
2. In the chat, ask "What's in my current note?"
3. Claude should reference the content from your note

### 4. Test Response Insertion
1. Ask Claude to "Write a summary of productivity tips"
2. When the response arrives, click "Insert at Cursor"
3. The response should be inserted into your current note

## Troubleshooting Installation Issues

### Plugin Won't Load

**Symptoms:** Plugin doesn't appear in Community plugins list

**Solutions:**
1. **Check Obsidian Version**
   ```
   Settings → About → Current version should be 1.4.0+
   ```

2. **Verify Plugin Files**
   ```bash
   # Check if plugin directory exists
   ls /path/to/vault/.obsidian/plugins/claude-cli-chat/
   
   # Should contain: main.js, manifest.json, styles.css
   ```

3. **Check Console for Errors**
   - Press `Ctrl/Cmd + Shift + I` to open developer tools
   - Look for errors in the Console tab
   - Common issues: missing files, permission errors

4. **Restart Obsidian**
   - Close Obsidian completely
   - Reopen and check plugins again

### Claude Code CLI Not Detected

**Symptoms:** "Claude CLI not found" error in settings

**Solutions:**
1. **Verify CLI Installation**
   ```bash
   # Test Claude CLI manually
   claude --version
   
   # Should return version information
   ```

2. **Check PATH Environment Variable**
   ```bash
   # Windows (Command Prompt)
   where claude
   
   # macOS/Linux
   which claude
   ```

3. **Manual Path Configuration**
   - Find your Claude CLI installation location
   - Set the full path in plugin settings
   - Include the executable name (e.g., `claude.exe` on Windows)

4. **Permission Issues (macOS/Linux)**
   ```bash
   # Make CLI executable
   chmod +x /path/to/claude
   
   # Check ownership
   ls -la /path/to/claude
   ```

### Connection Errors

**Symptoms:** Messages fail to send, timeout errors

**Solutions:**
1. **Check Network Connection**
   - Ensure internet connectivity
   - Test Claude CLI manually: `claude "Hello"`

2. **Authentication Issues**
   ```bash
   # Re-authenticate Claude CLI
   claude auth login
   ```

3. **Firewall/Proxy Settings**
   - Check if corporate firewall blocks Claude API
   - Configure proxy settings if needed

4. **CLI Process Issues**
   - Restart Obsidian
   - Clear plugin data: `Settings → Claude CLI Chat → Reset Data`

### Performance Issues

**Symptoms:** Slow responses, UI freezing

**Solutions:**
1. **Check System Resources**
   - Close unnecessary applications
   - Monitor CPU and memory usage

2. **Reduce Context Size**
   - Lower token limit in settings
   - Use "Selection Only" context mode

3. **Clear Chat History**
   - `Settings → Claude CLI Chat → Clear All Sessions`

4. **Restart Plugin**
   - Disable and re-enable the plugin
   - Restart Obsidian if needed

### Platform-Specific Issues

#### Windows
- **Execution Policy:** May need to allow script execution
- **Antivirus:** Whitelist Claude CLI and Obsidian
- **Path Separators:** Use backslashes in paths

#### macOS
- **Gatekeeper:** Allow Claude CLI in Security & Privacy
- **Quarantine:** Remove quarantine attribute: `xattr -d com.apple.quarantine /path/to/claude`
- **homebrew Installation:** Ensure `/usr/local/bin` is in PATH

#### Linux
- **Package Managers:** Install via snap, flatpak, or AppImage
- **Permissions:** Ensure execute permissions on CLI
- **Dependencies:** Install required libraries for Claude CLI

## Getting Help

If you're still experiencing issues:

### 1. Check Documentation
- [Usage Guide](./USAGE.md) - Detailed usage instructions
- [Troubleshooting Guide](./TROUBLESHOOTING.md) - Common issues and solutions

### 2. Community Support
- [GitHub Issues](https://github.com/caioniehues/obsidian-copilot/issues) - Report bugs
- [GitHub Discussions](https://github.com/caioniehues/obsidian-copilot/discussions) - Ask questions
- [Obsidian Community](https://obsidian.md/community) - General Obsidian support

### 3. Bug Reports
When reporting issues, include:
- Operating system and version
- Obsidian version
- Claude CLI version
- Plugin version
- Error messages (from developer console)
- Steps to reproduce the issue

## Next Steps

Once installation is complete:

1. **Read the Usage Guide** - [USAGE.md](./USAGE.md) for detailed feature overview
2. **Explore Chat Features** - Learn about context modes and response handling
3. **Customize Settings** - Adjust the plugin to your workflow preferences
4. **Set Up Workflows** - Integrate Claude into your daily note-taking routine

---

**Installation Complete!** 🎉 

You're now ready to use Claude directly within Obsidian. Open the chat panel (`Ctrl/Cmd + Shift + C`) and start your first conversation.