"""
Orchestrator Agent Executor
This module contains the implementation of the Orchestrator Agent's skills.
"""

import logging
import httpx
from typing import Dict, Any, Optional
import sys
from pathlib import Path
import asyncio
from datetime import datetime

# Add parent directory for common_utils access
parent_dir = Path(__file__).resolve().parent.parent.parent
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))

from common_utils.agent_discovery import get_agent_registry
from common_utils.agent_security import create_secure_headers
from common_utils.session_manager import get_session_manager
from common_utils.observability import get_observability_manager, trace_operation

logger = logging.getLogger(__name__)

class OrchestratorAgentExecutor:
    """
    The Orchestrator delegates tasks to specialized agents based on their
    advertised capabilities. It follows the hub-and-spoke model.
    """
    def __init__(self):
        self.agent_registry = get_agent_registry()
        self.session_manager = get_session_manager()
        self.observability = get_observability_manager()
        self.orchestrator_api_key = None  # Set during server initialization
        logger.info("OrchestratorAgentExecutor initialized.")

    async def delegate_task_skill(self, agent_name: str, skill_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Delegates a task to a specialized agent. This is the primary skill
        of the orchestrator, acting as the central hub for A2A communication.
        
        Args:
            agent_name: The name of the target agent to delegate the task to.
            skill_name: The name of the skill to invoke on the target agent.
            params: The parameters to pass to the agent's skill.

        Returns:
            The result from the specialized agent.
        """
        logger.info(f"Delegating task '{skill_name}' to agent '{agent_name}' with params: {params}")
        
        with trace_operation("delegate_task", agent=agent_name, skill=skill_name):
            try:
                agent_info = self.agent_registry.get_agent(agent_name)
                if not agent_info or agent_info.get("status") != "active":
                    raise ValueError(f"Agent '{agent_name}' is not available or not active.")
                
                endpoint = agent_info["card"]["url"]
                
                # Create a session for this interaction
                session = self.session_manager.create_session({
                    "task": "delegation",
                    "target_agent": agent_name,
                    "skill": skill_name
                })
                
                self.session_manager.add_event(session.session_id, "task_delegation_started", params)

                result = await self._call_agent(endpoint, skill_name, params)
                
                self.session_manager.add_event(session.session_id, "task_delegation_completed", result)
                
                return {
                    "status": "completed",
                    "delegation_to": agent_name,
                    "skill_executed": skill_name,
                    "result": result
                }

            except Exception as e:
                logger.exception(f"Error delegating task to {agent_name}: {e}")
                if 'session' in locals():
                    self.session_manager.add_event(session.session_id, "task_delegation_failed", {"error": str(e)})
                
                return {
                    "status": "error",
                    "error": str(e),
                    "agent_name": agent_name,
                    "skill_name": skill_name
                }

    async def _call_agent(self, agent_url: str, method: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Makes a secure, observable, and resilient call to a remote agent.
        """
        request_payload = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params,
            "id": f"orchestrator_{method}",
        }

        headers = await create_secure_headers()

        async with httpx.AsyncClient() as client:
            # The circuit breaker from common_utils would be integrated here in a production system
            # for resilience. For now, a direct call is made.
            response = await client.post(agent_url, json=request_payload, headers=headers, timeout=300.0)
            response.raise_for_status()
            response_data = response.json()
            
            if "error" in response_data:
                raise ValueError(f"Remote agent at {agent_url} returned error: {response_data['error']}")
            
            return response_data.get("result", {}) 