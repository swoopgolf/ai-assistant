#!/usr/bin/env python3
"""
Agent Creation Script

This script automates the creation of new agents from the agent_template.
It handles all necessary file modifications, renaming, and configuration updates.
"""

import os
import sys
import shutil
import yaml
import argparse
import re
from pathlib import Path
from typing import Dict, Any, List
import json

class AgentCreator:
    """Handles the creation of new agents from the template."""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.agent_template_path = project_root / "agent_template"
        self.config_path = project_root / "config" / "system_config.yaml"
        
    def create_agent(self, config: Dict[str, Any]) -> bool:
        """
        Create a new agent based on the provided configuration.
        
        Args:
            config: Dictionary containing agent configuration
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Validate configuration
            self._validate_config(config)
            
            # Check if agent already exists
            agent_path = self.project_root / config['agent_name']
            if agent_path.exists():
                print(f"❌ Agent '{config['agent_name']}' already exists at {agent_path}")
                return False
            
            # Check if port is already in use
            if self._is_port_in_use(config['port']):
                print(f"❌ Port {config['port']} is already in use by another agent")
                return False
            
            print(f"🚀 Creating new agent: {config['agent_name']}")
            
            # Step 1: Copy template directory
            self._copy_template(config['agent_name'])
            
            # Step 2: Rename internal package
            self._rename_internal_package(config['agent_name'])
            
            # Step 3: Update all template files
            self._update_template_files(config)
            
            # Step 4: Update system configuration
            self._update_system_config(config)
            
            print(f"✅ Agent '{config['agent_name']}' created successfully!")
            self._print_next_steps(config)
            
            return True
            
        except Exception as e:
            print(f"❌ Error creating agent: {str(e)}")
            return False
    
    def _validate_config(self, config: Dict[str, Any]) -> None:
        """Validate the agent configuration."""
        required_fields = ['agent_name', 'description', 'port', 'author_name', 'author_email']
        
        for field in required_fields:
            if field not in config or not config[field]:
                raise ValueError(f"Required field '{field}' is missing or empty")
        
        # Validate agent name format
        if not re.match(r'^[a-z][a-z0-9_-]*$', config['agent_name']):
            raise ValueError("Agent name must start with a lowercase letter and contain only lowercase letters, numbers, hyphens, and underscores")
        
        # Validate port range
        if not isinstance(config['port'], int) or config['port'] < 1024 or config['port'] > 65535:
            raise ValueError("Port must be an integer between 1024 and 65535")
    
    def _is_port_in_use(self, port: int) -> bool:
        """Check if the port is already configured for another agent."""
        try:
            with open(self.config_path, 'r') as f:
                system_config = yaml.safe_load(f)
            
            agents = system_config.get('agents', {})
            for agent_name, agent_config in agents.items():
                if agent_config.get('port') == port:
                    return True
            return False
        except:
            return False
    
    def _copy_template(self, agent_name: str) -> None:
        """Copy the agent template to a new directory."""
        target_path = self.project_root / agent_name
        print(f"📁 Copying template to {target_path}")
        shutil.copytree(self.agent_template_path, target_path)
    
    def _rename_internal_package(self, agent_name: str) -> None:
        """Rename the internal agent_template package to the new agent name."""
        agent_path = self.project_root / agent_name
        old_package_path = agent_path / "agent_template"
        new_package_path = agent_path / agent_name.replace('-', '_')
        
        print(f"📦 Renaming package from 'agent_template' to '{agent_name.replace('-', '_')}'")
        shutil.move(str(old_package_path), str(new_package_path))
    
    def _update_template_files(self, config: Dict[str, Any]) -> None:
        """Update all template files with the new configuration."""
        agent_path = self.project_root / config['agent_name']
        package_name = config['agent_name'].replace('-', '_')
        
        # Update pyproject.toml
        self._update_pyproject_toml(agent_path, config, package_name)
        
        # Update __main__.py
        self._update_main_py(agent_path, config, package_name)
        
        # Update agent_executor.py
        self._update_agent_executor(agent_path, config, package_name)
        
        # Update prompt.py
        self._update_prompt_py(agent_path, config, package_name)
        
        # Update tools.py
        self._update_tools_py(agent_path, config, package_name)
        
        # Update README.md
        self._update_readme(agent_path, config)
    
    def _update_pyproject_toml(self, agent_path: Path, config: Dict[str, Any], package_name: str) -> None:
        """Update the pyproject.toml file."""
        pyproject_path = agent_path / "pyproject.toml"
        
        with open(pyproject_path, 'r') as f:
            content = f.read()
        
        # Replace template values
        replacements = {
            'agent-template': config['agent_name'],
            'agent_template': package_name,
            'A template for creating new agents in the multi-agent framework.': config['description'],
            'Your Name <you@example.com>': f"{config['author_name']} <{config['author_email']}>",
        }
        
        for old, new in replacements.items():
            content = content.replace(old, new)
        
        with open(pyproject_path, 'w') as f:
            f.write(content)
        
        print(f"📝 Updated {pyproject_path}")
    
    def _update_main_py(self, agent_path: Path, config: Dict[str, Any], package_name: str) -> None:
        """Update the __main__.py file."""
        main_py_path = agent_path / package_name / "__main__.py"
        
        with open(main_py_path, 'r') as f:
            content = f.read()
        
        # Create title from agent name
        title = ' '.join(word.capitalize() for word in config['agent_name'].replace('-', ' ').replace('_', ' ').split())
        
        replacements = {
            'Agent Template - A2A Server Implementation': f'{title} - A2A Server Implementation',
            'agent_template': package_name,
            'Starting Agent Template A2A Server': f'Starting {title} A2A Server',
            'This is a template - customize for your specific use case': f'Specialized agent: {config["description"]}',
            '"agent_template"': f'"{package_name}"',
            '"Agent Template"': f'"{title}"',
            '10100': str(config['port']),
            'A template agent for creating new specialized agents.': config['description'],
            'template_v1.0': 'v1.0',
            '"template"': '"specialized"',
            '"example_tool", "data_processing"': json.dumps(config.get('capabilities', ['process_task', 'get_capabilities'])),
        }
        
        for old, new in replacements.items():
            content = content.replace(old, new)
        
        with open(main_py_path, 'w') as f:
            f.write(content)
        
        print(f"📝 Updated {main_py_path}")
    
    def _update_agent_executor(self, agent_path: Path, config: Dict[str, Any], package_name: str) -> None:
        """Update the agent_executor.py file."""
        executor_path = agent_path / package_name / "agent_executor.py"
        
        with open(executor_path, 'r') as f:
            content = f.read()
        
        # Create class name from agent name
        class_name = ''.join(word.capitalize() for word in config['agent_name'].replace('-', '_').split('_')) + 'Executor'
        
        replacements = {
            'Agent Template Executor': f'{config["agent_name"].replace("-", " ").title()} Executor',
            'This module provides a simple template for creating agent executors.': f'Executor for the {config["agent_name"]} agent.',
            'Template Agent Executor that provides basic agent functionality.': f'{config["agent_name"].replace("-", " ").title()} agent executor with specialized functionality.',
            'Customize this class for your specific agent requirements.': config['description'],
            'Agent Template initialized': f'{config["agent_name"].replace("-", " ").title()} initialized',
            'A basic skill that processes tasks. Customize this method for your specific use case.': f'Main processing skill for {config["agent_name"]}.',
            'Task processed successfully by agent template': f'Task processed successfully by {config["agent_name"]}',
            '"template"': '"specialized"',
            'A template agent that can be customized for specific use cases': config['description'],
        }
        
        for old, new in replacements.items():
            content = content.replace(old, new)
        
        with open(executor_path, 'w') as f:
            f.write(content)
        
        print(f"📝 Updated {executor_path}")
    
    def _update_prompt_py(self, agent_path: Path, config: Dict[str, Any], package_name: str) -> None:
        """Update the prompt.py file."""
        prompt_path = agent_path / package_name / "prompt.py"
        
        with open(prompt_path, 'r') as f:
            content = f.read()
        
        # Create a more specific prompt based on the agent description
        custom_prompt = f'''"""Prompts for the {config['agent_name']} agent."""

AGENT_PROMPT = """
You are a specialized {config['agent_name'].replace('-', ' ')} agent. {config['description']}

Your available tools and capabilities include:
{chr(10).join(f"- {cap}: Handles {cap.replace('_', ' ')} operations" for cap in config.get('capabilities', ['process_task', 'get_capabilities']))}

When processing requests:
1. Analyze the input requirements carefully
2. Use appropriate tools to process the data
3. Return clear, structured results
4. Handle errors gracefully and provide meaningful feedback

Always validate inputs and follow best practices for reliable operation.
"""'''
        
        with open(prompt_path, 'w') as f:
            f.write(custom_prompt)
        
        print(f"📝 Updated {prompt_path}")
    
    def _update_tools_py(self, agent_path: Path, config: Dict[str, Any], package_name: str) -> None:
        """Update the tools.py file."""
        tools_path = agent_path / package_name / "tools.py"
        
        with open(tools_path, 'r') as f:
            content = f.read()
        
        replacements = {
            'agent template': config['agent_name'],
            'example_tool': f"{package_name}_main_tool",
            'another_example_tool': f"{package_name}_data_tool",
            'example_function_tool': f"{package_name}_main_function_tool",
            'data_processing_tool': f"{package_name}_data_function_tool",
        }
        
        for old, new in replacements.items():
            content = content.replace(old, new)
        
        with open(tools_path, 'w') as f:
            f.write(content)
        
        print(f"📝 Updated {tools_path}")
    
    def _update_readme(self, agent_path: Path, config: Dict[str, Any]) -> None:
        """Update the README.md file."""
        readme_path = agent_path / "README.md"
        
        title = config['agent_name'].replace('-', ' ').title()
        
        readme_content = f"""# {title}

{config['description']}

## Overview

This agent is part of the multi-agent framework and provides specialized functionality for {config['description'].lower()}.

## Features

{chr(10).join(f"- {cap.replace('_', ' ').title()}" for cap in config.get('capabilities', ['Task Processing', 'Capability Reporting']))}

## Configuration

- **Port**: {config['port']}
- **Agent Name**: {config['agent_name']}
- **Version**: 1.0.0

## Usage

To start this agent:

```bash
cd {config['agent_name']}
python -m {config['agent_name'].replace('-', '_')}
```

## Health Check

```bash
curl http://localhost:{config['port']}/health
```

## Integration

This agent is automatically registered with the orchestrator and can be accessed through the A2A communication protocol.

## Development

- **Author**: {config['author_name']} <{config['author_email']}>
- **Created**: {self._get_current_date()}
- **Framework Version**: 2.0.0

## License

Apache License 2.0
"""
        
        with open(readme_path, 'w') as f:
            f.write(readme_content)
        
        print(f"📝 Updated {readme_path}")
    
    def _update_system_config(self, config: Dict[str, Any]) -> None:
        """Update the system configuration to include the new agent."""
        print(f"⚙️  Updating system configuration")
        
        with open(self.config_path, 'r') as f:
            system_config = yaml.safe_load(f)
        
        # Add new agent configuration
        package_name = config['agent_name'].replace('-', '_')
        agent_config = {
            'name': config['agent_name'].replace('-', ' ').title(),
            'host': 'localhost',
            'port': config['port'],
            'module_path': package_name,
            'description': config['description'],
            'features': {cap: True for cap in config.get('capabilities', ['basic_processing'])},
            'timeouts': {
                'startup': 30,
                'health_check': 10,
                'task_execution': 120
            },
            'resources': {
                'max_memory_mb': 512,
                'max_cpu_percent': 50
            }
        }
        
        if 'agents' not in system_config:
            system_config['agents'] = {}
        
        system_config['agents'][package_name] = agent_config
        
        with open(self.config_path, 'w') as f:
            yaml.dump(system_config, f, default_flow_style=False, indent=2)
        
        print(f"📝 Updated {self.config_path}")
    
    def _get_current_date(self) -> str:
        """Get current date in YYYY-MM-DD format."""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d")
    
    def _print_next_steps(self, config: Dict[str, Any]) -> None:
        """Print next steps for the user."""
        package_name = config['agent_name'].replace('-', '_')
        
        print("\n🎉 Agent created successfully!")
        print("\n📋 Next steps:")
        print(f"1. Navigate to your agent directory:")
        print(f"   cd {config['agent_name']}")
        print("\n2. Customize your agent implementation:")
        print(f"   - Edit {package_name}/agent_executor.py for your core logic")
        print(f"   - Edit {package_name}/tools.py to define your tools")
        print(f"   - Edit {package_name}/prompt.py for your agent prompts")
        print("\n3. Test your agent:")
        print(f"   python -m {package_name}")
        print("\n4. Verify it's running:")
        print(f"   curl http://localhost:{config['port']}/health")
        print("\n5. The agent is automatically registered with the orchestrator!")
        print(f"   Check config/system_config.yaml to see your agent configuration.")


def get_user_input() -> Dict[str, Any]:
    """Get user input for agent configuration."""
    print("🤖 Agent Creation Wizard")
    print("=" * 50)
    
    config = {}
    
    # Agent name
    while True:
        agent_name = input("\nEnter agent name (e.g., 'my-custom-agent'): ").strip()
        if re.match(r'^[a-z][a-z0-9_-]*$', agent_name):
            config['agent_name'] = agent_name
            break
        print("❌ Agent name must start with lowercase letter and contain only lowercase letters, numbers, hyphens, and underscores")
    
    # Description
    config['description'] = input("Enter agent description: ").strip()
    if not config['description']:
        config['description'] = f"Specialized agent for {agent_name} operations"
    
    # Port
    while True:
        try:
            port = int(input("Enter port number (1024-65535): ").strip())
            if 1024 <= port <= 65535:
                config['port'] = port
                break
            print("❌ Port must be between 1024 and 65535")
        except ValueError:
            print("❌ Please enter a valid number")
    
    # Author information
    config['author_name'] = input("Enter author name: ").strip()
    if not config['author_name']:
        config['author_name'] = "Developer"
    
    config['author_email'] = input("Enter author email: ").strip()
    if not config['author_email']:
        config['author_email'] = "developer@example.com"
    
    # Capabilities
    print("\nEnter agent capabilities (comma-separated, e.g., 'data_processing,file_handling'):")
    capabilities_input = input("Capabilities (leave empty for defaults): ").strip()
    if capabilities_input:
        config['capabilities'] = [cap.strip() for cap in capabilities_input.split(',')]
    else:
        config['capabilities'] = ['process_task', 'get_capabilities']
    
    return config


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Create a new agent from template')
    parser.add_argument('--config', type=str, help='JSON file with agent configuration')
    parser.add_argument('--interactive', action='store_true', default=True, help='Interactive mode (default)')
    
    args = parser.parse_args()
    
    # Find project root
    current_dir = Path(__file__).resolve().parent
    project_root = current_dir.parent
    
    creator = AgentCreator(project_root)
    
    if args.config:
        # Load configuration from file
        with open(args.config, 'r') as f:
            config = json.load(f)
    else:
        # Interactive mode
        config = get_user_input()
    
    # Create the agent
    success = creator.create_agent(config)
    
    if success:
        print("\n✅ Agent creation completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Agent creation failed!")
        sys.exit(1)


if __name__ == "__main__":
    main() 