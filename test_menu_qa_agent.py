#!/usr/bin/env python3
"""Test direct agent communication"""
import requests
import json

def test_menu_qa_agent():
    """Test direct communication with the menu qa agent"""
    
    print("Testing Menu QA Agent directly...")
    payload = {
        "jsonrpc": "2.0",
        "method": "process_task",
        "params": {
            "task_description": "dietary restriction",
            "parameters": {
                "restriction": "vegetarian"
            }
        },
        "id": "menu_qa_test"
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
    test_menu_qa_agent() 