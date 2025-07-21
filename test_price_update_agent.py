#!/usr/bin/env python3
"""Test direct agent communication"""
import requests
import json
import argparse

def test_price_update_agent(item_id, new_price):
    """Test direct communication with the price update agent"""
    
    print("Testing Price Update Agent directly...")
    payload = {
        "jsonrpc": "2.0",
        "method": "process_task",
        "params": {
            "task_description": "update price",
            "parameters": {
                "item_id": item_id,
                "new_price": new_price
            }
        },
        "id": "price_update_test"
    }
    
    try:
        response = requests.post(
            "http://localhost:10410/",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        print(f"Price Update Agent Status: {response.status_code}")
        print(f"Price Update Agent Response: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Parsed result: {json.dumps(result, indent=2)}")
        
    except Exception as e:
        print(f"Price Update Agent Error: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test the Price Update Agent.")
    parser.add_argument("--item_id", type=str, required=True, help="The ID of the item to update.")
    parser.add_argument("--new_price", type=float, required=True, help="The new price for the item.")
    args = parser.parse_args()
    
    test_price_update_agent(args.item_id, args.new_price) 