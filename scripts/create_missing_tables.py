"""
Script to create missing database tables for the club management system.
"""

import sys
import os
from pathlib import Path

# Add the parent directory to sys.path to make common_utils accessible
parent_dir = Path(__file__).parent.parent
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))

from common_utils.database import get_database_manager

def create_missing_tables():
    """Create missing database tables by executing the SQL script."""
    db_manager = get_database_manager()
    
    # Read the SQL file
    sql_file_path = Path(__file__).parent / "create_missing_tables.sql"
    
    if not sql_file_path.exists():
        print(f"SQL file not found: {sql_file_path}")
        return False
    
    with open(sql_file_path, 'r') as f:
        sql_content = f.read()
    
    # Split by semicolon to execute individual statements
    statements = [stmt.strip() for stmt in sql_content.split(';') if stmt.strip()]
    
    try:
        print("Creating missing database tables...")
        
        for i, statement in enumerate(statements, 1):
            if statement:
                print(f"Executing statement {i}/{len(statements)}")
                db_manager.execute_non_query(statement)
        
        print("✅ All tables created successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        return False

if __name__ == "__main__":
    success = create_missing_tables()
    sys.exit(0 if success else 1) 