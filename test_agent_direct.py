#!/usr/bin/env python3
"""Test direct agent communication"""
import requests
import json

def test_agent_direct():
    """Test direct communication with agents"""
    
    # Test menu agent
    print("Testing Menu QA Agent directly...")
    payload = {
        "jsonrpc": "2.0",
        "method": "process_task_skill",
        "params": {"task_description": "What vegetarian options do we have?"},
        "id": "direct_test"
    }
    
    try:
        response = requests.post(
            "http://localhost:10220/",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        print(f"Menu Agent Status: {response.status_code}")
        print(f"Menu Agent Response: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Parsed result: {json.dumps(result, indent=2)}")
        
    except Exception as e:
        print(f"Menu Agent Error: {e}")
    
    print("\n" + "="*50 + "\n")
    
    # Test orchestrator with debug
    print("Testing Orchestrator routing...")
    payload = {
        "jsonrpc": "2.0", 
        "method": "delegate_task",
        "params": {"task_description": "What vegetarian options do we have?"},
        "id": "orchestrator_test"
    }
    
    try:
        response = requests.post(
            "http://localhost:10200/",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        print(f"Orchestrator Status: {response.status_code}")
        print(f"Orchestrator Response: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Parsed result: {json.dumps(result, indent=2)}")
            
    except Exception as e:
        print(f"Orchestrator Error: {e}")

if __name__ == "__main__":
    test_agent_direct() 