"""
Database connection utility that reads configuration from environment.env
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
        print(f"✅ Loaded environment from {env_path}")
    else:
        print(f"❌ Environment file not found: {env_path}")
        return False
    return True

def get_db_config():
    """Get database configuration from environment variables"""
    return {
        'host': os.getenv('DB_HOST', '127.0.0.1'),
        'port': int(os.getenv('DB_PORT', '5433')),
        'database': os.getenv('DB_NAME', 'byrdi'),
        'user': os.getenv('DB_USER', 'postgres'),
        'password': os.getenv('DB_PASSWORD', 'postgres')
    }

def test_connection():
    """Test database connection"""
    if not load_environment():
        return False
    
    config = get_db_config()
    
    try:
        print("Attempting to connect to database...")
        print(f"Host: {config['host']}:{config['port']}")
        print(f"Database: {config['database']}")
        print(f"User: {config['user']}")
        
        conn = psycopg2.connect(**config)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Test query
        cursor.execute("SELECT version();")
        result = cursor.fetchone()
        
        print("✅ Database connection successful!")
        print(f"PostgreSQL version: {result['version']}")
        
        # Test if our tables exist
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name IN ('items', 'categories', 'orders', 'order_items', 'users', 'menus');
        """)
        tables = cursor.fetchall()
        
        print(f"\n📊 Found {len(tables)} core tables:")
        for table in tables:
            print(f"  - {table['table_name']}")
        
        # Check for missing tables that we need to create
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name IN ('price_history', 'import_log', 'promotional_pricing');
        """)
        new_tables = cursor.fetchall()
        
        print(f"\n🔧 Found {len(new_tables)} additional tables:")
        for table in new_tables:
            print(f"  - {table['table_name']}")
        
        missing_tables = set(['price_history', 'import_log', 'promotional_pricing']) - set([t['table_name'] for t in new_tables])
        if missing_tables:
            print(f"\n⚠️  Missing tables: {', '.join(missing_tables)}")
            print("Run create_missing_tables.sql to create them.")
        else:
            print(f"\n✅ All required tables are present!")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def create_missing_tables():
    """Create missing database tables"""
    if not load_environment():
        return False
    
    config = get_db_config()
    sql_file_path = Path(__file__).parent / "create_missing_tables.sql"
    
    if not sql_file_path.exists():
        print(f"❌ SQL file not found: {sql_file_path}")
        return False
    
    try:
        conn = psycopg2.connect(**config)
        cursor = conn.cursor()
        
        print("📊 Creating missing database tables...")
        
        with open(sql_file_path, 'r') as f:
            sql_content = f.read()
        
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
    print("🔌 Database Connection Test")
    print("=" * 40)
    
    if test_connection():
        # Check if we need to create tables
        config = get_db_config()
        conn = psycopg2.connect(**config)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name IN ('price_history', 'import_log', 'promotional_pricing');
        """)
        existing_tables = cursor.fetchall()
        cursor.close()
        conn.close()
        
        missing_tables = set(['price_history', 'import_log', 'promotional_pricing']) - set([t['table_name'] for t in existing_tables])
        
        if missing_tables:
            print(f"\n🛠️  Missing tables: {', '.join(missing_tables)}")
            print("Do you want to create missing tables? (y/n)")
            response = input().lower().strip()
            if response in ['y', 'yes']:
                create_missing_tables()
        else:
            print("\n✅ All tables are present. No action needed.")
    else:
        print("\n💡 Tips:")
        print("1. Make sure PostgreSQL is running")
        print("2. Check the database credentials in config/environment.env")
        print("3. Verify the database exists") 