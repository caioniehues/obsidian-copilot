# Agent OS Documentation

## Overview

Agent OS transforms Obsidian Copilot from a reactive query tool into a proactive knowledge companion. Five specialized agents work autonomously and collaboratively to enhance your knowledge management experience.

## Agent Types and Capabilities

### 1. Vault Analyzer Agent

**Type**: Autonomous  
**Schedule**: Daily at 2:00 AM  
**Purpose**: Continuously analyze your vault for patterns, connections, and insights

#### Capabilities
- **Pattern Detection**: Identifies recurring themes and concepts across your vault
- **Connection Discovery**: Finds non-obvious relationships between disparate notes
- **Knowledge Gap Analysis**: Identifies areas where information is missing or incomplete
- **Trend Identification**: Detects emerging topics and evolving themes over time
- **Quality Assessment**: Evaluates the completeness and interconnectedness of notes

#### Daily Analysis Protocol
1. **Data Collection** (0-10 min): Gather changed notes and metadata
2. **Pattern Analysis** (10-20 min): Extract themes, analyze links and tags
3. **Deep Analysis** (20-30 min): Semantic clustering, knowledge graph analysis
4. **Insight Generation** (30-40 min): Generate connections and gap identification
5. **Report Generation** (40-45 min): Create comprehensive markdown report

#### Output Example
```markdown
# Daily Vault Analysis Report
Date: 2024-01-15
Notes Analyzed: 127

## Executive Summary
- Emerging theme: "Agent architectures" (15 new mentions)
- Knowledge gap: Missing documentation on error handling
- Connection opportunity: Link "AI Ethics" notes with "Agent Design"

## New Patterns Detected
### Theme: Autonomous Systems
- Related notes: [[Agent Design]], [[Self-Learning Systems]]
- Growth: 300% over last week
```

### 2. Synthesis Assistant Agent

**Type**: Reactive  
**Trigger**: On-demand via commands  
**Purpose**: Create comprehensive syntheses from multiple documents

#### Capabilities
- **Multi-Document Synthesis**: Combine insights from 2-50 documents
- **Thematic Synthesis**: Organize information by themes
- **Chronological Synthesis**: Create timelines from scattered events
- **Argumentative Synthesis**: Build coherent arguments from evidence
- **Comparative Synthesis**: Compare and contrast perspectives

#### Synthesis Strategies

##### Thematic Synthesis
Groups and organizes information by themes:
- Identifies major themes across documents
- Creates hierarchical theme structures
- Maps sub-themes and variations

##### Chronological Synthesis
Organizes information temporally:
- Creates timelines from scattered events
- Tracks development of ideas over time
- Identifies causal chains

##### Argumentative Synthesis
Builds coherent arguments:
- Collects supporting evidence
- Identifies counter-arguments
- Evaluates argument strength

#### Command Usage
```markdown
## agent:synthesize
Synthesize my notes on machine learning

## agent:synthesize type=chronological
Create a timeline of my project notes

## agent:synthesize type=comparative
Compare perspectives on remote work
```

### 3. Context Optimizer Agent

**Type**: Background  
**Schedule**: Continuous (checks every 5 minutes)  
**Purpose**: Optimize retrieval and context building for maximum efficiency

#### Capabilities
- **Index Optimization**: Maintains search indices for peak performance
- **Cache Management**: Intelligent caching of frequently accessed content
- **Query Pattern Learning**: Learns from usage to improve future queries
- **Token Allocation**: Optimizes Claude's 200K context window usage
- **Performance Tuning**: Continuously improves response times

#### Optimization Strategies

##### Token Budget Allocation
```
Critical Context:     40% (60K tokens)
Relevant Context:     30% (45K tokens)
Supporting Context:   20% (30K tokens)
Peripheral Context:   10% (15K tokens)
```

##### Cache Architecture
- **Hot Cache** (Memory): 100MB, 1-hour TTL
- **Warm Cache** (Redis): 500MB, 24-hour TTL
- **Cold Cache** (Disk): 2GB, 7-day TTL

#### Performance Metrics
- Query latency p50: < 500ms
- Cache hit rate: > 60%
- Token utilization: > 80%
- Context quality score: > 0.75

### 4. Suggestion Engine Agent

**Type**: Proactive  
**Trigger**: Context-aware (monitors active note changes)  
**Purpose**: Provide intelligent, proactive recommendations

#### Capabilities
- **Related Content Discovery**: Find conceptually related documents
- **Query Enhancement**: Suggest improved search strategies
- **Workflow Optimization**: Recommend next actions
- **Knowledge Gap Alerts**: Identify missing information
- **Pattern Recognition**: Highlight emerging patterns

#### Suggestion Types

##### Content Suggestions
```markdown
## Related Note Found
**Title**: Advanced RAG Techniques
**Relevance**: 92%
**Why this matters**: Contains complementary research 
that extends your current analysis on retrieval systems.
```

##### Analysis Suggestions
```markdown
## Synthesis Opportunity Detected
**Documents**: 5 related notes on AI ethics
**Potential insights**:
- Convergent ideas across notes
- Unresolved contradictions
**Suggested action**: Create synthesis focusing on practical applications
```

#### Timing Strategy
- **Optimal moments**: After queries, during pauses, at section boundaries
- **Avoid interrupting**: Active typing, rapid navigation, focused reading
- **Debounce**: 2-second delay to prevent overwhelming

### 5. Research Assistant Agent

**Type**: Interactive  
**Trigger**: On-demand via commands  
**Purpose**: Conduct deep, comprehensive research across your vault

#### Capabilities
- **Literature Review**: Systematic analysis of all relevant sources
- **Evidence Gathering**: Build evidence chains from multiple sources
- **Hypothesis Testing**: Test ideas against vault knowledge
- **Citation Tracking**: Follow citation networks
- **Research Planning**: Create structured research plans

#### Research Depth Levels

| Level | Documents | Depth | Time | Use Case |
|-------|-----------|-------|------|----------|
| **Exploratory** | Up to 100 | Broad survey | 30 min | Initial research |
| **Focused** | Up to 20 | Deep dive | 15 min | Specific topics |
| **Comprehensive** | Up to 200 | Exhaustive | 60 min | Publication-ready |

#### Research Process
1. **Query Analysis**: Break down research question
2. **Search Strategy**: Multi-pronged search approach
3. **Evidence Collection**: Systematic gathering
4. **Analysis & Synthesis**: Theme and argument analysis
5. **Report Generation**: Comprehensive markdown report

#### Command Usage
```markdown
## agent:research
Research the evolution of transformer architectures

## agent:research depth=comprehensive
Exhaustive analysis of productivity systems

## agent:research type=hypothesis
Test hypothesis: "Spaced repetition improves long-term retention"
```

## Agent Memory System

### Memory Types

Agents store different types of memories in Basic Memory:

| Memory Type | Purpose | Example |
|-------------|---------|---------|
| **Patterns** | Recurring behaviors | "User frequently queries about AI ethics" |
| **Preferences** | User preferences | "Prefers bullet-point summaries" |
| **Executions** | Task history | "Synthesized 5 documents in 3.2 seconds" |
| **Insights** | Key findings | "Knowledge gap in security documentation" |
| **Feedback** | User responses | "User liked comprehensive timeline format" |

### Memory Format

Memories are stored as semantic markdown in Basic Memory:

```markdown
# Pattern Memory
**Agent**: vault-analyzer
**Created**: 2024-01-15T10:30:00
**Type**: pattern

## Observations
- [pattern] Detected pattern: Weekly review notes
- [frequency] Occurrence count: 12
- [confidence] Confidence level: 0.92

## Relations
- relates_to [[Work Patterns]]
- extends [[Productivity System]]
```

### Learning and Improvement

Agents learn through:
1. **Pattern Recognition**: Identifying recurring behaviors
2. **Feedback Integration**: Learning from user responses
3. **Performance Optimization**: Improving based on metrics
4. **Cross-Agent Sharing**: Learning from other agents' experiences

## Agent Coordination

### Inter-Agent Communication

Agents share information through Basic Memory:

```
Vault Analyzer → discovers patterns → Suggestion Engine
                                    ↓
                            suggests synthesis
                                    ↓
Synthesis Assistant ← retrieves context ← Context Optimizer
                    ↓
            creates synthesis
                    ↓
Research Assistant ← learns from synthesis patterns
```

### Priority System

When multiple agents need resources:
1. **Context Optimizer** (highest priority - maintains performance)
2. **Vault Analyzer** (scheduled, important insights)
3. **Suggestion Engine** (user-facing, real-time)
4. **Synthesis Assistant** (on-demand, can wait)
5. **Research Assistant** (resource-intensive, lowest priority)

## Configuration

### Enable/Disable Agents

Edit `.agent-os/agents/config.yaml`:

```yaml
agents:
  vault-analyzer:
    enabled: false  # Disable this agent
  
  suggestion-engine:
    enabled: true
    configuration:
      max_suggestions: 3  # Reduce suggestion count
      confidence_threshold: 0.8  # Higher quality bar
```

### Adjust Schedules

```yaml
agents:
  vault-analyzer:
    trigger:
      type: schedule
      interval: weekly  # Change from daily to weekly
      time: "09:00"    # Run at 9 AM instead
```

### Performance Tuning

```yaml
global:
  max_concurrent_agents: 2  # Reduce concurrent execution
  default_timeout: 30       # Shorter timeout
  max_context_tokens: 100000  # Reduce token usage
```

## API Usage

### Execute Agent Manually

```bash
curl -X POST http://localhost:8000/agents/vault-analyzer/execute \
  -H "Content-Type: application/json" \
  -d '{
    "parameters": {
      "depth": 3,
      "focus": "recent_changes"
    }
  }'
```

### Check Agent Status

```bash
curl http://localhost:8000/agents/vault-analyzer/status
```

### Get Agent History

```bash
curl http://localhost:8000/agents/vault-analyzer/history?limit=10
```

### View Schedule

```bash
curl http://localhost:8000/scheduler/info
```

## Best Practices

### 1. Initial Setup
- Let Vault Analyzer run for a few days to learn your vault
- Review and act on initial suggestions to train preferences
- Use Research Assistant for deep dives into new topics

### 2. Daily Workflow
- Check morning Vault Analysis report for insights
- Let Suggestion Engine guide discovery during work
- Use Synthesis Assistant for meeting prep or reports

### 3. Performance
- If slow, reduce max_context_tokens
- Disable unused agents to save resources
- Clear cache if behavior seems stuck

### 4. Learning
- Provide feedback on suggestions (helps all agents learn)
- Review agent memories periodically in Basic Memory
- Share successful patterns between projects

## Troubleshooting

### Agent Not Running

1. Check if enabled in config
2. Verify scheduler is running
3. Check agent status via API
4. Review logs for errors

### Poor Suggestions

1. Let agents accumulate more memories
2. Provide explicit feedback
3. Adjust confidence thresholds
4. Clear and rebuild patterns

### Performance Issues

1. Reduce concurrent agents
2. Lower token limits
3. Disable real-time agents temporarily
4. Optimize indices

## Future Enhancements

Planned improvements:
- Visual dashboard for agent activity
- Custom agent creation framework
- Workflow automation triggers
- External tool integration
- Collaborative multi-user agents