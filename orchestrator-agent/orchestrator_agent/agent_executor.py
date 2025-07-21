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
import json # Added for json.loads
import requests

# Add parent directory for common_utils access
parent_dir = Path(__file__).resolve().parent.parent.parent
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))

from google.adk.models.google_llm import Gemini
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
        self.llm = Gemini() # Initialize the LLM for routing
        logger.info("OrchestratorAgentExecutor initialized.")

    async def refresh_registry_skill(self) -> Dict[str, Any]:
        """Refresh the agent registry by discovering running agents."""
        try:
            logger.info("Refreshing agent registry...")
            
            # Known agent ports and names
            agents_info = [
                {"name": "classification-agent", "port": 10300},
                {"name": "order-history-qa-agent", "port": 10210},
                {"name": "menu-qa-agent", "port": 10220},
                {"name": "price-update-agent", "port": 10410},
                {"name": "pdf-ingestion-agent", "port": 10350}
            ]
            
            discovered_count = 0
            for agent_info in agents_info:
                try:
                    url = f"http://localhost:{agent_info['port']}/agent_card"
                    response = requests.get(url, timeout=5)
                    if response.status_code == 200:
                        agent_card = response.json()
                        
                        # Register with registry
                        self.agent_registry.agents[agent_info['name']] = {
                            "card": agent_card,
                            "registered_at": datetime.now().isoformat(),
                            "last_health_check": None,
                            "status": "active"
                        }
                        logger.info(f"Registered agent: {agent_info['name']}")
                        discovered_count += 1
                    else:
                        logger.warning(f"Agent {agent_info['name']} not responding on port {agent_info['port']}")
                        
                except Exception as e:
                    logger.warning(f"Failed to discover agent {agent_info['name']}: {e}")
            
            agents = self.agent_registry.list_agents()
            logger.info(f"Registry refresh complete. {discovered_count} agents discovered, {len(agents)} total agents available.")
            
            return {
                "status": "success",
                "discovered_agents": discovered_count,
                "total_agents": len(agents),
                "agents": list(agents.keys())
            }
            
        except Exception as e:
            logger.exception(f"Failed to refresh registry: {e}")
            return {
                "status": "error",
                "error": str(e)
            }

    async def _classify_task(self, task_description: str) -> Optional[Dict[str, Any]]:
        """Uses the classification agent to determine the best agent for a given task."""
        try:
            # Get classification agent info
            classification_agent = self.agent_registry.get_agent("classification-agent")
            if not classification_agent:
                logger.error("Classification agent is not registered")
                return None
            
            classification_endpoint = classification_agent["card"]["url"]
            
            # Prepare classification request
            classification_params = {
                "query": task_description,
                "conversation_context": {},
                "use_cache": True
            }
            
            # Call classification agent
            classification_result = await self._call_agent(
                classification_endpoint, 
                "execute", 
                classification_params
            )
            
            logger.info(f"Classification result: {classification_result}")
            return classification_result
            
        except Exception as e:
            logger.exception(f"Failed to classify task with classification agent: {e}")
            return None

    async def _get_agent_from_llm(self, task_description: str) -> Optional[str]:
        """Uses an LLM to determine the best agent for a given task."""
        # Get agents from registry (registry should be refreshed separately)
        agents = self.agent_registry.list_agents()
        if not agents:
            logger.error("No agents are registered. Attempting registry refresh.")
            # Try to refresh registry once if no agents found
            try:
                refresh_result = await self.refresh_registry_skill()
                agents = self.agent_registry.list_agents()
                if not agents:
                    logger.error("Still no agents after refresh.")
                    return None
            except Exception as e:
                logger.error(f"Registry refresh failed: {e}")
                return None

        # Format the agent capabilities for the prompt
        agent_descriptions = "\n".join(
            f"- {name}: {details['card'].get('description', 'No description')}"
            for name, details in agents.items()
        )

        prompt = f"""
        You are an intelligent routing agent. Your job is to select the best specialized agent to handle a user's request based on the agents' capabilities.

        Here are the available agents:
        {agent_descriptions}

        User Request: "{task_description}"

        Based on the user's request, which agent is the most appropriate?
        Return ONLY the name of the agent as a JSON string, for example: {{"agent_name": "order-history-qa-agent"}}
        
        Choose from these exact agent names:
        - order-history-qa-agent (for sales, orders, analytics, business intelligence)
        - menu-qa-agent (for menu items, ingredients, dietary info, availability)
        - price-update-agent (for updating prices, modifying items)
        - pdf-ingestion-agent (for processing PDF documents)
        """

        try:
            response_str = await self.llm.apredict(
                prompt, model="gemini-1.5-flash"
            )
            logger.info(f"LLM response: {response_str}")
            
            # The response should be a JSON string, parse it to get the agent name
            response_json = json.loads(response_str.strip())
            agent_name = response_json.get("agent_name")
            logger.info(f"LLM selected agent '{agent_name}' for the task.")
            return agent_name
        except Exception as e:
            logger.exception(f"Failed to get routing decision from LLM: {e}")
            # Fallback to simple keyword-based routing if LLM fails
            return self._fallback_routing(task_description)
    
    def _fallback_routing(self, task_description: str) -> Optional[str]:
        """Simple keyword-based routing fallback when LLM fails."""
        task_lower = task_description.lower()
        
        # Simple keyword matching for routing
        if any(word in task_lower for word in ['sales', 'revenue', 'analytics', 'order', 'business']):
            return "order-history-qa-agent"
        elif any(word in task_lower for word in ['menu', 'vegetarian', 'ingredients', 'dietary', 'availability']):
            return "menu-qa-agent"
        elif any(word in task_lower for word in ['price', 'update', 'cost', 'pricing']):
            return "price-update-agent"
        elif any(word in task_lower for word in ['pdf', 'document', 'upload', 'file']):
            return "pdf-ingestion-agent"
        else:
            # Default to menu agent for general queries
            logger.info(f"No specific routing found for '{task_description}', defaulting to menu-qa-agent")
            return "menu-qa-agent"

    async def delegate_task_skill(self, task_description: str) -> Dict[str, Any]:
        """
        Intelligently delegates a task to the correct specialized agent
        based on the provided task description, using the classification agent for routing.
        
        Args:
            task_description: A natural language description of the task.

        Returns:
            The result from the specialized agent.
        """
        logger.info(f"Orchestrator received task: '{task_description}'")

        # --- Classification-Based Routing ---
        classification_result = await self._classify_task(task_description)
        
        if not classification_result or classification_result.get("status") == "error":
            logger.warning(f"Classification failed for task: '{task_description}', using fallback routing")
            agent_name = self._fallback_routing(task_description)
        else:
            agent_name = classification_result.get("routing", {}).get("target_agent")
            logger.info(f"Classification agent recommended: {agent_name} (confidence: {classification_result.get('routing', {}).get('confidence', 0.0)})")

        skill_name = "process_task" # All specialized agents use a standard entry point

        if not agent_name:
            logger.warning(f"Could not determine a suitable agent for task: '{task_description}'")
            return {"status": "error", "message": "Could not determine the appropriate agent for your request."}

        logger.info(f"Routing task to agent: '{agent_name}'")

        params = {
            "task_description": task_description,
            "parameters": {},
            "classification": classification_result.get("classification", {}) if classification_result else {}
        }
        
        with trace_operation("delegate_task", agent=agent_name, skill=skill_name):
            try:
                agent_info = self.agent_registry.get_agent(agent_name)
                # Note: We are currently not checking agent health/status from the registry
                # to simplify the POC. In production, this check is critical.
                if not agent_info:
                    raise ValueError(f"Agent '{agent_name}' is not registered.")
                
                endpoint = agent_info["card"]["url"]
                
                session = self.session_manager.create_session({
                    "task": "delegation",
                    "target_agent": agent_name,
                    "skill": skill_name,
                    "description": task_description
                })
                self.session_manager.add_event(session.session_id, "task_delegation_started", params)

                result = await self._call_agent(endpoint, skill_name, params)
                
                self.session_manager.add_event(session.session_id, "task_delegation_completed", result)
                
                return {
                    "status": "completed",
                    "delegation_to": agent_name,
                    "result": result
                }

            except Exception as e:
                logger.exception(f"Error delegating task to {agent_name}: {e}")
                if 'session' in locals():
                    self.session_manager.add_event(session.session_id, "task_delegation_failed", {"error": str(e)})
                
                return {
                    "status": "error",
                    "error": str(e),
                    "agent_name": agent_name
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

        # Temporarily disable security headers for testing
        # headers = create_secure_headers("orchestrator")
        headers = {"Content-Type": "application/json"}

        async with httpx.AsyncClient() as client:
            # The circuit breaker from common_utils would be integrated here in a production system
            # for resilience. For now, a direct call is made.
            response = await client.post(agent_url, json=request_payload, headers=headers, timeout=300.0)
            response.raise_for_status()
            response_data = response.json()
            
            if "error" in response_data:
                raise ValueError(f"Remote agent at {agent_url} returned error: {response_data['error']}")
            
            return response_data.get("result", {}) 