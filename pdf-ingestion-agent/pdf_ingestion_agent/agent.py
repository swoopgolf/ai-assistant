"""
Agent Template
This module defines the top-level agent components for a generic agent.
The agent's business logic is implemented in the `AgentExecutor`.
"""

import logging

logger = logging.getLogger(__name__)

# The logic that was previously in this file has been moved to
# `agent_executor.py` to better align with the a2a-sdk structure.

# The `__main__.py` script now directly uses the `AgentExecutor`
# to create the A2A server and its skills. This file is kept for
# package structure but is no longer the primary implementation file.

logger.info("Agent Template package loaded. See agent_executor.py for implementation.")