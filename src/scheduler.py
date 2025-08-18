"""
Agent Scheduler for Agent OS
Manages scheduled, triggered, and continuous agent execution
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.date import DateTrigger
import json
from pathlib import Path

from .agents import (
    AgentManager, 
    AgentRequest, 
    AgentResponse,
    AgentStatus,
    TriggerType
)

logger = logging.getLogger(__name__)


class AgentScheduler:
    """Manages scheduled execution of agents"""
    
    def __init__(self, agent_manager: AgentManager):
        self.agent_manager = agent_manager
        self.scheduler = AsyncIOScheduler()
        self.monitoring_tasks: Dict[str, asyncio.Task] = {}
        self.trigger_handlers: Dict[str, Callable] = {}
        self.execution_history: List[Dict] = []
        self.max_history = 1000
        
        # Initialize scheduler
        self.setup_scheduled_agents()
        self.setup_monitoring_agents()
        
    def start(self):
        """Start the scheduler"""
        logger.info("Starting agent scheduler")
        self.scheduler.start()
        
        # Start monitoring tasks
        for agent_name, task_func in self.monitoring_tasks.items():
            asyncio.create_task(task_func())
    
    def stop(self):
        """Stop the scheduler"""
        logger.info("Stopping agent scheduler")
        self.scheduler.shutdown()
        
        # Cancel monitoring tasks
        for task in self.monitoring_tasks.values():
            if isinstance(task, asyncio.Task):
                task.cancel()
    
    def setup_scheduled_agents(self):
        """Setup agents with schedule triggers"""
        for agent_name, agent in self.agent_manager.agents.items():
            config = agent.config
            
            if not config.enabled:
                continue
            
            trigger_config = config.trigger
            trigger_type = trigger_config.get('type')
            
            if trigger_type == TriggerType.SCHEDULE:
                self.setup_scheduled_agent(agent_name, trigger_config)
    
    def setup_scheduled_agent(self, agent_name: str, trigger_config: Dict):
        """Setup a single scheduled agent"""
        interval = trigger_config.get('interval')
        time = trigger_config.get('time')
        
        if interval == 'daily' and time:
            # Parse time (HH:MM format)
            hour, minute = map(int, time.split(':'))
            trigger = CronTrigger(hour=hour, minute=minute)
            
        elif interval == 'hourly':
            trigger = IntervalTrigger(hours=1)
            
        elif interval == 'weekly':
            # Default to Sunday at specified time or midnight
            if time:
                hour, minute = map(int, time.split(':'))
            else:
                hour, minute = 0, 0
            trigger = CronTrigger(day_of_week='sun', hour=hour, minute=minute)
            
        elif isinstance(interval, int):
            # Interval in seconds
            trigger = IntervalTrigger(seconds=interval)
            
        else:
            logger.warning(f"Unknown schedule interval for {agent_name}: {interval}")
            return
        
        # Add job to scheduler
        self.scheduler.add_job(
            func=self.execute_scheduled_agent,
            trigger=trigger,
            args=[agent_name],
            id=f"scheduled_{agent_name}",
            name=f"Scheduled execution of {agent_name}",
            replace_existing=True
        )
        
        logger.info(f"Scheduled agent {agent_name} with trigger {trigger}")
    
    def setup_monitoring_agents(self):
        """Setup agents with continuous or context-aware triggers"""
        for agent_name, agent in self.agent_manager.agents.items():
            config = agent.config
            
            if not config.enabled:
                continue
            
            trigger_config = config.trigger
            trigger_type = trigger_config.get('type')
            
            if trigger_type == TriggerType.CONTINUOUS:
                self.setup_continuous_agent(agent_name, trigger_config)
            elif trigger_type == TriggerType.CONTEXT_AWARE:
                self.setup_context_aware_agent(agent_name, trigger_config)
    
    def setup_continuous_agent(self, agent_name: str, trigger_config: Dict):
        """Setup continuously monitoring agent"""
        check_interval = trigger_config.get('check_interval', 300)  # Default 5 minutes
        conditions = trigger_config.get('conditions', [])
        
        async def monitor():
            """Monitoring loop for continuous agent"""
            while True:
                try:
                    # Check conditions
                    should_run = await self.check_conditions(conditions)
                    
                    if should_run:
                        logger.info(f"Conditions met for {agent_name}, executing")
                        await self.execute_scheduled_agent(agent_name)
                    
                    # Wait before next check
                    await asyncio.sleep(check_interval)
                    
                except asyncio.CancelledError:
                    break
                except Exception as e:
                    logger.error(f"Error in continuous monitoring for {agent_name}: {e}")
                    await asyncio.sleep(check_interval)
        
        self.monitoring_tasks[agent_name] = monitor
        logger.info(f"Setup continuous monitoring for {agent_name}")
    
    def setup_context_aware_agent(self, agent_name: str, trigger_config: Dict):
        """Setup context-aware triggered agent"""
        monitors = trigger_config.get('monitors', [])
        debounce_ms = trigger_config.get('debounce_ms', 2000)
        
        async def monitor():
            """Monitoring loop for context-aware agent"""
            last_trigger = None
            
            while True:
                try:
                    # Check monitored conditions
                    trigger_context = await self.check_monitors(monitors)
                    
                    if trigger_context:
                        current_time = datetime.utcnow()
                        
                        # Apply debouncing
                        if last_trigger:
                            time_since_last = (current_time - last_trigger).total_seconds() * 1000
                            if time_since_last < debounce_ms:
                                await asyncio.sleep((debounce_ms - time_since_last) / 1000)
                                continue
                        
                        logger.info(f"Context trigger for {agent_name}")
                        await self.execute_scheduled_agent(
                            agent_name, 
                            context=trigger_context
                        )
                        last_trigger = current_time
                    
                    # Small delay to prevent busy loop
                    await asyncio.sleep(1)
                    
                except asyncio.CancelledError:
                    break
                except Exception as e:
                    logger.error(f"Error in context monitoring for {agent_name}: {e}")
                    await asyncio.sleep(5)
        
        self.monitoring_tasks[agent_name] = monitor
        logger.info(f"Setup context-aware monitoring for {agent_name}")
    
    async def check_conditions(self, conditions: List[str]) -> bool:
        """Check if conditions are met for agent execution"""
        for condition in conditions:
            if condition == 'cache_size_exceeded':
                # Check cache size
                cache_size = await self.get_cache_size()
                if cache_size > 500 * 1024 * 1024:  # 500MB
                    return True
                    
            elif condition == 'performance_degradation':
                # Check performance metrics
                performance = await self.get_performance_metrics()
                if performance.get('latency_ms', 0) > 3000:
                    return True
                    
            elif condition == 'new_documents_detected':
                # Check for new documents
                new_docs = await self.check_new_documents()
                if new_docs:
                    return True
        
        return False
    
    async def check_monitors(self, monitors: List[str]) -> Optional[Dict]:
        """Check monitored conditions and return trigger context"""
        context = {}
        
        for monitor in monitors:
            if monitor == 'active_note_changes':
                # Check for active note changes
                changes = await self.get_active_note_changes()
                if changes:
                    context['active_note_changes'] = changes
                    
            elif monitor == 'query_patterns':
                # Check query patterns
                patterns = await self.get_query_patterns()
                if patterns:
                    context['query_patterns'] = patterns
                    
            elif monitor == 'navigation_history':
                # Check navigation history
                history = await self.get_navigation_history()
                if history:
                    context['navigation_history'] = history
        
        return context if context else None
    
    async def execute_scheduled_agent(
        self, 
        agent_name: str, 
        context: Optional[Dict] = None
    ):
        """Execute a scheduled agent"""
        try:
            logger.info(f"Executing scheduled agent: {agent_name}")
            
            request = AgentRequest(
                agent_name=agent_name,
                context=context or {},
                parameters={}
            )
            
            response = await self.agent_manager.execute_agent(request)
            
            # Record execution
            self.record_execution(agent_name, request, response)
            
            if response.status == AgentStatus.COMPLETED:
                logger.info(f"Agent {agent_name} completed successfully")
            else:
                logger.error(f"Agent {agent_name} failed: {response.error}")
            
            return response
            
        except Exception as e:
            logger.error(f"Failed to execute scheduled agent {agent_name}: {e}")
            self.record_execution(
                agent_name,
                AgentRequest(agent_name=agent_name),
                AgentResponse(
                    agent_name=agent_name,
                    status=AgentStatus.FAILED,
                    error=str(e)
                )
            )
    
    def record_execution(
        self, 
        agent_name: str, 
        request: AgentRequest, 
        response: AgentResponse
    ):
        """Record agent execution in history"""
        execution = {
            'timestamp': datetime.utcnow().isoformat(),
            'agent_name': agent_name,
            'trigger': 'scheduled',
            'request': request.dict(),
            'response': response.dict()
        }
        
        self.execution_history.append(execution)
        
        # Trim history if too large
        if len(self.execution_history) > self.max_history:
            self.execution_history = self.execution_history[-self.max_history:]
    
    async def trigger_agent(
        self, 
        agent_name: str, 
        command: Optional[str] = None,
        parameters: Optional[Dict] = None,
        context: Optional[Dict] = None
    ) -> AgentResponse:
        """Manually trigger an agent execution"""
        logger.info(f"Manually triggering agent: {agent_name}")
        
        request = AgentRequest(
            agent_name=agent_name,
            command=command,
            parameters=parameters or {},
            context=context or {}
        )
        
        response = await self.agent_manager.execute_agent(request)
        
        # Record as manual trigger
        execution = {
            'timestamp': datetime.utcnow().isoformat(),
            'agent_name': agent_name,
            'trigger': 'manual',
            'request': request.dict(),
            'response': response.dict()
        }
        self.execution_history.append(execution)
        
        return response
    
    def get_schedule_info(self) -> List[Dict]:
        """Get information about scheduled agents"""
        jobs = []
        
        for job in self.scheduler.get_jobs():
            next_run = job.next_run_time
            jobs.append({
                'id': job.id,
                'name': job.name,
                'next_run': next_run.isoformat() if next_run else None,
                'trigger': str(job.trigger)
            })
        
        return jobs
    
    def get_execution_history(
        self, 
        agent_name: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict]:
        """Get execution history"""
        history = self.execution_history
        
        if agent_name:
            history = [h for h in history if h['agent_name'] == agent_name]
        
        return history[-limit:]
    
    def pause_agent(self, agent_name: str):
        """Pause scheduled execution of an agent"""
        job_id = f"scheduled_{agent_name}"
        self.scheduler.pause_job(job_id)
        logger.info(f"Paused agent: {agent_name}")
    
    def resume_agent(self, agent_name: str):
        """Resume scheduled execution of an agent"""
        job_id = f"scheduled_{agent_name}"
        self.scheduler.resume_job(job_id)
        logger.info(f"Resumed agent: {agent_name}")
    
    def reschedule_agent(
        self, 
        agent_name: str, 
        trigger_config: Dict
    ):
        """Reschedule an agent with new trigger configuration"""
        # Remove existing job
        job_id = f"scheduled_{agent_name}"
        self.scheduler.remove_job(job_id)
        
        # Add with new configuration
        self.setup_scheduled_agent(agent_name, trigger_config)
        logger.info(f"Rescheduled agent: {agent_name}")
    
    # Helper methods for condition checking (would integrate with actual system)
    
    async def get_cache_size(self) -> int:
        """Get current cache size in bytes"""
        # Would check actual cache size
        return 0
    
    async def get_performance_metrics(self) -> Dict[str, float]:
        """Get current performance metrics"""
        # Would get actual metrics
        return {'latency_ms': 1000}
    
    async def check_new_documents(self) -> bool:
        """Check if new documents have been added"""
        # Would check actual document changes
        return False
    
    async def get_active_note_changes(self) -> Optional[Dict]:
        """Get changes in active note"""
        # Would monitor actual note changes
        return None
    
    async def get_query_patterns(self) -> Optional[Dict]:
        """Get recent query patterns"""
        # Would analyze actual query patterns
        return None
    
    async def get_navigation_history(self) -> Optional[Dict]:
        """Get recent navigation history"""
        # Would track actual navigation
        return None


class SchedulerAPI:
    """API interface for the scheduler"""
    
    def __init__(self, scheduler: AgentScheduler):
        self.scheduler = scheduler
    
    async def trigger_agent(
        self,
        agent_name: str,
        command: Optional[str] = None,
        parameters: Optional[Dict] = None
    ) -> Dict:
        """Trigger an agent via API"""
        response = await self.scheduler.trigger_agent(
            agent_name,
            command,
            parameters
        )
        return response.dict()
    
    async def get_schedule(self) -> List[Dict]:
        """Get schedule information"""
        return self.scheduler.get_schedule_info()
    
    async def get_history(
        self,
        agent_name: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict]:
        """Get execution history"""
        return self.scheduler.get_execution_history(agent_name, limit)
    
    async def pause_agent(self, agent_name: str) -> Dict:
        """Pause an agent"""
        self.scheduler.pause_agent(agent_name)
        return {'status': 'paused', 'agent': agent_name}
    
    async def resume_agent(self, agent_name: str) -> Dict:
        """Resume an agent"""
        self.scheduler.resume_agent(agent_name)
        return {'status': 'resumed', 'agent': agent_name}
    
    async def get_agent_status(self, agent_name: str) -> Dict:
        """Get detailed agent status"""
        status = await self.scheduler.agent_manager.get_agent_status(agent_name)
        
        # Add schedule information
        schedule_info = [
            job for job in self.scheduler.get_schedule_info()
            if agent_name in job['id']
        ]
        
        status['schedule'] = schedule_info
        status['recent_executions'] = self.scheduler.get_execution_history(
            agent_name, 
            limit=5
        )
        
        return status