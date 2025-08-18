"""
Agent OS Backend Implementation
Provides autonomous agent capabilities for Obsidian Copilot
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel, Field
import yaml
import subprocess
from collections import defaultdict
import hashlib

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Agent types
class AgentType(str, Enum):
    AUTONOMOUS = "autonomous"
    REACTIVE = "reactive"
    BACKGROUND = "background"
    PROACTIVE = "proactive"
    INTERACTIVE = "interactive"

# Agent trigger types
class TriggerType(str, Enum):
    SCHEDULE = "schedule"
    ON_DEMAND = "on_demand"
    CONTINUOUS = "continuous"
    CONTEXT_AWARE = "context_aware"

# Agent status
class AgentStatus(str, Enum):
    IDLE = "idle"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    DISABLED = "disabled"

# Request/Response Models
class AgentRequest(BaseModel):
    agent_name: str
    command: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = {}
    context: Optional[Dict[str, Any]] = {}
    timeout: Optional[int] = 60

class AgentResponse(BaseModel):
    agent_name: str
    status: AgentStatus
    result: Optional[Any] = None
    error: Optional[str] = None
    execution_time: Optional[float] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class AgentConfig(BaseModel):
    name: str
    type: AgentType
    enabled: bool = True
    description: str
    trigger: Dict[str, Any]
    capabilities: List[str]
    configuration: Dict[str, Any]
    prompts: Optional[Dict[str, str]] = {}

class AgentManager:
    """Manages all Agent OS agents"""
    
    def __init__(self, config_path: str = ".agent-os/agents/config.yaml"):
        self.config_path = Path(config_path)
        self.agents: Dict[str, Agent] = {}
        self.agent_configs: Dict[str, AgentConfig] = {}
        self.running_agents: Dict[str, asyncio.Task] = {}
        self.agent_memory: Dict[str, List[Dict]] = defaultdict(list)
        
        # Load configuration
        self.load_config()
        self.initialize_agents()
    
    def load_config(self):
        """Load agent configurations from YAML"""
        try:
            with open(self.config_path, 'r') as f:
                config = yaml.safe_load(f)
                
            self.global_config = config.get('global', {})
            
            # Parse agent configurations
            for agent_name, agent_config in config.get('agents', {}).items():
                self.agent_configs[agent_name] = AgentConfig(
                    name=agent_name,
                    **agent_config
                )
                
            logger.info(f"Loaded {len(self.agent_configs)} agent configurations")
            
        except Exception as e:
            logger.error(f"Failed to load agent config: {e}")
            self.agent_configs = {}
    
    def initialize_agents(self):
        """Initialize all configured agents"""
        for name, config in self.agent_configs.items():
            if not config.enabled:
                logger.info(f"Agent {name} is disabled, skipping initialization")
                continue
                
            try:
                agent_class = self._get_agent_class(name)
                self.agents[name] = agent_class(config, self)
                logger.info(f"Initialized agent: {name}")
            except Exception as e:
                logger.error(f"Failed to initialize agent {name}: {e}")
    
    def _get_agent_class(self, agent_name: str):
        """Get the appropriate agent class based on name"""
        agent_classes = {
            'vault-analyzer': VaultAnalyzerAgent,
            'synthesis-assistant': SynthesisAssistantAgent,
            'context-optimizer': ContextOptimizerAgent,
            'suggestion-engine': SuggestionEngineAgent,
            'research-assistant': ResearchAssistantAgent
        }
        return agent_classes.get(agent_name, BaseAgent)
    
    async def execute_agent(self, request: AgentRequest) -> AgentResponse:
        """Execute an agent with the given request"""
        agent = self.agents.get(request.agent_name)
        
        if not agent:
            return AgentResponse(
                agent_name=request.agent_name,
                status=AgentStatus.FAILED,
                error=f"Agent {request.agent_name} not found"
            )
        
        if not agent.config.enabled:
            return AgentResponse(
                agent_name=request.agent_name,
                status=AgentStatus.DISABLED,
                error=f"Agent {request.agent_name} is disabled"
            )
        
        try:
            # Check if agent is already running
            if request.agent_name in self.running_agents:
                return AgentResponse(
                    agent_name=request.agent_name,
                    status=AgentStatus.RUNNING,
                    error="Agent is already running"
                )
            
            # Create task for agent execution
            task = asyncio.create_task(
                agent.execute(request)
            )
            self.running_agents[request.agent_name] = task
            
            # Wait for completion with timeout
            result = await asyncio.wait_for(
                task,
                timeout=request.timeout or self.global_config.get('default_timeout', 60)
            )
            
            # Store in memory
            self.agent_memory[request.agent_name].append({
                'timestamp': datetime.utcnow().isoformat(),
                'request': request.dict(),
                'response': result.dict()
            })
            
            return result
            
        except asyncio.TimeoutError:
            return AgentResponse(
                agent_name=request.agent_name,
                status=AgentStatus.FAILED,
                error=f"Agent execution timed out after {request.timeout} seconds"
            )
        except Exception as e:
            logger.error(f"Agent {request.agent_name} execution failed: {e}")
            return AgentResponse(
                agent_name=request.agent_name,
                status=AgentStatus.FAILED,
                error=str(e)
            )
        finally:
            # Clean up running agents
            if request.agent_name in self.running_agents:
                del self.running_agents[request.agent_name]
    
    async def get_agent_status(self, agent_name: str) -> Dict[str, Any]:
        """Get current status of an agent"""
        if agent_name not in self.agents:
            return {'error': f'Agent {agent_name} not found'}
        
        agent = self.agents[agent_name]
        is_running = agent_name in self.running_agents
        
        # Get recent history
        recent_history = self.agent_memory.get(agent_name, [])[-5:]
        
        return {
            'name': agent_name,
            'type': agent.config.type,
            'enabled': agent.config.enabled,
            'running': is_running,
            'description': agent.config.description,
            'capabilities': agent.config.capabilities,
            'recent_executions': recent_history
        }
    
    async def list_agents(self) -> List[Dict[str, Any]]:
        """List all available agents"""
        agents = []
        for name, agent in self.agents.items():
            is_running = name in self.running_agents
            agents.append({
                'name': name,
                'type': agent.config.type,
                'enabled': agent.config.enabled,
                'running': is_running,
                'description': agent.config.description
            })
        return agents
    
    def get_agent_memory(self, agent_name: str, limit: int = 10) -> List[Dict]:
        """Get agent execution history"""
        return self.agent_memory.get(agent_name, [])[-limit:]


class BaseAgent:
    """Base class for all agents"""
    
    def __init__(self, config: AgentConfig, manager: AgentManager):
        self.config = config
        self.manager = manager
        self.logger = logging.getLogger(f"agent.{config.name}")
    
    async def execute(self, request: AgentRequest) -> AgentResponse:
        """Execute the agent's main task"""
        start_time = datetime.utcnow()
        
        try:
            # Run the agent's specific logic
            result = await self.run(request)
            
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            
            return AgentResponse(
                agent_name=self.config.name,
                status=AgentStatus.COMPLETED,
                result=result,
                execution_time=execution_time
            )
            
        except Exception as e:
            self.logger.error(f"Agent execution failed: {e}")
            return AgentResponse(
                agent_name=self.config.name,
                status=AgentStatus.FAILED,
                error=str(e),
                execution_time=(datetime.utcnow() - start_time).total_seconds()
            )
    
    async def run(self, request: AgentRequest) -> Any:
        """Override this method in subclasses"""
        raise NotImplementedError("Subclasses must implement run method")
    
    async def call_claude(self, prompt: str, context: Optional[str] = None) -> str:
        """Call Claude CLI for analysis"""
        try:
            # Build the full prompt
            full_prompt = prompt
            if context:
                full_prompt = f"{context}\n\n{prompt}"
            
            # Call Claude CLI
            cmd = [
                "claude",
                "code",
                "--model", self.manager.global_config.get('claude_model', 'claude-3-5-sonnet-20241022'),
                "--max-tokens", str(self.manager.global_config.get('max_context_tokens', 150000))
            ]
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate(full_prompt.encode())
            
            if process.returncode != 0:
                raise Exception(f"Claude CLI failed: {stderr.decode()}")
            
            return stdout.decode()
            
        except Exception as e:
            self.logger.error(f"Failed to call Claude: {e}")
            raise


class VaultAnalyzerAgent(BaseAgent):
    """Analyzes the vault for patterns and insights"""
    
    async def run(self, request: AgentRequest) -> Dict[str, Any]:
        """Run vault analysis"""
        self.logger.info("Starting vault analysis")
        
        # Get vault statistics
        vault_stats = await self.get_vault_stats()
        
        # Analyze recent changes
        recent_analysis = await self.analyze_recent_changes()
        
        # Detect patterns
        patterns = await self.detect_patterns()
        
        # Generate insights
        insights = await self.generate_insights(vault_stats, recent_analysis, patterns)
        
        # Create report
        report = {
            'timestamp': datetime.utcnow().isoformat(),
            'statistics': vault_stats,
            'recent_changes': recent_analysis,
            'patterns': patterns,
            'insights': insights,
            'recommendations': await self.generate_recommendations(insights)
        }
        
        # Save report if configured
        if self.config.configuration.get('save_to'):
            await self.save_report(report)
        
        return report
    
    async def get_vault_stats(self) -> Dict[str, Any]:
        """Get basic vault statistics"""
        # This would integrate with the actual vault
        # For now, return mock data
        return {
            'total_notes': 0,
            'total_links': 0,
            'orphaned_notes': 0,
            'tag_count': 0
        }
    
    async def analyze_recent_changes(self) -> Dict[str, Any]:
        """Analyze recently modified notes"""
        # Would analyze actual recent changes
        return {
            'modified_today': 0,
            'created_today': 0,
            'deleted_today': 0
        }
    
    async def detect_patterns(self) -> List[Dict[str, Any]]:
        """Detect patterns in the vault"""
        # Would perform actual pattern detection
        return []
    
    async def generate_insights(self, stats, changes, patterns) -> List[str]:
        """Generate insights from analysis"""
        insights = []
        
        # Would use Claude to generate actual insights
        prompt = f"""
        Based on the following vault analysis, generate 3-5 key insights:
        
        Statistics: {json.dumps(stats, indent=2)}
        Recent Changes: {json.dumps(changes, indent=2)}
        Patterns: {json.dumps(patterns, indent=2)}
        
        Focus on actionable insights that would help improve knowledge management.
        """
        
        try:
            response = await self.call_claude(prompt)
            # Parse insights from response
            insights = [line.strip() for line in response.split('\n') if line.strip()]
        except:
            insights = ["Analysis completed but insight generation failed"]
        
        return insights
    
    async def generate_recommendations(self, insights) -> List[str]:
        """Generate recommendations based on insights"""
        return [
            "Consider linking orphaned notes",
            "Review and consolidate similar tags",
            "Update outdated content"
        ]
    
    async def save_report(self, report):
        """Save report to configured location"""
        # Would save to actual location
        self.logger.info(f"Report saved to {self.config.configuration.get('save_to')}")


class SynthesisAssistantAgent(BaseAgent):
    """Creates comprehensive syntheses from multiple documents"""
    
    async def run(self, request: AgentRequest) -> Dict[str, Any]:
        """Run synthesis task"""
        self.logger.info("Starting synthesis")
        
        # Get documents to synthesize
        documents = request.parameters.get('documents', [])
        synthesis_type = request.parameters.get('type', 'thematic')
        
        if len(documents) < 2:
            raise ValueError("Synthesis requires at least 2 documents")
        
        # Load document contents
        doc_contents = await self.load_documents(documents)
        
        # Perform synthesis based on type
        if synthesis_type == 'thematic':
            result = await self.thematic_synthesis(doc_contents)
        elif synthesis_type == 'chronological':
            result = await self.chronological_synthesis(doc_contents)
        elif synthesis_type == 'argumentative':
            result = await self.argumentative_synthesis(doc_contents)
        else:
            result = await self.comparative_synthesis(doc_contents)
        
        return {
            'synthesis_type': synthesis_type,
            'documents_analyzed': len(documents),
            'result': result,
            'timestamp': datetime.utcnow().isoformat()
        }
    
    async def load_documents(self, document_paths: List[str]) -> List[Dict[str, str]]:
        """Load document contents"""
        # Would load actual documents
        return [{'path': path, 'content': f'Content of {path}'} for path in document_paths]
    
    async def thematic_synthesis(self, documents: List[Dict]) -> str:
        """Create thematic synthesis"""
        prompt = self.config.prompts.get('analysis', '') + "\n\n"
        prompt += "Create a thematic synthesis of the following documents:\n\n"
        
        for doc in documents:
            prompt += f"Document: {doc['path']}\n{doc['content']}\n\n"
        
        prompt += "Identify major themes and create a comprehensive synthesis."
        
        return await self.call_claude(prompt)
    
    async def chronological_synthesis(self, documents: List[Dict]) -> str:
        """Create chronological synthesis"""
        prompt = "Create a chronological synthesis organizing information by time..."
        return await self.call_claude(prompt)
    
    async def argumentative_synthesis(self, documents: List[Dict]) -> str:
        """Create argumentative synthesis"""
        prompt = "Build a logical argument chain from the provided documents..."
        return await self.call_claude(prompt)
    
    async def comparative_synthesis(self, documents: List[Dict]) -> str:
        """Create comparative synthesis"""
        prompt = "Compare and contrast the perspectives in these documents..."
        return await self.call_claude(prompt)


class ContextOptimizerAgent(BaseAgent):
    """Optimizes context retrieval and caching"""
    
    async def run(self, request: AgentRequest) -> Dict[str, Any]:
        """Run context optimization"""
        self.logger.info("Starting context optimization")
        
        # Analyze current performance
        performance = await self.analyze_performance()
        
        # Optimize indices if needed
        if performance['index_performance'] < 0.8:
            await self.optimize_indices()
        
        # Clear stale cache
        cache_cleared = await self.clear_stale_cache()
        
        # Precompute common queries
        precomputed = await self.precompute_queries()
        
        return {
            'performance_before': performance,
            'optimizations_performed': {
                'indices_optimized': performance['index_performance'] < 0.8,
                'cache_cleared': cache_cleared,
                'queries_precomputed': precomputed
            },
            'performance_after': await self.analyze_performance()
        }
    
    async def analyze_performance(self) -> Dict[str, float]:
        """Analyze current system performance"""
        return {
            'cache_hit_rate': 0.65,
            'index_performance': 0.75,
            'query_latency_ms': 1500
        }
    
    async def optimize_indices(self):
        """Optimize search indices"""
        self.logger.info("Optimizing indices")
        # Would perform actual optimization
    
    async def clear_stale_cache(self) -> int:
        """Clear stale cache entries"""
        self.logger.info("Clearing stale cache")
        # Would clear actual cache
        return 42  # Number of entries cleared
    
    async def precompute_queries(self) -> int:
        """Precompute common queries"""
        self.logger.info("Precomputing common queries")
        # Would precompute actual queries
        return 10  # Number of queries precomputed


class SuggestionEngineAgent(BaseAgent):
    """Provides proactive suggestions"""
    
    async def run(self, request: AgentRequest) -> Dict[str, Any]:
        """Generate suggestions"""
        self.logger.info("Generating suggestions")
        
        context = request.context or {}
        
        # Analyze current context
        active_note = context.get('active_note')
        recent_queries = context.get('recent_queries', [])
        
        suggestions = []
        
        # Generate different types of suggestions
        if active_note:
            suggestions.extend(await self.suggest_related_notes(active_note))
        
        if recent_queries:
            suggestions.extend(await self.suggest_query_improvements(recent_queries))
        
        # Rank suggestions
        ranked_suggestions = await self.rank_suggestions(suggestions)
        
        return {
            'suggestions': ranked_suggestions[:5],  # Top 5 suggestions
            'total_generated': len(suggestions),
            'context_used': bool(active_note or recent_queries)
        }
    
    async def suggest_related_notes(self, note_path: str) -> List[Dict]:
        """Suggest related notes"""
        # Would find actual related notes
        return [
            {
                'type': 'related_note',
                'title': 'Related Note 1',
                'relevance': 0.92,
                'reason': 'Contains similar concepts'
            }
        ]
    
    async def suggest_query_improvements(self, queries: List[str]) -> List[Dict]:
        """Suggest query improvements"""
        return [
            {
                'type': 'query_improvement',
                'suggestion': 'Try adding tags to narrow results',
                'relevance': 0.85
            }
        ]
    
    async def rank_suggestions(self, suggestions: List[Dict]) -> List[Dict]:
        """Rank suggestions by relevance"""
        return sorted(suggestions, key=lambda x: x.get('relevance', 0), reverse=True)


class ResearchAssistantAgent(BaseAgent):
    """Assists with deep research tasks"""
    
    async def run(self, request: AgentRequest) -> Dict[str, Any]:
        """Run research task"""
        self.logger.info("Starting research")
        
        query = request.parameters.get('query', '')
        research_type = request.parameters.get('type', 'exploratory')
        depth = request.parameters.get('depth', 3)
        
        # Plan research
        research_plan = await self.create_research_plan(query, research_type)
        
        # Execute research
        findings = await self.execute_research(research_plan, depth)
        
        # Synthesize findings
        synthesis = await self.synthesize_findings(findings)
        
        # Generate report
        report = await self.generate_research_report(
            query, research_plan, findings, synthesis
        )
        
        return {
            'query': query,
            'research_type': research_type,
            'plan': research_plan,
            'findings_count': len(findings),
            'synthesis': synthesis,
            'report': report
        }
    
    async def create_research_plan(self, query: str, research_type: str) -> Dict:
        """Create research plan"""
        return {
            'main_question': query,
            'sub_questions': [
                f"What is known about {query}?",
                f"What are the key concepts related to {query}?",
                f"What evidence supports or contradicts {query}?"
            ],
            'search_strategy': research_type,
            'scope': 'vault-wide'
        }
    
    async def execute_research(self, plan: Dict, depth: int) -> List[Dict]:
        """Execute research plan"""
        findings = []
        
        # Would perform actual research
        for question in plan['sub_questions'][:depth]:
            findings.append({
                'question': question,
                'evidence': f"Evidence for {question}",
                'sources': ['Note1.md', 'Note2.md']
            })
        
        return findings
    
    async def synthesize_findings(self, findings: List[Dict]) -> str:
        """Synthesize research findings"""
        prompt = "Synthesize the following research findings:\n\n"
        for finding in findings:
            prompt += f"Question: {finding['question']}\n"
            prompt += f"Evidence: {finding['evidence']}\n\n"
        
        return await self.call_claude(prompt)
    
    async def generate_research_report(self, query, plan, findings, synthesis) -> str:
        """Generate research report"""
        report = f"# Research Report: {query}\n\n"
        report += f"## Research Plan\n{json.dumps(plan, indent=2)}\n\n"
        report += f"## Findings\n"
        for finding in findings:
            report += f"- {finding['question']}: {finding['evidence']}\n"
        report += f"\n## Synthesis\n{synthesis}\n"
        
        return report


# Create global agent manager instance
agent_manager = AgentManager()