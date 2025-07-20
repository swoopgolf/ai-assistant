#!/usr/bin/env python3
"""
Agent Cleanup Script

This script safely removes all agents created from the template and cleans up
any injected configuration. It preserves the core framework components.

Usage:
    python scripts/cleanup_agents.py                    # Interactive cleanup
    python scripts/cleanup_agents.py --dry-run          # Preview what would be removed
    python scripts/cleanup_agents.py --force            # Skip confirmation
    python scripts/cleanup_agents.py --preserve "agent1,agent2"  # Keep specific agents
"""

import os
import sys
import shutil
import yaml
import argparse
import json
from pathlib import Path
from typing import List, Dict, Set
from datetime import datetime
import re

class AgentCleanup:
    """Handles cleanup of created agents and configuration."""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.config_path = project_root / "config" / "system_config.yaml"
        self.protected_agents = {
            "agent_template", 
            "orchestrator-agent", 
            "orchestrator_agent",
            "common_utils",
            "config",
            "docs", 
            "monitoring",
            "scripts",
            "tests"
        }
        
    def find_agent_directories(self) -> List[Path]:
        """Find all agent directories in the project."""
        agent_dirs = []
        
        for item in self.project_root.iterdir():
            if not item.is_dir():
                continue
                
            # Skip protected directories
            if item.name in self.protected_agents:
                continue
                
            # Skip hidden directories and common non-agent dirs
            if item.name.startswith('.') or item.name in ['__pycache__', 'node_modules', '.git']:
                continue
                
            # Check if it looks like an agent directory
            if self._is_agent_directory(item):
                agent_dirs.append(item)
                
        return sorted(agent_dirs)
    
    def _is_agent_directory(self, path: Path) -> bool:
        """Check if a directory appears to be an agent."""
        # Must have pyproject.toml
        if not (path / "pyproject.toml").exists():
            return False
            
        # Must have a Python package inside (agent code)
        python_packages = []
        for item in path.iterdir():
            if item.is_dir() and (item / "__init__.py").exists():
                python_packages.append(item.name)
        
        # Should have at least one package that looks like an agent
        for pkg in python_packages:
            if any(agent_file in os.listdir(path / pkg) 
                   for agent_file in ['agent_executor.py', 'tools.py', '__main__.py']):
                return True
                
        return False
    
    def find_config_entries(self) -> Dict[str, Dict]:
        """Find agent entries in system configuration."""
        if not self.config_path.exists():
            return {}
            
        try:
            with open(self.config_path, 'r') as f:
                config = yaml.safe_load(f)
                
            agents = config.get('agents', {})
            created_agents = {}
            
            for agent_name, agent_config in agents.items():
                # Skip protected agents
                if agent_name in self.protected_agents:
                    continue
                    
                # Skip orchestrator (it's core)
                if 'orchestrator' in agent_name.lower():
                    continue
                    
                # Skip template
                if 'template' in agent_name.lower():
                    continue
                    
                created_agents[agent_name] = agent_config
                
            return created_agents
            
        except Exception as e:
            print(f"⚠️  Warning: Could not read system config: {e}")
            return {}
    
    def find_test_files(self) -> List[Path]:
        """Find temporary test files that should be cleaned up."""
        test_files = []
        
        # Look for test config files
        for pattern in ['*test*.json', '*demo*.json', '*temp*.json']:
            test_files.extend(self.project_root.glob(pattern))
            
        # Look in scripts directory  
        scripts_dir = self.project_root / "scripts"
        if scripts_dir.exists():
            for pattern in ['*test*.json', '*demo*.json', '*temp*.json']:
                test_files.extend(scripts_dir.glob(pattern))
                
        return test_files
    
    def create_backup(self) -> Path:
        """Create backup of system configuration."""
        if not self.config_path.exists():
            return None
            
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = self.config_path.parent / f"system_config_backup_{timestamp}.yaml"
        
        shutil.copy2(self.config_path, backup_path)
        return backup_path
    
    def preview_cleanup(self, preserve_agents: Set[str] = None) -> Dict:
        """Preview what would be cleaned up."""
        preserve_agents = preserve_agents or set()
        
        agent_dirs = self.find_agent_directories()
        config_entries = self.find_config_entries()
        test_files = self.find_test_files()
        
        # Filter out preserved agents
        agent_dirs = [d for d in agent_dirs if d.name not in preserve_agents]
        config_entries = {k: v for k, v in config_entries.items() if k not in preserve_agents}
        
        cleanup_plan = {
            'agent_directories': agent_dirs,
            'config_entries': config_entries,
            'test_files': test_files,
            'total_agents': len(agent_dirs),
            'total_config_entries': len(config_entries),
            'total_test_files': len(test_files)
        }
        
        return cleanup_plan
    
    def perform_cleanup(self, cleanup_plan: Dict, dry_run: bool = False) -> Dict:
        """Perform the actual cleanup."""
        results = {
            'removed_directories': [],
            'removed_config_entries': [],
            'removed_test_files': [],
            'errors': [],
            'backup_created': None
        }
        
        if dry_run:
            print("🔍 DRY RUN - No actual changes will be made")
            return results
            
        # Create backup of config
        if cleanup_plan['config_entries']:
            try:
                backup_path = self.create_backup()
                results['backup_created'] = str(backup_path) if backup_path else None
                if backup_path:
                    print(f"📄 Created config backup: {backup_path}")
            except Exception as e:
                results['errors'].append(f"Failed to create backup: {e}")
                
        # Remove agent directories
        for agent_dir in cleanup_plan['agent_directories']:
            try:
                print(f"🗑️  Removing agent directory: {agent_dir}")
                shutil.rmtree(agent_dir)
                results['removed_directories'].append(str(agent_dir))
            except Exception as e:
                error_msg = f"Failed to remove {agent_dir}: {e}"
                results['errors'].append(error_msg)
                print(f"❌ {error_msg}")
                
        # Remove config entries
        if cleanup_plan['config_entries']:
            try:
                self._clean_system_config(cleanup_plan['config_entries'])
                results['removed_config_entries'] = list(cleanup_plan['config_entries'].keys())
            except Exception as e:
                error_msg = f"Failed to clean system config: {e}"
                results['errors'].append(error_msg)
                print(f"❌ {error_msg}")
                
        # Remove test files
        for test_file in cleanup_plan['test_files']:
            try:
                print(f"🗑️  Removing test file: {test_file}")
                test_file.unlink()
                results['removed_test_files'].append(str(test_file))
            except Exception as e:
                error_msg = f"Failed to remove {test_file}: {e}"
                results['errors'].append(error_msg)
                print(f"❌ {error_msg}")
                
        return results
    
    def _clean_system_config(self, entries_to_remove: Dict) -> None:
        """Remove agent entries from system configuration."""
        if not self.config_path.exists():
            return
            
        with open(self.config_path, 'r') as f:
            config = yaml.safe_load(f)
            
        agents = config.get('agents', {})
        
        for agent_name in entries_to_remove.keys():
            if agent_name in agents:
                print(f"🗑️  Removing config entry: {agent_name}")
                del agents[agent_name]
                
        config['agents'] = agents
        
        with open(self.config_path, 'w') as f:
            yaml.dump(config, f, default_flow_style=False, indent=2)
    
    def print_cleanup_preview(self, cleanup_plan: Dict) -> None:
        """Print a detailed preview of what will be cleaned up."""
        print("🧹 Agent Cleanup Preview")
        print("=" * 50)
        
        if cleanup_plan['agent_directories']:
            print(f"\n📁 Agent Directories to Remove ({cleanup_plan['total_agents']}):")
            for agent_dir in cleanup_plan['agent_directories']:
                print(f"   - {agent_dir}")
                
        if cleanup_plan['config_entries']:
            print(f"\n⚙️  Configuration Entries to Remove ({cleanup_plan['total_config_entries']}):")
            for agent_name, config in cleanup_plan['config_entries'].items():
                port = config.get('port', 'N/A')
                desc = config.get('description', 'No description')[:50]
                print(f"   - {agent_name} (port {port}): {desc}...")
                
        if cleanup_plan['test_files']:
            print(f"\n🧪 Test Files to Remove ({cleanup_plan['total_test_files']}):")
            for test_file in cleanup_plan['test_files']:
                print(f"   - {test_file}")
                
        if not any([cleanup_plan['agent_directories'], 
                   cleanup_plan['config_entries'], 
                   cleanup_plan['test_files']]):
            print("\n✅ No cleanup needed - system is already clean!")
            
        print(f"\n📊 Summary:")
        print(f"   - {cleanup_plan['total_agents']} agent directories")
        print(f"   - {cleanup_plan['total_config_entries']} config entries") 
        print(f"   - {cleanup_plan['total_test_files']} test files")
        
    def print_cleanup_results(self, results: Dict) -> None:
        """Print the results of the cleanup operation."""
        print("\n🎯 Cleanup Results")
        print("=" * 50)
        
        if results['removed_directories']:
            print(f"\n✅ Removed {len(results['removed_directories'])} agent directories:")
            for directory in results['removed_directories']:
                print(f"   - {directory}")
                
        if results['removed_config_entries']:
            print(f"\n✅ Removed {len(results['removed_config_entries'])} config entries:")
            for entry in results['removed_config_entries']:
                print(f"   - {entry}")
                
        if results['removed_test_files']:
            print(f"\n✅ Removed {len(results['removed_test_files'])} test files:")
            for test_file in results['removed_test_files']:
                print(f"   - {test_file}")
                
        if results['backup_created']:
            print(f"\n💾 Configuration backup created: {results['backup_created']}")
            
        if results['errors']:
            print(f"\n❌ Errors encountered ({len(results['errors'])}):")
            for error in results['errors']:
                print(f"   - {error}")
                
        total_removed = (len(results['removed_directories']) + 
                        len(results['removed_config_entries']) + 
                        len(results['removed_test_files']))
        
        if total_removed == 0 and not results['errors']:
            print("\n✨ System was already clean!")
        elif results['errors']:
            print(f"\n⚠️  Cleanup completed with {len(results['errors'])} errors")
        else:
            print(f"\n🎉 Successfully cleaned up {total_removed} items!")


def get_user_confirmation(message: str) -> bool:
    """Get user confirmation for cleanup."""
    while True:
        response = input(f"\n{message} (y/N): ").strip().lower()
        if response in ['y', 'yes']:
            return True
        elif response in ['n', 'no', '']:
            return False
        else:
            print("Please enter 'y' for yes or 'n' for no.")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Clean up created agents and configuration')
    parser.add_argument('--dry-run', action='store_true', help='Preview cleanup without making changes')
    parser.add_argument('--force', action='store_true', help='Skip confirmation prompts')
    parser.add_argument('--preserve', type=str, help='Comma-separated list of agents to preserve')
    parser.add_argument('--config-only', action='store_true', help='Only clean configuration, not directories')
    parser.add_argument('--dirs-only', action='store_true', help='Only clean directories, not configuration')
    
    args = parser.parse_args()
    
    # Find project root
    current_dir = Path(__file__).resolve().parent
    project_root = current_dir.parent
    
    cleanup = AgentCleanup(project_root)
    
    # Parse preserve list
    preserve_agents = set()
    if args.preserve:
        preserve_agents = set(agent.strip() for agent in args.preserve.split(','))
        print(f"🔒 Preserving agents: {', '.join(preserve_agents)}")
    
    # Get cleanup plan
    cleanup_plan = cleanup.preview_cleanup(preserve_agents)
    
    # Apply filters if specified
    if args.config_only:
        cleanup_plan['agent_directories'] = []
        cleanup_plan['test_files'] = []
        
    if args.dirs_only:
        cleanup_plan['config_entries'] = {}
        
    # Show preview
    cleanup.print_cleanup_preview(cleanup_plan)
    
    # Check if there's anything to clean
    total_items = (cleanup_plan['total_agents'] + 
                  cleanup_plan['total_config_entries'] + 
                  cleanup_plan['total_test_files'])
    
    if total_items == 0:
        print("\n✅ System is already clean!")
        return
    
    # Get confirmation unless forced or dry run
    if not args.dry_run and not args.force:
        if not get_user_confirmation("Proceed with cleanup?"):
            print("🚫 Cleanup cancelled by user")
            return
    
    # Perform cleanup
    results = cleanup.perform_cleanup(cleanup_plan, dry_run=args.dry_run)
    
    # Show results
    cleanup.print_cleanup_results(results)
    
    if args.dry_run:
        print("\n💡 Run without --dry-run to perform actual cleanup")
    elif results['errors']:
        sys.exit(1)  # Exit with error code if there were errors


if __name__ == "__main__":
    main() 