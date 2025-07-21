"""
Script to check the structure of existing database tables
"""

import os
import psycopg2
from psycopg2.extras import RealDictCursor
from pathlib import Path
from dotenv import load_dotenv

def load_environment():
    """Load environment variables from config/environment.env"""
    env_path = Path(__file__).parent.parent / "config" / "environment.env"
    if env_path.exists():
        load_dotenv(env_path)
        return True
    return False

def get_db_config():
    """Get database configuration from environment variables"""
    return {
        'host': os.getenv('DB_HOST', '127.0.0.1'),
        'port': int(os.getenv('DB_PORT', '5432')),
        'database': os.getenv('DB_NAME', 'byrdi'),
        'user': os.getenv('DB_USER', 'postgres'),
        'password': os.getenv('DB_PASSWORD', 'postgres')
    }

def check_table_structure():
    """Check the structure of existing tables"""
    if not load_environment():
        return False
    
    config = get_db_config()
    
    try:
        conn = psycopg2.connect(**config)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Get all tables
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            ORDER BY table_name;
        """)
        tables = cursor.fetchall()
        
        print("📊 Database Table Structures")
        print("=" * 50)
        
        for table in tables:
            table_name = table['table_name']
            print(f"\n🗂️  Table: {table_name}")
            
            # Get columns for this table
            cursor.execute("""
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns 
                WHERE table_name = %s 
                AND table_schema = 'public'
                ORDER BY ordinal_position;
            """, (table_name,))
            
            columns = cursor.fetchall()
            
            if columns:
                print("   Columns:")
                for col in columns:
                    nullable = "NULL" if col['is_nullable'] == 'YES' else "NOT NULL"
                    default = f" DEFAULT {col['column_default']}" if col['column_default'] else ""
                    print(f"     - {col['column_name']}: {col['data_type']} {nullable}{default}")
            else:
                print("     No columns found")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error checking table structure: {e}")
        return False

if __name__ == "__main__":
    check_table_structure() 