"""Tool definitions for the price-update-agent."""

import os
from datetime import datetime, date
from typing import Dict, List, Any, Optional
from google.adk.tools import FunctionTool
from common_utils.database import get_database_manager

db_manager = get_database_manager()

def update_item_price(item_id: int, new_price: float, reason: str = "", changed_by: str = "system") -> Dict[str, Any]:
    """
    Update the price of a menu item with audit logging.
    
    Args:
        item_id: ID of the item to update
        new_price: New price for the item
        reason: Reason for the price change
        changed_by: Who made the change
        
    Returns:
        Dict with update status and details
    """
    try:
        # Get current price first
        current_item = db_manager.execute_query("SELECT price, name FROM items WHERE id = %(id)s", {'id': item_id})
        if not current_item:
            return {"status": "error", "message": "Item not found"}
        
        old_price = float(current_item[0]['price'])
        item_name = current_item[0]['name']
        
        # Validate price change
        max_increase = float(os.getenv('MAX_PRICE_INCREASE', 50))
        percent_increase = ((new_price - old_price) / old_price) * 100 if old_price > 0 else 0
        
        if percent_increase > max_increase:
            return {"status": "error", "message": f"Price increase of {percent_increase:.1f}% exceeds maximum allowed ({max_increase}%)"}
        
        # Update item price
        queries = [
            ("UPDATE items SET price = %(new_price)s, updated_at = NOW() WHERE id = %(id)s", 
             {'new_price': new_price, 'id': item_id}),
            # Note: This will fail if price_history table doesn't exist - need to create it
            ("INSERT INTO price_history (item_id, old_price, new_price, change_reason, changed_by, changed_at) VALUES (%(item_id)s, %(old_price)s, %(new_price)s, %(reason)s, %(changed_by)s, NOW())",
             {'item_id': item_id, 'old_price': old_price, 'new_price': new_price, 'reason': reason, 'changed_by': changed_by})
        ]
        
        success = db_manager.execute_transaction(queries)
        
        if success:
            return {
                "status": "success",
                "item_id": item_id,
                "item_name": item_name,
                "old_price": old_price,
                "new_price": new_price,
                "percent_change": percent_increase,
                "message": f"Price updated for {item_name} from ${old_price:.2f} to ${new_price:.2f}"
            }
        else:
            return {"status": "error", "message": "Failed to update price"}
            
    except Exception as e:
        return {"status": "error", "message": str(e)}

def bulk_price_update(updates: List[Dict[str, Any]], reason: str = "", changed_by: str = "system") -> Dict[str, Any]:
    """
    Update multiple item prices in bulk.
    
    Args:
        updates: List of dicts with item_id and new_price
        reason: Reason for bulk update
        changed_by: Who made the changes
        
    Returns:
        Dict with bulk update results
    """
    max_bulk = int(os.getenv('MAX_BULK_ITEMS', 100))
    if len(updates) > max_bulk:
        return {"status": "error", "message": f"Bulk update limited to {max_bulk} items"}
    
    results = []
    for update in updates:
        result = update_item_price(update['item_id'], update['new_price'], reason, changed_by)
        results.append(result)
    
    successful = len([r for r in results if r.get('status') == 'success'])
    return {
        "status": "success",
        "total_items": len(updates),
        "successful_updates": successful,
        "failed_updates": len(updates) - successful,
        "results": results
    }

def update_item_availability(item_id: int, available: bool, reason: str = "") -> Dict[str, Any]:
    """
    Update item availability status.
    
    Args:
        item_id: ID of the item
        available: True to enable, False to disable
        reason: Reason for availability change
        
    Returns:
        Dict with update status
    """
    try:
        query = "UPDATE items SET disabled = %(disabled)s, updated_at = NOW() WHERE id = %(id)s"
        params = {'disabled': not available, 'id': item_id}
        
        rows_affected = db_manager.execute_non_query(query, params)
        
        if rows_affected > 0:
            return {
                "status": "success",
                "item_id": item_id,
                "available": available,
                "message": f"Item {'enabled' if available else 'disabled'} successfully"
            }
        else:
            return {"status": "error", "message": "Item not found"}
            
    except Exception as e:
        return {"status": "error", "message": str(e)}

def set_promotional_pricing(item_id: int, promo_price: float, start_date: str, end_date: str, promo_name: str = "") -> Dict[str, Any]:
    """
    Set promotional pricing for an item (placeholder - requires promotional_pricing table).
    
    Args:
        item_id: ID of the item
        promo_price: Promotional price
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)
        promo_name: Name of the promotion
        
    Returns:
        Dict with operation status
    """
    # This would require the promotional_pricing table to be created
    return {
        "status": "pending",
        "message": "Promotional pricing requires promotional_pricing table to be created",
        "item_id": item_id,
        "promo_price": promo_price,
        "start_date": start_date,
        "end_date": end_date,
        "promo_name": promo_name
    }

def revert_price_change(change_id: int) -> Dict[str, Any]:
    """
    Revert a previous price change (requires price_history table).
    
    Args:
        change_id: ID from price_history table
        
    Returns:
        Dict with revert status
    """
    # This would require the price_history table to be created
    return {
        "status": "pending",
        "message": "Price change reversion requires price_history table to be created",
        "change_id": change_id
    }

def get_price_history(item_id: int, limit: int = 10) -> List[Dict[str, Any]]:
    """
    Get price change history for an item (requires price_history table).
    
    Args:
        item_id: ID of the item
        limit: Number of records to return
        
    Returns:
        List of price change records
    """
    try:
        query = """
            SELECT * FROM price_history 
            WHERE item_id = %(item_id)s 
            ORDER BY changed_at DESC 
            LIMIT %(limit)s
        """
        params = {'item_id': item_id, 'limit': limit}
        return db_manager.execute_query(query, params)
    except Exception as e:
        return [{"status": "error", "message": "price_history table not found"}]

def validate_price_change(item_id: int, new_price: float) -> Dict[str, Any]:
    """
    Validate a proposed price change without executing it.
    
    Args:
        item_id: ID of the item
        new_price: Proposed new price
        
    Returns:
        Dict with validation results
    """
    try:
        current_item = db_manager.execute_query("SELECT price, name FROM items WHERE id = %(id)s", {'id': item_id})
        if not current_item:
            return {"valid": False, "message": "Item not found"}
        
        old_price = float(current_item[0]['price'])
        item_name = current_item[0]['name']
        
        if new_price <= 0:
            return {"valid": False, "message": "Price must be greater than 0"}
        
        percent_change = ((new_price - old_price) / old_price) * 100 if old_price > 0 else 0
        max_increase = float(os.getenv('MAX_PRICE_INCREASE', 50))
        
        valid = abs(percent_change) <= max_increase
        
        return {
            "valid": valid,
            "item_name": item_name,
            "current_price": old_price,
            "proposed_price": new_price,
            "percent_change": percent_change,
            "max_allowed_change": max_increase,
            "message": "Valid price change" if valid else f"Price change exceeds maximum allowed ({max_increase}%)"
        }
        
    except Exception as e:
        return {"valid": False, "message": str(e)}

# Create FunctionTool instances
update_item_price_tool = FunctionTool(func=update_item_price)
bulk_price_update_tool = FunctionTool(func=bulk_price_update)
update_item_availability_tool = FunctionTool(func=update_item_availability)
set_promotional_pricing_tool = FunctionTool(func=set_promotional_pricing)
revert_price_change_tool = FunctionTool(func=revert_price_change)
get_price_history_tool = FunctionTool(func=get_price_history)
validate_price_change_tool = FunctionTool(func=validate_price_change)

# List of all available tools for dynamic discovery
ALL_TOOLS = [
    update_item_price_tool,
    bulk_price_update_tool,
    update_item_availability_tool,
    set_promotional_pricing_tool,
    revert_price_change_tool,
    get_price_history_tool,
    validate_price_change_tool,
] 