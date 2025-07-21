#!/usr/bin/env python3
"""
Test script to check and fix agent registry for the orchestrator
"""
import sys
import json
import requests
from pathlib import Path

# Add parent directory to sys.path to access common_utils
parent_dir = Path(__file__).parent.parent
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))

from common_utils.agent_discovery import get_agent_registry

def test_agent_registry():
    """Test the agent registry to see what agents are available"""
    print("[INFO] Testing Agent Registry...")
    
    registry = get_agent_registry()
    agents = registry.list_agents()
    
    print(f"[INFO] Found {len(agents)} registered agents:")
    for name, info in agents.items():
        print(f"  - {name}: {info.get('card', {}).get('description', 'No description')}")
        print(f"    URL: {info.get('card', {}).get('url', 'No URL')}")
        print(f"    Skills: {[skill.get('id', 'unknown') for skill in info.get('card', {}).get('skills', [])]}")
    
    return agents

def manually_register_agents():
    """Manually register the running agents with the registry"""
    print("\n[INFO] Manually registering running agents...")
    
    agents_info = [
        {
            "name": "order-history-qa-agent",
            "url": "http://localhost:10210",
            "description": "Specialized agent for answering questions about order history, sales analytics, and business intelligence queries using natural language to SQL conversion"
        },
        {
            "name": "menu-qa-agent", 
            "url": "http://localhost:10220",
            "description": "Specialized agent for answering questions about current menu items, availability, pricing, ingredients, and dietary restrictions"
        },
        {
            "name": "price-update-agent",
            "url": "http://localhost:10410", 
            "description": "Specialized agent for executing menu price updates, item modifications, and availability changes through natural language commands with database write operations"
        },
        {
            "name": "pdf-ingestion-agent",
            "url": "http://localhost:10350",
            "description": "Specialized agent for extracting menu items and data from PDF documents, processing unstructured content, and inserting new items into the database"
        }
    ]
    
    registry = get_agent_registry()
    
    for agent_info in agents_info:
        try:
            # Fetch agent card from the running agent
            response = requests.get(f"{agent_info['url']}/agent_card", timeout=5)
            if response.status_code == 200:
                agent_card = response.json()
                
                # Register with registry
                registry.agents[agent_info['name']] = {
                    "card": agent_card,
                    "registered_at": "2025-01-21T00:00:00",
                    "last_health_check": None,
                    "status": "active"
                }
                print(f"  [OK] Registered {agent_info['name']}")
            else:
                print(f"  [ERROR] Could not fetch agent card for {agent_info['name']}")
                
        except Exception as e:
            print(f"  [ERROR] Failed to register {agent_info['name']}: {e}")

def test_routing():
    """Test the orchestrator routing with different queries"""
    print("\n[INFO] Testing Orchestrator Routing...")
    
    test_queries = [
        "What were the total sales last week?",
        "What vegetarian options do we have?", 
        "Update the price of burgers to 12.99",
        "How many orders were placed yesterday?"
    ]
    
    for query in test_queries:
        print(f"\n[TEST] Query: '{query}'")
        
        payload = {
            "jsonrpc": "2.0",
            "method": "delegate_task",
            "params": {"task_description": query},
            "id": "registry_test"
        }
        
        try:
            response = requests.post(
                "http://localhost:10200/",
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if "result" in result:
                    if result["result"].get("status") == "completed":
                        agent_name = result["result"].get("delegation_to", "unknown")
                        print(f"  [SUCCESS] Routed to: {agent_name}")
                    else:
                        print(f"  [ERROR] {result['result'].get('message', 'Unknown error')}")
                else:
                    print(f"  [ERROR] Invalid response format")
            else:
                print(f"  [ERROR] HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            print(f"  [ERROR] Request failed: {e}")

def main():
    """Main test function"""
    print("Agent Registry and Routing Test")
    print("=" * 50)
    
    # Test current registry state
    agents = test_agent_registry()
    
    # If no agents, manually register them
    if not agents:
        manually_register_agents()
        agents = test_agent_registry()
    
    # Test routing
    if agents:
        test_routing()
    else:
        print("\n[ERROR] No agents available for routing tests")

if __name__ == "__main__":
    main() 