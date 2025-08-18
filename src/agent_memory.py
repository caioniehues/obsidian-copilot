"""
Agent Memory System using Basic Memory
Integrates with Basic Memory MCP server for persistent, semantic agent learning
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
import hashlib
from collections import defaultdict

logger = logging.getLogger(__name__)


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
        
        # Initialize memory structure
        asyncio.create_task(self._initialize_memory_structure())
    
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