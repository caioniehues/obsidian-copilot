# 🚀 Getting Started with Obsidian Copilot

> Your first 30 minutes with your new AI knowledge companion

## Your First 10 Minutes

### Minute 1-3: Test Basic Generation

Once everything is installed and running, open any note in Obsidian and type:

```markdown
## What is quantum computing?
```

Wait 5-10 seconds. You'll see Claude analyze your vault and generate a comprehensive response, incorporating any relevant notes you have.

**What's happening behind the scenes:**
1. The `##` trigger is detected
2. RAG searches your vault for relevant content
3. Context builds using your configured strategy
4. Claude processes up to 200K tokens
5. Response streams back to your note

### Minute 4-6: Try Your First Agent

Let's use the Synthesis Assistant to combine multiple notes:

```markdown
## agent:synthesize
Create a synthesis of my recent notes
```

The agent will:
- Find related recent notes
- Identify common themes
- Create a comprehensive synthesis
- Maintain source links

### Minute 7-10: Explore Suggestions

The Suggestion Engine is already watching. Try:

```markdown
## agent:suggest
What should I explore based on this note?
```

You'll get:
- Related notes you might have missed
- Knowledge gaps to fill
- Recommended next actions
- Query improvements

## Understanding the Basics

### The Double-Hash Trigger

The simplest way to interact is the `##` trigger:

```markdown
## Any question or request here
```

This works in any note, anywhere in your vault.

### Context Strategies

You have three ways to build context:

| Strategy | When to Use | Example |
|----------|-------------|---------|
| `full_docs` | Need complete understanding | `## strategy=full_docs`<br>`Analyze my complete PKM system` |
| `smart_chunks` | Balanced performance (default) | `## What are my thoughts on productivity?` |
| `hierarchical` | Quick overviews | `## strategy=hierarchical`<br>`Summarize my project notes` |

### The Five Agents

Each agent has a specific role:

1. **🔍 Vault Analyzer** - Runs nightly, finds patterns
2. **📝 Synthesis Assistant** - Combines multiple documents
3. **⚡ Context Optimizer** - Makes everything faster
4. **💡 Suggestion Engine** - Proactive recommendations
5. **🔬 Research Assistant** - Deep research tasks

## Your Daily Workflow

### Morning Routine (5 minutes)

1. **Check the overnight analysis:**
   ```markdown
   [[Agent Reports/Daily Analysis/2024-01-15]]
   ```
   
2. **Review suggestions for the day:**
   ```markdown
   ## agent:suggest type=daily
   What should I focus on today?
   ```

3. **Set your research agenda:**
   ```markdown
   ## agent:gaps
   What knowledge gaps should I address?
   ```

### During Work

**When writing:** Let suggestions guide you
```markdown
## continue
## expand this section
## find related notes
```

**When researching:** Use the Research Assistant
```markdown
## agent:research
Deep dive into [your topic]
```

**When synthesizing:** Combine your knowledge
```markdown
## agent:synthesize type=thematic
Connect my notes on [topic]
```

### Evening Review (3 minutes)

```markdown
## What did I learn today?
## agent:patterns timeframe="today"
## agent:synthesize type=chronological
Timeline of today's work
```

## Essential Commands

### Basic Queries
```markdown
## What are my notes about X?
## Summarize my meeting notes from this week
## Find connections between A and B
```

### Agent Commands
```markdown
## agent:synthesize          # Combine documents
## agent:research            # Deep research
## agent:suggest             # Get suggestions
## agent:analyze-vault       # Run analysis now
## agent:patterns            # Find patterns
```

### Context Control
```markdown
## strategy=full_docs       # Maximum context
## tokens=150000            # Set token limit
## timeframe="7d"           # Last 7 days only
## folder="Projects"        # Specific folder
```

## Understanding Responses

### Response Format
```markdown
## Your Query

### 🤖 Response from [Agent Name]
[Generated content with citations [[Note1]], [[Note2]]]

**Context used**: 45,231 tokens
**Documents analyzed**: 23
**Generation time**: 7.3s
**Confidence**: High
```

### Confidence Indicators
- **High**: Strong evidence from multiple sources
- **Medium**: Moderate evidence or single source
- **Low**: Limited evidence or inference

### Following Up
After any response:
- `## explain` - Get more detail
- `## continue` - Continue the thought
- `## refine` - Refine with new context
- `## synthesize this` - Create synthesis

## Tips for New Users

### Start Simple
1. Use basic `##` queries first
2. Try one agent at a time
3. Build complexity gradually

### Learn Your Agents
- **Vault Analyzer**: Check reports weekly
- **Synthesis**: Use for meeting prep
- **Suggestions**: Follow during exploration
- **Research**: Before starting projects

### Best Practices
1. **Be specific** in queries
2. **Use your tags** and [[links]]
3. **Try different strategies** for different needs
4. **Provide feedback** to help agents learn
5. **Check agent memories** to see learning

## Common First-Day Issues

### "No documents found"
- Check your vault path ends with `/`
- Rebuild indices: `make build-artifacts`
- Try broader search terms

### "Slow responses"
- Normal for first runs (building cache)
- Use `hierarchical` strategy for speed
- Context Optimizer will improve this

### "Agents not responding"
- They need time to learn (1-3 days)
- Check status: http://localhost:8000/agents/list
- Run manual analysis first

## What's Next?

### After Your First Day
1. Explore [Basic Usage](./basic-usage.md)
2. Learn [Agent Commands](./agent-commands.md)
3. Try [Advanced Features](./advanced-features.md)

### After Your First Week
1. Review agent memories
2. Customize agent settings
3. Develop personal workflows
4. Share successful patterns

## Quick Reference Card

### Most Used Commands
```markdown
## [question]                      # Basic query
## agent:synthesize                # Combine notes
## agent:suggest                   # Get suggestions
## agent:research                  # Deep research
## strategy=full_docs              # Max context
## continue                        # Continue response
```

### Keyboard Shortcuts

Configure in Obsidian settings:

- `Cmd/Ctrl + Shift + G` - Generate from selection
- `Cmd/Ctrl + Shift + S` - Synthesize current note
- `Cmd/Ctrl + Shift + R` - Research mode
- `Cmd/Ctrl + Shift + A` - Analyze vault

### Help Commands
```markdown
## help                            # Show help
## status                          # System status
## agents                          # List agents
```

---

**Navigation**: [← Setup](../setup/installation.md) | [Basic Usage →](./basic-usage.md)