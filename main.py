"""
SmartPLC AI Agent
Entry Point
"""
import sys
from pathlib import Path

from loguru import logger
from PySide6.QtWidgets import QApplication

# Add config to Python path
sys.path.insert(0, str(Path(__file__).parent / "config"))

from core.data.database import init_database
from gui.views.main_window import MainWindow


def setup_logging():
    """Configure logging with loguru"""
    log_dir = Path("data/logs")
    log_dir.mkdir(parents=True, exist_ok=True)
    
    logger.add(
        "data/logs/plc_studio_{time}.log",
        rotation="100 MB",
        retention="30 days",
        level="INFO",
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>"
    )
    logger.info("SmartPLC AI Agent starting...")


def main():
    """Main application entry point"""
    setup_logging()
    
    # Initialize database
    logger.info("Initializing database...")
    init_database()
    
    # Pre-warm AI components in background (optional but faster)
    logger.info("Pre-loading AI components...")
    try:
        # This will load models in background while GUI starts
        from threading import Thread
        def preload_ai():
            try:
                from core.llm.rag_engine import get_rag_engine
                from core.llm.openai_client import get_openai_client
                logger.debug("Pre-loading RAG engine...")
                get_rag_engine()  # Loads sentence-transformers
                logger.debug("Pre-loading OpenAI client...")
                # OpenAI client will be created on first use (needs API key check)
            except Exception as e:
                logger.debug(f"Pre-load skipped: {e}")
        
        Thread(target=preload_ai, daemon=True).start()
    except Exception as e:
        logger.warning(f"Could not pre-load AI: {e}")
    
    # Create Qt Application
    app = QApplication(sys.argv)
    app.setApplicationName("SmartPLC AI Agent")
    app.setOrganizationName("SmartPLC")
    
    # Load default theme
    from gui.core.theme_manager import get_theme_manager
    theme_manager = get_theme_manager()
    theme_manager.load_theme("light")  # Start with light theme
    
    # Create and show main window
    logger.info("Creating main window...")
    window = MainWindow()
    window.show()
    
    logger.info("Application ready")
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
