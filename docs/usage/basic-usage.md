# 📖 Basic Usage Guide

> Core features and daily workflows with Obsidian Copilot

## Core Features

### The Foundation: Query and Response

The heart of Obsidian Copilot is simple: ask questions, get intelligent answers.

```markdown
## How do neural networks work?
```

This single line triggers a sophisticated process:
1. **Retrieval**: Searches your vault for relevant content
2. **Context Building**: Assembles up to 200K tokens of context
3. **Analysis**: Claude processes your knowledge base
4. **Generation**: Creates comprehensive, cited response

### Types of Queries

#### Information Retrieval
```markdown
## What are my notes about productivity?
## Summarize my thoughts on AI ethics
## Find connections between psychology and philosophy in my notes
```

#### Synthesis Requests
```markdown
## Create an outline from my project notes
## Combine my meeting notes from this week
## Build an argument from my research on climate change
```

#### Analysis Queries
```markdown
## What patterns exist in my daily notes?
## How has my thinking on X evolved?
## What knowledge gaps exist in my PKM system?
```

## Daily Workflows

### Morning Knowledge Review

Start your day with insights from overnight analysis:

```markdown
# Morning Review - {{date}}

## agent:analyze-vault
[[Agent Reports/Daily Analysis/{{date}}]]

## What should I focus on today?

## agent:gaps
What knowledge gaps need attention?
```

### Research Workflow

When diving into a new topic:

```markdown
# Research: [Topic Name]

## agent:research depth=exploratory
What do I already know about [topic]?

## Find all related notes

## agent:research depth=focused
Deep dive into [specific aspect]

## agent:synthesize
Create comprehensive summary
```

### Writing Workflow

For content creation:

```markdown
# Draft: [Document Name]

## Gather relevant materials

## agent:synthesize type=outline
Create structure from my notes

## Expand introduction section

## agent:suggest
What am I missing?

## agent:review
Check coherence and completeness
```

### Meeting Preparation

Before important meetings:

```markdown
# Meeting Prep: [Meeting Name]

## agent:synthesize timeframe="7d"
Summarize recent progress

## What are the key discussion points?

## agent:research
Background on attendee interests

## Generate agenda from notes
```

## Context Strategies Explained

### When to Use Each Strategy

#### Full Documents (`full_docs`)
**Use when you need:**
- Complete understanding of complex topics
- Detailed analysis with full context
- Comprehensive research reports
- Maximum accuracy over speed

**Example scenarios:**
```markdown
## strategy=full_docs
Analyze the complete theoretical framework in my philosophy notes

## strategy=full_docs tokens=180000
Use maximum context to understand my entire knowledge management system
```

#### Smart Chunks (`smart_chunks`)
**Use when you need:**
- Balanced performance and accuracy
- Standard research and synthesis
- Most day-to-day queries
- Good results without waiting

**Example scenarios:**
```markdown
## strategy=smart_chunks
What are the main themes in my psychology notes?

## Summarize my recent thoughts on productivity
(Uses smart_chunks by default)
```

#### Hierarchical (`hierarchical`)
**Use when you need:**
- Quick overviews and summaries
- Fast responses for simple queries
- Browsing and exploration
- Working with very large vaults

**Example scenarios:**
```markdown
## strategy=hierarchical
Give me a high-level overview of my projects

## strategy=hierarchical timeframe="24h"
Quick summary of today's notes
```

## Working with Retrieved Documents

### Understanding Context Display

When you make a query, you'll see:

```markdown
## Your Query

### Retrieved Documents
- [[Note 1]] (relevance: 0.92)
- [[Note 2]] (relevance: 0.87)
- [[Note 3]] (relevance: 0.85)

### Response
[Generated content with inline citations [[Note 1]]]
```

### Following Citations

Click any [[Note Name]] to:
- Jump to the source note
- Verify context
- Explore related content
- Continue research

### Refining Results

If results aren't quite right:

```markdown
## refine with more context about X
## exclude folder="Archive"
## focus on recent notes
## include tags="#important"
```

## Query Modifiers

### Timeframe Filters
```markdown
## timeframe="7d"        # Last 7 days
## timeframe="30d"       # Last month
## timeframe="today"     # Today only
## since="2024-01-01"    # Since specific date
```

### Content Filters
```markdown
## tags="#project,#active"     # Specific tags
## folder="Projects/Current"   # Specific folder
## exclude="Archive,Trash"     # Exclude folders
## author="@john"              # By author (if tracked)
```

### Output Control
```markdown
## format=bullet              # Bullet points
## format=outline            # Hierarchical outline
## format=table              # Table format
## length=brief              # Concise response
## length=comprehensive      # Detailed response
```

## Chaining Operations

Build complex workflows by chaining commands:

```markdown
## agent:research
Research everything about habit formation

## agent:synthesize type=thematic
Now synthesize the research by theme

## agent:suggest based-on=synthesis
What experiments could I try?

## Create action plan from suggestions
```

## Interactive Refinement

### Continuing Responses
```markdown
## continue
Continue where you left off

## expand section="Implementation"
Provide more detail on implementation

## elaborate with examples
Add concrete examples
```

### Clarifying and Correcting
```markdown
## clarify the second point
## correct: the date should be 2024
## rephrase in simpler terms
## translate to Spanish
```

## Batch Processing

Process multiple queries efficiently:

```markdown
## batch
1. Summarize all daily notes from this week
2. Find patterns across project notes  
3. Create synthesis of research notes
4. Generate weekly review
## end-batch
```

## Working with Templates

### Create from Template
```markdown
## template="Weekly Review"
Generate weekly review from template

## template="Research Note" topic="AI Safety"
Create research note on AI Safety
```

### Save as Template
```markdown
## save-template name="Meeting Notes"
Save this structure as a template
```

## Performance Tips

### For Faster Responses
1. Use `hierarchical` strategy
2. Limit timeframe with `timeframe="7d"`
3. Specify folders with `folder="specific"`
4. Use cached queries when possible

### For Better Accuracy
1. Use `full_docs` strategy
2. Include more context in query
3. Use specific tags and links
4. Provide examples of desired output

### For Large Vaults
1. Always specify timeframes
2. Use folder filters
3. Enable caching
4. Run Context Optimizer regularly

## Common Patterns

### Daily Note Integration
```markdown
# Daily Note {{date}}

## Morning
## agent:suggest type=daily
What should I focus on today?

## Evening  
## What did I accomplish today?
## agent:patterns timeframe="today"
```

### Project Documentation
```markdown
# Project: [Name]

## agent:synthesize folder="Projects/[Name]"
Current status summary

## agent:gaps
What's missing from this project?

## Generate next steps
```

### Learning Enhancement
```markdown
# Study: [Topic]

## agent:research
What do I know about [topic]?

## Create study guide

## agent:quiz
Generate practice questions

## agent:synthesize type=outline
Create comprehensive outline
```

---

**Navigation**: [← Getting Started](./getting-started.md) | [Agent Commands →](./agent-commands.md)