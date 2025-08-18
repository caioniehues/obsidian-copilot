# 🚀 Plugin-Only Installation Guide

> **Quick Start**: Get Obsidian Copilot running in 2 minutes without Docker or backend setup!

## Overview

This guide shows you how to install and use Obsidian Copilot as a **standalone plugin** - just like any other Obsidian community plugin. No Docker, no backend server, no complex setup required!

### What You Get

#### ✨ Direct Mode (No Backend)
- Direct API calls to Claude or OpenAI
- Instant setup - just add your API key
- Works immediately after installation
- No Docker or server required
- Perfect for trying out the plugin

#### 🚀 Enhanced Mode (Optional Backend)
- All Direct Mode features PLUS:
- RAG (Retrieval Augmented Generation) from your vault
- Semantic search across all notes
- Agent OS with 5 autonomous agents
- Advanced context strategies
- No API key needed (uses backend's)

## Installation Steps

### Step 1: Download the Plugin

#### Option A: From GitHub Release (Recommended)
1. Go to [Releases](https://github.com/caioniehues/obsidian-copilot/releases)
2. Download `obsidian-copilot.zip` from the latest release
3. Extract the zip file

#### Option B: Build from Source
```bash
# Clone the repository
git clone https://github.com/caioniehues/obsidian-copilot.git
cd obsidian-copilot/plugin

# Install dependencies and build
npm install
npm run build
```

### Step 2: Install to Obsidian

1. **Open your vault folder**
   - On Mac: `~/YourVault/.obsidian/plugins/`
   - On Windows: `C:\Users\YourName\YourVault\.obsidian\plugins\`
   - On Linux: `~/YourVault/.obsidian/plugins/`

2. **Create plugin folder**
   ```bash
   mkdir -p YourVault/.obsidian/plugins/obsidian-copilot
   ```

3. **Copy plugin files**
   
   You need these 3 files:
   - `main.js` - The plugin code
   - `manifest.json` - Plugin metadata
   - `styles.css` - Plugin styles

   ```bash
   # If you downloaded the release
   cp -r extracted-folder/* YourVault/.obsidian/plugins/obsidian-copilot/
   
   # If you built from source
   cp plugin/main.js plugin/manifest.json plugin/styles.css \
      YourVault/.obsidian/plugins/obsidian-copilot/
   ```

### Step 3: Enable the Plugin

1. Open Obsidian
2. Go to **Settings** → **Community plugins**
3. Turn off **Restricted mode** if not already done
4. Click **Reload plugins** button
5. Find **Copilot** in the list
6. Toggle the switch to **ON** ✅

### Step 4: Configure API Key

1. In Obsidian settings, click on **Copilot** plugin settings
2. Choose your **Operation Mode**:
   - **Auto (Recommended)** - Uses backend when available, API otherwise
   - **Direct API Only** - Always use your API key
   - **Backend Only** - Requires backend server

3. Select **API Provider**:
   - **Anthropic Claude** (Recommended)
   - **OpenAI**

4. Enter your **API Key**:
   - For Claude: Get from [console.anthropic.com](https://console.anthropic.com)
   - For OpenAI: Get from [platform.openai.com](https://platform.openai.com)

5. Configure **Model**:
   - Claude: `claude-3-5-sonnet-20241022` (default)
   - OpenAI: `gpt-4-turbo-preview` (default)

## Usage

### Basic Generation

In any note, type a heading followed by two hashtags:

```markdown
## What is machine learning?

[Copilot will generate content here]
```

### Commands

The plugin adds these commands (access with `Cmd/Ctrl + P`):

- **Copilot: Draft section** - Generate content for selected heading
- **Copilot: Draft section (no context)** - Generate without vault context
- **Copilot: Reflect on the week** - Weekly journal reflection

### Status Indicator

Look at the bottom status bar:
- `✨ Direct` - Using direct API calls
- `🚀 Enhanced` - Backend detected and active
- `⏳ Checking...` - Testing backend availability

## API Costs

### Anthropic Claude
- **Claude 3.5 Sonnet**: ~$3 per million input tokens, $15 per million output
- **Average cost**: $0.01-0.03 per generation
- **Monthly estimate**: $5-20 for regular use

### OpenAI
- **GPT-4 Turbo**: ~$10 per million input tokens, $30 per million output
- **Average cost**: $0.02-0.05 per generation
- **Monthly estimate**: $10-30 for regular use

💡 **Tip**: Both are much cheaper than ChatGPT Plus ($20/month) or Claude Pro ($20/month)!

## Optional: Add Backend Later

Want RAG and advanced features? You can add the backend anytime:

### Quick Backend Setup
```bash
# One-time setup
cd obsidian-copilot
export OBSIDIAN_PATH=/path/to/your/vault/
docker-compose -f docker-compose.simple.yml up
```

The plugin will automatically detect the backend and switch to Enhanced mode!

### Benefits of Adding Backend
- 🔍 Search across all your notes for relevant context
- 🧠 Semantic understanding of your knowledge base
- 🤖 5 autonomous agents for advanced tasks
- 💾 No API costs (can use Claude CLI)
- 📊 Advanced analytics and insights

## Troubleshooting

### Plugin Not Appearing
1. Make sure files are in correct folder: `.obsidian/plugins/obsidian-copilot/`
2. Files needed: `main.js`, `manifest.json`, `styles.css`
3. Reload Obsidian: `Cmd/Ctrl + R`
4. Check console for errors: `Cmd/Ctrl + Shift + I`

### API Key Issues
- **"Invalid API key"**: Check key is correct and has no extra spaces
- **"Rate limited"**: You've hit API limits, wait or upgrade plan
- **"No response"**: Check internet connection

### Generation Not Working
1. Check status bar for mode indicator
2. Verify API key is set in settings
3. Try "Direct API Only" mode
4. Check Obsidian console for errors

### Backend Detection
- Backend takes 30-60 seconds to start
- Check `http://localhost:8000/health` in browser
- Plugin checks every 30 seconds in Auto mode
- Use "Check Now" button in settings to test

## Comparison Table

| Feature | Direct Mode | With Backend |
|---------|------------|--------------|
| **Setup Time** | 2 minutes | 15 minutes |
| **Requirements** | API key only | Docker + Backend |
| **API Costs** | Yes (~$0.02/query) | Optional |
| **Vault Search** | ❌ | ✅ RAG |
| **Semantic Search** | ❌ | ✅ |
| **Agents** | ❌ | ✅ 5 agents |
| **Context Window** | Limited | 200K tokens |
| **Works Offline** | ❌ | ✅ (with local models) |

## Next Steps

### For Basic Users
1. Start using the plugin with your API key
2. Try different prompts and commands
3. Experiment with Claude vs OpenAI

### For Power Users
1. [Set up the backend](./installation.md) for full features
2. [Configure agents](../agents/overview.md)
3. [Customize context strategies](../features/claude-features.md)

## Support

- **GitHub Issues**: [Report bugs](https://github.com/caioniehues/obsidian-copilot/issues)
- **Documentation**: [Full docs](../README.md)
- **Community**: Join our Discord (coming soon)

---

**Remember**: You can always start simple with just the plugin and add the backend later when you want more features! 🎉