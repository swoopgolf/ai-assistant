#!/usr/bin/env python3
"""Test with security headers"""
import requests
import json
from common_utils.agent_security import create_secure_headers

def test_with_security_headers():
    """Test menu-qa-agent with security headers like orchestrator would send"""
    
    print("Testing Menu QA Agent with security headers...")
    payload = {
        "jsonrpc": "2.0",
        "method": "process_task",
        "params": {
            "task_description": "What vegetarian options do we have on the menu?",
            "parameters": {}
        },
        "id": "orchestrator_process_task"
    }
    
    headers = create_secure_headers("orchestrator")
    print(f"Using headers: {headers}")
    
    try:
        response = requests.post(
            "http://localhost:10220/",
            json=payload,
            headers=headers,
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
    test_with_security_headers() 