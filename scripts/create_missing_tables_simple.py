"""
Simple script to create missing database tables using psycopg2 directly.
"""

import psycopg2
from pathlib import Path

def create_missing_tables():
    """Create missing database tables by executing the SQL script."""
    
    # Database connection parameters
    conn_params = {
        'host': '127.0.0.1',
        'port': 5432,
        'database': 'byrdi',
        'user': 'postgres',
        'password': 'Byrdi123!'
    }
    
    # Read the SQL file
    sql_file_path = Path(__file__).parent / "create_missing_tables.sql"
    
    if not sql_file_path.exists():
        print(f"SQL file not found: {sql_file_path}")
        return False
    
    with open(sql_file_path, 'r') as f:
        sql_content = f.read()
    
    try:
        print("Connecting to database...")
        conn = psycopg2.connect(**conn_params)
        cursor = conn.cursor()
        
        print("Creating missing database tables...")
        
        # Split by semicolon and execute each statement
        statements = [stmt.strip() for stmt in sql_content.split(';') if stmt.strip()]
        
        for i, statement in enumerate(statements, 1):
            if statement:
                print(f"Executing statement {i}/{len(statements)}")
                cursor.execute(statement)
        
        conn.commit()
        print("✅ All tables created successfully!")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        return False

if __name__ == "__main__":
    success = create_missing_tables()
    exit(0 if success else 1) 