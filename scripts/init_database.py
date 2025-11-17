"""
Database Setup Script
Creates database, initializes schema, and populates with default data
Run this script before first start of the application
"""
from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "config"))

from loguru import logger
from core.data.database import init_database, get_session, Project, Signal, Parameter


def setup_database():
    """Complete database setup"""
    logger.info("=" * 80)
    logger.info("SmartPLC AI Agent - Database Setup")
    logger.info("=" * 80)
    
    # Step 1: Create database schema
    logger.info("\n[1/4] Creating database schema...")
    try:
        init_database()
        logger.success("✓ Database schema created")
    except Exception as e:
        logger.error(f"✗ Failed to create database schema: {e}")
        return False
    
    # Step 2: Initialize signals
    logger.info("\n[2/4] Initializing PLC signals...")
    try:
        from init_signals import init_signals
        init_signals()
        logger.success("✓ Signals initialized")
    except Exception as e:
        logger.error(f"✗ Failed to initialize signals: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False
    
    # Step 3: Initialize parameters
    logger.info("\n[3/4] Initializing default parameters...")
    try:
        from init_parameters import init_parameters
        init_parameters()
        logger.success("✓ Parameters initialized")
    except Exception as e:
        logger.error(f"✗ Failed to initialize parameters: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False
    
    # Step 4: Initialize knowledge base (RAG)
    logger.info("\n[4/4] Initializing knowledge base (RAG)...")
    try:
        from init_knowledge_base import load_knowledge_base
        load_knowledge_base()
        logger.success("✓ Knowledge base initialized")
    except Exception as e:
        logger.warning(f"⚠ Knowledge base initialization failed (optional): {e}")
        logger.info("  → You can initialize it later with: python scripts/init_knowledge_base.py")
    
    # Verify database
    logger.info("\n" + "=" * 80)
    logger.info("Database Setup Complete - Verification:")
    logger.info("=" * 80)
    
    try:
        session = get_session()
        
        # Count projects
        project_count = session.query(Project).count()
        logger.info(f"  Projects:   {project_count}")
        
        # Count signals
        signal_count = session.query(Signal).count()
        logger.info(f"  Signals:    {signal_count}")
        
        # Count parameters
        param_count = session.query(Parameter).count()
        logger.info(f"  Parameters: {param_count}")
        
        # Show active project
        active_project = session.query(Project).filter_by(is_active=True).first()
        if active_project:
            logger.info(f"\n  Active Project: '{active_project.name}'")
            logger.info(f"  Description:    {active_project.description}")
        
        session.close()
        
        logger.info("\n" + "=" * 80)
        logger.success("✓ Database setup successful!")
        logger.info("=" * 80)
        logger.info("\nYou can now start the application:")
        logger.info("  → python main.py")
        logger.info("  → or use: start.bat")
        logger.info("\n")
        
        return True
        
    except Exception as e:
        logger.error(f"✗ Database verification failed: {e}")
        return False


if __name__ == "__main__":
    success = setup_database()
    sys.exit(0 if success else 1)
