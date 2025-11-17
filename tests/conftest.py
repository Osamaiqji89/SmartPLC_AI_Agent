"""
Test Configuration for SmartPLC AI Agent
"""
import sys
import os
from pathlib import Path

import pytest

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Set environment variables for testing
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
os.environ.setdefault("OPENAI_API_KEY", "test-key-for-testing")


@pytest.fixture
def mock_plc():
    """Fixture for Mock PLC instance"""
    try:
        from core.plc.mock_plc import MockPLC
        plc = MockPLC(update_interval_ms=100)
        yield plc
        plc.stop()
    except Exception as e:
        pytest.skip(f"Mock PLC not available: {e}")


@pytest.fixture
def rag_engine():
    """Fixture for RAG engine"""
    try:
        from core.llm.rag_engine import RAGEngine
        import tempfile
        
        with tempfile.TemporaryDirectory() as tmpdir:
            engine = RAGEngine(
                persist_dir=tmpdir,
                collection_name="test_collection"
            )
            yield engine
    except Exception as e:
        pytest.skip(f"RAG engine not available: {e}")


@pytest.fixture
def test_database():
    """Fixture for test database"""
    try:
        import tempfile
        from core.data.database import Base, get_engine
        from sqlalchemy import create_engine
        
        # Create in-memory database
        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(engine)
        
        yield engine
        
        engine.dispose()
    except Exception as e:
        pytest.skip(f"Database not available: {e}")


@pytest.fixture
def sample_documents():
    """Sample documents for testing"""
    return [
        {
            "content": "AI_02_PressureSensor: Drucksensor Typ Endress+Hauser Cerabar. Messbereich 0-10 bar.",
            "metadata": {"source": "Test Manual", "category": "signals"}
        },
        {
            "content": "Fehlercode E4401: Kommunikationsfehler mit I/O-Modul 3. Prüfen Sie die Verkabelung.",
            "metadata": {"source": "Error DB", "category": "errors"}
        },
        {
            "content": "Tank-Füllanlage: Pumpe P1 fördert Wasser in Tank 1. Alarm bei 95% Füllstand.",
            "metadata": {"source": "Process Manual", "category": "processes"}
        }
    ]
