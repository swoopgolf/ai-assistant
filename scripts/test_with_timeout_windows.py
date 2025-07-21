#!/usr/bin/env python3
"""
Windows-compatible timeout-based test script for the Orchestrator Agent
"""
import requests
import json
import sys
import time
import threading
from concurrent.futures import ThreadPoolExecutor, TimeoutError

def quick_health_check():
    """Quick health check with timeout"""
    try:
        response = requests.get("http://localhost:10200/health", timeout=5)
        if response.status_code == 200:
            print("[OK] Orchestrator is healthy")
            return True
        else:
            print(f"[ERROR] Orchestrator health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"[ERROR] Health check failed: {e}")
        return False

def test_agent_discovery():
    """Test if agents can be discovered with timeout"""
    agents = [
        ("Order History QA", "http://localhost:10210/agent_card"),
        ("Menu QA", "http://localhost:10220/agent_card"),
        ("Price Update", "http://localhost:10410/agent_card"),
    ]
    
    discovered = []
    for name, url in agents:
        try:
            response = requests.get(url, timeout=3)
            if response.status_code == 200:
                discovered.append(name)
                print(f"[OK] {name} agent is running")
            else:
                print(f"[ERROR] {name} agent not responding")
        except Exception as e:
            print(f"[ERROR] {name} agent error: {e}")
    
    return discovered

def make_orchestrator_request(payload, timeout_seconds):
    """Make a request to orchestrator with timeout"""
    try:
        response = requests.post(
            "http://localhost:10200/",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=timeout_seconds
        )
        return response
    except Exception as e:
        raise e

def test_orchestrator_with_timeout(query, test_name, max_timeout=15):
    """Test orchestrator with strict timeout using ThreadPoolExecutor"""
    print(f"\n[TEST] {test_name}: '{query}'")
    
    payload = {
        "jsonrpc": "2.0",
        "method": "delegate_task",
        "params": {"task_description": query},
        "id": f"timeout_test_{int(time.time())}"
    }
    
    start_time = time.time()
    
    try:
        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(make_orchestrator_request, payload, max_timeout - 2)
            response = future.result(timeout=max_timeout)
            
        duration = time.time() - start_time
        
        if response.status_code == 200:
            result = response.json()
            print(f"[SUCCESS] Response received in {duration:.2f}s")
            
            if "result" in result:
                if result["result"].get("status") == "completed":
                    agent_name = result["result"].get("delegation_to", "unknown")
                    print(f"  -> Routed to: {agent_name}")
                    return True, agent_name
                elif result["result"].get("status") == "error":
                    error_msg = result["result"].get("message", "Unknown error")
                    print(f"  -> Error: {error_msg}")
                    return False, error_msg
                else:
                    print(f"  -> Unexpected status: {result['result'].get('status')}")
                    return False, "unexpected_status"
            else:
                print(f"  -> Invalid response format")
                return False, "invalid_format"
        else:
            duration = time.time() - start_time
            print(f"[ERROR] HTTP {response.status_code} in {duration:.2f}s")
            return False, f"http_{response.status_code}"
            
    except TimeoutError:
        print(f"[TIMEOUT] Test timed out after {max_timeout} seconds")
        return False, "timeout"
    except Exception as e:
        duration = time.time() - start_time
        print(f"[ERROR] Test failed in {duration:.2f}s: {e}")
        return False, str(e)

def test_registry_refresh():
    """Test registry refresh endpoint with timeout"""
    print("\n[TEST] Registry Refresh")
    
    payload = {
        "jsonrpc": "2.0",
        "method": "refresh_registry",
        "params": {},
        "id": "refresh_test"
    }
    
    try:
        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(make_orchestrator_request, payload, 8)
            response = future.result(timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            print("[SUCCESS] Registry refresh completed")
            if "result" in result and result["result"].get("status") == "success":
                agent_count = result["result"].get("total_agents", 0)
                print(f"  -> {agent_count} agents registered")
                return True
            else:
                print(f"  -> Refresh failed: {result}")
                return False
        else:
            print(f"[ERROR] Refresh failed: HTTP {response.status_code}")
            return False
            
    except TimeoutError:
        print("[TIMEOUT] Registry refresh timed out")
        return False
    except Exception as e:
        print(f"[ERROR] Registry refresh error: {e}")
        return False

def test_simple_routing():
    """Test simple routing without LLM to check basic functionality"""
    print("\n[TEST] Simple JSON-RPC Test")
    
    # Test a simple endpoint first
    try:
        response = requests.get("http://localhost:10200/capabilities", timeout=5)
        if response.status_code == 200:
            caps = response.json()
            print(f"[OK] Orchestrator capabilities: {caps.get('skills', [])}")
            return True
        else:
            print(f"[ERROR] Cannot get capabilities: {response.status_code}")
            return False
    except Exception as e:
        print(f"[ERROR] Capabilities test failed: {e}")
        return False

def main():
    """Main test function with comprehensive timeout handling"""
    print("=== Windows Timeout-Based Orchestrator Testing ===")
    print(f"Started at: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Quick health check
    if not quick_health_check():
        print("\n[ABORT] Orchestrator not healthy, stopping tests")
        return
    
    # Test simple functionality first
    print("\n--- Basic Functionality ---")
    simple_test = test_simple_routing()
    
    # Test agent discovery
    print("\n--- Agent Discovery ---")
    discovered_agents = test_agent_discovery()
    print(f"Discovered {len(discovered_agents)} agents: {discovered_agents}")
    
    # Test registry refresh
    print("\n--- Registry Refresh ---")
    refresh_success = test_registry_refresh()
    
    # Test orchestrator routing with different queries
    print("\n--- Orchestrator Routing Tests ---")
    test_cases = [
        ("What were the total sales last week?", "Sales Query"),
        ("What vegetarian options do we have?", "Menu Query"),
        ("Update the price of burgers to 12.99", "Price Update"),
        ("Show me business analytics", "Analytics Query")
    ]
    
    results = []
    for query, test_name in test_cases:
        success, result = test_orchestrator_with_timeout(query, test_name, max_timeout=25)
        results.append((test_name, success, result))
        time.sleep(2)  # Brief pause between tests
    
    # Summary
    print("\n=== Test Summary ===")
    print(f"Completed at: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Basic Functionality: {'SUCCESS' if simple_test else 'FAILED'}")
    print(f"Agent Discovery: {len(discovered_agents)} agents found")
    print(f"Registry Refresh: {'SUCCESS' if refresh_success else 'FAILED'}")
    print("Routing Tests:")
    
    success_count = 0
    for test_name, success, result in results:
        status = "SUCCESS" if success else "FAILED"
        print(f"  - {test_name}: {status} ({result})")
        if success:
            success_count += 1
    
    print(f"\nOverall: {success_count}/{len(results)} routing tests successful")
    
    if success_count > 0:
        print("\n[CONCLUSION] System is partially or fully functional!")
    elif refresh_success and len(discovered_agents) > 0:
        print("\n[CONCLUSION] Agents discovered and registry works, but routing fails")
        print("  -> Likely LLM or routing logic issue")
    else:
        print("\n[CONCLUSION] System needs debugging - basic issues detected")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[INTERRUPTED] Test interrupted by user")
    except Exception as e:
        print(f"\n[FATAL] Unexpected error: {e}")
        import traceback
        traceback.print_exc() 