"""
Menu Qa Agent Executor
Executor for the menu-qa-agent agent.
"""

import logging
from typing import Dict, Any, List, Optional
import sys
from pathlib import Path

# Add parent directory for common_utils access
parent_dir = Path(__file__).resolve().parent.parent.parent
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))

from common_utils.data_handle_manager import get_data_handle_manager

import redis
import os
import json
from typing import Dict, Any
from fuzzywuzzy import fuzz
from .tools import (get_menu_item, search_menu_by_category, search_by_dietary_restriction, get_item_price, check_availability, search_by_ingredient, get_full_menu)

logger = logging.getLogger(__name__)

class AgentExecutor:
    """
    Menu Qa Agent agent executor with specialized functionality.
    Specialized agent for answering questions about current menu items, availability, pricing, ingredients, and dietary restrictions
    """
    
    def __init__(self):
        self.data_manager = get_data_handle_manager()
        logger.info("Menu Qa Agent initialized")
        # Disable Redis for now since it's not running
        # self.redis_client = redis.from_url(os.getenv('REDIS_URL', 'redis://localhost:6379/0'))
        # self.cache_ttl = 300  # 5 minutes for menu cache
        self.redis_client = None
        self.cache_ttl = 300

    def _get_from_cache(self, key: str) -> Optional[Dict]:
        # Skip caching if Redis is not available
        return None
        # cached = self.redis_client.get(key)
        # return json.loads(cached) if cached else None

    def _set_to_cache(self, key: str, value: Dict) -> None:
        # Skip caching if Redis is not available
        pass
        # self.redis_client.setex(key, self.cache_ttl, json.dumps(value))

    async def process_task_skill(self, task_description: str, parameters: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Main processing skill for menu-qa-agent.
        
        Args:
            task_description: Description of the task to perform
            parameters: Optional parameters for the task
            
        Returns:
            Dict containing the result of the task processing
        """
        try:
            logger.info(f"Processing task: {task_description}")
            
            if parameters is None:
                parameters = {}
            
            task_lower = task_description.lower()
            cache_key = f"menu_qa:{hash(task_description + str(parameters))}"

            cached = self._get_from_cache(cache_key)
            if cached:
                return cached

            if 'get item' in task_lower or 'details' in task_lower:
                result = get_menu_item(parameters.get('identifier', ''))
            elif 'category' in task_lower:
                result = search_menu_by_category(parameters.get('category', ''))
            elif 'dietary' in task_lower or 'restriction' in task_lower:
                result = search_by_dietary_restriction(parameters.get('restriction', ''))
            elif 'price' in task_lower:
                result = get_item_price(parameters.get('item_id', 0))
            elif 'availability' in task_lower:
                result = {'available': check_availability(parameters.get('item_id', 0))}
            elif 'ingredient' in task_lower:
                result = search_by_ingredient(parameters.get('ingredient', ''))
            elif 'full menu' in task_lower:
                result = get_full_menu(parameters.get('location_id'))
            else:
                # Fuzzy search fallback
                all_items = get_full_menu()
                result = [item for item in all_items if fuzz.partial_ratio(task_description, item['name']) > 70][:5]

            self._set_to_cache(cache_key, result)
            return result
            
        except Exception as e:
            logger.error(f"Error processing task: {str(e)}")
            return {"status": "error", "error": str(e)}

    async def get_capabilities_skill(self) -> Dict[str, Any]:
        """
        Returns the capabilities of this agent.
        
        Returns:
            Dict describing agent capabilities
        """
        return {
            "agent_type": "specialized",
            "capabilities": [
                "process_task_skill",
                "get_capabilities_skill"
            ],
            "description": "Specialized agent for answering questions about current menu items, availability, pricing, ingredients, and dietary restrictions",
            "version": "1.0.0"
        } 

    async def get_env_vars_skill(self) -> Dict[str, Any]:
        """
        Returns the environment variables.
        
        Returns:
            Dict containing the environment variables
        """
        return dict(os.environ) 