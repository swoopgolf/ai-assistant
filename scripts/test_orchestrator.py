#!/usr/bin/env python3
"""
Test script for the Orchestrator Agent
"""
import requests
import json
import sys
import time

def wait_for_orchestrator(max_retries=30, delay=1):
    """Wait for orchestrator to be ready"""
    for attempt in range(max_retries):
        try:
            response = requests.get("http://localhost:10200/health", timeout=5)
            if response.status_code == 200:
                print("[OK] Orchestrator is healthy.")
                return True
        except Exception as e:
            print(f"... Waiting for orchestrator to be ready...")
            time.sleep(delay)
    
    print("[ERROR] Timed out waiting for orchestrator.")
    return False

def send_task_to_orchestrator(task_description):
    """Send a task to the orchestrator using correct JSON-RPC format"""
    url = "http://localhost:10200/"
    
    # Correct JSON-RPC format for the orchestrator
    payload = {
        "jsonrpc": "2.0",
        "method": "delegate_task",
        "params": {
            "task_description": task_description
        },
        "id": "test_1"
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            print(f"\n[SUCCESS] Task completed:")
            print(json.dumps(result, indent=2))
            return True
        else:
            print(f"\n[ERROR] Request failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"\n[ERROR] Failed to send request: {e}")
        return False

def main():
    """Main test function"""
    if len(sys.argv) < 2:
        print("Usage: python test_orchestrator.py \"Your task description\"")
        print("\nExample tasks:")
        print("  \"What were the total sales last week?\"")
        print("  \"What vegetarian options do we have?\"")
        print("  \"Update the price of burgers to $12.99\"")
        return
    
    task_description = sys.argv[1]
    
    print("[TESTING] Club Management AI Assistant")
    print("Ask me anything about sales, the menu, or prices. I'll route your question to the right agent.")
    print(f"\n{task_description}")
    
    # Wait for orchestrator to be ready
    if not wait_for_orchestrator():
        return
    
    # Send the task
    success = send_task_to_orchestrator(task_description)
    
    if success:
        print("\n[OK] Test completed successfully!")
    else:
        print("\n[FAILED] Test failed!")

if __name__ == "__main__":
    main() 