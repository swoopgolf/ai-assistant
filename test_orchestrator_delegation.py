#!/usr/bin/env python3
"""Test orchestrator delegation functionality"""
import requests
import json

def test_orchestrator_delegation():
    """Test that orchestrator can delegate tasks to menu-qa-agent"""
    
    print("Testing Orchestrator → Menu QA Agent delegation...")
    payload = {
        "jsonrpc": "2.0",
        "method": "delegate_task",
        "params": {
            "task_description": "dietary restriction vegetarian"
        },
        "id": "orchestrator_delegation_test"
    }
    
    try:
        response = requests.post(
            "http://localhost:10200/",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        print(f"Orchestrator Status: {response.status_code}")
        print(f"Orchestrator Response: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Parsed result: {json.dumps(result, indent=2)}")
        
    except Exception as e:
        print(f"Orchestrator Error: {e}")

if __name__ == "__main__":
    test_orchestrator_delegation() 