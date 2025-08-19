# Troubleshooting Guide

> Common issues and solutions for the Claude CLI Chat Plugin

## Quick Diagnostic Checklist

Before diving into specific issues, run through this quick checklist:

- [ ] Obsidian version 1.4.0+ installed
- [ ] Claude CLI Chat plugin enabled in Community plugins
- [ ] Claude Code CLI installed and accessible in terminal
- [ ] Internet connection active
- [ ] Plugin settings configured with correct CLI path

If all items check out but you're still having issues, continue to the specific problem sections below.

## Claude CLI Detection Problems

### Issue: "Claude CLI Not Found" Error

**Symptoms:**
- Red error message in plugin settings
- "Test Connection" fails
- Chat panel shows connection error

**Diagnostic Steps:**

1. **Verify CLI Installation**
   ```bash
   # Test if Claude CLI is installed and working
   claude --version
   
   # Expected output: Claude CLI version x.x.x
   # If command not found, Claude CLI is not installed properly
   ```

2. **Check Installation Path**
   ```bash
   # Windows (Command Prompt)
   where claude
   
   # macOS/Linux (Terminal)
   which claude
   
   # Note the exact path returned
   ```

3. **Verify PATH Environment Variable**
   ```bash
   # Check if CLI location is in PATH
   echo $PATH  # macOS/Linux
   echo %PATH%  # Windows
   ```

**Solutions:**

#### Solution 1: Reinstall Claude Code CLI
1. Visit [claude.ai/code](https://claude.ai/code)
2. Download the latest installer for your platform
3. Follow installation instructions completely
4. Restart terminal and test: `claude --version`

#### Solution 2: Manual Path Configuration
1. Find your Claude CLI location:
   ```bash
   find / -name "claude" 2>/dev/null  # Linux/macOS
   dir C:\ /s /b | findstr claude.exe  # Windows
   ```

2. Set the full path in plugin settings:
   ```
   Windows: C:\Users\[username]\AppData\Local\Claude\claude.exe
   macOS: /Applications/Claude.app/Contents/MacOS/claude
   Linux: /usr/local/bin/claude
   ```

#### Solution 3: Permission Issues (macOS/Linux)
```bash
# Make Claude CLI executable
chmod +x /path/to/claude

# Check ownership
ls -la /path/to/claude

# If owned by root, you may need sudo:
sudo chmod +x /path/to/claude
```

#### Solution 4: macOS Gatekeeper Issues
```bash
# Remove quarantine flag
sudo xattr -rd com.apple.quarantine /path/to/claude

# Or allow in System Preferences:
# System Preferences → Security & Privacy → General
# Click "Allow Anyway" for Claude CLI
```

### Issue: CLI Found But Authentication Fails

**Symptoms:**
- Plugin detects CLI correctly
- Messages fail to send
- "Authentication failed" errors

**Solutions:**

1. **Re-authenticate Claude CLI**
   ```bash
   # Sign out and back in
   claude auth logout
   claude auth login
   
   # Follow prompts to re-authenticate
   ```

2. **Check Account Status**
   ```bash
   # Verify authentication status
   claude auth status
   
   # Should show: Logged in as [your-email]
   ```

3. **Clear Authentication Cache**
   ```bash
   # Clear stored credentials
   claude auth clear
   claude auth login
   ```

## Performance Issues and Optimization

### Issue: Slow Response Times

**Symptoms:**
- Messages take >30 seconds to get responses
- UI freezes during message sending
- Timeout errors in chat

**Diagnostic Steps:**

1. **Check System Resources**
   - Open Task Manager/Activity Monitor
   - Look for high CPU or memory usage
   - Note if other applications are consuming resources

2. **Test CLI Directly**
   ```bash
   # Time a direct CLI request
   time claude "Hello, how are you?"
   
   # Should complete in <10 seconds typically
   ```

3. **Check Network Connection**
   ```bash
   # Test internet connectivity
   ping google.com
   curl -I https://claude.ai
   ```

**Solutions:**

#### Solution 1: Reduce Context Size
1. **Lower Token Limit**
   - Go to plugin settings
   - Reduce "Context Token Limit" to 2000 or less
   - Try "No Context" mode for testing

2. **Use Selection Mode**
   - Instead of "Current Note", use "Selection"
   - Highlight only relevant text before asking questions

#### Solution 2: Optimize System Performance
1. **Close Unnecessary Applications**
   - Close browser tabs, other editors
   - Stop background processes
   - Free up RAM

2. **Restart Obsidian**
   - Close and reopen Obsidian
   - Disable/re-enable the plugin
   - Clear plugin cache in settings

#### Solution 3: Network Optimization
1. **Check for Proxy/Firewall Issues**
   ```bash
   # Test direct connection
   curl -I https://api.anthropic.com
   
   # If blocked, configure proxy settings
   ```

2. **Use Different Network**
   - Try mobile hotspot
   - Switch to different WiFi network
   - Check with IT department about corporate firewalls

### Issue: High Memory Usage

**Symptoms:**
- Obsidian becomes sluggish over time
- System runs out of memory
- Plugin crashes with large conversations

**Solutions:**

1. **Clear Chat History**
   - Settings → Claude CLI Chat → Clear All Sessions
   - Or manually delete old sessions

2. **Reduce History Limits**
   - Settings → Claude CLI Chat → Advanced
   - Set "History limit" to 100-200 messages
   - Enable "Auto-cleanup old messages"

3. **Restart Plugin Regularly**
   - Disable and re-enable plugin daily
   - Or restart Obsidian completely

## Vault Integration Troubleshooting

### Issue: Context Not Being Included

**Symptoms:**
- Claude doesn't seem to see note content
- Responses ignore current note
- Context preview shows empty

**Diagnostic Steps:**

1. **Check Context Mode**
   - Verify context mode is set to "Current Note"
   - Look for context indicator in chat panel

2. **Verify Note Content**
   - Ensure current note has content
   - Check if note is saved (unsaved changes may not be included)

3. **Test with Simple Note**
   - Create a new note with simple text
   - Ask "What's in my current note?"

**Solutions:**

#### Solution 1: Refresh Context
1. Switch context mode to "None" and back to "Current Note"
2. Close and reopen the chat panel
3. Save current note and try again

#### Solution 2: Check Content Filters
1. Settings → Claude CLI Chat → Context
2. Verify "Include links" and other options are enabled
3. Check if content is being filtered out

#### Solution 3: Manual Context Override
1. Click context indicator to expand preview
2. Click "Edit Context" 
3. Manually paste note content
4. Save and send message

### Issue: Wrong Content Being Shared

**Symptoms:**
- Claude references different note than current
- Outdated content being shared
- Sensitive information accidentally included

**Immediate Actions:**
1. **Stop Current Session**
   - Click "Stop" if message is still sending
   - Clear current session: `Ctrl/Cmd + Shift + K`

2. **Review Context Preview**
   - Always check context preview before sending
   - Look for sensitive information
   - Verify correct content is selected

**Prevention Solutions:**

1. **Enable Context Confirmation**
   - Settings → Privacy & Security
   - Enable "Confirm before sharing large context"
   - Enable "Show context preview"

2. **Use Selection Mode for Sensitive Work**
   - Switch to "Selection" context mode
   - Manually highlight only relevant text
   - Review selection before sending

3. **Regular Context Audits**
   - Periodically review what content is being shared
   - Clear sessions containing sensitive information
   - Export important conversations before clearing

## Error Messages and Their Meanings

### Common Error Messages

#### "Claude CLI process failed to start"
**Meaning:** Plugin cannot launch the Claude CLI executable

**Solutions:**
- Verify CLI path in settings
- Check file permissions
- Ensure CLI is not corrupted

#### "Request timeout after 30 seconds"
**Meaning:** Claude API is taking too long to respond

**Solutions:**
- Check internet connection
- Reduce context size
- Retry with simpler message
- Check Claude API status

#### "Authentication token expired"
**Meaning:** Claude CLI authentication has expired

**Solutions:**
- Run `claude auth login` in terminal
- Restart plugin after re-authentication
- Check account status in Claude dashboard

#### "Maximum context length exceeded"
**Meaning:** Your message + context is too large for the model

**Solutions:**
- Reduce context token limit in settings
- Use "Selection" mode instead of "Current Note"
- Split large requests into smaller parts

#### "Network connection failed"
**Meaning:** Cannot reach Claude API servers

**Solutions:**
- Check internet connectivity
- Verify firewall/proxy settings
- Try different network connection

### Debug Information Collection

When reporting bugs, collect this information:

1. **System Information**
   ```bash
   # Operating system and version
   uname -a  # Linux/macOS
   systeminfo  # Windows
   
   # Claude CLI version
   claude --version
   
   # Node.js version (if applicable)
   node --version
   ```

2. **Plugin Information**
   - Obsidian version: Settings → About
   - Plugin version: Community plugins list
   - Enabled plugins: May conflict with other plugins

3. **Error Logs**
   - Open Developer Tools: `Ctrl/Cmd + Shift + I`
   - Copy Console errors
   - Note exact error messages

4. **Configuration**
   - CLI path setting
   - Context mode setting
   - Any custom shortcuts or settings

## Platform-Specific Issues

### Windows Issues

#### Issue: "Access Denied" Errors
**Causes:** Windows security policies, antivirus interference
**Solutions:**
- Run Obsidian as Administrator (temporary test)
- Add Claude CLI to antivirus whitelist
- Check Windows Defender SmartScreen settings

#### Issue: Command Prompt Flashing
**Causes:** CLI process visibility on Windows
**Solutions:**
- Update to latest plugin version
- Check for Windows security warnings
- Verify CLI installation integrity

#### Issue: Path with Spaces Problems
**Causes:** Windows path handling with spaces
**Solutions:**
- Use 8.3 filename format if needed
- Ensure path is properly quoted in settings
- Try moving CLI to path without spaces

### macOS Issues

#### Issue: "Operation Not Permitted"
**Causes:** macOS System Integrity Protection
**Solutions:**
```bash
# Check SIP status
csrutil status

# Add Obsidian to Full Disk Access:
# System Preferences → Security & Privacy → Privacy → Full Disk Access
```

#### Issue: Gatekeeper Blocking CLI
**Causes:** Unsigned executable restrictions
**Solutions:**
```bash
# Remove quarantine
sudo xattr -rd com.apple.quarantine /path/to/claude

# Or manually allow in Security preferences
```

#### Issue: PATH Issues with GUI Apps
**Causes:** GUI apps don't inherit terminal PATH
**Solutions:**
- Use full path to CLI in plugin settings
- Add CLI location to system PATH via .bash_profile
- Restart Obsidian after PATH changes

### Linux Issues

#### Issue: AppImage/Snap Permissions
**Causes:** Sandboxing restrictions
**Solutions:**
```bash
# For AppImage
chmod +x Obsidian.AppImage

# For Snap, check permissions
snap connections obsidian
```

#### Issue: Missing Dependencies
**Causes:** Missing shared libraries
**Solutions:**
```bash
# Check dependencies
ldd /path/to/claude

# Install missing libraries
sudo apt-get install libc6 libssl1.1  # Ubuntu/Debian
sudo yum install glibc openssl  # CentOS/RHEL
```

#### Issue: XDG Directory Issues
**Causes:** Non-standard directory structure
**Solutions:**
- Ensure `.obsidian` directory has correct permissions
- Check XDG_CONFIG_HOME environment variable
- Verify plugin directory structure

## FAQ - Frequently Asked Questions

### General Questions

**Q: Is my data secure when using this plugin?**
A: Yes. The plugin only sends what you explicitly include as context. No API keys are stored locally - authentication is handled by Claude CLI. Always review context preview before sending.

**Q: Can I use this offline?**
A: No, Claude requires an internet connection to function. The plugin needs to communicate with Claude's API through the CLI.

**Q: Does this work with Obsidian Sync?**
A: Yes, chat history and settings sync with Obsidian Sync. However, the Claude CLI must be installed on each device.

**Q: How much does this cost to use?**
A: The plugin is free. Claude usage is subject to Anthropic's pricing and limits. Check your Claude account for usage details.

### Technical Questions

**Q: Why do I need Claude Code CLI instead of API keys?**
A: Claude Code CLI provides better security, handles authentication automatically, and gives access to the latest Claude models without managing API keys.

**Q: Can I use different Claude models?**
A: Yes, you can select from available models in the plugin settings. Model availability depends on your Claude account level.

**Q: How do I backup my chat history?**
A: Chat history is stored in your vault's `.obsidian` directory. Export important conversations to notes for permanent storage.

**Q: Can I use this with multiple vaults?**
A: Yes, each vault has independent settings and chat history. You'll need to configure the plugin separately in each vault.

### Workflow Questions

**Q: How do I prevent sharing sensitive information?**
A: Enable "Show context preview" and "Confirm before sharing large context" in settings. Always review the context preview before sending messages.

**Q: Can I customize the chat interface appearance?**
A: Basic customization is available in settings (font size, theme). The interface follows Obsidian's theme automatically.

**Q: How do I share conversations with team members?**
A: Export conversations as notes, then share those notes through your normal Obsidian collaboration workflow.

**Q: What's the best way to organize exported conversations?**
A: Create a dedicated folder (e.g., "AI Conversations") and use consistent naming conventions. Tag exported notes for easy searching.

## Getting Additional Help

### Documentation Resources

1. **Installation Guide** - [INSTALLATION.md](./INSTALLATION.md)
2. **Usage Guide** - [USAGE.md](./USAGE.md)
3. **Project Documentation** - [../README.md](../README.md)

### Community Support

1. **GitHub Issues** - [Report bugs](https://github.com/caioniehues/obsidian-copilot/issues)
   - Use issue templates
   - Include diagnostic information
   - Search existing issues first

2. **GitHub Discussions** - [Ask questions](https://github.com/caioniehues/obsidian-copilot/discussions)
   - General questions and discussion
   - Feature requests
   - Community tips and tricks

3. **Obsidian Community** - [General Obsidian support](https://obsidian.md/community)
   - Discord server
   - Forum discussions
   - Plugin-specific channels

### Reporting Bugs

When reporting bugs, include:

1. **Environment Information**
   - Operating system and version
   - Obsidian version
   - Plugin version
   - Claude CLI version

2. **Problem Description**
   - Expected behavior
   - Actual behavior
   - Steps to reproduce
   - Error messages

3. **Diagnostic Data**
   - Console logs (Developer Tools → Console)
   - Plugin settings (screenshot)
   - Example messages that fail

4. **Workarounds Tried**
   - List what you've already attempted
   - Results of each attempt

### Contributing Fixes

If you've found a solution to a common problem:

1. **Update Documentation** - Submit PR with improved troubleshooting steps
2. **Share in Discussions** - Help other users with similar issues  
3. **Report Success** - Comment on issues when solutions work
4. **Suggest Improvements** - Ideas for preventing common problems

---

**Still Need Help?** 🤔

If you've worked through this guide and still can't resolve your issue:

1. Check the [GitHub Issues](https://github.com/caioniehues/obsidian-copilot/issues) for similar problems
2. Create a new issue with detailed information
3. Join the community discussions for real-time help
4. Consider reaching out through Obsidian's community channels

Remember: Most issues have simple solutions, and the community is always ready to help!