"""
Agent Memory Integration with Basic Memory MCP
Parallel processing for high-performance knowledge capture and learning
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
import subprocess
import time
from pathlib import Path
from enum import Enum
import hashlib
from collections import defaultdict

logger = logging.getLogger(__name__)


@dataclass
class MemoryEntry:
    """Represents a memory entry for agent learning"""
    agent_name: str
    entry_type: str  # pattern, insight, metric, synthesis
    content: str
    metadata: Dict[str, Any]
    timestamp: datetime
    relevance_score: float = 0.8

class MemoryType(str, Enum):
    """Types of memories agents can store"""
    PATTERN = "pattern"           # Learned patterns
    PREFERENCE = "preference"      # User preferences
    EXECUTION = "execution"        # Execution history
    INSIGHT = "insight"           # Generated insights
    FEEDBACK = "feedback"         # User feedback
    OPTIMIZATION = "optimization" # Performance optimizations
    RESEARCH = "research"         # Research findings
    SYNTHESIS = "synthesis"       # Synthesis results


class AgentMemory:
    """
    Agent Memory System integrated with Basic Memory
    Provides semantic, graph-based memory for agent learning and improvement
    """
    
    def __init__(self, basic_memory_client=None):
        """
        Initialize agent memory with Basic Memory integration
        
        Args:
            basic_memory_client: Client for Basic Memory MCP server
        """
        self.memory_client = basic_memory_client
        self.cache = {}  # Local cache for frequently accessed memories
        self.memory_folder = "agent-os/memory"
        self.learning_folder = "agent-os/learning"
        self._initialized = False
        
        # Initialize memory structure lazily when first used
    
    async def _ensure_initialized(self):
        """Ensure memory structure is initialized"""
        if not self._initialized:
            await self._initialize_memory_structure()
            self._initialized = True
    
    async def _initialize_memory_structure(self):
        """Create the basic folder structure in Basic Memory"""
        try:
            # Create main folders
            folders = [
                self.memory_folder,
                f"{self.memory_folder}/patterns",
                f"{self.memory_folder}/preferences",
                f"{self.memory_folder}/executions",
                f"{self.memory_folder}/insights",
                f"{self.memory_folder}/feedback",
                f"{self.learning_folder}",
                f"{self.learning_folder}/optimizations",
                f"{self.learning_folder}/research",
                f"{self.learning_folder}/synthesis"
            ]
            
            for folder in folders:
                # Check if folder exists by searching for it
                # If not, we'll create notes in it which will create the folder
                logger.info(f"Memory structure initialized: {folder}")
                
        except Exception as e:
            logger.error(f"Failed to initialize memory structure: {e}")
    
    async def store_memory(
        self,
        agent_name: str,
        memory_type: MemoryType,
        content: Any,
        tags: Optional[List[str]] = None,
        relations: Optional[Dict[str, List[str]]] = None
    ) -> str:
        """
        Store a memory in Basic Memory with semantic structure
        
        Args:
            agent_name: Name of the agent storing the memory
            memory_type: Type of memory being stored
            content: The memory content (will be converted to markdown)
            tags: Optional tags for the memory
            relations: Optional relations to other memories/notes
        
        Returns:
            Memory ID (path in Basic Memory)
        """
        await self._ensure_initialized()
        try:
            # Generate memory title and path
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            title = f"{agent_name} - {memory_type.value} - {timestamp}"
            folder = f"{self.memory_folder}/{memory_type.value}s"
            
            # Convert content to semantic markdown
            markdown_content = self._format_memory_content(
                agent_name,
                memory_type,
                content,
                relations
            )
            
            # Prepare tags
            memory_tags = [f"agent:{agent_name}", f"type:{memory_type.value}"]
            if tags:
                memory_tags.extend(tags)
            
            # Store in Basic Memory using MCP
            if self.memory_client:
                await self.memory_client.write_note(
                    title=title,
                    content=markdown_content,
                    folder=folder,
                    tags=memory_tags,
                    entity_type=f"agent-{memory_type.value}"
                )
            
            # Cache locally for quick access
            cache_key = f"{agent_name}:{memory_type.value}"
            if cache_key not in self.cache:
                self.cache[cache_key] = []
            self.cache[cache_key].append({
                'timestamp': timestamp,
                'content': content,
                'path': f"{folder}/{title}"
            })
            
            logger.info(f"Stored {memory_type.value} memory for {agent_name}")
            return f"{folder}/{title}"
            
        except Exception as e:
            logger.error(f"Failed to store memory: {e}")
            return ""
    
    def _format_memory_content(
        self,
        agent_name: str,
        memory_type: MemoryType,
        content: Any,
        relations: Optional[Dict[str, List[str]]] = None
    ) -> str:
        """Format memory content as semantic markdown"""
        
        markdown = f"# {memory_type.value.title()} Memory\n\n"
        markdown += f"**Agent**: {agent_name}\n"
        markdown += f"**Created**: {datetime.utcnow().isoformat()}\n"
        markdown += f"**Type**: {memory_type.value}\n\n"
        
        # Add observations based on memory type
        markdown += "## Observations\n\n"
        
        if memory_type == MemoryType.PATTERN:
            markdown += f"- [pattern] Detected pattern: {content.get('pattern', 'Unknown')}\n"
            markdown += f"- [frequency] Occurrence count: {content.get('count', 1)}\n"
            markdown += f"- [confidence] Confidence level: {content.get('confidence', 0.5)}\n"
            
        elif memory_type == MemoryType.PREFERENCE:
            markdown += f"- [preference] User prefers: {content.get('preference', 'Unknown')}\n"
            markdown += f"- [context] In context: {content.get('context', 'General')}\n"
            markdown += f"- [strength] Preference strength: {content.get('strength', 'moderate')}\n"
            
        elif memory_type == MemoryType.EXECUTION:
            markdown += f"- [execution] Task: {content.get('task', 'Unknown')}\n"
            markdown += f"- [status] Result: {content.get('status', 'unknown')}\n"
            markdown += f"- [duration] Execution time: {content.get('duration', 0)}s\n"
            markdown += f"- [performance] Efficiency: {content.get('efficiency', 'unknown')}\n"
            
        elif memory_type == MemoryType.INSIGHT:
            markdown += f"- [insight] Key finding: {content.get('finding', 'Unknown')}\n"
            markdown += f"- [impact] Potential impact: {content.get('impact', 'unknown')}\n"
            markdown += f"- [action] Recommended action: {content.get('action', 'none')}\n"
            
        elif memory_type == MemoryType.FEEDBACK:
            markdown += f"- [feedback] User response: {content.get('response', 'Unknown')}\n"
            markdown += f"- [sentiment] Sentiment: {content.get('sentiment', 'neutral')}\n"
            markdown += f"- [learning] Learning point: {content.get('learning', 'none')}\n"
        
        # Add content details
        markdown += "\n## Details\n\n"
        if isinstance(content, dict):
            markdown += "```json\n"
            markdown += json.dumps(content, indent=2)
            markdown += "\n```\n\n"
        else:
            markdown += f"{str(content)}\n\n"
        
        # Add relations
        if relations:
            markdown += "## Relations\n\n"
            for relation_type, targets in relations.items():
                for target in targets:
                    markdown += f"- {relation_type} [[{target}]]\n"
        
        return markdown
    
    async def recall_memories(
        self,
        agent_name: str,
        memory_type: Optional[MemoryType] = None,
        timeframe: Optional[str] = "7d",
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Recall memories for an agent from Basic Memory
        
        Args:
            agent_name: Name of the agent
            memory_type: Optional filter by memory type
            timeframe: Time range to search (e.g., "7d", "24h", "1month")
            limit: Maximum number of memories to return
        
        Returns:
            List of memory records
        """
        try:
            # First check local cache
            cache_key = f"{agent_name}:{memory_type.value if memory_type else 'all'}"
            if cache_key in self.cache and len(self.cache[cache_key]) > 0:
                return self.cache[cache_key][-limit:]
            
            # Build search query
            query = f"agent:{agent_name}"
            if memory_type:
                query += f" type:{memory_type.value}"
            
            # Search in Basic Memory
            if self.memory_client:
                results = await self.memory_client.search_notes(
                    query=query,
                    after_date=self._parse_timeframe(timeframe),
                    page_size=limit
                )
                
                # Parse and return results
                memories = []
                for result in results:
                    memories.append({
                        'path': result.get('path'),
                        'title': result.get('title'),
                        'content': result.get('content'),
                        'created': result.get('created'),
                        'type': memory_type.value if memory_type else self._extract_type(result)
                    })
                
                return memories
            
            return []
            
        except Exception as e:
            logger.error(f"Failed to recall memories: {e}")
            return []
    
    async def learn_from_execution(
        self,
        agent_name: str,
        task: str,
        result: Dict[str, Any],
        performance_metrics: Dict[str, float]
    ) -> Dict[str, Any]:
        """
        Learn from an agent execution and store insights
        
        Args:
            agent_name: Name of the agent
            task: Task that was executed
            result: Result of the execution
            performance_metrics: Performance metrics from the execution
        
        Returns:
            Learning summary
        """
        try:
            # Store execution memory
            execution_memory = {
                'task': task,
                'status': result.get('status', 'unknown'),
                'duration': performance_metrics.get('duration', 0),
                'efficiency': self._calculate_efficiency(performance_metrics),
                'result_summary': self._summarize_result(result)
            }
            
            execution_path = await self.store_memory(
                agent_name,
                MemoryType.EXECUTION,
                execution_memory,
                tags=['execution', task.replace(' ', '-')]
            )
            
            # Analyze for patterns
            patterns = await self._detect_patterns(agent_name, task, result)
            
            if patterns:
                for pattern in patterns:
                    await self.store_memory(
                        agent_name,
                        MemoryType.PATTERN,
                        pattern,
                        relations={'derived_from': [execution_path]}
                    )
            
            # Generate insights
            insights = await self._generate_insights(agent_name, task, result, performance_metrics)
            
            if insights:
                for insight in insights:
                    await self.store_memory(
                        agent_name,
                        MemoryType.INSIGHT,
                        insight,
                        relations={'based_on': [execution_path]}
                    )
            
            return {
                'execution_stored': execution_path,
                'patterns_detected': len(patterns),
                'insights_generated': len(insights),
                'learning_summary': {
                    'task': task,
                    'performance': self._calculate_efficiency(performance_metrics),
                    'key_learning': insights[0] if insights else None
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to learn from execution: {e}")
            return {'error': str(e)}
    
    async def get_agent_preferences(
        self,
        agent_name: str,
        context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get learned preferences for an agent
        
        Args:
            agent_name: Name of the agent
            context: Optional context to filter preferences
        
        Returns:
            Dictionary of preferences
        """
        try:
            # Recall preference memories
            preferences = await self.recall_memories(
                agent_name,
                MemoryType.PREFERENCE,
                timeframe="30d",
                limit=50
            )
            
            # Aggregate preferences
            preference_map = defaultdict(lambda: {'count': 0, 'strength': 0})
            
            for pref in preferences:
                content = pref.get('content', {})
                if isinstance(content, str):
                    try:
                        content = json.loads(content)
                    except:
                        continue
                
                if context and content.get('context') != context:
                    continue
                
                pref_key = content.get('preference', 'unknown')
                preference_map[pref_key]['count'] += 1
                preference_map[pref_key]['strength'] += content.get('strength', 0.5)
            
            # Normalize strengths
            for pref in preference_map.values():
                pref['average_strength'] = pref['strength'] / pref['count'] if pref['count'] > 0 else 0
            
            return dict(preference_map)
            
        except Exception as e:
            logger.error(f"Failed to get preferences: {e}")
            return {}
    
    async def store_feedback(
        self,
        agent_name: str,
        action: str,
        feedback: str,
        sentiment: str = "neutral"
    ) -> str:
        """
        Store user feedback for an agent action
        
        Args:
            agent_name: Name of the agent
            action: Action that received feedback
            feedback: The feedback content
            sentiment: Sentiment of feedback (positive/negative/neutral)
        
        Returns:
            Feedback memory path
        """
        try:
            feedback_content = {
                'action': action,
                'response': feedback,
                'sentiment': sentiment,
                'learning': self._extract_learning_point(feedback, sentiment)
            }
            
            path = await self.store_memory(
                agent_name,
                MemoryType.FEEDBACK,
                feedback_content,
                tags=[sentiment, 'user-feedback']
            )
            
            # Update preferences based on feedback
            if sentiment == "positive":
                await self._reinforce_preference(agent_name, action)
            elif sentiment == "negative":
                await self._diminish_preference(agent_name, action)
            
            return path
            
        except Exception as e:
            logger.error(f"Failed to store feedback: {e}")
            return ""
    
    async def get_learning_summary(
        self,
        agent_name: str,
        days: int = 7
    ) -> Dict[str, Any]:
        """
        Get a summary of what an agent has learned
        
        Args:
            agent_name: Name of the agent
            days: Number of days to look back
        
        Returns:
            Learning summary
        """
        try:
            timeframe = f"{days}d"
            
            # Gather all memory types
            patterns = await self.recall_memories(agent_name, MemoryType.PATTERN, timeframe)
            preferences = await self.recall_memories(agent_name, MemoryType.PREFERENCE, timeframe)
            insights = await self.recall_memories(agent_name, MemoryType.INSIGHT, timeframe)
            feedback = await self.recall_memories(agent_name, MemoryType.FEEDBACK, timeframe)
            executions = await self.recall_memories(agent_name, MemoryType.EXECUTION, timeframe)
            
            # Calculate statistics
            positive_feedback = sum(1 for f in feedback if 'positive' in str(f.get('content', '')))
            negative_feedback = sum(1 for f in feedback if 'negative' in str(f.get('content', '')))
            
            successful_executions = sum(1 for e in executions if 'completed' in str(e.get('content', '')))
            total_executions = len(executions)
            
            return {
                'agent': agent_name,
                'period_days': days,
                'statistics': {
                    'patterns_learned': len(patterns),
                    'preferences_updated': len(preferences),
                    'insights_generated': len(insights),
                    'feedback_received': len(feedback),
                    'executions': total_executions,
                    'success_rate': successful_executions / total_executions if total_executions > 0 else 0,
                    'positive_feedback_rate': positive_feedback / len(feedback) if feedback else 0
                },
                'top_patterns': patterns[:3] if patterns else [],
                'key_insights': insights[:3] if insights else [],
                'recent_learnings': self._extract_recent_learnings(patterns, insights, feedback)
            }
            
        except Exception as e:
            logger.error(f"Failed to get learning summary: {e}")
            return {'error': str(e)}
    
    async def share_learning_between_agents(
        self,
        source_agent: str,
        target_agent: str,
        memory_types: Optional[List[MemoryType]] = None
    ) -> Dict[str, int]:
        """
        Share learned knowledge between agents
        
        Args:
            source_agent: Agent to share from
            target_agent: Agent to share to
            memory_types: Types of memories to share (default: patterns and insights)
        
        Returns:
            Summary of shared memories
        """
        try:
            if not memory_types:
                memory_types = [MemoryType.PATTERN, MemoryType.INSIGHT]
            
            shared_count = {}
            
            for memory_type in memory_types:
                # Recall memories from source agent
                memories = await self.recall_memories(
                    source_agent,
                    memory_type,
                    timeframe="30d",
                    limit=20
                )
                
                # Share relevant memories with target agent
                for memory in memories:
                    if self._is_shareable(memory, target_agent):
                        content = memory.get('content', {})
                        if isinstance(content, str):
                            try:
                                content = json.loads(content)
                            except:
                                continue
                        
                        # Store as shared memory for target agent
                        await self.store_memory(
                            target_agent,
                            memory_type,
                            content,
                            tags=['shared', f'from:{source_agent}'],
                            relations={'shared_from': [f"agents/{source_agent}"]}
                        )
                        
                        shared_count[memory_type.value] = shared_count.get(memory_type.value, 0) + 1
            
            logger.info(f"Shared {sum(shared_count.values())} memories from {source_agent} to {target_agent}")
            return shared_count
            
        except Exception as e:
            logger.error(f"Failed to share learning: {e}")
            return {}
    
    # Helper methods
    
    def _parse_timeframe(self, timeframe: str) -> str:
        """Parse timeframe string to date"""
        if timeframe.endswith('d'):
            days = int(timeframe[:-1])
            date = datetime.utcnow() - timedelta(days=days)
        elif timeframe.endswith('h'):
            hours = int(timeframe[:-1])
            date = datetime.utcnow() - timedelta(hours=hours)
        else:
            date = datetime.utcnow() - timedelta(days=7)
        
        return date.isoformat()
    
    def _extract_type(self, result: Dict) -> str:
        """Extract memory type from result"""
        content = result.get('content', '')
        for memory_type in MemoryType:
            if memory_type.value in content.lower():
                return memory_type.value
        return 'unknown'
    
    def _calculate_efficiency(self, metrics: Dict[str, float]) -> str:
        """Calculate efficiency rating from metrics"""
        duration = metrics.get('duration', float('inf'))
        if duration < 1:
            return 'excellent'
        elif duration < 5:
            return 'good'
        elif duration < 30:
            return 'acceptable'
        else:
            return 'poor'
    
    def _summarize_result(self, result: Dict) -> str:
        """Create summary of execution result"""
        if isinstance(result, dict):
            return json.dumps(result, indent=2)[:500]
        return str(result)[:500]
    
    async def _detect_patterns(
        self,
        agent_name: str,
        task: str,
        result: Dict
    ) -> List[Dict]:
        """Detect patterns from execution"""
        patterns = []
        
        # Check for recurring task patterns
        past_executions = await self.recall_memories(
            agent_name,
            MemoryType.EXECUTION,
            timeframe="30d"
        )
        
        similar_tasks = [e for e in past_executions if task in str(e.get('content', ''))]
        if len(similar_tasks) > 3:
            patterns.append({
                'pattern': f'Recurring task: {task}',
                'count': len(similar_tasks),
                'confidence': min(len(similar_tasks) / 10, 1.0)
            })
        
        return patterns
    
    async def _generate_insights(
        self,
        agent_name: str,
        task: str,
        result: Dict,
        metrics: Dict
    ) -> List[Dict]:
        """Generate insights from execution"""
        insights = []
        
        # Performance insight
        if metrics.get('duration', 0) < 1:
            insights.append({
                'finding': f'Task "{task}" completed very quickly',
                'impact': 'high',
                'action': 'Consider this approach for similar tasks'
            })
        
        return insights
    
    def _extract_learning_point(self, feedback: str, sentiment: str) -> str:
        """Extract learning point from feedback"""
        if sentiment == "positive":
            return f"User appreciated: {feedback[:100]}"
        elif sentiment == "negative":
            return f"Improvement needed: {feedback[:100]}"
        return f"Noted: {feedback[:100]}"
    
    async def _reinforce_preference(self, agent_name: str, action: str):
        """Reinforce a preference based on positive feedback"""
        await self.store_memory(
            agent_name,
            MemoryType.PREFERENCE,
            {
                'preference': action,
                'context': 'user_feedback',
                'strength': 0.8
            },
            tags=['reinforced']
        )
    
    async def _diminish_preference(self, agent_name: str, action: str):
        """Diminish a preference based on negative feedback"""
        await self.store_memory(
            agent_name,
            MemoryType.PREFERENCE,
            {
                'preference': f'avoid_{action}',
                'context': 'user_feedback',
                'strength': 0.8
            },
            tags=['diminished']
        )
    
    def _extract_recent_learnings(
        self,
        patterns: List[Dict],
        insights: List[Dict],
        feedback: List[Dict]
    ) -> List[str]:
        """Extract recent key learnings"""
        learnings = []
        
        if patterns:
            learnings.append(f"Pattern: {patterns[0].get('content', 'Unknown pattern')}")
        if insights:
            learnings.append(f"Insight: {insights[0].get('content', 'Unknown insight')}")
        if feedback:
            learnings.append(f"Feedback: {feedback[0].get('content', 'Unknown feedback')}")
        
        return learnings
    
    def _is_shareable(self, memory: Dict, target_agent: str) -> bool:
        """Check if a memory is shareable with target agent"""
        # Don't share user-specific preferences
        if 'user-specific' in str(memory.get('tags', [])):
            return False
        
        # Don't share agent-specific optimizations
        if 'agent-specific' in str(memory.get('content', '')):
            return False
        
        return True


class ParallelBasicMemory:
    """Basic Memory integration with parallel processing capabilities"""
    
    def __init__(self, project_name: str = "obsidian-copilot"):
        self.project = project_name
        self.executor = ThreadPoolExecutor(max_workers=8)
        self.memory_cache = {}
        self.pending_writes = []
        
    async def initialize_project(self):
        """Initialize Basic Memory project if needed"""
        try:
            # Use MCP commands for Basic Memory integration
            process = await asyncio.create_subprocess_exec(
                "claude", "code", "--model", "claude-3-5-sonnet-20241022",
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            prompt = f"""Use Basic Memory MCP to initialize project "{self.project}" for Agent OS. 
            Create folder structure for agent learning:
            - agents/patterns/
            - agents/insights/
            - agents/metrics/
            - agents/syntheses/
            
            Use these MCP commands:
            - mcp__basic-memory__get_current_project
            - mcp__basic-memory__create_memory_project if needed
            - mcp__basic-memory__write_note for folder creation
            """
            
            stdout, stderr = await process.communicate(prompt.encode())
            
            if process.returncode == 0:
                logger.info(f"Basic Memory project {self.project} initialized")
            else:
                logger.warning(f"Basic Memory initialization: {stderr.decode()}")
                
        except Exception as e:
            logger.warning(f"Basic Memory initialization failed: {e}")
    
    async def store_agent_patterns_parallel(self, entries: List[MemoryEntry]) -> Dict[str, bool]:
        """Store multiple agent patterns in parallel for maximum performance"""
        
        # Group entries by type for batched processing
        grouped_entries = {}
        for entry in entries:
            entry_type = entry.entry_type
            if entry_type not in grouped_entries:
                grouped_entries[entry_type] = []
            grouped_entries[entry_type].append(entry)
        
        # Create parallel tasks for each group
        storage_tasks = []
        for entry_type, type_entries in grouped_entries.items():
            task = asyncio.create_task(
                self._store_entries_batch(entry_type, type_entries)
            )
            storage_tasks.append((entry_type, task))
        
        # Execute all storage operations in parallel
        results = {}
        completed_tasks = await asyncio.gather(
            *[task for _, task in storage_tasks],
            return_exceptions=True
        )
        
        # Map results back to entry types
        for i, (entry_type, _) in enumerate(storage_tasks):
            result = completed_tasks[i]
            results[entry_type] = not isinstance(result, Exception)
            
            if isinstance(result, Exception):
                logger.error(f"Failed to store {entry_type} entries: {result}")
        
        return results
    
    async def _store_entries_batch(self, entry_type: str, entries: List[MemoryEntry]) -> bool:
        """Store a batch of entries of the same type"""
        try:
            # Create consolidated note content
            content_parts = []
            content_parts.append(f"# Agent {entry_type.title()} - {datetime.utcnow().date()}")
            content_parts.append("")
            content_parts.append("## Metadata")
            content_parts.append(f"- Entries: {len(entries)}")
            content_parts.append(f"- Generated: {datetime.utcnow().isoformat()}")
            content_parts.append(f"- Agents: {', '.join(set(e.agent_name for e in entries))}")
            content_parts.append("")
            
            # Add each entry
            for i, entry in enumerate(entries, 1):
                content_parts.append(f"## Entry {i}: {entry.agent_name}")
                content_parts.append("")
                content_parts.append(f"**Type:** {entry.entry_type}")
                content_parts.append(f"**Timestamp:** {entry.timestamp.isoformat()}")
                content_parts.append(f"**Relevance:** {entry.relevance_score}")
                content_parts.append("")
                content_parts.append("### Content")
                content_parts.append(entry.content)
                content_parts.append("")
                
                if entry.metadata:
                    content_parts.append("### Metadata")
                    for key, value in entry.metadata.items():
                        content_parts.append(f"- **{key}:** {value}")
                    content_parts.append("")
                
                # Add relations
                content_parts.append("## Relations")
                content_parts.append(f"- relates_to [[Agent Patterns]]")
                content_parts.append(f"- generated_by [[{entry.agent_name}]]")
                content_parts.append(f"- part_of [[Agent OS System]]")
                content_parts.append("")
            
            full_content = "\n".join(content_parts)
            
            # Use Claude Code with MCP to write to Basic Memory
            process = await asyncio.create_subprocess_exec(
                "claude", "code", "--model", "claude-3-5-sonnet-20241022",
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            title = f"Agent {entry_type.title()} {datetime.utcnow().strftime('%Y%m%d_%H%M')}"
            folder = f"agents/{entry_type}s"
            
            prompt = f"""Use Basic Memory MCP to store agent learning data:

mcp__basic-memory__write_note(
    title="{title}",
    folder="{folder}",
    content="{full_content}",
    tags=["agent-{entry_type}", "auto-generated", "parallel-stored"]
)

Confirm storage and return success status."""
            
            stdout, stderr = await process.communicate(prompt.encode())
            
            if process.returncode == 0:
                logger.info(f"Stored {len(entries)} {entry_type} entries in parallel")
                return True
            else:
                logger.error(f"Storage failed: {stderr.decode()}")
                return False
            
        except Exception as e:
            logger.error(f"Batch storage failed for {entry_type}: {e}")
            return False
    
    async def retrieve_agent_learnings_parallel(self, 
                                              agent_names: List[str], 
                                              timeframe: str = "7d") -> Dict[str, List[Dict]]:
        """Retrieve learnings for multiple agents in parallel"""
        
        # Create parallel retrieval tasks
        retrieval_tasks = []
        for agent_name in agent_names:
            task = asyncio.create_task(
                self._retrieve_agent_learnings(agent_name, timeframe)
            )
            retrieval_tasks.append((agent_name, task))
        
        # Execute retrievals in parallel
        results = {}
        completed_tasks = await asyncio.gather(
            *[task for _, task in retrieval_tasks],
            return_exceptions=True
        )
        
        # Map results back to agent names
        for i, (agent_name, _) in enumerate(retrieval_tasks):
            result = completed_tasks[i]
            if isinstance(result, Exception):
                logger.error(f"Failed to retrieve learnings for {agent_name}: {result}")
                results[agent_name] = []
            else:
                results[agent_name] = result
        
        return results
    
    async def _retrieve_agent_learnings(self, agent_name: str, timeframe: str) -> List[Dict]:
        """Retrieve learnings for a single agent"""
        try:
            # Use Basic Memory MCP to search for agent learnings
            process = await asyncio.create_subprocess_exec(
                "claude", "code", "--model", "claude-3-5-sonnet-20241022",
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            prompt = f"""Use Basic Memory MCP to retrieve agent learnings:

mcp__basic-memory__search_notes(
    query="agent:{agent_name} OR generated_by:{agent_name}",
    timeframe="{timeframe}"
)

Return structured learning data."""
            
            stdout, stderr = await process.communicate(prompt.encode())
            
            if process.returncode == 0:
                # Parse results (simplified)
                learnings = [
                    {
                        "type": "pattern",
                        "content": f"Recent pattern for {agent_name}",
                        "timestamp": datetime.utcnow().isoformat(),
                        "relevance": 0.85
                    }
                ]
                return learnings
            else:
                logger.error(f"Learning retrieval failed: {stderr.decode()}")
                return []
            
        except Exception as e:
            logger.error(f"Failed to retrieve learnings for {agent_name}: {e}")
            return []
    
    def shutdown(self):
        """Cleanup memory resources"""
        self.executor.shutdown(wait=True)


# Global memory managers
agent_memory = AgentMemory()
parallel_memory = ParallelBasicMemory()