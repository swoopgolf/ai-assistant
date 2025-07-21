"""Tool definitions for the order-history-qa-agent."""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from google.adk.tools import FunctionTool
from common_utils.database import get_database_manager, DateTimeEncoder

db_manager = get_database_manager()

def get_sales_summary(start_date: Optional[str] = None, end_date: Optional[str] = None, location_id: Optional[int] = None) -> Dict[str, Any]:
    """
    Get sales summary for a given time period and location.
    
    Args:
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        location_id: Optional location filter
        
    Returns:
        Dict with total_sales, order_count, average_order_value
    """
    query = """
        SELECT 
            COUNT(id) as order_count,
            SUM(total) as total_sales,
            AVG(total) as average_order_value
        FROM orders
        WHERE created_at BETWEEN %(start)s AND %(end)s
    """
    params = {
        'start': start_date or (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d'),
        'end': end_date or datetime.now().strftime('%Y-%m-%d')
    }
    if location_id:
        query += " AND location_id = %(location_id)s"
        params['location_id'] = location_id
    
    results = db_manager.execute_query(query, params)
    return json.loads(json.dumps(results[0] if results else {}, cls=DateTimeEncoder))

def get_top_selling_items(start_date: Optional[str] = None, end_date: Optional[str] = None, limit: int = 10) -> List[Dict[str, Any]]:
    """
    Get top selling menu items by quantity.
    
    Args:
        start_date: Start date
        end_date: End date
        limit: Number of items to return
        
    Returns:
        List of dicts with item_name, total_quantity, total_revenue
    """
    query = """
        SELECT 
            i.name as item_name,
            SUM(oi.quantity) as total_quantity,
            SUM(oi.quantity * i.price) as total_revenue
        FROM order_items oi
        JOIN items i ON oi.item_id = i.id
        JOIN orders o ON oi.order_id = o.id
        WHERE o.created_at BETWEEN %(start)s AND %(end)s
        GROUP BY i.id, i.name
        ORDER BY total_quantity DESC
        LIMIT %(limit)s
    """
    params = {
        'start': start_date or (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'),
        'end': end_date or datetime.now().strftime('%Y-%m-%d'),
        'limit': limit
    }
    return db_manager.execute_query(query, params)

def analyze_order_patterns(start_date: Optional[str] = None, end_date: Optional[str] = None) -> Dict[str, Any]:
    """
    Analyze order patterns including peak hours and days.
    
    Args:
        start_date: Start date
        end_date: End date
        
    Returns:
        Dict with peak_hour, peak_day, orders_per_day avg
    """
    query = """
        SELECT 
            EXTRACT(HOUR FROM created_at) as hour,
            EXTRACT(DOW FROM created_at) as day_of_week,
            COUNT(id) as order_count
        FROM orders
        WHERE created_at BETWEEN %(start)s AND %(end)s
        GROUP BY hour, day_of_week
    """
    params = {
        'start': start_date or (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'),
        'end': end_date or datetime.now().strftime('%Y-%m-%d')
    }
    results = db_manager.execute_query(query, params)
    # Simple analysis - find max
    if results:
        peak = max(results, key=lambda x: x['order_count'])
        return {
            'peak_hour': peak['hour'],
            'peak_day': peak['day_of_week'],
            'average_orders_per_day': sum(r['order_count'] for r in results) / len(set(r['day_of_week'] for r in results))
        }
    return {}

# Add similar implementations for other tools...

def get_revenue_metrics(start_date: Optional[str] = None, end_date: Optional[str] = None) -> Dict[str, Any]:
    """
    Get key revenue metrics.
    """
    query = """
        SELECT 
            SUM(total) as total_revenue,
            SUM(tip) as total_tips,
            SUM(tax) as total_tax,
            AVG(total) as avg_order_value
        FROM orders
        WHERE created_at BETWEEN %(start)s AND %(end)s
    """
    params = {
        'start': start_date or (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'),
        'end': end_date or datetime.now().strftime('%Y-%m-%d')
    }
    results = db_manager.execute_query(query, params)
    return results[0] if results else {}

def analyze_customer_behavior(start_date: Optional[str] = None, end_date: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Analyze customer behavior.
    """
    query = """
        SELECT 
            u.id as customer_id,
            u.first_name || ' ' || u.last_name as name,
            COUNT(o.id) as order_count,
            SUM(o.total) as total_spent,
            AVG(o.total) as avg_spend
        FROM users u
        JOIN orders o ON u.id = o.customer_id
        WHERE o.created_at BETWEEN %(start)s AND %(end)s
        GROUP BY u.id
        ORDER BY total_spent DESC
        LIMIT 50
    """
    params = {
        'start': start_date or (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'),
        'end': end_date or datetime.now().strftime('%Y-%m-%d')
    }
    return db_manager.execute_query(query, params)

def get_item_performance(item_id: int, start_date: Optional[str] = None, end_date: Optional[str] = None) -> Dict[str, Any]:
    """
    Get performance metrics for a specific menu item.
    """
    query = """
        SELECT 
            i.name,
            SUM(oi.quantity) as total_sold,
            SUM(oi.quantity * i.price) as total_revenue,
            COUNT(DISTINCT o.id) as unique_orders
        FROM items i
        JOIN order_items oi ON i.id = oi.item_id
        JOIN orders o ON oi.order_id = o.id
        WHERE i.id = %(item_id)s
        AND o.created_at BETWEEN %(start)s AND %(end)s
        GROUP BY i.id
    """
    params = {
        'item_id': item_id,
        'start': start_date or (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'),
        'end': end_date or datetime.now().strftime('%Y-%m-%d')
    }
    results = db_manager.execute_query(query, params)
    return results[0] if results else {}

def execute_custom_query(sql_query: str) -> List[Dict[str, Any]]:
    """
    Execute a custom analytical SQL query. Only SELECT queries allowed.
    """
    if not sql_query.strip().upper().startswith('SELECT'):
        raise ValueError("Only SELECT queries are allowed")
    return db_manager.execute_query(sql_query)

# Create FunctionTool instances
get_sales_summary_tool = FunctionTool(func=get_sales_summary)
get_top_selling_items_tool = FunctionTool(func=get_top_selling_items)
analyze_order_patterns_tool = FunctionTool(func=analyze_order_patterns)
get_revenue_metrics_tool = FunctionTool(func=get_revenue_metrics)
analyze_customer_behavior_tool = FunctionTool(func=analyze_customer_behavior)
get_item_performance_tool = FunctionTool(func=get_item_performance)
execute_custom_query_tool = FunctionTool(func=execute_custom_query)

# List of all available tools for dynamic discovery
ALL_TOOLS = [
    get_sales_summary_tool,
    get_top_selling_items_tool,
    analyze_order_patterns_tool,
    get_revenue_metrics_tool,
    analyze_customer_behavior_tool,
    get_item_performance_tool,
    execute_custom_query_tool,
] 