#!/usr/bin/env python3
"""
Multi-Agent System Runner

This script automates the startup and shutdown of all agents and the MCP server
for the AI Assistant framework.

It starts all services as background processes and ensures they are terminated
gracefully when the script is stopped (e.g., via Ctrl+C).
"""

import subprocess
import time
import sys
import atexit
from pathlib import Path
import io
import threading
import os
import socket

# --- Configuration ---
# List of services to run. Each entry is a tuple of:
# (service_name, directory, module_to_run, port)
SERVICES = [
    ("MCP Server", "common_utils", "mcp_server.tool_server", 11001),
    ("Orchestrator", "orchestrator-agent", "orchestrator_agent", 10200),
    ("Menu QA Agent", "menu-qa-agent", "menu_qa_agent", 10220),
    ("Order History QA Agent", "order-history-qa-agent", "order_history_qa_agent", 10210),
    ("Price Update Agent", "price-update-agent", "price_update_agent", 10410),
    ("PDF Ingestion Agent", "pdf-ingestion-agent", "pdf_ingestion_agent", 10350),
]

processes = []

def is_port_in_use(port: int) -> bool:
    """Check if a local port is already in use."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

def stream_reader(pipe, name):
    """Read and print lines from a subprocess's pipe."""
    if not pipe:
        return
    try:
        for line in iter(pipe.readline, ''):
            print(f"[{name}] {line.strip()}")
    finally:
        pipe.close()

def cleanup_processes():
    """Terminate all running child processes."""
    print("\nShutting down all services...")
    for proc, name in processes:
        if proc.poll() is None:  # If the process is still running
            print(f"  Terminating {name} (PID: {proc.pid})...")
            proc.terminate()
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                print(f"  {name} did not terminate gracefully, killing.")
                proc.kill()
    print("Cleanup complete.")

def main():
    """Start all services and monitor them."""
    print("Starting AI Assistant System")
    print("=" * 40)
    
    # Register the cleanup function to run on script exit
    atexit.register(cleanup_processes)

    project_root = Path(__file__).parent.parent
    
    for name, directory, module, port in SERVICES:
        # Check if the port is already in use
        if is_port_in_use(port):
            print(f"[ERROR] Port {port} for {name} is already in use.")
            print("   Please stop the existing process or choose a different port.")
            # Don't exit immediately, let atexit handle cleanup of any started processes
            sys.exit(1)

        service_path = project_root / directory
        if not service_path.is_dir():
            print(f"[ERROR] Directory for {name} not found at: {service_path}")
            sys.exit(1)

        print(f"  Starting {name}...")
        try:
            # We use sys.executable to ensure we're using the same Python interpreter
            # that is running this script.
            
            # Set the PYTHONPATH for the child process to include the project root
            env = os.environ.copy()
            env["PYTHONPATH"] = str(project_root)
            
            proc = subprocess.Popen(
                [sys.executable, "-m", module],
                cwd=service_path,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT, # Redirect stderr to stdout
                text=True,
                bufsize=1, # Line-buffered
                env=env,
            )
            processes.append((proc, name))
            print(f"  [OK] {name} started with PID: {proc.pid}")
            time.sleep(1) # Stagger startups slightly
        except FileNotFoundError:
            print(f"[ERROR] Could not find the module '{module}' for {name}.")
            print("   Please ensure the agent has been installed correctly (e.g., 'pip install -e .')")
            sys.exit(1)
        except Exception as e:
            print(f"[ERROR] An unexpected error occurred while starting {name}: {e}")
            sys.exit(1)

    print("\n[OK] All services have been started.")
    print("Press Ctrl+C to stop the system.")
    print("=" * 40)
    print("\n--- Live Log Output ---")

    # Start threads to read from each process's stdout
    threads = []
    for proc, name in processes:
        thread = threading.Thread(target=stream_reader, args=(proc.stdout, name))
        thread.daemon = True
        thread.start()
        threads.append(thread)

    try:
        # Keep the main thread alive to monitor processes
        while True:
            for proc, name in processes:
                if proc.poll() is not None:
                    print(f"\n[ERROR] [{name}] has terminated unexpectedly. Exiting system.")
                    # The atexit handler will take care of the rest.
                    sys.exit(1)
            time.sleep(1) # Main loop delay
    except KeyboardInterrupt:
        # The cleanup function will be called automatically by atexit
        pass
    except Exception as e:
        print(f"\nAn unexpected error occurred in the monitor loop: {e}")
    finally:
        sys.exit(0)


if __name__ == "__main__":
    main() 