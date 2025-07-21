"""Tool definitions for the menu-qa-agent."""

from typing import Dict, List, Any, Optional
from google.adk.tools import FunctionTool
from common_utils.database import get_database_manager

db_manager = get_database_manager()

def get_menu_item(identifier: str) -> Dict[str, Any]:
    """
    Retrieve menu item details by name or ID.
    
    Args:
        identifier: Item name or ID
    
    Returns:
        Dict with item details
    """
    if identifier.isdigit():
        query = "SELECT * FROM items WHERE id = %(id)s"
        params = {'id': int(identifier)}
    else:
        query = "SELECT * FROM items WHERE name ILIKE %(name)s"
        params = {'name': f'%{identifier}%'}
    results = db_manager.execute_query(query, params)
    return results[0] if results else {}

def search_menu_by_category(category: str) -> List[Dict[str, Any]]:
    """
    Search menu items by category name.
    """
    query = """
        SELECT i.* FROM items i
        JOIN categories c ON i.category_id = c.id
        WHERE c.name ILIKE %(category)s AND i.disabled = false
    """
    params = {'category': f'%{category}%'}
    return db_manager.execute_query(query, params)

def search_by_dietary_restriction(restriction: str) -> List[Dict[str, Any]]:
    """
    Search by dietary restriction. Note: Schema lacks dietary_flags, returning all for now.
    """
    # TODO: Implement properly when schema updated
    query = "SELECT * FROM items WHERE disabled = false LIMIT 10"
    return db_manager.execute_query(query)

def get_item_price(item_id: int) -> Dict[str, float]:
    """
    Get current price for item.
    """
    query = "SELECT price FROM items WHERE id = %(id)s"
    params = {'id': item_id}
    results = db_manager.execute_query(query, params)
    return {'price': results[0]['price'] if results else 0.0}

def check_availability(item_id: int) -> bool:
    """
    Check if item is available (not disabled).
    """
    query = "SELECT disabled FROM items WHERE id = %(id)s"
    params = {'id': item_id}
    results = db_manager.execute_query(query, params)
    return not results[0]['disabled'] if results else False

def search_by_ingredient(ingredient: str) -> List[Dict[str, Any]]:
    """
    Search items by ingredient in description (since no ingredient field).
    """
    query = "SELECT * FROM items WHERE description ILIKE %(ingredient)s AND disabled = false"
    params = {'ingredient': f'%{ingredient}%'}
    return db_manager.execute_query(query, params)

def get_full_menu(location_id: Optional[int] = None) -> List[Dict[str, Any]]:
    """
    Get full menu, optionally filtered by location.
    """
    query = "SELECT i.* FROM items i JOIN categories c ON i.category_id = c.id JOIN menus m ON c.menu_id = m.id WHERE i.disabled = false"
    params = {}
    if location_id:
        query += " AND m.location_id = %(location_id)s"
        params['location_id'] = location_id
    return db_manager.execute_query(query, params)

# Create FunctionTool instances
get_menu_item_tool = FunctionTool(func=get_menu_item)
search_menu_by_category_tool = FunctionTool(func=search_menu_by_category)
search_by_dietary_restriction_tool = FunctionTool(func=search_by_dietary_restriction)
get_item_price_tool = FunctionTool(func=get_item_price)
check_availability_tool = FunctionTool(func=check_availability)
search_by_ingredient_tool = FunctionTool(func=search_by_ingredient)
get_full_menu_tool = FunctionTool(func=get_full_menu)

# Update ALL_TOOLS
ALL_TOOLS = [
    get_menu_item_tool,
    search_menu_by_category_tool,
    search_by_dietary_restriction_tool,
    get_item_price_tool,
    check_availability_tool,
    search_by_ingredient_tool,
    get_full_menu_tool,
] 