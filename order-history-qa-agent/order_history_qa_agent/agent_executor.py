"""
Order History Qa Agent Executor
Executor for the order-history-qa-agent agent.
"""

import logging
import os
import redis
import json
from typing import Dict, Any, List, Optional
import sys
from pathlib import Path

# Add parent directory for common_utils access
parent_dir = Path(__file__).resolve().parent.parent.parent
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))

from common_utils.data_handle_manager import get_data_handle_manager
from .tools import (get_sales_summary, get_top_selling_items, analyze_order_patterns, get_revenue_metrics, analyze_customer_behavior, get_item_performance, execute_custom_query)

logger = logging.getLogger(__name__)

class AgentExecutor:
    """
    Order History Qa Agent agent executor with specialized functionality.
    Specialized agent for answering questions about order history, sales analytics, and business intelligence queries using natural language to SQL conversion
    """
    
    def __init__(self):
        self.data_manager = get_data_handle_manager()
        logger.info("Order History Qa Agent initialized")
        # Disable Redis for now since it's not running
        # self.redis_client = redis.from_url(os.getenv('REDIS_URL', 'redis://localhost:6379/0'))
        # self.cache_ttl = int(os.getenv('ANALYTICS_CACHE_TTL', 3600))
        self.redis_client = None
        self.cache_ttl = int(os.getenv('ANALYTICS_CACHE_TTL', 3600))

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
        Main processing skill for order-history-qa-agent.
        
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
            
            # Simple routing based on task_description keywords
            task_lower = task_description.lower()
            cache_key = f"order_history:{hash(task_description + str(parameters))}"

            cached_result = self._get_from_cache(cache_key)
            if cached_result:
                logger.info("Returning cached result")
                return cached_result

            if 'sales summary' in task_lower:
                result = get_sales_summary(**parameters)
            elif 'top selling' in task_lower:
                result = get_top_selling_items(**parameters)
            elif 'order patterns' in task_lower:
                result = analyze_order_patterns(**parameters)
            elif 'revenue metrics' in task_lower:
                result = get_revenue_metrics(**parameters)
            elif 'customer behavior' in task_lower:
                result = analyze_customer_behavior(**parameters)
            elif 'item performance' in task_lower:
                result = get_item_performance(**parameters.get('item_id', 0), **parameters)
            elif 'custom query' in task_lower:
                result = execute_custom_query(parameters.get('sql_query', ''))
            else:
                result = {'message': 'Task not recognized', 'task': task_description}

            # For visualization, add simple text-based chart if applicable
            if isinstance(result, list) and len(result) > 0 and 'total_quantity' in result[0]:
                # Simple bar chart for top items
                chart = '\n'.join([f"{item['item_name']}: {'*' * int(item['total_quantity'] / 10)}" for item in result])
                result['visualization'] = chart

            self._set_to_cache(cache_key, result)
            return result
            
        except Exception as e:
            logger.error(f"Error processing task: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "message": "Failed to process task"
            }

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
            "description": "Specialized agent for answering questions about order history, sales analytics, and business intelligence queries using natural language to SQL conversion",
            "version": "1.0.0"
        } 