#!/usr/bin/env python3
"""Test order history agent functionality"""
import requests
import json

def test_order_history_agent():
    """Test direct communication with the order history agent"""
    
    print("Testing Order History QA Agent directly...")
    payload = {
        "jsonrpc": "2.0",
        "method": "process_task",
        "params": {
            "task_description": "sales summary",
            "parameters": {
                "start_date": "2021-01-01",
                "end_date": "2021-12-31"
            }
        },
        "id": "order_history_test"
    }
    
    try:
        response = requests.post(
            "http://localhost:10210/",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        print(f"Order History Agent Status: {response.status_code}")
        print(f"Order History Agent Response: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Parsed result: {json.dumps(result, indent=2)}")
        
    except Exception as e:
        print(f"Order History Agent Error: {e}")

if __name__ == "__main__":
    test_order_history_agent() 