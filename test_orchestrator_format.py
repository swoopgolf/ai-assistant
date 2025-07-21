#!/usr/bin/env python3
"""Test exact orchestrator request format"""
import requests
import json

def test_exact_orchestrator_format():
    """Test menu-qa-agent with exact format orchestrator would send"""
    
    print("Testing Menu QA Agent with orchestrator format...")
    payload = {
        "jsonrpc": "2.0",
        "method": "process_task",
        "params": {
            "task_description": "What vegetarian options do we have on the menu?",
            "parameters": {}
        },
        "id": "orchestrator_process_task"
    }
    
    try:
        response = requests.post(
            "http://localhost:10220/",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        print(f"Menu QA Agent Status: {response.status_code}")
        print(f"Menu QA Agent Response: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Parsed result: {json.dumps(result, indent=2)}")
        
    except Exception as e:
        print(f"Menu QA Agent Error: {e}")

if __name__ == "__main__":
    test_exact_orchestrator_format() 