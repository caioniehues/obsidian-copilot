# 🤖 Agent Commands Reference

> Complete guide to all agent commands and capabilities

## Agent Overview

| Agent | Type | Purpose | Trigger |
|-------|------|---------|---------|
| **Vault Analyzer** | Autonomous | Daily vault analysis | 2 AM daily / On-demand |
| **Synthesis Assistant** | Reactive | Multi-document synthesis | On-demand |
| **Context Optimizer** | Background | Performance optimization | Continuous |
| **Suggestion Engine** | Proactive | Real-time suggestions | Context-aware |
| **Research Assistant** | Interactive | Deep research | On-demand |

## Vault Analyzer Commands

### Basic Analysis
```markdown
## agent:analyze-vault
Run complete vault analysis now
```

### Focused Analysis
```markdown
## agent:analyze topic="machine learning"
Analyze specific topic across vault

## agent:analyze folder="Projects"
Analyze specific folder

## agent:analyze timeframe="7d"
Analyze recent changes only
```

### Pattern Detection
```markdown
## agent:patterns
Detect all patterns in vault

## agent:patterns timeframe="30d"
Patterns from last 30 days

## agent:patterns type="writing"
Specific pattern types
```

### Knowledge Gaps
```markdown
## agent:gaps
Find all knowledge gaps

## agent:gaps topic="AI"
Gaps in specific topic

## agent:gaps priority="high"
High-priority gaps only
```

### Trend Analysis
```markdown
## agent:trends
Identify emerging trends

## agent:trends timeframe="90d"
Long-term trend analysis
```

### Daily Report
```markdown
## agent:daily-report
View today's analysis report

## agent:report date="2024-01-15"
View specific date's report
```

## Synthesis Assistant Commands

### Basic Synthesis
```markdown
## agent:synthesize
Create synthesis from context

## agent:synthesize notes=["Note1", "Note2", "Note3"]
Synthesize specific notes
```

### Synthesis Types

#### Thematic Synthesis
```markdown
## agent:synthesize type=thematic
Group information by themes

## agent:synthesize type=thematic depth=3
Deep thematic analysis with sub-themes
```

#### Chronological Synthesis
```markdown
## agent:synthesize type=chronological
Create timeline from notes

## agent:synthesize type=chronological range="2024"
Timeline for specific period
```

#### Argumentative Synthesis
```markdown
## agent:synthesize type=argumentative
Build logical argument

## agent:synthesize type=argumentative thesis="AI will transform education"
Argument for specific thesis
```

#### Comparative Synthesis
```markdown
## agent:synthesize type=comparative
Compare and contrast perspectives

## agent:synthesize type=comparative items=["Method A", "Method B"]
Compare specific items
```

### Synthesis Options
```markdown
## agent:synthesize format=outline
Output as structured outline

## agent:synthesize format=summary
Concise summary format

## agent:synthesize format=report
Comprehensive report format

## agent:synthesize citations=true
Include all source citations

## agent:synthesize max_docs=20
Limit document count
```

## Context Optimizer Commands

The Context Optimizer runs automatically, but you can interact with it:

### Status Check
```markdown
## agent:optimizer-status
Check optimization status

## agent:cache-stats
View cache statistics
```

### Manual Optimization
```markdown
## agent:optimize
Run optimization now

## agent:optimize-index
Rebuild search indices

## agent:clear-cache
Clear all caches
```

### Performance Tuning
```markdown
## agent:tune performance="speed"
Optimize for speed

## agent:tune performance="accuracy"
Optimize for accuracy

## agent:tune performance="balanced"
Balanced optimization
```

## Suggestion Engine Commands

### Get Suggestions
```markdown
## agent:suggest
Get suggestions for current context

## agent:suggest type=related
Find related content

## agent:suggest type=next-actions
Suggest next steps

## agent:suggest type=queries
Suggest better queries
```

### Suggestion Control
```markdown
## suggestions:on
Enable proactive suggestions

## suggestions:off
Disable proactive suggestions

## suggestions:sensitivity=high
More frequent suggestions

## suggestions:sensitivity=low
Fewer suggestions
```

### Specific Suggestions
```markdown
## agent:suggest-connections
Find connection opportunities

## agent:suggest-synthesis
Suggest synthesis opportunities

## agent:suggest-research
Suggest research directions

## agent:suggest-improvements
Suggest note improvements
```

## Research Assistant Commands

### Basic Research
```markdown
## agent:research
Research current topic

## agent:research query="quantum computing"
Research specific topic
```

### Research Depth Levels

#### Exploratory Research
```markdown
## agent:research depth=exploratory
Broad survey of topic (30 min, 100 docs)

## agent:research depth=exploratory focus="applications"
Exploratory with focus area
```

#### Focused Research
```markdown
## agent:research depth=focused
Deep dive into topic (15 min, 20 docs)

## agent:research depth=focused questions=["Q1", "Q2"]
Focused on specific questions
```

#### Comprehensive Research
```markdown
## agent:research depth=comprehensive
Exhaustive analysis (60 min, 200 docs)

## agent:research depth=comprehensive output="paper"
Publication-ready research
```

### Research Types

#### Literature Review
```markdown
## agent:research type=literature_review
Systematic literature review

## agent:research type=literature_review criteria="peer-reviewed"
Review with specific criteria
```

#### Hypothesis Testing
```markdown
## agent:research type=hypothesis
Test hypothesis against vault

## agent:research type=hypothesis statement="X causes Y"
Test specific hypothesis
```

#### Evidence Gathering
```markdown
## agent:research type=evidence
Gather supporting evidence

## agent:research type=evidence claim="AI improves productivity"
Evidence for specific claim
```

#### Citation Tracking
```markdown
## agent:research type=citations
Track citation network

## agent:research type=citations source="[[Core Note]]"
Citations from specific source
```

### Research Options
```markdown
## agent:research format=report
Full research report

## agent:research format=outline
Research outline

## agent:research format=evidence-table
Evidence in table format

## agent:research include=external
Include external references

## agent:research exclude="Archive"
Exclude specific folders
```

## Combined Agent Workflows

### Research to Synthesis Pipeline
```markdown
## agent:research depth=comprehensive
Complete research on topic

## agent:synthesize type=thematic
Synthesize research findings

## agent:gaps based-on=synthesis
Identify remaining gaps
```

### Analysis to Action Pipeline
```markdown
## agent:analyze-vault
Run vault analysis

## agent:suggest based-on=analysis
Get suggestions from analysis

## Create action plan
Generate actionable steps
```

### Learning Enhancement Pipeline
```markdown
## agent:research type=literature_review
Review topic literature

## agent:synthesize type=outline
Create study outline

## agent:suggest type=next-actions
Suggest learning path
```

## Agent Configuration Commands

### View Configuration
```markdown
## agent:config
Show all agent configurations

## agent:config agent="vault-analyzer"
Show specific agent config
```

### Modify Settings
```markdown
## agent:config vault-analyzer schedule="weekly"
Change schedule

## agent:config suggestion-engine sensitivity="high"
Adjust sensitivity

## agent:config research-assistant timeout="120"
Set timeout
```

### Enable/Disable Agents
```markdown
## agent:enable vault-analyzer
Enable specific agent

## agent:disable suggestion-engine
Disable specific agent

## agent:status
Show all agent statuses
```

## Agent Memory Commands

### View Memories
```markdown
## agent:memories
View all agent memories

## agent:memories agent="vault-analyzer"
Specific agent's memories

## agent:memories type="pattern"
Specific memory types
```

### Memory Management
```markdown
## agent:learn
Store current context as learning

## agent:forget pattern="specific pattern"
Remove specific memory

## agent:reset-memory agent="suggestion-engine"
Reset agent's memory
```

## Special Commands

### Agent Collaboration
```markdown
## agents:collaborate task="comprehensive review"
Multiple agents work together

## agents:conference topic="project planning"
All agents provide input
```

### Batch Agent Operations
```markdown
## agents:batch
- analyze vault
- synthesize findings  
- suggest improvements
- research gaps
## agents:end-batch
```

### Agent Explanations
```markdown
## agent:explain
Explain last agent action

## agent:explain decision="suggestion"
Explain specific decision

## agent:reasoning
Show agent reasoning process
```

### Following Up on Agent Responses

After any agent response, you can:

```markdown
## explain
Get more detail about the response

## continue
Continue the thought or analysis

## refine with [new context]
Refine response with additional information

## synthesize this
Create synthesis from the response content
```

## Command Modifiers

### Universal Modifiers
These work with most agent commands:

```markdown
timeframe="7d"           # Time range
folder="Projects"        # Specific folder
tags="#important"        # Filter by tags
exclude="Archive"        # Exclude content
format="outline"         # Output format
verbose=true            # Detailed output
cache=false             # Skip cache
priority="high"         # Set priority
```

### Chaining Commands
```markdown
## agent:research | agent:synthesize
Chain research into synthesis

## agent:analyze > "Analysis Results"
Save output to note

## agent:suggest && agent:research
Run both if first succeeds
```

## Scheduling Commands

### One-time Scheduling
```markdown
## agent:schedule analyze-vault time="15:00"
Schedule for specific time

## agent:schedule research date="2024-01-20"
Schedule for specific date
```

### Recurring Schedules
```markdown
## agent:schedule-recurring vault-analyzer interval="daily"
Daily schedule

## agent:schedule-recurring synthesis interval="weekly" day="friday"
Weekly schedule
```

## API Integration

For programmatic access:

```bash
# Execute agent
curl -X POST http://localhost:8000/agents/vault-analyzer/execute

# Check status
curl http://localhost:8000/agents/vault-analyzer/status

# Get history
curl http://localhost:8000/agents/vault-analyzer/history
```

---

**Navigation**: [← Basic Usage](./basic-usage.md) | [Advanced Features →](./advanced-features.md)