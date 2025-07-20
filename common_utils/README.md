# Common Utils

Common utilities package for the multi-agent framework. Provides shared utilities for agent communication, configuration, security, and management.

## Features

- **Agent Server**: Base classes for creating agent servers with A2A communication
- **Agent Discovery**: Service discovery and registration for agents
- **Agent Configuration**: Standardized configuration management
- **Security**: Authentication, authorization, and security utilities
- **MCP Tool Server**: Model Context Protocol server for external tool integration
- **Observability**: Monitoring, logging, and tracing utilities
- **Session Management**: State and context management for multi-turn conversations
- **Circuit Breaker**: Resilience patterns for fault tolerance
- **Port Management**: Utilities for port allocation and conflict detection

## Installation

```bash
# From the project root
pip install -e ./common_utils
```

## Usage

### Creating an Agent Server

```python
from common_utils import create_agent_server

# Create agent server with standardized configuration
server = create_agent_server(
    executor=my_executor,
    agent_name="my_agent",
    title="My Custom Agent",
    port=10101,
    agent_description="Description of my agent"
)

# Run the server
server.run()
```

### Agent Discovery

```python
from common_utils.agent_discovery import get_agent_registry

# Get agent registry
registry = get_agent_registry()

# Register an agent
await registry.register_agent("my_agent", "localhost", 10101)

# Discover agents
agents = await registry.get_available_agents()
```

### MCP Tool Server

```python
from common_utils.mcp_server.tool_server import McpToolServer, BaseTool

class MyTool(BaseTool):
    def execute(self, params):
        return {"result": "processed"}

# Create and run MCP server
server = McpToolServer()
server.register_tool("my_tool", MyTool())
await server.start()
```

## Core Components

- **base_agent_server.py**: Base agent server implementation
- **agent_config.py**: Configuration management utilities
- **agent_discovery.py**: Service discovery mechanisms
- **security.py**: Security and authentication features
- **mcp_server/**: Model Context Protocol server implementation
- **observability.py**: Monitoring and tracing utilities
- **session_manager.py**: Session and state management
- **enhanced_logging.py**: Advanced logging capabilities 