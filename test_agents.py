#!/usr/bin/env python3
"""
Simple agent testing script to validate the setup
"""

import requests
import time
import subprocess
import sys
from pathlib import Path

def test_agent_health(agent_name, port, timeout=5):
    """Test if an agent is running and healthy."""
    try:
        response = requests.get(f"http://localhost:{port}/health", timeout=timeout)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ {agent_name} (port {port}): HEALTHY")
            print(f"   Status: {data.get('status', 'unknown')}")
            return True
        else:
            print(f"❌ {agent_name} (port {port}): HTTP {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ {agent_name} (port {port}): CONNECTION FAILED - {e}")
        return False

def start_agent(agent_dir, timeout=10):
    """Start an agent and wait for it to be ready."""
    print(f"🚀 Starting {agent_dir}...")
    
    # Change to agent directory and start
    agent_path = Path(agent_dir)
    if not agent_path.exists():
        print(f"❌ Agent directory {agent_dir} not found")
        return None
    
    # Start the agent as a subprocess
    try:
        proc = subprocess.Popen(
            [sys.executable, "-m", agent_path.name.replace('-', '_')],
            cwd=agent_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Give it a moment to start
        time.sleep(2)
        
        if proc.poll() is None:  # Still running
            print(f"✅ {agent_dir} process started (PID: {proc.pid})")
            return proc
        else:
            stdout, stderr = proc.communicate()
            print(f"❌ {agent_dir} failed to start:")
            print(f"   STDOUT: {stdout.decode()}")
            print(f"   STDERR: {stderr.decode()}")
            return None
            
    except Exception as e:
        print(f"❌ Failed to start {agent_dir}: {e}")
        return None

def main():
    """Test all agents in the system."""
    print("🧪 AI Assistant Agent System Test")
    print("=" * 50)
    
    # Define agents to test
    agents = [
        ("Orchestrator Agent", "orchestrator-agent", 10200),
        ("Order History QA Agent", "order-history-qa-agent", 10210),
        ("Menu QA Agent", "menu-qa-agent", 10220),
        ("PDF Ingestion Agent", "pdf-ingestion-agent", 10350),
        ("Price Update Agent", "price-update-agent", 10410),
    ]
    
    print("\n📋 Configuration Check")
    print("-" * 30)
    
    # Check if environment file exists
    env_file = Path("config/environment.env")
    if env_file.exists():
        print("✅ Environment file found")
        # Try to load and validate config
        try:
            import os
            from dotenv import load_dotenv
            load_dotenv(env_file)
            
            required_vars = ["DB_HOST", "DB_PORT", "DB_NAME", "GOOGLE_API_KEY"]
            missing = []
            for var in required_vars:
                if not os.getenv(var):
                    missing.append(var)
            
            if missing:
                print(f"⚠️  Missing environment variables: {', '.join(missing)}")
            else:
                print("✅ All required environment variables set")
                
        except Exception as e:
            print(f"⚠️  Could not validate environment: {e}")
    else:
        print("❌ Environment file not found")
    
    print("\n🏥 Health Check (Existing Agents)")
    print("-" * 40)
    
    # Test if any agents are already running
    healthy_agents = []
    for name, _, port in agents:
        if test_agent_health(name, port):
            healthy_agents.append(name)
    
    if not healthy_agents:
        print("\n🚀 No agents running. Testing startup capability...")
        print("-" * 50)
        
        # Try to start one agent as a test
        test_agent = "menu-qa-agent"
        proc = start_agent(test_agent)
        
        if proc:
            time.sleep(3)  # Wait for startup
            success = test_agent_health("Menu QA Agent", 10220)
            
            # Clean up
            proc.terminate()
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()
            
            if success:
                print("\n✅ Agent startup test PASSED")
            else:
                print("\n❌ Agent startup test FAILED")
        else:
            print("\n❌ Could not start test agent")
    
    print("\n📊 System Status Summary")
    print("-" * 30)
    print(f"Healthy agents: {len(healthy_agents)}/{len(agents)}")
    
    if len(healthy_agents) == len(agents):
        print("🎉 All agents are healthy!")
    elif healthy_agents:
        print(f"⚠️  Some agents are running: {', '.join(healthy_agents)}")
    else:
        print("💡 No agents currently running. Use individual startup commands.")
    
    print("\n🎯 Next Steps:")
    print("1. Start agents individually: cd <agent-dir> && python -m <agent_module>")
    print("2. Test orchestrator: curl http://localhost:10200/health")
    print("3. Run integration tests: python test_integration.py")

if __name__ == "__main__":
    main() 