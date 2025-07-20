# Scripts Directory

This directory contains utility scripts for the Multi-Agent Framework.

## 🤖 Agent Creation Tools

### Quick Start

The easiest way to create a new agent:

**Linux/macOS:**
```bash
./scripts/create_agent.sh
```

**Windows:**
```cmd
scripts\create_agent.bat
```

This will launch an interactive wizard that guides you through the agent creation process.

### create_new_agent.py

A comprehensive Python script that automates the creation of new agents from the `agent_template`. This script handles all the necessary file modifications, renaming, and configuration updates.

#### Features

- ✅ **Interactive Wizard**: Guides you through agent configuration step-by-step
- ✅ **Configuration File Support**: Use JSON config files for automated agent creation
- ✅ **Validation**: Validates agent names, ports, and configuration
- ✅ **Conflict Detection**: Prevents creating agents with duplicate names or ports
- ✅ **Complete Automation**: Updates all template files, system configuration, and documentation
- ✅ **Cross-Platform**: Works on Windows, macOS, and Linux

#### Usage Options

##### 1. Interactive Mode (Recommended for beginners)

```bash
python scripts/create_new_agent.py
```

This will prompt you for:
- Agent name (e.g., `my-custom-agent`)
- Description
- Port number (1024-65535)
- Author information
- Agent capabilities

##### 2. Configuration File Mode (Recommended for automation)

```bash
python scripts/create_new_agent.py --config scripts/example_agent_config.json
```

Create your own config file based on `example_agent_config.json`:

```json
{
  "agent_name": "my-data-agent",
  "description": "Specialized agent for data processing",
  "port": 10300,
  "author_name": "Your Name",
  "author_email": "your.email@company.com",
  "capabilities": [
    "process_data",
    "analyze_results",
    "generate_reports"
  ]
}
```

#### What the Script Does

1. **📁 Copies Template**: Creates a new directory from `agent_template`
2. **📦 Renames Package**: Renames internal `agent_template` package to your agent name
3. **📝 Updates Files**: Modifies all template files with your configuration:
   - `pyproject.toml` - Project configuration and dependencies
   - `__main__.py` - Entry point with your agent's details
   - `agent_executor.py` - Core logic with customized class and method names
   - `prompt.py` - Agent-specific prompts and instructions
   - `tools.py` - Tool definitions with your naming conventions
   - `README.md` - Complete documentation for your agent
4. **⚙️ Updates System Config**: Adds your agent to `config/system_config.yaml`
5. **🎯 Provides Next Steps**: Clear instructions for customization and testing

#### Validation Rules

- **Agent Name**: Must start with lowercase letter, contain only lowercase letters, numbers, hyphens, and underscores
- **Port**: Must be between 1024-65535 and not already in use
- **Required Fields**: All configuration fields must be provided

#### Example Output

```
🤖 Agent Creation Wizard
==================================================

Enter agent name (e.g., 'my-custom-agent'): file-processor-agent
Enter agent description: Processes and analyzes various file formats
Enter port number (1024-65535): 10250
Enter author name: John Smith
Enter author email: john.smith@company.com

Enter agent capabilities (comma-separated, e.g., 'data_processing,file_handling'):
Capabilities (leave empty for defaults): file_upload,format_conversion,content_analysis

🚀 Creating new agent: file-processor-agent
📁 Copying template to /path/to/ai-assistant/file-processor-agent
📦 Renaming package from 'agent_template' to 'file_processor_agent'
📝 Updated /path/to/ai-assistant/file-processor-agent/pyproject.toml
📝 Updated /path/to/ai-assistant/file-processor-agent/file_processor_agent/__main__.py
📝 Updated /path/to/ai-assistant/file-processor-agent/file_processor_agent/agent_executor.py
📝 Updated /path/to/ai-assistant/file-processor-agent/file_processor_agent/prompt.py
📝 Updated /path/to/ai-assistant/file-processor-agent/file_processor_agent/tools.py
📝 Updated /path/to/ai-assistant/file-processor-agent/README.md
⚙️  Updating system configuration
📝 Updated /path/to/ai-assistant/config/system_config.yaml
✅ Agent 'file-processor-agent' created successfully!

🎉 Agent created successfully!

📋 Next steps:
1. Navigate to your agent directory:
   cd file-processor-agent

2. Customize your agent implementation:
   - Edit file_processor_agent/agent_executor.py for your core logic
   - Edit file_processor_agent/tools.py to define your tools
   - Edit file_processor_agent/prompt.py for your agent prompts

3. Test your agent:
   python -m file_processor_agent

4. Verify it's running:
   curl http://localhost:10250/health

5. The agent is automatically registered with the orchestrator!
   Check config/system_config.yaml to see your agent configuration.
```

### Helper Scripts

#### create_agent.sh (Linux/macOS)

Bash wrapper script that provides a convenient way to run the agent creator with environment validation.

#### create_agent.bat (Windows)

Windows batch file wrapper with the same functionality as the bash script.

#### example_agent_config.json

Example configuration file showing all available options. Copy and modify this file to create agents programmatically.

## 🧪 Testing Tools

### integration_test_framework.py

Framework for running integration tests across the multi-agent system.

### start_test_environment.py

Sets up a complete test environment with all agents running for integration testing.

## 🚀 Deployment Scripts

### deploy.sh

Handles deployment of the multi-agent framework to various environments.

## Best Practices

### Agent Naming

- Use lowercase letters, numbers, hyphens, and underscores only
- Be descriptive: `data-processor-agent` not `agent1`
- Use hyphens for multi-word names: `file-upload-agent`

### Port Selection

- Use ports in ranges:
  - 10000-10099: Core framework agents
  - 10100-10199: Template and utility agents  
  - 10200-10299: Data processing agents
  - 10300-10399: File handling agents
  - 10400-10499: Communication agents
  - 10500+: Custom domain-specific agents

### Configuration Management

- Keep a central record of all created agents and their ports
- Use descriptive names for capabilities that clearly indicate functionality
- Document any external dependencies your agent requires

## Troubleshooting

### Common Issues

1. **Port Already in Use**
   - The script checks for port conflicts automatically
   - Choose a different port if one is already assigned

2. **Permission Denied**
   - Make sure you have write permissions in the project directory
   - On Unix systems, ensure scripts are executable: `chmod +x scripts/create_agent.sh`

3. **Template Not Found**
   - Ensure you're running the script from the project root directory
   - Verify that `agent_template/` directory exists

4. **Python Not Found**
   - Install Python 3.9 or later
   - Ensure Python is in your system PATH

### Getting Help

- Check the main project documentation in `docs/`
- Review existing agents like `orchestrator-agent` for examples
- Examine the `agent_template` structure for reference 