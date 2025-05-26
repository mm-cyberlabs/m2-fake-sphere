"""
Database Connection Manager
This module handles PostgreSQL database connections using connection pooling.
"""

import psycopg2
from psycopg2 import pool
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


class DatabaseConnectionManager:
    """
    Manages PostgreSQL database connections with connection pooling support.
    """

    def __init__(self, connection_parameters: Dict[str, Any]):
        """
        Initialize the database connection manager.

        Args:
            connection_parameters: Dictionary containing database connection parameters
                - host: Database host address
                - port: Database port number
                - database: Database name
                - user: Database username
                - password: Database password
        """
        self.connection_parameters = connection_parameters
        self.connection_pool: Optional[psycopg2.pool.SimpleConnectionPool] = None
        self._initialize_connection_pool()

    def _initialize_connection_pool(self) -> None:
        """
        Initialize the connection pool with the provided parameters.

        Raises:
            psycopg2.Error: If connection pool creation fails
        """
        try:
            self.connection_pool = psycopg2.pool.SimpleConnectionPool(
                minconn=1,
                maxconn=5,
                host=self.connection_parameters['host'],
                port=self.connection_parameters['port'],
                database=self.connection_parameters['database'],
                user=self.connection_parameters['user'],
                password=self.connection_parameters['password']
            )
            logger.info("Database connection pool initialized successfully")
        except psycopg2.Error as error:
            logger.error(f"Failed to initialize connection pool: {error}")
            raise

    def get_connection(self) -> psycopg2.extensions.connection:
        """
        Get a connection from the pool.

        Returns:
            A database connection object

        Raises:
            psycopg2.Error: If getting connection fails
        """
        if not self.connection_pool:
            raise psycopg2.Error("Connection pool not initialized")

        return self.connection_pool.getconn()

    def release_connection(self, connection: psycopg2.extensions.connection) -> None:
        """
        Release a connection back to the pool.

        Args:
            connection: The connection to release
        """
        if self.connection_pool and connection:
            self.connection_pool.putconn(connection)

    def close_all_connections(self) -> None:
        """
        Close all connections in the pool.
        """
        if self.connection_pool:
            self.connection_pool.closeall()
            logger.info("All database connections closed")