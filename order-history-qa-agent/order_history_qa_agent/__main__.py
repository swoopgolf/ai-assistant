#!/usr/bin/env python3
"""
Order History Qa Agent - A2A Server Implementation
"""

import logging
import sys
from pathlib import Path

# Add the parent directory to sys.path to make common_utils accessible
parent_dir = Path(__file__).parent.parent.parent
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))

from common_utils import create_agent_server
from .agent_executor import AgentExecutor

logger = logging.getLogger(__name__)

def main():
    """Main entry point for the agent template."""
    logging.basicConfig(level=logging.INFO)
    logger.info("🤖 Starting Order History Qa Agent A2A Server")
    logger.info("🔧 Specialized agent: Specialized agent for answering questions about order history, sales analytics, and business intelligence queries using natural language to SQL conversion")

    # Create executor
    executor = AgentExecutor()

    # Create standardized agent server
    server = create_agent_server(
        executor=executor,
        agent_name="order_history_qa_agent",
        title="Order History Qa Agent",
        port=10210,  # Use a different port for templates
        agent_description="Specialized agent for answering questions about order history, sales analytics, and business intelligence queries using natural language to SQL conversion",
        version="v1.0",
        custom_health_data={
            "agent_type": "specialized",
            "supported_operations": [
                ["sales_analytics", "order_history_queries", "natural_language_to_sql", "business_intelligence", "revenue_reporting", "customer_analytics", "trend_analysis", "performance_metrics"]
            ]
        }
    )

    # Run the server
    server.run()

if __name__ == "__main__":
    main() 