#!/usr/bin/env python3
"""
Menu Qa Agent - A2A Server Implementation
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
    logger.info("🤖 Starting Menu Qa Agent A2A Server")
    logger.info("🔧 Specialized agent: Specialized agent for answering questions about current menu items, availability, pricing, ingredients, and dietary restrictions")

    # Create executor
    executor = AgentExecutor()

    # Create standardized agent server
    server = create_agent_server(
        executor=executor,
        agent_name="menu_qa_agent",
        title="Menu Qa Agent",
        port=10220,  # Use a different port for templates
        agent_description="Specialized agent for answering questions about current menu items, availability, pricing, ingredients, and dietary restrictions",
        version="v1.0",
        custom_health_data={
            "agent_type": "specialized",
            "supported_operations": [
                ["menu_queries", "item_lookup", "price_inquiry", "availability_check", "dietary_information", "ingredient_search", "category_browsing", "menu_navigation"]
            ]
        }
    )

    # Run the server
    server.run()

if __name__ == "__main__":
    main() 