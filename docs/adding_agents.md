# Adding New Agents to the Multi-Agent Framework

This guide provides step-by-step instructions for creating new agents using the provided agent template.

## 📋 **Prerequisites**

- Understanding of the A2A (Agent-to-Agent) protocol for inter-agent communication
- Python 3.9+ development environment
- Basic knowledge of FastAPI and asyncio
- Familiarity with the Google ADK tool framework

## 🏗️ **Agent Architecture Overview**

Each agent in the system follows this standard structure:

```
my-custom-agent/
├── pyproject.toml              # Dependencies and build configuration
├── README.md                   # Agent-specific documentation
├── my_agent/                   # Main agent package (renamed from template)
│   ├── __init__.py            # Package initialization
│   ├── __main__.py            # A2A server entry point
│   ├── agent.py               # Agent initialization (minimal)
│   ├── agent_executor.py      # Core agent logic and skills
│   ├── tools.py               # Tool definitions using Google ADK
│   └── prompt.py              # Agent prompts and descriptions
└── tests/                     # Unit tests (optional)
    └── test_tools.py
```

## 🚀 **Step-by-Step Agent Creation**

### **Step 1: Copy the Agent Template**

```bash
# From the project root
cp -r agent_template my-custom-agent
cd my-custom-agent
```

### **Step 2: Rename the Agent Package**

```bash
# Rename the internal package directory
mv agent_template my_agent
```

### **Step 3: Update pyproject.toml**

Edit `pyproject.toml` to reflect your agent:

```toml
[tool.poetry]
name = "my-custom-agent"
version = "0.1.0"
description = "Description of what your agent does."
packages = [{include = "my_agent"}]

# Update the start script
[project.scripts]
start = "my_agent.__main__:main"

# Add any specific dependencies your agent needs
[project]
dependencies = [
    "a2a-sdk>=0.2.12",
    "fastapi>=0.115.0",
    # Add your specific dependencies here
    # "pandas>=2.0.0",
    # "requests>=2.31.0",
]
```

### **Step 4: Update Agent Configuration**

Edit `my_agent/__main__.py` to configure your agent:

```python
def main():
    """Main entry point for your custom agent."""
    logging.basicConfig(level=logging.INFO)
    logger.info("🤖 Starting My Custom Agent A2A Server")

    # Create executor
    executor = AgentExecutor()

    # Create standardized agent server
    server = create_agent_server(
        executor=executor,
        agent_name="my_custom_agent",        # Update this
        title="My Custom Agent",             # Update this
        port=10101,                          # Choose a unique port
        agent_description="Describe what your agent does.", # Update this
        version="v1.0",
        custom_health_data={
            "agent_type": "custom",
            "supported_operations": [
                "your_skill_1", "your_skill_2"  # List your skills
            ]
        }
    )

    server.run()
```

### **Step 5: Implement Your Agent Logic**

Edit `my_agent/agent_executor.py` to implement your specific functionality:

```python
class AgentExecutor:
    """
    Your Custom Agent Executor
    """
    
    def __init__(self):
        self.data_manager = get_data_handle_manager()
        logger.info("My Custom Agent initialized")

    async def your_custom_skill(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Implement your agent's main functionality here.
        
        Args:
            input_data: Input parameters for your agent
            
        Returns:
            Dict containing the results
        """
        try:
            # Your custom logic here
            result = self.process_data(input_data)
            
            return {
                "status": "success",
                "result": result
            }
            
        except Exception as e:
            logger.error(f"Error in custom skill: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    def process_data(self, data):
        """Your custom processing logic."""
        # Implement your specific functionality
        return {"processed": True, "data": data}
```

### **Step 6: Define Your Tools**

Edit `my_agent/tools.py` to define the tools your agent exposes:

```python
from google.adk.tools import FunctionTool

def my_tool_function(param1: str, param2: int = 10) -> dict:
    """
    A custom tool that performs specific operations.
    
    Args:
        param1: Description of parameter 1
        param2: Description of parameter 2
        
    Returns:
        dict: Result of the operation
    """
    # Your tool implementation
    return {
        "result": f"Processed {param1} with value {param2}",
        "success": True
    }

# Create ADK FunctionTool instances
my_custom_tool = FunctionTool(func=my_tool_function)

# List of all available tools
ALL_TOOLS = [
    my_custom_tool,
]
```

### **Step 7: Customize the Agent Prompt**

Edit `my_agent/prompt.py`:

```python
"""Prompts for your custom agent."""

AGENT_PROMPT = """
You are a specialized agent that performs [specific functionality].

Your available tools include:
- my_tool_function: Description of what this tool does

When processing requests:
1. Analyze the input requirements
2. Use appropriate tools to process the data
3. Return clear, structured results

Always validate inputs and handle errors gracefully.
"""
```

### **Step 8: Update System Configuration**

Add your agent to `config/system_config.yaml`:

```yaml
agents:
  my_custom_agent:
    host: "localhost"
    port: 10101
    description: "Description of your agent"
    capabilities:
      - "your_custom_skill"
```

### **Step 9: Test Your Agent**

1. **Start your agent:**
   ```bash
   cd my-custom-agent
   python -m my_agent
   ```

2. **Verify it's running:**
   ```bash
   curl http://localhost:10101/health
   ```

3. **Test via the Orchestrator:**
   The Orchestrator can now discover and use your agent's capabilities.

## 🔧 **Advanced Customization**

### Adding External Dependencies

If your agent needs external services, add them to your `pyproject.toml`:

```toml
dependencies = [
    "requests>=2.31.0",
    "pandas>=2.0.0",
    "numpy>=1.24.0",
]
```

### Adding MCP Server Support

If your agent needs to expose tools via MCP, refer to the existing `common_utils/mcp_server/tool_server.py` for examples.

### Custom Health Checks

Override the health check in your agent executor:

```python
async def health_check(self) -> Dict[str, Any]:
    """Custom health check for your agent."""
    return {
        "status": "healthy",
        "custom_metrics": {
            "items_processed": self.items_processed,
            "last_update": self.last_update.isoformat()
        }
    }
```

## 🚨 **Common Issues**

1. **Port Conflicts:** Ensure each agent uses a unique port
2. **Import Errors:** Check that your package name matches directory structure
3. **Tool Registration:** Verify tools are properly listed in `ALL_TOOLS`
4. **Configuration:** Ensure system_config.yaml is updated

## 📚 **Next Steps**

1. Update the Orchestrator's prompt to be aware of your new agent
2. Add integration tests in the `tests/` directory
3. Document your agent's capabilities for other developers
4. Consider adding monitoring and logging specific to your agent's domain

For more details on the framework architecture, see `docs/ARCHITECTURE.md`. 