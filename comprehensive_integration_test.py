#!/usr/bin/env python3
"""Comprehensive Integration Test Suite"""
import requests
import json
import time

def test_all_agents():
    """Run comprehensive tests on all agents"""
    
    results = {
        "orchestrator": {"status": "unknown", "tests": []},
        "menu_qa": {"status": "unknown", "tests": []},
        "order_history": {"status": "unknown", "tests": []},
        "price_update": {"status": "unknown", "tests": []},
        "pdf_ingestion": {"status": "unknown", "tests": []},
    }
    
    print("🧪 Comprehensive Integration Test Suite")
    print("=" * 50)
    
    # Test 1: Health Checks
    print("\n📋 1. Health Check Tests")
    print("-" * 30)
    
    agents = [
        ("orchestrator", 10200),
        ("menu_qa", 10220),
        ("order_history", 10210),
        ("price_update", 10410),
        ("pdf_ingestion", 10350)
    ]
    
    for name, port in agents:
        try:
            response = requests.get(f"http://localhost:{port}/health", timeout=5)
            if response.status_code == 200:
                results[name]["status"] = "healthy"
                results[name]["tests"].append({"test": "health_check", "result": "✅ PASS"})
                print(f"✅ {name.replace('_', '-').title()} Agent (port {port}): HEALTHY")
            else:
                results[name]["status"] = "unhealthy"
                results[name]["tests"].append({"test": "health_check", "result": f"❌ FAIL - Status {response.status_code}"})
                print(f"❌ {name.replace('_', '-').title()} Agent (port {port}): UNHEALTHY")
        except Exception as e:
            results[name]["status"] = "error"
            results[name]["tests"].append({"test": "health_check", "result": f"❌ ERROR - {str(e)}"})
            print(f"❌ {name.replace('_', '-').title()} Agent (port {port}): ERROR - {e}")
    
    # Test 2: Individual Agent Functionality
    print("\n🔧 2. Functionality Tests")
    print("-" * 30)
    
    # Test Menu QA Agent
    print("Testing Menu QA Agent...")
    try:
        payload = {
            "jsonrpc": "2.0",
            "method": "process_task",
            "params": {
                "task_description": "dietary restriction",
                "parameters": {"restriction": "vegetarian"}
            },
            "id": "test_menu"
        }
        response = requests.post("http://localhost:10220/", json=payload, timeout=10)
        if response.status_code == 200 and "result" in response.json():
            results["menu_qa"]["tests"].append({"test": "functionality", "result": "✅ PASS"})
            print("✅ Menu QA: Successfully returned dietary restriction data")
        else:
            results["menu_qa"]["tests"].append({"test": "functionality", "result": "❌ FAIL"})
            print("❌ Menu QA: Failed functionality test")
    except Exception as e:
        results["menu_qa"]["tests"].append({"test": "functionality", "result": f"❌ ERROR - {str(e)}"})
        print(f"❌ Menu QA: Error - {e}")
    
    # Test Order History Agent
    print("Testing Order History Agent...")
    try:
        payload = {
            "jsonrpc": "2.0",
            "method": "process_task",
            "params": {
                "task_description": "sales summary",
                "parameters": {"start_date": "2021-01-01", "end_date": "2021-12-31"}
            },
            "id": "test_orders"
        }
        response = requests.post("http://localhost:10210/", json=payload, timeout=10)
        if response.status_code == 200 and "result" in response.json():
            data = response.json()["result"]
            if "total_sales" in data:
                results["order_history"]["tests"].append({"test": "functionality", "result": "✅ PASS"})
                print(f"✅ Order History: Successfully returned sales data (${data['total_sales']})")
            else:
                results["order_history"]["tests"].append({"test": "functionality", "result": "❌ FAIL - No sales data"})
                print("❌ Order History: No sales data returned")
        else:
            results["order_history"]["tests"].append({"test": "functionality", "result": "❌ FAIL"})
            print("❌ Order History: Failed functionality test")
    except Exception as e:
        results["order_history"]["tests"].append({"test": "functionality", "result": f"❌ ERROR - {str(e)}"})
        print(f"❌ Order History: Error - {e}")
    
    # Test Price Update Agent
    print("Testing Price Update Agent...")
    try:
        payload = {
            "jsonrpc": "2.0",
            "method": "process_task",
            "params": {
                "task_description": "update price",
                "parameters": {"item_id": 1, "new_price": 15.99}
            },
            "id": "test_price"
        }
        response = requests.post("http://localhost:10410/", json=payload, timeout=10)
        if response.status_code == 200:
            results["price_update"]["tests"].append({"test": "functionality", "result": "✅ PASS"})
            print("✅ Price Update: Successfully processed price update request")
        else:
            results["price_update"]["tests"].append({"test": "functionality", "result": "❌ FAIL"})
            print("❌ Price Update: Failed functionality test")
    except Exception as e:
        results["price_update"]["tests"].append({"test": "functionality", "result": f"❌ ERROR - {str(e)}"})
        print(f"❌ Price Update: Error - {e}")
    
    # Test 3: Integration - Orchestrator Delegation
    print("\n🔗 3. Integration Tests")
    print("-" * 30)
    
    print("Testing Orchestrator → Menu QA delegation...")
    try:
        payload = {
            "jsonrpc": "2.0",
            "method": "delegate_task",
            "params": {"task_description": "dietary restriction vegetarian"},
            "id": "test_delegation"
        }
        response = requests.post("http://localhost:10200/", json=payload, timeout=30)
        if response.status_code == 200:
            data = response.json()["result"]
            if data.get("status") == "completed" and data.get("delegation_to") == "menu-qa-agent":
                results["orchestrator"]["tests"].append({"test": "delegation", "result": "✅ PASS"})
                print("✅ Orchestrator: Successfully delegated to menu-qa-agent")
            else:
                results["orchestrator"]["tests"].append({"test": "delegation", "result": "❌ FAIL - Delegation failed"})
                print("❌ Orchestrator: Delegation failed")
        else:
            results["orchestrator"]["tests"].append({"test": "delegation", "result": "❌ FAIL"})
            print("❌ Orchestrator: Failed delegation test")
    except Exception as e:
        results["orchestrator"]["tests"].append({"test": "delegation", "result": f"❌ ERROR - {str(e)}"})
        print(f"❌ Orchestrator: Error - {e}")
    
    # Test 4: Performance Check
    print("\n⚡ 4. Performance Tests")
    print("-" * 30)
    
    for name, port in agents[:3]:  # Test first 3 agents for performance
        try:
            start_time = time.time()
            response = requests.get(f"http://localhost:{port}/health", timeout=5)
            response_time = time.time() - start_time
            
            if response_time < 1.0:
                results[name]["tests"].append({"test": "performance", "result": f"✅ PASS ({response_time:.3f}s)"})
                print(f"✅ {name.replace('_', '-').title()}: Response time {response_time:.3f}s")
            else:
                results[name]["tests"].append({"test": "performance", "result": f"⚠️ SLOW ({response_time:.3f}s)"})
                print(f"⚠️ {name.replace('_', '-').title()}: Slow response time {response_time:.3f}s")
        except Exception as e:
            results[name]["tests"].append({"test": "performance", "result": f"❌ ERROR - {str(e)}"})
            print(f"❌ {name.replace('_', '-').title()}: Performance test error")
    
    # Summary
    print("\n📊 Test Summary")
    print("=" * 50)
    
    total_tests = 0
    passed_tests = 0
    
    for agent_name, agent_data in results.items():
        print(f"\n{agent_name.replace('_', '-').title()} Agent:")
        for test in agent_data["tests"]:
            print(f"  {test['test']}: {test['result']}")
            total_tests += 1
            if "✅ PASS" in test['result']:
                passed_tests += 1
    
    success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
    print(f"\n🎯 Overall Success Rate: {passed_tests}/{total_tests} ({success_rate:.1f}%)")
    
    if success_rate >= 80:
        print("🎉 SYSTEM STATUS: EXCELLENT")
    elif success_rate >= 60:
        print("✅ SYSTEM STATUS: GOOD")
    elif success_rate >= 40:
        print("⚠️ SYSTEM STATUS: NEEDS IMPROVEMENT")
    else:
        print("❌ SYSTEM STATUS: CRITICAL ISSUES")
    
    return results

if __name__ == "__main__":
    test_all_agents() 