"""
Enhanced Agent OS Implementation with Parallel Execution
Optimized for maximum performance through concurrent operations
"""

import asyncio
import json
import logging
import os
import pickle
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any, Union, Tuple
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from functools import partial
import aiofiles
import yaml
import numpy as np
from collections import defaultdict
import hashlib
import redis.asyncio as redis
from dataclasses import dataclass, field
import time
from src.agent_memory import parallel_memory, MemoryEntry, MemoryType

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Performance monitoring decorator
def measure_performance(func):
    """Decorator to measure function performance"""
    async def wrapper(*args, **kwargs):
        start = time.time()
        result = await func(*args, **kwargs)
        duration = time.time() - start
        logger.debug(f"{func.__name__} took {duration:.2f}s")
        return result
    return wrapper

@dataclass
class ParallelTask:
    """Represents a task that can be executed in parallel"""
    name: str
    func: callable
    args: tuple = field(default_factory=tuple)
    kwargs: dict = field(default_factory=dict)
    priority: int = 5
    timeout: Optional[float] = None

class ParallelExecutor:
    """Manages parallel execution of multiple tasks"""
    
    def __init__(self, max_workers: int = 5):
        self.max_workers = max_workers
        self.thread_pool = ThreadPoolExecutor(max_workers=max_workers)
        self.process_pool = ProcessPoolExecutor(max_workers=max_workers)
        
    async def execute_parallel(self, tasks: List[ParallelTask]) -> Dict[str, Any]:
        """Execute multiple tasks in parallel"""
        # Sort by priority
        tasks.sort(key=lambda x: x.priority)
        
        # Create coroutines for all tasks
        coroutines = []
        task_names = []
        
        for task in tasks:
            if asyncio.iscoroutinefunction(task.func):
                # Async function - run directly
                coro = task.func(*task.args, **task.kwargs)
            else:
                # Sync function - run in thread pool
                coro = asyncio.get_event_loop().run_in_executor(
                    self.thread_pool,
                    partial(task.func, *task.args, **task.kwargs)
                )
            
            # Apply timeout if specified
            if task.timeout:
                coro = asyncio.wait_for(coro, timeout=task.timeout)
            
            coroutines.append(coro)
            task_names.append(task.name)
        
        # Execute all tasks concurrently
        results = await asyncio.gather(*coroutines, return_exceptions=True)
        
        # Map results to task names
        return {
            name: result if not isinstance(result, Exception) else {'error': str(result)}
            for name, result in zip(task_names, results)
        }
    
    def shutdown(self):
        """Cleanup executor pools"""
        self.thread_pool.shutdown(wait=True)
        self.process_pool.shutdown(wait=True)

class EnhancedVaultAnalyzer:
    """Enhanced Vault Analyzer with parallel processing capabilities"""
    
    def __init__(self, vault_path: str, vault_dict: Dict):
        self.vault_path = Path(vault_path)
        self.vault_dict = vault_dict
        self.executor = ParallelExecutor(max_workers=10)
        self.cache = {}
        
    @measure_performance
    async def analyze_vault_parallel(self) -> Dict[str, Any]:
        """Perform comprehensive vault analysis using parallel execution"""
        
        # Define all analysis tasks
        tasks = [
            ParallelTask(
                name="statistics",
                func=self._get_vault_statistics,
                priority=1
            ),
            ParallelTask(
                name="recent_changes",
                func=self._analyze_recent_changes,
                priority=2
            ),
            ParallelTask(
                name="orphaned_notes",
                func=self._find_orphaned_notes,
                priority=3
            ),
            ParallelTask(
                name="link_analysis",
                func=self._analyze_links,
                priority=3
            ),
            ParallelTask(
                name="tag_analysis",
                func=self._analyze_tags,
                priority=4
            ),
            ParallelTask(
                name="content_patterns",
                func=self._detect_content_patterns,
                priority=5
            ),
            ParallelTask(
                name="knowledge_gaps",
                func=self._identify_knowledge_gaps,
                priority=5
            ),
            ParallelTask(
                name="emerging_themes",
                func=self._detect_emerging_themes,
                priority=6
            ),
            ParallelTask(
                name="quality_metrics",
                func=self._calculate_quality_metrics,
                priority=7
            ),
            ParallelTask(
                name="suggestions",
                func=self._generate_suggestions,
                priority=8
            )
        ]
        
        # Execute all tasks in parallel
        logger.info(f"Executing {len(tasks)} analysis tasks in parallel...")
        results = await self.executor.execute_parallel(tasks)
        
        # Combine results
        analysis = {
            'timestamp': datetime.utcnow().isoformat(),
            'vault_path': str(self.vault_path),
            **results
        }
        
        # Generate insights based on all results
        analysis['insights'] = await self._generate_insights(results)
        
        # Store learning results in parallel
        await self._store_learning_parallel(analysis, results)
        
        return analysis
    
    async def _get_vault_statistics(self) -> Dict[str, int]:
        """Get comprehensive vault statistics"""
        stats = {
            'total_notes': len(self.vault_dict),
            'total_words': 0,
            'total_links': 0,
            'unique_tags': set(),
            'avg_note_length': 0
        }
        
        # Process in parallel batches
        batch_size = 100
        batches = [
            list(self.vault_dict.items())[i:i+batch_size]
            for i in range(0, len(self.vault_dict), batch_size)
        ]
        
        async def process_batch(batch):
            batch_stats = {'words': 0, 'links': 0, 'tags': set()}
            for _, doc in batch:
                content = doc.get('chunk', '')
                batch_stats['words'] += len(content.split())
                batch_stats['links'] += content.count('[[')
                # Extract tags
                import re
                tags = re.findall(r'#(\w+)', content)
                batch_stats['tags'].update(tags)
            return batch_stats
        
        # Process batches concurrently
        batch_results = await asyncio.gather(
            *[process_batch(batch) for batch in batches]
        )
        
        # Aggregate results
        for result in batch_results:
            stats['total_words'] += result['words']
            stats['total_links'] += result['links']
            stats['unique_tags'].update(result['tags'])
        
        stats['unique_tags'] = len(stats['unique_tags'])
        stats['avg_note_length'] = stats['total_words'] // max(stats['total_notes'], 1)
        
        return stats
    
    async def _analyze_recent_changes(self) -> Dict[str, Any]:
        """Analyze recently modified notes"""
        # This would integrate with actual file system
        # For now, return mock data
        return {
            'modified_today': 5,
            'created_today': 2,
            'deleted_today': 0,
            'most_edited': ['Note1.md', 'Note2.md'],
            'trend': 'increasing'
        }
    
    async def _find_orphaned_notes(self) -> List[str]:
        """Find notes with no incoming or outgoing links"""
        orphaned = []
        
        # Create link graph
        link_graph = defaultdict(set)
        for doc_id, doc in self.vault_dict.items():
            content = doc.get('chunk', '')
            # Extract links
            import re
            links = re.findall(r'\[\[([^\]]+)\]\]', content)
            for link in links:
                link_graph[doc['title']].add(link)
                link_graph[link].add(doc['title'])
        
        # Find orphaned notes
        for doc_id, doc in self.vault_dict.items():
            title = doc['title']
            if title not in link_graph or len(link_graph[title]) == 0:
                orphaned.append(title)
        
        return orphaned[:10]  # Return top 10
    
    async def _analyze_links(self) -> Dict[str, Any]:
        """Analyze link structure in the vault"""
        link_data = {
            'total_links': 0,
            'broken_links': [],
            'most_linked': [],
            'link_density': 0
        }
        
        link_counts = defaultdict(int)
        all_titles = {doc['title'] for doc in self.vault_dict.values()}
        
        for doc in self.vault_dict.values():
            content = doc.get('chunk', '')
            import re
            links = re.findall(r'\[\[([^\]]+)\]\]', content)
            
            link_data['total_links'] += len(links)
            
            for link in links:
                link_counts[link] += 1
                if link not in all_titles:
                    link_data['broken_links'].append(link)
        
        # Get most linked notes
        link_data['most_linked'] = sorted(
            link_counts.items(), 
            key=lambda x: x[1], 
            reverse=True
        )[:5]
        
        # Calculate link density
        total_words = sum(len(doc.get('chunk', '').split()) for doc in self.vault_dict.values())
        link_data['link_density'] = link_data['total_links'] / max(total_words, 1) * 1000
        
        return link_data
    
    async def _analyze_tags(self) -> Dict[str, Any]:
        """Analyze tag usage in the vault"""
        tag_counts = defaultdict(int)
        tag_cooccurrence = defaultdict(set)
        
        for doc in self.vault_dict.values():
            content = doc.get('chunk', '')
            import re
            tags = re.findall(r'#(\w+)', content)
            
            for tag in tags:
                tag_counts[tag] += 1
                tag_cooccurrence[tag].update(tags)
        
        return {
            'total_unique_tags': len(tag_counts),
            'most_used_tags': sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:10],
            'tag_clusters': self._find_tag_clusters(tag_cooccurrence),
            'unused_tags': [tag for tag, count in tag_counts.items() if count == 1]
        }
    
    def _find_tag_clusters(self, cooccurrence: Dict[str, set]) -> List[List[str]]:
        """Find clusters of related tags"""
        clusters = []
        processed = set()
        
        for tag, related in cooccurrence.items():
            if tag not in processed:
                cluster = [tag]
                for related_tag in related:
                    if related_tag != tag and len(cooccurrence[related_tag] & related) > 2:
                        cluster.append(related_tag)
                        processed.add(related_tag)
                
                if len(cluster) > 1:
                    clusters.append(cluster)
                processed.add(tag)
        
        return clusters[:5]  # Return top 5 clusters
    
    async def _detect_content_patterns(self) -> List[Dict[str, Any]]:
        """Detect recurring patterns in content"""
        patterns = []
        
        # Look for common phrases
        phrase_counts = defaultdict(int)
        
        for doc in self.vault_dict.values():
            content = doc.get('chunk', '').lower()
            # Extract 3-word phrases
            words = content.split()
            for i in range(len(words) - 2):
                phrase = ' '.join(words[i:i+3])
                if len(phrase) > 10:  # Filter short phrases
                    phrase_counts[phrase] += 1
        
        # Find most common patterns
        common_phrases = sorted(
            phrase_counts.items(), 
            key=lambda x: x[1], 
            reverse=True
        )[:10]
        
        for phrase, count in common_phrases:
            if count > 3:  # Minimum threshold
                patterns.append({
                    'pattern': phrase,
                    'frequency': count,
                    'type': 'phrase'
                })
        
        return patterns
    
    async def _identify_knowledge_gaps(self) -> List[str]:
        """Identify potential knowledge gaps in the vault"""
        gaps = []
        
        # Look for questions without answers
        questions = []
        for doc in self.vault_dict.values():
            content = doc.get('chunk', '')
            import re
            found_questions = re.findall(r'[^.!?]*\?', content)
            questions.extend(found_questions)
        
        # Analyze questions for patterns
        unanswered_topics = set()
        for question in questions:
            # Simple heuristic: if question appears multiple times, it might be unanswered
            if questions.count(question) > 1:
                unanswered_topics.add(question.strip())
        
        gaps = list(unanswered_topics)[:10]
        
        return gaps
    
    async def _detect_emerging_themes(self) -> List[Dict[str, Any]]:
        """Detect emerging themes in recent content"""
        # This would analyze temporal patterns
        # For now, return mock emerging themes
        return [
            {'theme': 'AI and automation', 'growth_rate': 0.25, 'mentions': 15},
            {'theme': 'Knowledge management', 'growth_rate': 0.18, 'mentions': 12},
            {'theme': 'Claude integration', 'growth_rate': 0.42, 'mentions': 8}
        ]
    
    async def _calculate_quality_metrics(self) -> Dict[str, float]:
        """Calculate quality metrics for the vault"""
        metrics = {
            'completeness': 0.0,
            'connectivity': 0.0,
            'organization': 0.0,
            'consistency': 0.0
        }
        
        # Completeness: ratio of notes with substantial content
        substantial_notes = sum(
            1 for doc in self.vault_dict.values() 
            if len(doc.get('chunk', '').split()) > 100
        )
        metrics['completeness'] = substantial_notes / max(len(self.vault_dict), 1)
        
        # Connectivity: average links per note
        total_links = sum(
            doc.get('chunk', '').count('[[') 
            for doc in self.vault_dict.values()
        )
        metrics['connectivity'] = min(total_links / max(len(self.vault_dict), 1) / 5, 1.0)
        
        # Organization: presence of tags and structure
        tagged_notes = sum(
            1 for doc in self.vault_dict.values() 
            if '#' in doc.get('chunk', '')
        )
        metrics['organization'] = tagged_notes / max(len(self.vault_dict), 1)
        
        # Consistency: similar formatting across notes
        metrics['consistency'] = 0.75  # Placeholder
        
        return metrics
    
    async def _generate_suggestions(self) -> List[Dict[str, str]]:
        """Generate actionable suggestions for vault improvement"""
        suggestions = [
            {
                'type': 'organization',
                'suggestion': 'Consider adding tags to untagged notes for better organization',
                'priority': 'medium'
            },
            {
                'type': 'connectivity',
                'suggestion': 'Link orphaned notes to related content to improve knowledge graph',
                'priority': 'high'
            },
            {
                'type': 'content',
                'suggestion': 'Expand stub notes with less than 100 words',
                'priority': 'low'
            },
            {
                'type': 'maintenance',
                'suggestion': 'Fix broken links to maintain vault integrity',
                'priority': 'high'
            },
            {
                'type': 'synthesis',
                'suggestion': 'Create synthesis notes for clustered topics',
                'priority': 'medium'
            }
        ]
        
        return suggestions
    
    async def _generate_insights(self, analysis_results: Dict[str, Any]) -> List[str]:
        """Generate insights from analysis results using Claude"""
        insights = []
        
        # Generate insights based on analysis
        if 'statistics' in analysis_results and not isinstance(analysis_results['statistics'], dict):
            stats = analysis_results.get('statistics', {})
            if stats.get('total_notes', 0) > 100:
                insights.append(f"Your vault contains {stats['total_notes']} notes with strong potential for synthesis")
        
        if 'orphaned_notes' in analysis_results:
            orphaned = analysis_results['orphaned_notes']
            if len(orphaned) > 5:
                insights.append(f"Found {len(orphaned)} orphaned notes that could benefit from linking")
        
        if 'emerging_themes' in analysis_results:
            themes = analysis_results['emerging_themes']
            if themes:
                top_theme = themes[0] if themes else None
                if top_theme:
                    insights.append(f"Emerging theme '{top_theme.get('theme', 'Unknown')}' shows {top_theme.get('growth_rate', 0)*100:.0f}% growth")
        
        if 'quality_metrics' in analysis_results:
            metrics = analysis_results['quality_metrics']
            if metrics.get('connectivity', 0) < 0.5:
                insights.append("Vault connectivity is below optimal - consider adding more cross-references")
        
        return insights
    
    async def _store_learning_parallel(self, analysis: Dict[str, Any], results: Dict[str, Any]):
        """Store analysis learnings in Basic Memory using parallel processing"""
        try:
            # Create memory entries for different types of learnings
            memory_entries = []
            
            # Store patterns as memory entries
            if 'content_patterns' in results and results['content_patterns']:
                for pattern in results['content_patterns']:
                    entry = MemoryEntry(
                        agent_name='vault-analyzer',
                        entry_type='pattern',
                        content=f"Detected content pattern: {pattern.get('pattern', 'Unknown')} (frequency: {pattern.get('frequency', 0)})",
                        metadata={
                            'pattern_type': pattern.get('type', 'phrase'),
                            'frequency': pattern.get('frequency', 0),
                            'vault_size': len(self.vault_dict)
                        },
                        timestamp=datetime.utcnow(),
                        relevance_score=0.8
                    )
                    memory_entries.append(entry)
            
            # Store insights as memory entries
            if analysis.get('insights'):
                for insight in analysis['insights']:
                    entry = MemoryEntry(
                        agent_name='vault-analyzer',
                        entry_type='insight',
                        content=insight,
                        metadata={
                            'analysis_timestamp': analysis['timestamp'],
                            'vault_metrics': results.get('statistics', {}),
                            'generated_by': 'vault-analyzer'
                        },
                        timestamp=datetime.utcnow(),
                        relevance_score=0.9
                    )
                    memory_entries.append(entry)
            
            # Store quality metrics
            if 'quality_metrics' in results:
                metrics = results['quality_metrics']
                entry = MemoryEntry(
                    agent_name='vault-analyzer',
                    entry_type='metrics',
                    content=f"Quality Assessment: Completeness={metrics.get('completeness', 0):.2f}, Connectivity={metrics.get('connectivity', 0):.2f}, Organization={metrics.get('organization', 0):.2f}",
                    metadata={
                        'completeness': metrics.get('completeness', 0),
                        'connectivity': metrics.get('connectivity', 0),
                        'organization': metrics.get('organization', 0),
                        'consistency': metrics.get('consistency', 0)
                    },
                    timestamp=datetime.utcnow(),
                    relevance_score=0.85
                )
                memory_entries.append(entry)
            
            # Store suggestions for future reference
            if 'suggestions' in results:
                for suggestion in results['suggestions']:
                    entry = MemoryEntry(
                        agent_name='vault-analyzer',
                        entry_type='recommendation',
                        content=f"Recommendation: {suggestion.get('suggestion', 'Unknown')} (Priority: {suggestion.get('priority', 'medium')})",
                        metadata={
                            'type': suggestion.get('type', 'general'),
                            'priority': suggestion.get('priority', 'medium'),
                            'category': 'improvement'
                        },
                        timestamp=datetime.utcnow(),
                        relevance_score=0.7
                    )
                    memory_entries.append(entry)
            
            # Store all entries in parallel using Basic Memory
            if memory_entries:
                storage_results = await parallel_memory.store_agent_patterns_parallel(memory_entries)
                success_count = sum(1 for success in storage_results.values() if success)
                logger.info(f"Stored {success_count}/{len(memory_entries)} learning entries in Basic Memory")
            
        except Exception as e:
            logger.error(f"Failed to store learning in parallel: {e}")


class EnhancedAgentManager:
    """Enhanced Agent Manager with parallel execution capabilities"""
    
    def __init__(self, config_path: str = ".agent-os/agents/config.yaml"):
        self.config_path = Path(config_path)
        self.agents = {}
        self.executor = ParallelExecutor(max_workers=5)
        self.redis_client = None
        self.memory = defaultdict(list)
        
        # Load configuration
        self.load_config()
        self._memory_initialized = False
        
        # Initialize Basic Memory integration lazily
    
    async def _ensure_memory_initialized(self):
        """Ensure memory is initialized"""
        if not self._memory_initialized:
            await self.initialize_memory()
            self._memory_initialized = True
        
    def load_config(self):
        """Load agent configuration"""
        try:
            with open(self.config_path, 'r') as f:
                self.config = yaml.safe_load(f)
            logger.info(f"Loaded agent configuration from {self.config_path}")
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            self.config = {}
    
    async def initialize_memory(self):
        """Initialize Basic Memory integration for agents"""
        try:
            await parallel_memory.initialize_project()
            logger.info("Basic Memory integration initialized for Agent OS")
        except Exception as e:
            logger.warning(f"Basic Memory initialization failed: {e}")
    
    async def initialize_redis(self):
        """Initialize Redis connection for caching and coordination"""
        try:
            self.redis_client = await redis.from_url(
                "redis://localhost:6379",
                encoding="utf-8",
                decode_responses=True
            )
            await self.redis_client.ping()
            logger.info("Redis connection established")
        except Exception as e:
            logger.warning(f"Redis not available: {e}. Using in-memory cache.")
            self.redis_client = None
    
    @measure_performance
    async def execute_agents_parallel(self, agent_names: List[str], context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute multiple agents in parallel"""
        
        # Create tasks for each agent
        tasks = []
        for agent_name in agent_names:
            if agent_name in ['vault-analyzer', 'synthesis-assistant', 'context-optimizer']:
                tasks.append(ParallelTask(
                    name=agent_name,
                    func=self.execute_agent,
                    args=(agent_name, context),
                    priority=self._get_agent_priority(agent_name),
                    timeout=60
                ))
        
        # Execute all agents in parallel
        logger.info(f"Executing {len(tasks)} agents in parallel...")
        results = await self.executor.execute_parallel(tasks)
        
        # Store results in memory
        timestamp = datetime.utcnow().isoformat()
        for agent_name, result in results.items():
            self.memory[agent_name].append({
                'timestamp': timestamp,
                'result': result
            })
        
        # Cache results if Redis available
        if self.redis_client:
            for agent_name, result in results.items():
                cache_key = f"agent:{agent_name}:latest"
                await self.redis_client.setex(
                    cache_key,
                    3600,  # 1 hour TTL
                    json.dumps(result)
                )
        
        return results
    
    async def execute_agent(self, agent_name: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single agent"""
        await self._ensure_memory_initialized()
        logger.info(f"Executing agent: {agent_name}")
        
        # Check cache first
        if self.redis_client:
            cache_key = f"agent:{agent_name}:latest"
            cached = await self.redis_client.get(cache_key)
            if cached:
                logger.info(f"Using cached result for {agent_name}")
                return json.loads(cached)
        
        # Execute agent based on type
        if agent_name == 'vault-analyzer':
            # Load vault data
            vault_dict = pickle.load(open("data/vault_dict.pickle", "rb"))
            vault_path = os.environ.get('OBSIDIAN_PATH', '/obsidian-vault')
            
            analyzer = EnhancedVaultAnalyzer(vault_path, vault_dict)
            result = await analyzer.analyze_vault_parallel()
            
        elif agent_name == 'synthesis-assistant':
            result = {
                'status': 'ready',
                'capabilities': ['thematic', 'chronological', 'argumentative'],
                'max_documents': 50
            }
            
        elif agent_name == 'context-optimizer':
            result = {
                'cache_hit_rate': 0.72,
                'avg_latency_ms': 1250,
                'optimizations_available': ['index_rebuild', 'cache_clear']
            }
            
        else:
            result = {'status': 'not_implemented'}
        
        return result
    
    def _get_agent_priority(self, agent_name: str) -> int:
        """Get agent priority from config"""
        priorities = {
            'context-optimizer': 1,
            'vault-analyzer': 2,
            'suggestion-engine': 3,
            'synthesis-assistant': 4,
            'research-assistant': 5
        }
        return priorities.get(agent_name, 5)
    
    async def get_agent_status_parallel(self, agent_names: List[str]) -> Dict[str, Dict]:
        """Get status of multiple agents in parallel"""
        tasks = [
            ParallelTask(
                name=agent_name,
                func=self._get_single_agent_status,
                args=(agent_name,)
            )
            for agent_name in agent_names
        ]
        
        return await self.executor.execute_parallel(tasks)
    
    async def _get_single_agent_status(self, agent_name: str) -> Dict:
        """Get status of a single agent"""
        config = self.config.get('agents', {}).get(agent_name, {})
        
        # Check if agent has recent results in cache
        last_execution = None
        if self.redis_client:
            cache_key = f"agent:{agent_name}:latest"
            cached = await self.redis_client.get(cache_key)
            if cached:
                last_execution = datetime.utcnow().isoformat()
        
        return {
            'enabled': config.get('enabled', False),
            'type': config.get('type', 'unknown'),
            'description': config.get('description', ''),
            'last_execution': last_execution,
            'capabilities': config.get('capabilities', [])
        }
    
    def cleanup(self):
        """Cleanup resources"""
        self.executor.shutdown()
        if self.redis_client:
            asyncio.create_task(self.redis_client.close())


# Create global enhanced agent manager
enhanced_agent_manager = EnhancedAgentManager()