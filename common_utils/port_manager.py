#!/usr/bin/env python3

# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Port Management Utilities

Provides utilities for checking port availability and managing port conflicts.
"""

import socket
import logging
from typing import List, Optional, Set

logger = logging.getLogger(__name__)

class PortManager:
    """Manages port allocation and conflict detection."""
    
    def __init__(self):
        self.reserved_ports: Set[int] = set()
    
    def is_port_available(self, port: int, host: str = "localhost") -> bool:
        """Check if a port is available for binding."""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(1)
                result = sock.connect_ex((host, port))
                return result != 0  # 0 means connection successful (port in use)
        except Exception as e:
            logger.warning(f"Error checking port {port}: {e}")
            return False
    
    def find_available_port(self, preferred_port: int, start_range: int = 10000, end_range: int = 11000) -> Optional[int]:
        """Find an available port, preferring the specified port."""
        # First try the preferred port
        if self.is_port_available(preferred_port):
            return preferred_port
        
        # If preferred port is not available, search in range
        logger.warning(f"Preferred port {preferred_port} not available, searching for alternatives...")
        
        for port in range(start_range, end_range):
            if port not in self.reserved_ports and self.is_port_available(port):
                logger.info(f"Found available port: {port}")
                return port
        
        return None
    
    def reserve_port(self, port: int) -> bool:
        """Reserve a port to prevent conflicts."""
        if self.is_port_available(port):
            self.reserved_ports.add(port)
            return True
        return False
    
    def release_port(self, port: int):
        """Release a reserved port."""
        self.reserved_ports.discard(port)
    
    def check_agent_ports(self, agent_ports: dict) -> dict:
        """Check availability of multiple agent ports."""
        results = {}
        
        for agent_name, port in agent_ports.items():
            available = self.is_port_available(port)
            results[agent_name] = {
                "port": port,
                "available": available,
                "status": "available" if available else "in_use"
            }
            
            if not available:
                logger.warning(f"Port {port} for {agent_name} is already in use")
        
        return results

# Global port manager instance
_port_manager = None

def get_port_manager() -> PortManager:
    """Get the global port manager instance."""
    global _port_manager
    if _port_manager is None:
        _port_manager = PortManager()
    return _port_manager

def check_agent_ports_available() -> dict:
    """Check if all standard agent ports are available."""
    standard_ports = {
        "data_loader": 10006,
        "data_analyst": 10007,
        "data_cleaning": 10008,
        "data_enrichment": 10009,
        "presentation": 10010,
        "rootcause_analyst": 10011,
        "schema_profiler": 10012
    }
    
    manager = get_port_manager()
    return manager.check_agent_ports(standard_ports) 