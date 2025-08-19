# Usage Guide

> Complete guide to using the Claude CLI Chat Plugin for Obsidian

## Getting Started

### Your First Chat

After [installing the plugin](./INSTALLATION.md), let's start your first conversation:

1. **Open the Chat Panel**
   - Press `Ctrl/Cmd + Shift + C`
   - Or click the Claude chat icon in the ribbon
   - Or use Command Palette: "Open Claude Chat"

2. **Send Your First Message**
   - Type your message in the input area
   - Press `Ctrl/Cmd + Enter` or click the Send button
   - Watch as Claude responds in real-time

3. **Handle the Response**
   - **Copy:** Click 📋 to copy response to clipboard
   - **Insert:** Click 📝 to insert at current cursor position
   - **Retry:** Click 🔄 to generate a new response

### First 10 Minutes Checklist

- [ ] Open chat panel and verify connection
- [ ] Send a test message and receive response
- [ ] Try inserting a response into a note
- [ ] Test the context feature with your current note
- [ ] Explore the settings to customize experience

## Chat Interface Overview

### Main Chat Panel

The chat interface is designed to integrate seamlessly with your Obsidian workflow:

```
┌─────────────────────────────────────────┐
│ Claude Code Chat               [⚙️] [×] │ ← Header with settings
├─────────────────────────────────────────┤
│ 💬 Conversation Area                    │ ← Message history
│                                         │
│  👤 Your questions and requests         │
│  🤖 Claude's responses                  │ ← With action buttons
│                                         │
│  📄 Context indicator                   │ ← Shows included content
├─────────────────────────────────────────┤
│ 📝 Message input area                   │ ← Type your messages
│ [Context: Current Note] [🔗] [📤]      │ ← Controls and send
└─────────────────────────────────────────┘
```

### Interface Elements

#### Message History
- **User messages** appear with your profile indicator
- **Claude responses** show with timestamp and action buttons
- **System messages** indicate context changes or status updates
- **Scroll behavior** automatically scrolls to newest messages

#### Action Buttons on Responses
- **📋 Copy** - Copy response text to clipboard (preserves formatting)
- **📝 Insert** - Insert response at current cursor position in active note
- **🆕 New Note** - Create a new note with the response content
- **📎 Append** - Add response to end of current note
- **🔄 Retry** - Generate a new response for the same prompt
- **✏️ Edit** - Edit the message and regenerate response

#### Context Indicator
Shows what content is being included with your messages:
- **Current Note** - Content from your active note
- **Selection** - Only your highlighted text
- **Multiple Files** - Content from linked notes
- **Custom** - Manually edited context

## Vault Integration and Context Features

### Context Modes

The plugin can automatically include relevant content with your messages:

#### 1. Current Note Mode (Default)
```
Context: Current Note (487 tokens)
┌─────────────────────────────────────┐
│ # My Research Notes                 │
│                                     │
│ This document contains information  │
│ about Claude integration...         │
└─────────────────────────────────── │
```

**When to use:** General questions about your current work

#### 2. Selection Mode
```
Context: Selection (134 tokens)
┌─────────────────────────────────────┐
│ > The key insight is that users     │
│ > need seamless AI integration      │
│ > without complexity.               │
└─────────────────────────────────── │
```

**When to use:** Questions about specific text you've highlighted

#### 3. No Context Mode
```
Context: None
┌─────────────────────────────────────┐
│ No content included                 │
└─────────────────────────────────── │
```

**When to use:** General questions unrelated to your notes

#### 4. Linked Notes Mode (Advanced)
```
Context: Current + Linked (1,247 tokens)
┌─────────────────────────────────────┐
│ Current: Research Notes             │
│ Linked: Project Timeline            │
│ Linked: Meeting Minutes             │
└─────────────────────────────────── │
```

**When to use:** Complex queries spanning multiple related notes

### Managing Context

#### Context Preview
Always review what's being shared:

1. **View Context Preview**
   - Click the context indicator to expand preview
   - See token count and content summary
   - Verify sensitive information before sending

2. **Edit Context**
   - Click "Edit Context" to modify content
   - Remove sensitive information
   - Add additional relevant context

3. **Context Token Management**
   - Monitor token usage (shown in preview)
   - Adjust token limits in settings
   - Use "Smart Truncation" for large contexts

#### Best Practices for Context
- **Be Specific:** Use selection mode for targeted questions
- **Review Before Sending:** Check context preview for sensitive data
- **Optimize for Relevance:** Include only relevant content
- **Monitor Token Usage:** Stay within limits for best performance

## Session Management and History

### Chat Sessions

The plugin supports multiple concurrent chat sessions:

#### Creating Sessions
1. **New Session:** `Ctrl/Cmd + Shift + N` or click "+ New"
2. **Name Sessions:** Click session title to rename
3. **Switch Sessions:** Click session tabs or use dropdown

#### Session Types
- **General Chat** - Default session for general questions
- **Project-Specific** - Focused conversations about specific projects
- **Research Sessions** - Deep research and analysis
- **Quick Queries** - Short, ephemeral conversations

### Chat History

#### Persistence
- **Auto-save:** Conversations save automatically
- **Cross-session:** History persists when Obsidian restarts
- **Sync-safe:** Compatible with Obsidian sync

#### Managing History
1. **Search Conversations**
   - Use search bar to find past messages
   - Filter by date, session, or content
   - Jump to specific conversations

2. **Clear History**
   - Individual messages: Right-click → Delete
   - Entire session: Session menu → Clear Session
   - All history: Settings → Clear All Data

#### History Limits
- **Default:** 500 messages per session
- **Configurable:** 100-2000 message range
- **Auto-cleanup:** Old messages archived automatically

## Export Functionality

### Export Options

Transform your conversations into permanent notes:

#### 1. Export as New Note
```markdown
# Claude Conversation - 2025-08-19

## Context
Current note: Research Notes (487 tokens)

## Conversation

**User (2:34 PM):** Can you help me understand the key concepts?

**Claude (2:35 PM):** Based on your research notes, the key concepts are:
1. Integration patterns
2. User experience design
3. Performance optimization
...

## Metadata
- Session: Research Session
- Model: claude-3-5-sonnet-20241022
- Duration: 15 minutes
- Messages: 8
```

#### 2. Insert Selected Messages
- Select specific messages to insert
- Maintain formatting and structure
- Include or exclude timestamps

#### 3. Export Session Summary
```markdown
# Session Summary: Project Planning

**Duration:** 45 minutes
**Topic:** New feature development
**Key Insights:**
- Technical approach clarified
- Timeline established  
- Resource requirements defined

**Action Items:**
1. [ ] Create technical specification
2. [ ] Schedule team review
3. [ ] Begin prototype development
```

### Export Formats

#### Markdown (Default)
- Native Obsidian format
- Preserves links and formatting
- Compatible with templates

#### Plain Text
- Simple text format
- Good for external use
- Lightweight and portable

#### JSON
- Complete conversation data
- Includes metadata and timestamps
- Useful for archiving or analysis

### Export Best Practices

1. **Regular Exports:** Export important conversations to permanent notes
2. **Organize by Topic:** Create dedicated folders for different conversation types
3. **Use Templates:** Create templates for consistent export formatting
4. **Tag Exports:** Use tags to categorize exported conversations
5. **Link to Original:** Maintain links to source notes and context

## Keyboard Shortcuts and Tips

### Default Shortcuts

| Action | Shortcut | Alternative |
|--------|----------|-------------|
| **Open Chat** | `Ctrl/Cmd + Shift + C` | Ribbon icon |
| **Send Message** | `Ctrl/Cmd + Enter` | Send button |
| **Insert Response** | `Ctrl/Cmd + Shift + I` | Insert button |
| **New Session** | `Ctrl/Cmd + Shift + N` | + New button |
| **Clear Session** | `Ctrl/Cmd + Shift + K` | Session menu |
| **Copy Last Response** | `Ctrl/Cmd + Shift + Y` | Copy button |
| **Retry Last** | `Ctrl/Cmd + R` | Retry button |

### Message Input Shortcuts

| Action | Shortcut | Description |
|--------|----------|-------------|
| **Send Message** | `Ctrl/Cmd + Enter` | Send current message |
| **New Line** | `Shift + Enter` | Add line break in message |
| **Clear Input** | `Ctrl/Cmd + K` | Clear message input |
| **Paste and Send** | `Ctrl/Cmd + Shift + V` | Paste and immediately send |
| **Toggle Context** | `Ctrl/Cmd + /` | Cycle through context modes |

### Navigation Shortcuts

| Action | Shortcut | Description |
|--------|----------|-------------|
| **Focus Input** | `/` | Quick focus on message input |
| **Scroll to Bottom** | `End` | Jump to newest message |
| **Scroll to Top** | `Home` | Jump to oldest message |
| **Next Session** | `Ctrl/Cmd + Tab` | Switch to next session |
| **Previous Session** | `Ctrl/Cmd + Shift + Tab` | Switch to previous session |

### Pro Tips

#### Input Efficiency
- **Multi-line Messages:** Use `Shift + Enter` for line breaks
- **Quick Commands:** Type `/help` for command reference
- **Template Messages:** Save common queries as snippets
- **Voice Input:** Use OS voice input features

#### Context Optimization
- **Smart Selection:** Select relevant text before asking questions
- **Context Switching:** Use `Ctrl/Cmd + /` to quickly change modes
- **Preview First:** Always check context before sending sensitive content
- **Batch Questions:** Ask multiple related questions in one context

#### Response Management
- **Immediate Insert:** Use `Ctrl/Cmd + Shift + I` right after response
- **Compare Responses:** Use retry feature to get different perspectives
- **Chain Conversations:** Reference previous responses in follow-up questions
- **Export Regularly:** Don't lose valuable insights

## Settings Configuration

### Basic Settings

Access settings via `Settings → Community Plugins → Claude CLI Chat → ⚙️`

#### Claude Configuration
```
┌─ Claude Settings ───────────────────────┐
│ CLI Path: [/usr/local/bin/claude      ] │ ← Auto-detected or manual
│ Model: [claude-3-5-sonnet-20241022  ▼] │ ← Available models
│ Temperature: [0.7] (0.0 - 2.0)         │ ← Response creativity
│ Max Tokens: [4000]                      │ ← Response length limit
│ Timeout: [30] seconds                   │ ← Request timeout
└─────────────────────────────────────────┘
```

#### Context Settings
```
┌─ Context Configuration ─────────────────┐
│ Default Mode: [Current Note        ▼]  │ ← Auto context mode
│ Token Limit: [4000]                     │ ← Context size limit
│ □ Include metadata                      │ ← File properties
│ ☑ Include links                         │ ← Internal links
│ ☑ Smart truncation                      │ ← Intelligent content cutting
│ Linked depth: [2] levels                │ ← How deep to follow links
└─────────────────────────────────────────┘
```

#### Interface Settings
```
┌─ Interface Preferences ─────────────────┐
│ Theme: [Auto (follows Obsidian)    ▼]  │ ← Light/dark theme
│ Font size: [14px]                       │ ← Chat text size
│ Panel position: [Right sidebar     ▼]  │ ← Where to show chat
│ ☑ Show timestamps                       │ ← Message timestamps
│ ☑ Enable sound notifications            │ ← Audio alerts
│ Animation: [Smooth              ▼]     │ ← UI transitions
└─────────────────────────────────────────┘
```

### Advanced Settings

#### Performance Tuning
```
┌─ Performance Options ───────────────────┐
│ Max sessions: [5]                       │ ← Concurrent sessions
│ History limit: [500] messages           │ ← Per-session limit
│ Cache size: [100MB]                     │ ← Response caching
│ ☑ Background processing                 │ ← Non-blocking operations
│ ☑ Lazy loading                          │ ← Load content on demand
│ Memory limit: [200MB]                   │ ← Plugin memory cap
└─────────────────────────────────────────┘
```

#### Privacy Controls
```
┌─ Privacy & Security ────────────────────┐
│ ☐ Send vault metadata                   │ ← File properties
│ ☑ Confirm before sharing large context  │ ← Privacy protection
│ ☑ Show context preview                  │ ← Always show what's shared
│ Data retention: [30] days               │ ← Auto-delete old chats
│ ☐ Enable telemetry                      │ ← Usage analytics
│ Export location: [claude-conversations] │ ← Default export folder
└─────────────────────────────────────────┘
```

### Customizing Shortcuts

1. **Open Shortcut Settings**
   - `Settings → Hotkeys`
   - Search for "Claude CLI Chat"

2. **Assign Custom Shortcuts**
   - Click on command to modify
   - Press desired key combination
   - Resolve conflicts if needed

3. **Common Customizations**
   - Gamers: Use `F1-F12` keys
   - Mac users: Use `Cmd + Option` combinations
   - Workflow-specific: Match your other tools

## Advanced Usage Patterns

### Research Workflows

#### Literature Review
1. **Gather Sources:** Collect papers and articles in notes
2. **Session Setup:** Create "Literature Review" session
3. **Contextual Analysis:** Include source notes as context
4. **Synthesis:** Ask Claude to identify themes and connections
5. **Export Results:** Create summary notes with findings

#### Comparative Analysis
1. **Multiple Documents:** Open related notes
2. **Linked Context:** Use "Current + Linked" mode
3. **Comparative Questions:** "Compare approaches in these documents"
4. **Generate Matrix:** Ask for comparison tables
5. **Visual Summaries:** Request diagrams or flowcharts

### Writing Workflows

#### Content Development
1. **Outline Creation:** Start with high-level structure
2. **Section Development:** Focus on one section at a time
3. **Selection Context:** Highlight specific paragraphs for improvement
4. **Iterative Refinement:** Use retry for different approaches
5. **Final Polish:** Grammar, style, and coherence checks

#### Academic Writing
1. **Research Phase:** Literature review and note-taking
2. **Structure Planning:** Outline with Claude's help
3. **Section Writing:** Draft sections with contextual support
4. **Citation Integration:** Ask about source integration
5. **Revision Cycles:** Multiple passes with different focuses

### Coding and Technical Work

#### Code Review and Debugging
1. **Include Code:** Copy code into notes or use selection
2. **Specific Questions:** Ask about specific functions or errors
3. **Best Practices:** Request code improvements
4. **Documentation:** Generate comments and documentation
5. **Testing:** Create test cases and examples

#### Learning and Exploration
1. **Concept Clarification:** Ask about new technologies
2. **Example Requests:** Get practical examples
3. **Troubleshooting:** Debug issues with context
4. **Best Practices:** Learn industry standards
5. **Project Planning:** Architecture and design discussions

### Team Collaboration

#### Meeting Preparation
1. **Agenda Creation:** Draft meeting agendas
2. **Background Research:** Gather context on topics
3. **Question Generation:** Prepare discussion questions
4. **Document Review:** Analyze shared documents
5. **Action Planning:** Create follow-up action items

#### Knowledge Sharing
1. **Documentation:** Create team documentation
2. **Onboarding:** Develop training materials
3. **Process Documentation:** Record workflows and procedures
4. **Decision Records:** Document important decisions
5. **FAQ Creation:** Build knowledge bases

## Next Steps

Now that you understand the core usage patterns:

1. **Practice Daily Integration** - Use Claude for regular note-taking tasks
2. **Explore Advanced Features** - Try different context modes and export options  
3. **Customize Your Setup** - Adjust settings and shortcuts to your workflow
4. **Build Workflows** - Develop consistent patterns for your common tasks
5. **Check Troubleshooting** - Review [TROUBLESHOOTING.md](./TROUBLESHOOTING.md) for common issues

---

**Happy Chatting!** 🎉

You're now equipped to make the most of Claude within your Obsidian workflow. Remember to experiment with different approaches to find what works best for your specific use cases.