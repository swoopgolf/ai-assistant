#!/usr/bin/env python3
"""
Agent Discovery System - Dynamic agent discovery for A2A framework.

This module provides a registry that reads from the central system_config.yaml
to discover agents and their capabilities.
"""

import logging
import asyncio
import httpx
from typing import Dict, List, Optional, Any
from datetime import datetime

from .types import AgentCard
from .config import get_config

logger = logging.getLogger(__name__)

class AgentRegistry:
    """
    Central registry for A2A agent discovery, using system_config.yaml as the
    single source of truth for agent definitions.
    """
    
    def __init__(self):
        self.agents: Dict[str, Dict[str, Any]] = {}
        self.load_registry_from_config()
        
    async def register_self(self, agent_name: str, agent_url: str) -> bool:
        """Allows an agent to register itself with the registry."""
        # This is a simplified registration. A real implementation would
        # fetch the agent's full capabilities card.
        logger.info(f"Registering agent '{agent_name}' with URL: {agent_url}")
        self.agents[agent_name] = {
            "card": {
                "name": agent_name,
                "url": agent_url,
                "description": "Self-registered agent", # Placeholder description
            },
            "registered_at": datetime.now().isoformat(),
            "status": "active" # Assume active upon registration
        }
        return True

    def load_registry_from_config(self):
        """Load agent definitions from the central system_config.yaml."""
        try:
            agent_configs = get_config("agents")
            if not agent_configs:
                logger.warning("No 'agents' section found in system_config.yaml")
                return

            for agent_name, config in agent_configs.items():
                agent_card = {
                    "name": agent_name,
                    "description": config.get("description", ""),
                    "url": f"http://{config.get('host')}:{config.get('port')}",
                    "skills": [{"id": skill, "name": skill} for skill in config.get("capabilities", [])],
                    "version": config.get("version", "1.0.0")
                }
                
                self.agents[agent_name] = {
                    "card": agent_card,
                    "registered_at": datetime.now().isoformat(),
                    "last_health_check": None,
                    "status": "active" # Assume active from config
                }
            logger.info(f"Loaded {len(self.agents)} agents from system_config.yaml")

        except Exception as e:
            logger.exception(f"Failed to load agent registry from config: {e}")
            self.agents = {}
    
    def get_agent(self, agent_name: str) -> Optional[Dict[str, Any]]:
        """Get agent information by name."""
        return self.agents.get(agent_name)
    
    def get_agent_by_capability(self, capability: str) -> List[Dict[str, Any]]:
        """Find agents that have a specific capability (skill)."""
        matching_agents = []
        for agent_name, agent_info in self.agents.items():
            if agent_info.get("status") == "active":
                agent_card = agent_info.get("card", {})
                skills = agent_card.get("skills", [])
                for skill in skills:
                    if skill.get("id") == capability:
                        matching_agents.append(agent_info)
                        break
        return matching_agents
    
    def list_agents(self, only_active: bool = True) -> Dict[str, Dict[str, Any]]:
        """List all registered agents."""
        if only_active:
            # Health checks would update the status dynamically
            return {name: info for name, info in self.agents.items() if info.get("status") == "active"}
        return self.agents.copy()
    
    def get_agent_endpoints(self) -> Dict[str, str]:
        """Get a mapping of agent names to their endpoints."""
        return {
            agent_name: info["card"]["url"]
            for agent_name, info in self.agents.items()
            if info.get("status") == "active"
        }
    
    async def health_check_agent(self, agent_name: str) -> bool:
        """Check if an agent is responding to health checks."""
        agent_info = self.agents.get(agent_name)
        if not agent_info:
            return False
        
        url = agent_info["card"]["url"]
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{url}/health")
                is_healthy = response.status_code == 200
                
                agent_info["last_health_check"] = datetime.now().isoformat()
                agent_info["status"] = "active" if is_healthy else "unhealthy"
                return is_healthy
                
        except Exception as e:
            logger.warning(f"Health check failed for {agent_name}: {e}")
            agent_info["last_health_check"] = datetime.now().isoformat()
            agent_info["status"] = "unreachable"
            return False

# Global registry instance
_registry = None

def get_agent_registry() -> AgentRegistry:
    """Get the global agent registry instance."""
    global _registry
    if _registry is None:
        _registry = AgentRegistry()
    return _registry

# Create alias for backward compatibility
AgentDiscoveryClient = AgentRegistry

def register_agent_with_registry(agent_card) -> bool:
    """Register agent with registry for backward compatibility."""
    logger.info(f"Agent registration requested")
    return True 