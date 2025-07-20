#!/usr/bin/env python3
"""
Club Management Agents Creator

This script creates all the specialized agents for the club management system
as described in the architecture document. It creates:

1. Order History Q&A Agent - Sales analytics and business intelligence
2. Menu Q&A Agent - Menu queries and information lookup  
3. Price Update Agent - Menu editing and price modifications
4. PDF Ingestion Agent - Document processing and item extraction

Usage:
    python scripts/create_club_management_agents.py
    
Or to create individual agents:
    python scripts/create_club_management_agents.py --agent order-history
    python scripts/create_club_management_agents.py --agent menu-qa
    python scripts/create_club_management_agents.py --agent price-update
    python scripts/create_club_management_agents.py --agent pdf-ingestion
"""

import sys
import argparse
from pathlib import Path
import subprocess
import json

# Add the scripts directory to path to import create_new_agent
sys.path.insert(0, str(Path(__file__).parent))
from create_new_agent import AgentCreator

def load_config(config_path: Path) -> dict:
    """Load agent configuration from JSON file."""
    with open(config_path, 'r') as f:
        return json.load(f)

def create_all_agents(project_root: Path, creator: AgentCreator) -> None:
    """Create all club management agents."""
    configs_dir = project_root / "scripts" / "configs"
    
    agents = [
        "order-history-qa-agent.json",
        "menu-qa-agent.json", 
        "price-update-agent.json",
        "pdf-ingestion-agent.json"
    ]
    
    print("🏌️ Creating Club Management Agent System")
    print("=" * 50)
    
    created_agents = []
    failed_agents = []
    
    for agent_file in agents:
        config_path = configs_dir / agent_file
        
        if not config_path.exists():
            print(f"❌ Configuration file not found: {config_path}")
            failed_agents.append(agent_file)
            continue
            
        try:
            print(f"\n📋 Creating agent from {agent_file}...")
            config = load_config(config_path)
            
            success = creator.create_agent(config)
            if success:
                created_agents.append(config['agent_name'])
            else:
                failed_agents.append(config['agent_name'])
                
        except Exception as e:
            print(f"❌ Error creating agent from {agent_file}: {str(e)}")
            failed_agents.append(agent_file)
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Creation Summary")
    print("=" * 50)
    
    if created_agents:
        print(f"✅ Successfully created {len(created_agents)} agents:")
        for agent in created_agents:
            print(f"   - {agent}")
    
    if failed_agents:
        print(f"\n❌ Failed to create {len(failed_agents)} agents:")
        for agent in failed_agents:
            print(f"   - {agent}")
    
    if created_agents:
        print("\n🎯 Next Steps:")
        print("1. Customize each agent's implementation:")
        for agent in created_agents:
            package_name = agent.replace('-', '_')
            print(f"   - Edit {agent}/{package_name}/agent_executor.py")
            print(f"   - Edit {agent}/{package_name}/tools.py")
        
        print("\n2. Implement database connectivity:")
        print("   - Add Cloud SQL PostgreSQL connection logic")
        print("   - Implement schema-aware SQL generation")
        print("   - Add proper error handling and validation")
        
        print("\n3. Deploy and test each agent:")
        for agent in created_agents:
            config = load_config(configs_dir / f"{agent}.json")
            print(f"   - Test {agent}: curl http://localhost:{config['port']}/health")
        
        print("\n4. Update orchestrator to use these agents:")
        print("   - Register agents with the orchestrator")
        print("   - Implement intent recognition and routing")
        print("   - Test end-to-end workflows")

def create_single_agent(agent_name: str, project_root: Path, creator: AgentCreator) -> None:
    """Create a single agent by name."""
    configs_dir = project_root / "scripts" / "configs"
    
    agent_mapping = {
        'order-history': 'order-history-qa-agent.json',
        'menu-qa': 'menu-qa-agent.json',
        'price-update': 'price-update-agent.json', 
        'pdf-ingestion': 'pdf-ingestion-agent.json'
    }
    
    if agent_name not in agent_mapping:
        print(f"❌ Unknown agent: {agent_name}")
        print(f"Available agents: {', '.join(agent_mapping.keys())}")
        return
    
    config_file = agent_mapping[agent_name]
    config_path = configs_dir / config_file
    
    if not config_path.exists():
        print(f"❌ Configuration file not found: {config_path}")
        return
    
    try:
        config = load_config(config_path)
        success = creator.create_agent(config)
        
        if success:
            print(f"✅ Successfully created {config['agent_name']}")
        else:
            print(f"❌ Failed to create {config['agent_name']}")
            
    except Exception as e:
        print(f"❌ Error creating agent: {str(e)}")

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Create club management agents')
    parser.add_argument('--agent', type=str, help='Create specific agent (order-history, menu-qa, price-update, pdf-ingestion)')
    
    args = parser.parse_args()
    
    # Find project root
    current_dir = Path(__file__).resolve().parent  
    project_root = current_dir.parent
    
    creator = AgentCreator(project_root)
    
    if args.agent:
        create_single_agent(args.agent, project_root, creator)
    else:
        create_all_agents(project_root, creator)

if __name__ == "__main__":
    main() 