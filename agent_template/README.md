# Agent Template

This directory contains a template for creating new agents in the multi-agent framework.

## Usage

1. Copy this entire `agent_template` directory to create a new agent
2. Rename the directory to match your agent's purpose (e.g., `my-custom-agent`)
3. Update the following files:
   - `pyproject.toml`: Change name, description, dependencies
   - `agent_template/`: Rename this directory to match your agent
   - `__main__.py`: Update agent name, port, and description
   - `agent_executor.py`: Implement your specific agent logic
   - `tools.py`: Define your agent's tools and capabilities
   - `prompt.py`: Customize the agent prompt

## Key Files

- `agent_executor.py`: Main agent logic and skills
- `tools.py`: Tool definitions using Google ADK
- `prompt.py`: Agent prompt and instructions
- `__main__.py`: Entry point and server configuration

Refer to `docs/adding_agents.md` for detailed instructions. 