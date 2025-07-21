#!/usr/bin/env python3
"""
Price Update Agent - A2A Server Implementation
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
    logger.info("🤖 Starting Price Update Agent A2A Server")
    logger.info("🔧 Specialized agent: Specialized agent for executing menu price updates, item modifications, and availability changes through natural language commands with database write operations")

    # Create executor
    executor = AgentExecutor()

    # Create standardized agent server
    server = create_agent_server(
        executor=executor,
        agent_name="price_update_agent",
        title="Price Update Agent",
        port=10410,  # Use a different port for templates
        agent_description="Specialized agent for executing menu price updates, item modifications, and availability changes through natural language commands with database write operations",
        version="v1.0",
        custom_health_data={
            "agent_type": "specialized",
            "supported_operations": [
                ["price_updates", "menu_editing", "item_modifications", "availability_management", "bulk_price_changes", "category_adjustments", "promotional_pricing", "audit_logging", "change_validation"]
            ]
        }
    )

    # Run the server
    server.run()

if __name__ == "__main__":
    main() 