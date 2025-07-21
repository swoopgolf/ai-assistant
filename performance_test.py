#!/usr/bin/env python3
"""Performance Testing Suite"""
import requests
import json
import time
import statistics
from concurrent.futures import ThreadPoolExecutor
import threading

def measure_response_time(url, payload=None, method="GET"):
    """Measure response time for a single request"""
    start_time = time.time()
    try:
        if method == "GET":
            response = requests.get(url, timeout=10)
        else:
            response = requests.post(url, json=payload, headers={"Content-Type": "application/json"}, timeout=10)
        end_time = time.time()
        return {
            "success": True,
            "response_time": end_time - start_time,
            "status_code": response.status_code
        }
    except Exception as e:
        end_time = time.time()
        return {
            "success": False,
            "response_time": end_time - start_time,
            "error": str(e)
        }

def load_test_agent(agent_name, port, concurrent_requests=5, total_requests=20):
    """Run load test on a specific agent"""
    print(f"\n⚡ Load Testing {agent_name} Agent (Port {port})")
    print("-" * 40)
    
    url = f"http://localhost:{port}/health"
    
    def make_request():
        return measure_response_time(url)
    
    # Sequential baseline test
    print("🔍 Sequential Baseline (1 request)...")
    baseline = make_request()
    if baseline["success"]:
        print(f"   Baseline response time: {baseline['response_time']:.3f}s")
    else:
        print(f"   Baseline failed: {baseline.get('error', 'Unknown error')}")
        return
    
    # Concurrent load test
    print(f"🚀 Concurrent Load Test ({concurrent_requests} concurrent, {total_requests} total)...")
    
    start_time = time.time()
    results = []
    
    with ThreadPoolExecutor(max_workers=concurrent_requests) as executor:
        futures = [executor.submit(make_request) for _ in range(total_requests)]
        for future in futures:
            results.append(future.result())
    
    total_time = time.time() - start_time
    
    # Analyze results
    successful_requests = [r for r in results if r["success"]]
    failed_requests = [r for r in results if not r["success"]]
    
    if successful_requests:
        response_times = [r["response_time"] for r in successful_requests]
        
        print(f"   📊 Results Summary:")
        print(f"      ✅ Successful requests: {len(successful_requests)}/{total_requests}")
        print(f"      ❌ Failed requests: {len(failed_requests)}")
        print(f"      ⏱️  Total test time: {total_time:.3f}s")
        print(f"      🏃 Requests per second: {total_requests/total_time:.2f}")
        print(f"      📈 Response Time Stats:")
        print(f"         • Average: {statistics.mean(response_times):.3f}s")
        print(f"         • Median: {statistics.median(response_times):.3f}s")
        print(f"         • Min: {min(response_times):.3f}s")
        print(f"         • Max: {max(response_times):.3f}s")
        
        if len(response_times) > 1:
            print(f"         • Std Dev: {statistics.stdev(response_times):.3f}s")
        
        # Performance assessment
        avg_time = statistics.mean(response_times)
        if avg_time < 0.1:
            print(f"      🎉 Performance: EXCELLENT (< 100ms)")
        elif avg_time < 0.5:
            print(f"      ✅ Performance: GOOD (< 500ms)")
        elif avg_time < 1.0:
            print(f"      ⚠️  Performance: ACCEPTABLE (< 1s)")
        else:
            print(f"      ❌ Performance: NEEDS IMPROVEMENT (> 1s)")
    else:
        print(f"   ❌ All requests failed!")

def functionality_performance_test():
    """Test performance of actual functionality, not just health checks"""
    print(f"\n🎯 Functionality Performance Tests")
    print("=" * 50)
    
    # Test Menu QA functionality performance
    print("\n🍽️ Menu QA Agent - Dietary Restriction Query")
    payload = {
        "jsonrpc": "2.0",
        "method": "process_task",
        "params": {
            "task_description": "dietary restriction",
            "parameters": {"restriction": "vegetarian"}
        },
        "id": "perf_test_menu"
    }
    
    results = []
    for i in range(5):
        result = measure_response_time("http://localhost:10220/", payload, "POST")
        results.append(result)
        if result["success"]:
            print(f"   Request {i+1}: {result['response_time']:.3f}s ✅")
        else:
            print(f"   Request {i+1}: FAILED ❌")
    
    successful = [r for r in results if r["success"]]
    if successful:
        avg_time = statistics.mean([r["response_time"] for r in successful])
        print(f"   Average functionality response time: {avg_time:.3f}s")
    
    # Test Order History functionality performance
    print("\n📊 Order History Agent - Sales Summary Query")
    payload = {
        "jsonrpc": "2.0",
        "method": "process_task",
        "params": {
            "task_description": "sales summary",
            "parameters": {"start_date": "2021-01-01", "end_date": "2021-12-31"}
        },
        "id": "perf_test_orders"
    }
    
    results = []
    for i in range(3):  # Fewer tests for database queries
        result = measure_response_time("http://localhost:10210/", payload, "POST")
        results.append(result)
        if result["success"]:
            print(f"   Request {i+1}: {result['response_time']:.3f}s ✅")
        else:
            print(f"   Request {i+1}: FAILED ❌")
    
    successful = [r for r in results if r["success"]]
    if successful:
        avg_time = statistics.mean([r["response_time"] for r in successful])
        print(f"   Average database query response time: {avg_time:.3f}s")

def run_performance_tests():
    """Run complete performance test suite"""
    print("🚀 AI Assistant System - Performance Test Suite")
    print("=" * 60)
    
    agents = [
        ("Orchestrator", 10200),
        ("Menu QA", 10220),
        ("Order History", 10210),
        ("Price Update", 10410),
        ("PDF Ingestion", 10350)
    ]
    
    # Health check load tests
    for name, port in agents:
        load_test_agent(name, port, concurrent_requests=3, total_requests=10)
    
    # Functionality performance tests
    functionality_performance_test()
    
    print(f"\n🏁 Performance Testing Complete!")
    print("=" * 60)

if __name__ == "__main__":
    run_performance_tests() 