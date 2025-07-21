#!/usr/bin/env python3
"""
Classification Agent - A2A Server Implementation
"""

import logging
import sys
from pathlib import Path

# Add the parent directory to sys.path to make common_utils accessible
parent_dir = Path(__file__).parent.parent.parent
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))

from common_utils.base_agent_server import create_agent_server
from .agent_executor import ClassificationAgentExecutor

logger = logging.getLogger(__name__)

def main():
    """Main entry point for the classification agent."""
    logging.basicConfig(level=logging.INFO)
    logger.info("🔍 Starting Classification Agent A2A Server")

    # Create executor
    executor = ClassificationAgentExecutor()

    # Create standardized agent server
    server = create_agent_server(
        executor=executor,
        agent_name="classification",
        title="Classification Agent",
        port=10300,
        agent_description="AI-powered query classification agent that categorizes user requests and provides routing decisions for the orchestrator.",
        version="1.0.0",
        custom_health_data={
            "role": "classifier",
            "supported_tasks": ["classify_query"],
            "supported_query_types": executor.get_supported_query_types(),
            "agent_mapping": executor.get_agent_mapping()
        }
    )

    # Run the server
    server.run()

if __name__ == "__main__":
    main() 