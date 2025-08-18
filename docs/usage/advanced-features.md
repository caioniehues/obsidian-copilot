# 🚀 Advanced Features & Workflows

> Sophisticated usage patterns for power users

## Advanced Daily Workflows

### Comprehensive Morning Routine

```markdown
# Morning Knowledge Review - {{date}}

## 1. Check overnight analysis:
[[Agent Reports/Daily Analysis/{{date}}]]

## 2. Review suggestions:
## agent:suggestions type=morning
What should I focus on today?

## 3. Set research agenda:
## agent:research type=agenda
What knowledge gaps should I address?

## 4. Pattern analysis:
## agent:patterns timeframe="24h"
What patterns emerged yesterday?
```

### Advanced Research Workflow

**Complete Research Pipeline:**
```markdown
# Research Project: [Topic Name]

## 1. Exploratory Phase:
## agent:research depth=exploratory
What do I know about [topic]?

## 2. Gap Analysis:
## agent:gaps topic="[topic]"
What's missing from my understanding?

## 3. Deep Dive:
## agent:research depth=comprehensive
Complete analysis of [specific aspect]

## 4. Synthesis:
## agent:synthesize type=argumentative
Build argument from my research on [topic]

## 5. Knowledge Integration:
## agent:suggest type=next-actions
What should I explore next?
```

### Writing Enhancement Workflow

**From Research to Publication:**
```markdown
# Writing Project: [Title]

## 1. Gather relevant notes:
## related to="current topic"
Find all relevant materials

## 2. Create outline:
## agent:synthesize type=outline
Create structured outline from my notes

## 3. Fill sections iteratively:
## expand section="Introduction"
## expand section="Main Arguments"
## expand section="Conclusion"

## 4. Review for coherence:
## agent:review
Review this draft for consistency with my notes

## 5. Final enhancement:
## agent:suggest type=improvements
How can this be strengthened?
```

## Multi-Agent Collaboration Patterns

### Research → Synthesis → Action Pipeline

```markdown
## Step 1: Research Phase
## agent:research depth=comprehensive
Research everything about [topic]

## Step 2: Synthesis Phase  
## agent:synthesize type=thematic
Now synthesize those research findings by theme

## Step 3: Action Planning
## agent:suggest based-on=synthesis
What concrete actions should I take?

## Step 4: Gap Assessment
## agent:gaps based-on=research
What questions remain unanswered?
```

### Analysis → Insights → Strategy Pipeline

```markdown
## Step 1: Deep Analysis
## agent:analyze topic="current project"
Analyze my current project comprehensively

## Step 2: Pattern Recognition
## agent:patterns based-on=analysis
What patterns emerge from this analysis?

## Step 3: Strategic Planning
## agent:suggest type=strategic based-on=patterns
What strategic moves should I consider?

## Step 4: Implementation Planning
## Create detailed action plan from suggestions
```

## Advanced Agent Features

### Multi-Note Synthesis

**Synthesize specific sets of notes:**
```markdown
## agent:synthesize notes=["Project A", "Project B", "Lessons Learned"]
Create synthesis connecting these specific notes
```

### Pattern Detection Across Time

**Find patterns across different timeframes:**
```markdown
## agent:patterns timeframe="30d"
What patterns emerged in the last month?

## agent:patterns timeframe="90d" type="conceptual"
Long-term conceptual pattern analysis

## agent:patterns type="behavioral" focus="productivity"
Analyze my productivity behavior patterns
```

### Knowledge Graph Exploration

**Explore connections systematically:**
```markdown
## agent:graph center="Machine Learning"
Map connections from machine learning to other topics

## agent:graph depth=3 center="Philosophy"
Deep connection mapping around philosophy

## agent:connections between=["AI Ethics", "Technology", "Society"]
Explore specific conceptual relationships
```

### Custom Agent Behavior

**Modify agent focus and behavior:**
```markdown
## agent:config vault-analyzer focus=["AI", "productivity", "philosophy"]
Configure analyzer to focus on specific topics

## agent:config synthesis-assistant style="academic"
Set synthesis to use academic writing style

## agent:config research-assistant depth="comprehensive"
Default to comprehensive research mode
```

## Advanced Context Strategies

### Batch Processing

**Process multiple related queries efficiently:**
```markdown
## batch
1. Summarize my daily notes from last week
2. Find connections between current projects
3. Identify recurring themes across all notes
4. Generate weekly learning summary
5. Create action items for next week
## end-batch
```

### Context Chaining

**Build context progressively:**
```markdown
## strategy=hierarchical
Quick overview of my knowledge base

## strategy=smart_chunks context=previous
Now dive deeper into most interesting areas  

## strategy=full_docs context=focused
Complete analysis of selected focus areas
```

### Dynamic Context Control

**Adapt context based on query evolution:**
```markdown
## tokens=50000
Start with moderate context

## expand context by 50%
Increase for more detailed analysis

## focus on="recent insights"
Narrow to most relevant recent content
```

## Specialized Workflows

### Literature Review Automation

```markdown
# Literature Review: [Topic]

## 1. Source Identification:
## agent:research type=literature_review criteria="academic"
Find all academic sources in my notes

## 2. Thematic Organization:
## agent:synthesize type=thematic sources=literature
Organize by research themes

## 3. Gap Analysis:
## agent:gaps type=research_questions
What research questions are unaddressed?

## 4. Citation Network:
## agent:research type=citations
Map citation relationships

## 5. Summary Generation:
## agent:synthesize type=literature_summary
Create comprehensive literature summary
```

### Hypothesis Testing Framework

```markdown
# Hypothesis Testing: [Statement]

## 1. Evidence Gathering:
## agent:research type=evidence claim="[hypothesis]"
Gather all supporting and contradicting evidence

## 2. Quality Assessment:
## agent:analyze evidence quality="peer-reviewed"
Assess strength and reliability of sources

## 3. Argument Construction:
## agent:synthesize type=argumentative pro-con="[hypothesis]"
Build balanced argument structure

## 4. Conclusion Drawing:
## agent:evaluate hypothesis="[statement]" confidence="statistical"
Statistical evaluation of hypothesis support
```

### Project Management Integration

```markdown
# Project Review: [Project Name]

## 1. Status Analysis:
## agent:analyze folder="Projects/[Name]" type="progress"
Analyze current project status

## 2. Milestone Tracking:
## agent:patterns type="completion" timeframe="project-duration"
Track milestone completion patterns

## 3. Risk Assessment:
## agent:gaps type="project-risks"
Identify potential project risks

## 4. Resource Optimization:
## agent:suggest type="resource-allocation" based-on="analysis"
Optimize resource allocation

## 5. Timeline Adjustment:
## agent:synthesize type="timeline" include="dependencies"
Create realistic timeline with dependencies
```

## Agent Memory Management

### Understanding Agent Learning

**View what agents have learned:**
```markdown
# Agent Learning Review

## View Pattern Memories:
tag:#agent:vault-analyzer AND tag:#type:pattern

## View Preference Learning:
tag:#agent:suggestion-engine AND tag:#type:preference

## View Insight Generation:
tag:#type:insight created:7d
```

### Memory-Driven Workflows

**Leverage agent learning for better results:**
```markdown
## agent:preferences
What have you learned about my working style?

## agent:adapt-to-preferences
Adjust your responses based on learned preferences

## agent:memory-guided-research topic="[current-interest]"
Research based on learned interest patterns
```

### Feedback Integration

**Help agents learn more effectively:**
```markdown
## agent:feedback positive="detailed citations"
I prefer responses with detailed source citations

## agent:feedback improvement="shorter-summaries"
Please provide more concise summaries

## agent:learn pattern="morning-research"
Remember I do research work in the morning
```

## Performance Optimization

### Cache Management

**Optimize performance with strategic caching:**
```markdown
## cache:save name="weekly-review-template"
Cache this weekly review pattern

## cache:load name="research-methodology" 
Load cached research approach

## cache:stats
View cache hit rates and performance
```

### Context Optimization

**Balance speed vs. accuracy:**
```markdown
## agent:tune performance="speed" sacrifice="detail"
Optimize for faster responses

## agent:tune performance="accuracy" allow="longer-wait"
Optimize for maximum accuracy

## agent:benchmark current-settings
Benchmark current performance configuration
```

## Advanced Integration Patterns

### Cross-Vault Analysis

```markdown
## agent:compare-vaults source="work" target="personal"
Compare knowledge patterns across vaults

## agent:synthesize-across-contexts work="technical" personal="creative"
Find connections between different life areas
```

### Temporal Analysis

```markdown
## agent:evolution topic="AI understanding" timeframe="6m"
How has my understanding evolved over 6 months?

## agent:growth-trajectory skill="writing" metrics="complexity"
Analyze skill development trajectory

## agent:predict-interests based-on="learning-patterns"
Predict future areas of interest
```

### Meta-Cognitive Enhancement

```markdown
## agent:analyze learning-style
How do I learn most effectively?

## agent:optimize knowledge-workflow
Suggest improvements to my knowledge workflow

## agent:metacognitive-review timeframe="month"
Review my thinking patterns and biases
```

---

**Navigation**: [← Agent Commands](./agent-commands.md) | [Troubleshooting →](../troubleshooting/)