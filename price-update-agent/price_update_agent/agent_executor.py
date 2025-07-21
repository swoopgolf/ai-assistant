"""
Price Update Agent Executor
Executor for the price-update-agent agent.
"""

import logging
from typing import Dict, Any, List, Optional
import sys
import os
from pathlib import Path

# Add parent directory for common_utils access
parent_dir = Path(__file__).resolve().parent.parent.parent
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))

from common_utils.data_handle_manager import get_data_handle_manager
from .tools import (
    update_item_price,
    bulk_price_update,
    update_item_availability,
    set_promotional_pricing,
    revert_price_change,
    get_price_history,
    validate_price_change
)

logger = logging.getLogger(__name__)

class AgentExecutor:
    """
    Price Update Agent executor with specialized functionality for price updates and menu modifications.
    """
    
    def __init__(self):
        self.data_manager = get_data_handle_manager()
        self.require_approval = os.getenv('REQUIRE_APPROVAL', 'false').lower() == 'true'
        self.approval_threshold = float(os.getenv('REQUIRE_REASON_ABOVE_PERCENT', '20'))
        logger.info("Price Update Agent initialized")

    async def process_task_skill(self, task_description: str, parameters: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Main processing skill for price-update-agent with task routing and validation.
        
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
            
            # Route tasks based on description
            if "update price" in task_lower or "change price" in task_lower:
                return await self._handle_price_update(parameters)
            elif "bulk update" in task_lower or "bulk price" in task_lower:
                return await self._handle_bulk_price_update(parameters)
            elif "availability" in task_lower or "enable" in task_lower or "disable" in task_lower:
                return await self._handle_availability_change(parameters)
            elif "promotional" in task_lower or "promo" in task_lower:
                return await self._handle_promotional_pricing(parameters)
            elif "revert" in task_lower or "undo" in task_lower:
                return await self._handle_price_revert(parameters)
            elif "history" in task_lower or "audit" in task_lower:
                return await self._handle_price_history(parameters)
            elif "validate" in task_lower or "check" in task_lower:
                return await self._handle_validation(parameters)
            else:
                return {
                    "status": "error",
                    "message": f"Unknown task type: {task_description}. Supported: update price, bulk update, availability, promotional, revert, history, validate"
                }
            
        except Exception as e:
            logger.error(f"Error processing task: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "message": "Failed to process task"
            }

    async def _handle_price_update(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Handle individual price updates with approval workflow."""
        item_id = parameters.get('item_id')
        new_price = parameters.get('new_price')
        reason = parameters.get('reason', '')
        changed_by = parameters.get('changed_by', 'system')
        
        if not item_id or not new_price:
            return {"status": "error", "message": "item_id and new_price are required"}
        
        # Validate the change first
        validation = validate_price_change(item_id, new_price)
        if not validation.get('valid'):
            return {"status": "error", "message": validation.get('message')}
        
        # Check if approval is required
        percent_change = abs(validation.get('percent_change', 0))
        if self.require_approval and percent_change > self.approval_threshold:
            if not reason:
                return {
                    "status": "approval_required",
                    "message": f"Price change of {percent_change:.1f}% requires approval and reason",
                    "validation": validation
                }
        
        # Execute the price update
        result = update_item_price(item_id, new_price, reason, changed_by)
        return result

    async def _handle_bulk_price_update(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Handle bulk price updates."""
        updates = parameters.get('updates', [])
        reason = parameters.get('reason', '')
        changed_by = parameters.get('changed_by', 'system')
        
        if not updates:
            return {"status": "error", "message": "updates list is required"}
        
        # Validate all changes first
        validations = []
        for update in updates:
            validation = validate_price_change(update.get('item_id'), update.get('new_price'))
            validations.append(validation)
            if not validation.get('valid'):
                return {"status": "error", "message": f"Validation failed for item {update.get('item_id')}: {validation.get('message')}"}
        
        # Execute bulk update
        result = bulk_price_update(updates, reason, changed_by)
        return result

    async def _handle_availability_change(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Handle item availability changes."""
        item_id = parameters.get('item_id')
        available = parameters.get('available')
        reason = parameters.get('reason', '')
        
        if item_id is None or available is None:
            return {"status": "error", "message": "item_id and available are required"}
        
        result = update_item_availability(item_id, available, reason)
        return result

    async def _handle_promotional_pricing(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Handle promotional pricing setup."""
        result = set_promotional_pricing(
            parameters.get('item_id'),
            parameters.get('promo_price'),
            parameters.get('start_date'),
            parameters.get('end_date'),
            parameters.get('promo_name', '')
        )
        return result

    async def _handle_price_revert(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Handle price change reversion."""
        change_id = parameters.get('change_id')
        if not change_id:
            return {"status": "error", "message": "change_id is required"}
        
        result = revert_price_change(change_id)
        return result

    async def _handle_price_history(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Handle price history retrieval."""
        item_id = parameters.get('item_id')
        limit = parameters.get('limit', 10)
        
        if not item_id:
            return {"status": "error", "message": "item_id is required"}
        
        history = get_price_history(item_id, limit)
        return {"status": "success", "history": history}

    async def _handle_validation(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Handle price change validation."""
        item_id = parameters.get('item_id')
        new_price = parameters.get('new_price')
        
        if not item_id or not new_price:
            return {"status": "error", "message": "item_id and new_price are required"}
        
        validation = validate_price_change(item_id, new_price)
        return {"status": "success", "validation": validation}

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
            "description": "Specialized agent for executing menu price updates, item modifications, and availability changes with approval workflows and audit logging",
            "version": "1.0.0",
            "supported_tasks": [
                "update_price",
                "bulk_price_update", 
                "availability_change",
                "promotional_pricing",
                "price_revert",
                "price_history",
                "validate_price_change"
            ]
        } 