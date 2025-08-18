# 📚 Obsidian Copilot User Guide

> Your complete guide to using Obsidian Copilot with Agent OS

## Table of Contents

1. [Getting Started](#getting-started)
2. [Basic Usage](#basic-usage)
3. [Working with Agents](#working-with-agents)
4. [Context Strategies](#context-strategies)
5. [Daily Workflows](#daily-workflows)
6. [Advanced Features](#advanced-features)
7. [Tips & Best Practices](#tips--best-practices)
8. [Command Reference](#command-reference)

## Getting Started

### Your First Query

The simplest way to use Obsidian Copilot is the double-hash trigger:

```markdown
## How do neural networks learn?
```

Simply type this in any note, wait 5-10 seconds, and watch as Claude analyzes your vault and generates a comprehensive response.

### How It Works

1. **You type** a question after `##`
2. **RAG retrieves** relevant notes from your vault
3. **Context builds** using your chosen strategy
4. **Claude analyzes** with up to 200K tokens
5. **Response appears** below your question

## Basic Usage

### Simple Questions

Ask anything, and Copilot searches your vault for context:

```markdown
## What are my thoughts on productivity?
## Summarize my meeting notes from last week
## What connections exist between my psychology and philosophy notes?
```

### Direct Commands

Control behavior with inline commands:

```markdown
## strategy=full_docs
Comprehensive analysis of my research on consciousness

## tokens=180000
Use maximum context to analyze my entire PKM system

## focus=recent
What have I been learning about lately?
```

## Working with Agents

### The 5 Agents at Your Service

#### 1. 🔍 Vault Analyzer (Autonomous)

Runs daily at 2 AM, analyzing your entire vault.

**Check the daily report:**
```markdown
[[Agent Reports/Daily Analysis/2024-01-15]]
```

**Run manually:**
```markdown
## agent:analyze-vault
```

**Focused analysis:**
```markdown
## agent:analyze topic="machine learning"
Analyze my machine learning notes specifically
```

#### 2. 📝 Synthesis Assistant (On-Demand)

Creates comprehensive syntheses from multiple documents.

**Basic synthesis:**
```markdown
## agent:synthesize
Create a synthesis of my notes on habits
```

**Thematic synthesis:**
```markdown
## agent:synthesize type=thematic
Group my psychology notes by theme
```

**Chronological synthesis:**
```markdown
## agent:synthesize type=chronological
Timeline of my project development notes
```

**Comparative synthesis:**
```markdown
## agent:synthesize type=comparative docs=["Note1", "Note2", "Note3"]
Compare different productivity systems I've studied
```

#### 3. ⚡ Context Optimizer (Background)

Works continuously to improve performance. No commands needed - it just makes everything faster!

**Check optimization status:**
```bash
curl http://localhost:8000/agents/context-optimizer/status
```

#### 4. 💡 Suggestion Engine (Proactive)

Watches as you work and provides suggestions.

**Enable/disable suggestions:**
```markdown
## suggestions:on
## suggestions:off
```

**Get suggestions for current note:**
```markdown
## agent:suggest
What should I explore related to this note?
```

#### 5. 🔬 Research Assistant (Interactive)

Conducts deep research across your vault.

**Basic research:**
```markdown
## agent:research
Research the evolution of my thoughts on AI
```

**Comprehensive research:**
```markdown
## agent:research depth=comprehensive
Exhaustive analysis of my knowledge management system
```

**Literature review:**
```markdown
## agent:research type=literature_review
Review all my notes on cognitive science
```

**Hypothesis testing:**
```markdown
## agent:research type=hypothesis
Test: "My productivity increases with time-blocking"
```

## Context Strategies

### Choosing the Right Strategy

| Strategy | Best For | Token Usage | Speed |
|----------|----------|-------------|--------|
| `full_docs` | Deep understanding, comprehensive analysis | 150K-200K | Slower (10-15s) |
| `smart_chunks` | Balanced performance, most queries | 50K-100K | Moderate (5-10s) |
| `hierarchical` | Large vaults, quick responses | 30K-50K | Fast (2-5s) |

### Strategy Examples

**Full Documents** - When you need complete context:
```markdown
## strategy=full_docs
Analyze the complete argument structure in my philosophy notes
```

**Smart Chunks** - For balanced performance:
```markdown
## strategy=smart_chunks
What are the main themes in my research notes?
```

**Hierarchical** - For quick overviews:
```markdown
## strategy=hierarchical
Give me a high-level summary of my PKM system
```

## Daily Workflows

### Morning Routine

1. **Check overnight analysis:**
   ```markdown
   [[Agent Reports/Daily Analysis/{{date}}]]
   ```

2. **Review suggestions:**
   ```markdown
   ## agent:suggestions type=morning
   What should I focus on today?
   ```

3. **Set research agenda:**
   ```markdown
   ## agent:research type=agenda
   What knowledge gaps should I address?
   ```

### Research Workflow

1. **Start with exploration:**
   ```markdown
   ## agent:research depth=exploratory
   What do I know about [topic]?
   ```

2. **Identify gaps:**
   ```markdown
   ## agent:gaps topic="[topic]"
   What's missing from my understanding?
   ```

3. **Deep dive:**
   ```markdown
   ## agent:research depth=comprehensive
   Complete analysis of [specific aspect]
   ```

4. **Synthesize findings:**
   ```markdown
   ## agent:synthesize type=argumentative
   Build argument from my research on [topic]
   ```

### Writing Workflow

1. **Gather relevant notes:**
   ```markdown
   ## related to="current topic"
   Find all relevant materials
   ```

2. **Create outline:**
   ```markdown
   ## agent:synthesize type=outline
   Create structured outline from my notes
   ```

3. **Fill sections:**
   ```markdown
   ## expand section="[section name]"
   Elaborate on this section using my notes
   ```

4. **Check coherence:**
   ```markdown
   ## agent:review
   Review this draft for consistency with my notes
   ```

## Advanced Features

### Multi-Note Synthesis

Synthesize specific sets of notes:

```markdown
## agent:synthesize notes=["Project A", "Project B", "Lessons Learned"]
Create synthesis connecting these specific notes
```

### Pattern Detection

Find patterns across time:

```markdown
## agent:patterns timeframe="30d"
What patterns emerged in the last month?
```

### Knowledge Graph Exploration

Explore connections:

```markdown
## agent:graph center="Machine Learning"
Map connections from machine learning to other topics
```

### Custom Agent Behavior

Modify agent focus:

```markdown
## agent:config vault-analyzer focus=["AI", "productivity", "philosophy"]
Configure analyzer to focus on specific topics
```

### Batch Processing

Process multiple queries:

```markdown
## batch
1. Summarize my daily notes from last week
2. Find connections between projects
3. Identify recurring themes
## end-batch
```

## Tips & Best Practices

### For Better Results

1. **Be specific** with queries
   - ❌ "Tell me about productivity"
   - ✅ "How has my understanding of productivity evolved over the last 6 months?"

2. **Use context clues**
   - ❌ "Summarize the meeting"
   - ✅ "Summarize my meeting notes tagged #client-meeting from this week"

3. **Leverage your tags and links**
   - The system understands Obsidian's `[[links]]` and `#tags`
   - Reference them in queries for better targeting

### For Faster Responses

1. **Use hierarchical strategy** for overviews
2. **Limit scope** with timeframes or tags
3. **Cache common queries** with `## cache:save name="query-name"`
4. **Disable unused agents** to free resources

### For Deeper Analysis

1. **Use full_docs strategy** for complete context
2. **Chain queries** to build understanding
3. **Combine agents** for comprehensive research
4. **Review agent memories** to understand their learning

### Agent Collaboration Examples

**Research → Synthesis flow:**
```markdown
## agent:research
Research everything about habit formation

## agent:synthesize type=thematic
Now synthesize those research findings by theme
```

**Analysis → Suggestions flow:**
```markdown
## agent:analyze topic="current project"
Analyze my current project notes

## agent:suggest based-on=analysis
What should I explore next?
```

## Command Reference

### Basic Queries
- `## [question]` - Ask anything
- `## strategy=[type] [question]` - Specify context strategy
- `## tokens=[number] [question]` - Set max tokens
- `## focus=[area] [question]` - Focus on specific area

### Agent Commands

#### Vault Analyzer
- `## agent:analyze-vault` - Run full analysis
- `## agent:analyze topic="[topic]"` - Focused analysis
- `## agent:patterns` - Detect patterns
- `## agent:gaps` - Find knowledge gaps

#### Synthesis Assistant
- `## agent:synthesize` - Basic synthesis
- `## agent:synthesize type=thematic` - By themes
- `## agent:synthesize type=chronological` - Timeline
- `## agent:synthesize type=comparative` - Compare
- `## agent:synthesize type=argumentative` - Build argument

#### Research Assistant
- `## agent:research` - Basic research
- `## agent:research depth=exploratory` - Broad survey
- `## agent:research depth=focused` - Specific topic
- `## agent:research depth=comprehensive` - Exhaustive
- `## agent:research type=hypothesis` - Test hypothesis
- `## agent:research type=literature_review` - Review sources

#### Suggestion Engine
- `## agent:suggest` - Get suggestions
- `## suggestions:on/off` - Toggle suggestions
- `## agent:suggest type=next-actions` - Next steps
- `## agent:suggest type=related` - Related content

### Context Control
- `## strategy=full_docs` - Complete documents
- `## strategy=smart_chunks` - Intelligent chunks
- `## strategy=hierarchical` - Hierarchical context
- `## tokens=150000` - Set token limit
- `## cache:save name="[name]"` - Cache query
- `## cache:load name="[name]"` - Load cached

### Filtering
- `## timeframe="7d"` - Last 7 days
- `## tags="#tag1,#tag2"` - Specific tags
- `## folder="Projects"` - Specific folder
- `## exclude="Archive"` - Exclude folder

### Special Commands
- `## batch ... ## end-batch` - Multiple queries
- `## explain` - Explain last response
- `## continue` - Continue previous response
- `## refine` - Refine previous response

## Keyboard Shortcuts

Configure in Obsidian settings:

- `Cmd/Ctrl + Shift + G` - Generate from selection
- `Cmd/Ctrl + Shift + S` - Synthesize current note
- `Cmd/Ctrl + Shift + R` - Research mode
- `Cmd/Ctrl + Shift + A` - Analyze vault

## Understanding Agent Responses

### Response Format

```markdown
## Your Query

### 🤖 Response from [Agent Name]
[Generated content]

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

After any response, you can:
- `## explain` - Get more detail
- `## continue` - Continue the thought
- `## refine with [new context]` - Refine with additional info
- `## synthesize this` - Create synthesis from response

## Troubleshooting Common Issues

### "No relevant documents found"
- Check your vault path ends with `/`
- Rebuild indices: `make build-artifacts`
- Try broader search terms

### "Response cut off"
- Increase token limit: `## tokens=180000`
- Use `## continue` to get rest

### "Slow responses"
- Switch to `hierarchical` strategy
- Reduce token limit
- Check if Context Optimizer is running

### "Agents not responding"
- Check status: `curl http://localhost:8000/agents/list`
- Restart scheduler: `make restart-scheduler`
- Check logs: `.agent-os/logs/`

## Learning from Agent Memories

### View What Agents Learned

Search your vault for agent memories:

```markdown
tag:#agent:vault-analyzer
tag:#type:pattern
tag:#type:insight
tag:#type:preference
```

### Understanding Memory Structure

```markdown
# Pattern Memory
**Agent**: vault-analyzer
**Type**: pattern

## Observations
- [pattern] You frequently research AI ethics
- [frequency] 15 times in last month
- [confidence] 0.92

## Relations
- relates_to [[AI Research]]
- influences [[Writing Topics]]
```

### Using Memories

Agent memories improve their performance:
- Patterns help predict your needs
- Preferences customize responses
- Insights guide suggestions
- Feedback improves accuracy

## Best Practices Summary

1. **Start Simple**: Use basic `##` queries first
2. **Learn Agents**: Try each agent individually
3. **Find Your Flow**: Develop personal workflows
4. **Review Learning**: Check agent memories weekly
5. **Provide Feedback**: Help agents learn your preferences
6. **Experiment**: Try different strategies and commands
7. **Chain Operations**: Combine agents for power workflows

---

**Pro Tip**: The more you use the system, the smarter it gets. Agents learn from every interaction and share knowledge to better serve your needs.

For technical details, see [AGENTS.md](./AGENTS.md). For API usage, see [API.md](./API.md).