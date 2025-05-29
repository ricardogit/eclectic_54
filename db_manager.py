#!/usr/bin/env python
"""
PostgreSQL Database Schema Creator/Updater

This script creates or updates a PostgreSQL database schema based on SQLAlchemy models.
It can be used to initialize a new database or update an existing one.
"""

import os
import sys
import argparse
import logging
from configparser import ConfigParser
from sqlalchemy import create_engine, inspect
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Import your models
from models import db, User, Document, DocumentSection, DocumentCollaborator, SectionLock, SectionRevision, \
    CollaborationSession, Paper, Citation, Keyword, Collection, SearchQuery, AIProvider, ScientificDatabase

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger('db_manager')


def load_config(config_path):
    """
    Load database configuration from a .ini file

    Args:
        config_path: Path to config file

    Returns:
        Dictionary with database connection parameters
    """
    if not os.path.exists(config_path):
        logger.error(f"Config file not found: {config_path}")
        sys.exit(1)

    parser = ConfigParser()
    parser.read(config_path)

    # Get the PostgreSQL connection details
    if 'postgresql' not in parser.sections():
        logger.error("PostgreSQL configuration section not found in config file")
        sys.exit(1)

    db_config = {}
    params = ['host', 'port', 'database', 'user', 'password']

    for param in params:
        if param in parser['postgresql']:
            db_config[param] = parser['postgresql'][param]
        else:
            logger.warning(f"Parameter {param} not found in config, using default if available")

    return db_config


def get_connection_string(db_config):
    """
    Create a PostgreSQL connection string from config

    Args:
        db_config: Dictionary with connection parameters

    Returns:
        SQLAlchemy connection string
    """
    # Build connection string
    user = db_config.get('user', 'postgres')
    password = db_config.get('password', '')
    host = db_config.get('host', 'localhost')
    port = db_config.get('port', '5432')
    database = db_config.get('database', 'dasheditor')

    # Create connection string with password if provided
    if password:
        connection_string = f"postgresql://{user}:{password}@{host}:{port}/{database}"
    else:
        connection_string = f"postgresql://{user}@{host}:{port}/{database}"

    return connection_string


def check_database_exists(engine, database_name):
    """
    Check if the specified database exists

    Args:
        engine: SQLAlchemy engine connected to PostgreSQL
        database_name: Name of the database to check

    Returns:
        Boolean indicating if database exists
    """
    with engine.connect() as conn:
        result = conn.execute(f"SELECT 1 FROM pg_database WHERE datname = '{database_name}'")
        return result.scalar() is not None


def create_database(engine, database_name):
    """
    Create a new PostgreSQL database

    Args:
        engine: SQLAlchemy engine connected to PostgreSQL
        database_name: Name of the database to create
    """
    # Connect to the default 'postgres' database to create a new DB
    with engine.connect() as conn:
        # Disconnect all users from the database if it exists
        conn.execute("COMMIT")
        conn.execute(f"""
        DO $$
        BEGIN
            IF EXISTS (SELECT 1 FROM pg_database WHERE datname = '{database_name}') THEN
                EXECUTE format('REVOKE CONNECT ON DATABASE {database_name} FROM public');

                -- Close all connections to the database
                EXECUTE format('
                    SELECT pg_terminate_backend(pid) 
                    FROM pg_stat_activity 
                    WHERE datname = ''%s'' AND pid <> pg_backend_pid()',
                    '{database_name}');
            END IF;
        END
        $$;
        """)

        # Create the database with UTF-8 encoding
        conn.execute("COMMIT")
        conn.execute(f"DROP DATABASE IF EXISTS {database_name}")
        conn.execute("COMMIT")
        conn.execute(f"CREATE DATABASE {database_name} WITH ENCODING 'UTF8'")
        logger.info(f"Created database: {database_name}")


def initialize_database(connection_string, drop_first=False):
    """
    Initialize the database schema

    Args:
        connection_string: PostgreSQL connection string
        drop_first: If True, drop all tables before creating
    """
    # Create SQLAlchemy engine
    engine = create_engine(connection_string)

    if drop_first:
        logger.warning("Dropping all existing tables...")
        db.Model.metadata.drop_all(engine)
        logger.info("All tables dropped successfully")

    # Create all tables
    try:
        db.Model.metadata.create_all(engine)
        logger.info("Database schema created successfully")
    except Exception as e:
        logger.error(f"Error creating schema: {str(e)}")
        sys.exit(1)


def validate_models(connection_string):
    """
    Validate the database schema against the models

    Args:
        connection_string: PostgreSQL connection string

    Returns:
        Dictionary with missing tables and columns
    """
    # Create SQLAlchemy engine
    engine = create_engine(connection_string)
    inspector = inspect(engine)

    # Get existing tables
    existing_tables = inspector.get_table_names()
    model_tables = db.Model.metadata.tables.keys()

    # Find missing tables
    missing_tables = [table for table in model_tables if table not in existing_tables]

    # Check for missing columns in existing tables
    missing_columns = {}
    for table_name in model_tables:
        if table_name in existing_tables:
            # Get columns from model
            model_columns = {c.name: c for c in db.Model.metadata.tables[table_name].columns}
            # Get existing columns from database
            existing_columns = {c["name"]: c for c in inspector.get_columns(table_name)}

            # Find missing columns
            table_missing_columns = [col for col in model_columns if col not in existing_columns]
            if table_missing_columns:
                missing_columns[table_name] = table_missing_columns

    return {
        "missing_tables": missing_tables,
        "missing_columns": missing_columns
    }


def update_database(connection_string):
    """
    Update existing database schema to match models

    Args:
        connection_string: PostgreSQL connection string
    """
    # Create SQLAlchemy engine
    engine = create_engine(connection_string)

    # Validate models against existing schema
    validation = validate_models(connection_string)

    if not validation["missing_tables"] and not validation["missing_columns"]:
        logger.info("Database schema is already up to date")
        return

    # Create missing tables
    if validation["missing_tables"]:
        logger.info(f"Creating {len(validation['missing_tables'])} missing tables...")
        for table_name in validation["missing_tables"]:
            # Create the table
            table = db.Model.metadata.tables[table_name]
            table.create(engine)
            logger.info(f"Created table: {table_name}")

    # Add missing columns
    # Note: This is a simplified approach. Production systems should use Alembic for migrations.
    if validation["missing_columns"]:
        logger.info(f"Adding missing columns to {len(validation['missing_columns'])} tables...")
        with engine.connect() as conn:
            for table_name, columns in validation["missing_columns"].items():
                logger.info(f"Updating table '{table_name}' with {len(columns)} new columns")
                table = db.Model.metadata.tables[table_name]

                for column_name in columns:
                    column = table.columns[column_name]
                    column_type = column.type.compile(engine.dialect)
                    nullable = "NULL" if column.nullable else "NOT NULL"
                    default = f"DEFAULT {column.default.arg}" if column.default is not None else ""

                    # Build and execute ALTER TABLE statement
                    alter_stmt = f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type} {nullable} {default}"
                    conn.execute(alter_stmt)
                    logger.info(f"Added column: {table_name}.{column_name}")


def main():
    """Main function to handle command-line arguments and execute operations"""
    parser = argparse.ArgumentParser(description='PostgreSQL Database Schema Manager')

    parser.add_argument('--config', '-c', type=str, default='database.ini',
                        help='Path to database configuration file')
    parser.add_argument('--action', '-a', type=str, choices=['create', 'update', 'validate'],
                        default='update', help='Action to perform')
    parser.add_argument('--drop-tables', action='store_true',
                        help='Drop all tables before creating (use with caution!)')
    parser.add_argument('--create-db', action='store_true',
                        help='Create the database if it does not exist')

    args = parser.parse_args()

    # Load configuration
    db_config = load_config(args.config)

    # If requested, check and create the database
    if args.create_db:
        # Connect to default postgres database
        db_name = db_config['database']
        db_config['database'] = 'postgres'  # Use default postgres database
        admin_conn_string = get_connection_string(db_config)

        engine = create_engine(admin_conn_string)
        if not check_database_exists(engine, db_name):
            create_database(engine, db_name)
        else:
            logger.info(f"Database {db_name} already exists")

        # Reset database name for subsequent operations
        db_config['database'] = db_name

    # Get connection string for the target database
    connection_string = get_connection_string(db_config)

    # Perform the requested action
    if args.action == 'create':
        initialize_database(connection_string, args.drop_tables)
    elif args.action == 'update':
        update_database(connection_string)
    elif args.action == 'validate':
        validation = validate_models(connection_string)
        if not validation["missing_tables"] and not validation["missing_columns"]:
            logger.info("Database schema is valid - matches models")
        else:
            if validation["missing_tables"]:
                logger.warning(f"Missing tables: {', '.join(validation['missing_tables'])}")
            if validation["missing_columns"]:
                for table, columns in validation["missing_columns"].items():
                    logger.warning(f"Table '{table}' missing columns: {', '.join(columns)}")
            logger.info("Run with --action=update to apply changes")


if __name__ == "__main__":
    main()
