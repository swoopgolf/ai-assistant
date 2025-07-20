#!/usr/bin/env python3
"""
Agent Template - A2A Server Implementation
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
    logger.info("🤖 Starting Agent Template A2A Server")
    logger.info("🔧 This is a template - customize for your specific use case")

    # Create executor
    executor = AgentExecutor()

    # Create standardized agent server
    server = create_agent_server(
        executor=executor,
        agent_name="agent_template",
        title="Agent Template",
        port=10100,  # Use a different port for templates
        agent_description="A template agent for creating new specialized agents.",
        version="template_v1.0",
        custom_health_data={
            "agent_type": "template",
            "supported_operations": [
                "example_tool", "data_processing"
            ]
        }
    )

    # Run the server
    server.run()

if __name__ == "__main__":
    main() 