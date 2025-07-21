"""
Database connectivity utilities for club management agents.

Provides PostgreSQL connection management, query execution, and transaction handling
with proper error handling, connection pooling, and security measures.
"""

import os
import logging
import asyncpg
import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2.pool import ThreadedConnectionPool
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass
import json
from datetime import datetime, date
import decimal

logger = logging.getLogger(__name__)

@dataclass
class DatabaseConfig:
    """Database configuration parameters."""
    host: str
    port: int
    database: str
    username: str
    password: str
    pool_size: int = 5
    max_overflow: int = 10
    
    @classmethod
    def from_env(cls) -> 'DatabaseConfig':
        """Create database config from environment variables."""
        return cls(
            host=os.getenv('DB_HOST', '127.0.0.1'),
            port=int(os.getenv('DB_PORT', '5432')),
            database=os.getenv('DB_NAME', 'byrdi'),
            username=os.getenv('DB_USER', 'postgres'),
            password=os.getenv('DB_PASSWORD', 'Byrdi123!'),
            pool_size=int(os.getenv('DB_POOL_SIZE', '5')),
            max_overflow=int(os.getenv('DB_MAX_OVERFLOW', '10'))
        )
    
    @property
    def connection_string(self) -> str:
        """Get SQLAlchemy connection string."""
        return f"postgresql://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"

class DatabaseManager:
    """Manages database connections and operations."""
    
    def __init__(self, config: Optional[DatabaseConfig] = None):
        self.config = config or DatabaseConfig.from_env()
        self._engine = None
        self._session_maker = None
        self._connection_pool = None
        
    def initialize(self):
        """Initialize database connections and pools."""
        try:
            # SQLAlchemy engine for ORM operations
            self._engine = create_engine(
                self.config.connection_string,
                pool_size=self.config.pool_size,
                max_overflow=self.config.max_overflow,
                pool_pre_ping=True,
                echo=os.getenv('DB_ECHO', 'false').lower() == 'true'
            )
            
            self._session_maker = sessionmaker(bind=self._engine)
            
            # psycopg2 connection pool for raw SQL operations
            self._connection_pool = ThreadedConnectionPool(
                minconn=1,
                maxconn=self.config.pool_size,
                host=self.config.host,
                port=self.config.port,
                database=self.config.database,
                user=self.config.username,
                password=self.config.password,
                cursor_factory=RealDictCursor
            )
            
            logger.info("Database connections initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise
    
    @contextmanager
    def get_connection(self):
        """Get a database connection from the pool."""
        if not self._connection_pool:
            self.initialize()
            
        conn = None
        try:
            conn = self._connection_pool.getconn()
            yield conn
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"Database operation failed: {e}")
            raise
        finally:
            if conn:
                self._connection_pool.putconn(conn)
    
    @contextmanager 
    def get_session(self):
        """Get a SQLAlchemy session."""
        if not self._session_maker:
            self.initialize()
            
        session = self._session_maker()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Session operation failed: {e}")
            raise
        finally:
            session.close()
    
    def execute_query(self, query: str, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Execute a SELECT query and return results."""
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, params or {})
                results = cursor.fetchall()
                return [dict(row) for row in results]
    
    def execute_non_query(self, query: str, params: Optional[Dict[str, Any]] = None) -> int:
        """Execute INSERT, UPDATE, DELETE and return affected rows."""
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, params or {})
                conn.commit()
                return cursor.rowcount
    
    def execute_transaction(self, queries: List[tuple]) -> bool:
        """Execute multiple queries in a transaction."""
        with self.get_connection() as conn:
            try:
                with conn.cursor() as cursor:
                    for query, params in queries:
                        cursor.execute(query, params or {})
                conn.commit()
                return True
            except Exception as e:
                conn.rollback()
                logger.error(f"Transaction failed: {e}")
                raise
    
    def test_connection(self) -> bool:
        """Test database connectivity."""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT 1")
                    result = cursor.fetchone()
                    return result[0] == 1
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False

class QueryBuilder:
    """Helper class for building safe SQL queries."""
    
    @staticmethod
    def safe_where_clause(filters: Dict[str, Any]) -> tuple[str, Dict[str, Any]]:
        """Build a safe WHERE clause from filters."""
        if not filters:
            return "", {}
        
        conditions = []
        params = {}
        
        for key, value in filters.items():
            # Sanitize column names (allow only alphanumeric and underscore)
            if not key.replace('_', '').isalnum():
                raise ValueError(f"Invalid column name: {key}")
            
            param_key = f"param_{len(params)}"
            conditions.append(f"{key} = %({param_key})s")
            params[param_key] = value
        
        where_clause = " WHERE " + " AND ".join(conditions)
        return where_clause, params
    
    @staticmethod
    def safe_order_clause(order_by: Optional[str], order_dir: str = "ASC") -> str:
        """Build a safe ORDER BY clause."""
        if not order_by:
            return ""
        
        # Sanitize column name
        if not order_by.replace('_', '').isalnum():
            raise ValueError(f"Invalid column name: {order_by}")
        
        # Validate direction
        order_dir = order_dir.upper()
        if order_dir not in ["ASC", "DESC"]:
            order_dir = "ASC"
        
        return f" ORDER BY {order_by} {order_dir}"
    
    @staticmethod
    def safe_limit_clause(limit: Optional[int], offset: Optional[int] = None) -> tuple[str, Dict[str, Any]]:
        """Build a safe LIMIT/OFFSET clause."""
        clause = ""
        params = {}
        
        if limit is not None:
            if not isinstance(limit, int) or limit < 0:
                raise ValueError("Limit must be a non-negative integer")
            clause += " LIMIT %(limit)s"
            params["limit"] = limit
        
        if offset is not None:
            if not isinstance(offset, int) or offset < 0:
                raise ValueError("Offset must be a non-negative integer")
            clause += " OFFSET %(offset)s"
            params["offset"] = offset
        
        return clause, params

class DateTimeEncoder(json.JSONEncoder):
    """JSON encoder for datetime and decimal objects."""
    
    def default(self, obj):
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        elif isinstance(obj, decimal.Decimal):
            return float(obj)
        return super().default(obj)

# Global database manager instance
db_manager = DatabaseManager()

def get_database_manager() -> DatabaseManager:
    """Get the global database manager instance."""
    return db_manager

def init_database():
    """Initialize the global database manager."""
    db_manager.initialize()

# Convenience functions for common operations
def execute_query(query: str, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    """Execute a query using the global database manager."""
    return db_manager.execute_query(query, params)

def execute_non_query(query: str, params: Optional[Dict[str, Any]] = None) -> int:
    """Execute a non-query using the global database manager."""
    return db_manager.execute_non_query(query, params)

def test_connection() -> bool:
    """Test database connection using the global database manager."""
    return db_manager.test_connection() 