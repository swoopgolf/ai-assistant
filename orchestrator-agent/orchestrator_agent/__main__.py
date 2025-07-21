#!/usr/bin/env python3
"""
Orchestrator Agent - A2A Server Implementation
"""

import logging
import sys
from pathlib import Path

# Add the parent directory to sys.path to make common_utils accessible
parent_dir = Path(__file__).parent.parent.parent
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))

from common_utils.base_agent_server import create_agent_server
from .agent_executor import OrchestratorAgentExecutor

logger = logging.getLogger(__name__)

def main():
    """Main entry point for the orchestrator agent."""
    logging.basicConfig(level=logging.INFO)
    logger.info("🎯 Starting Orchestrator Agent A2A Server")

    # Create executor
    executor = OrchestratorAgentExecutor()

    # Create standardized agent server
    server = create_agent_server(
        executor=executor,
        agent_name="orchestrator",
        title="Orchestrator Agent",
        port=10200,
        agent_description="Central coordinator for the multi-agent framework. Dispatches tasks to specialized agents.",
        version="2.0.0",
        custom_health_data={
            "role": "coordinator",
            "supported_tasks": ["delegate_task"]
        }
    )

    # Run the server
    server.run()

if __name__ == "__main__":
    main() 