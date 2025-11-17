"""
Database Models
SQLAlchemy ORM models for PLC data persistence
"""

from datetime import datetime
from enum import Enum
from typing import Optional

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    create_engine,
)
from sqlalchemy.orm import DeclarativeBase, relationship, sessionmaker


class Base(DeclarativeBase):
    """Base class for all models"""

    pass


class SignalType(str, Enum):
    """Signal types"""

    DIGITAL_INPUT = "DIGITAL_INPUT"
    DIGITAL_OUTPUT = "DIGITAL_OUTPUT"
    ANALOG_INPUT = "ANALOG_INPUT"
    ANALOG_OUTPUT = "ANALOG_OUTPUT"
    TIMER = "TIMER"
    COUNTER = "COUNTER"


class Project(Base):
    """PLC Project"""

    __tablename__ = "projects"

    id = Column(Integer, primary_key=True)
    name = Column(String(200), unique=True, nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)

    # Relationships
    signals = relationship("Signal", back_populates="project", cascade="all, delete-orphan")
    parameters = relationship("Parameter", back_populates="project", cascade="all, delete-orphan")


class Signal(Base):
    """PLC Signal (I/O)"""

    __tablename__ = "signals"

    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)

    name = Column(String(200), nullable=False)
    address = Column(String(50))  # PLC address (e.g., %IW100)
    type = Column(String(50), nullable=False)  # SignalType enum
    unit = Column(String(20))  # bar, °C, RPM, etc.

    # Value constraints
    range_min = Column(Float)
    range_max = Column(Float)

    # Current value
    current_value = Column(Float)
    last_update = Column(DateTime)

    # Metadata
    description = Column(Text)
    sensor_type = Column(String(100))  # Manufacturer/model
    alarm_threshold = Column(Float)
    warning_threshold = Column(Float)

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    project = relationship("Project", back_populates="signals")
    history = relationship("SignalHistory", back_populates="signal", cascade="all, delete-orphan")


class SignalHistory(Base):
    """Time-series data for signals"""

    __tablename__ = "signal_history"

    id = Column(Integer, primary_key=True)
    signal_id = Column(Integer, ForeignKey("signals.id"), nullable=False)

    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    value = Column(Float, nullable=False)

    signal = relationship("Signal", back_populates="history")


class Parameter(Base):
    """PLC Configuration Parameters"""

    __tablename__ = "parameters"

    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)

    name = Column(String(200), nullable=False)
    category = Column(String(100))  # timer, setpoint, threshold, etc.

    value = Column(Float, nullable=False)
    unit = Column(String(20))
    min_value = Column(Float)
    max_value = Column(Float)

    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    project = relationship("Project", back_populates="parameters")


class AlarmLog(Base):
    """Alarm and event logging"""

    __tablename__ = "alarm_logs"

    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    signal_name = Column(String(200), nullable=False)
    alarm_type = Column(String(50))  # warning, critical, error
    severity = Column(String(20))  # low, medium, high

    message = Column(Text, nullable=False)
    value = Column(Float)
    threshold = Column(Float)

    acknowledged = Column(Boolean, default=False)
    acknowledged_at = Column(DateTime)
    acknowledged_by = Column(String(100))


class ChatHistory(Base):
    """AI Chat conversation history"""

    __tablename__ = "chat_history"

    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    role = Column(String(20), nullable=False)  # user, assistant, system
    content = Column(Text, nullable=False)

    # Context metadata
    context_signal = Column(String(200))  # Related signal if any
    context_data = Column(JSON)  # Additional context

    # Token usage tracking
    prompt_tokens = Column(Integer)
    completion_tokens = Column(Integer)


class SignalDocumentation(Base):
    """Documentation for signals (RAG knowledge base)"""

    __tablename__ = "signal_documentation"

    id = Column(Integer, primary_key=True)
    signal_id = Column(Integer, ForeignKey("signals.id"))

    doc_type = Column(String(50))  # manual, datasheet, note, faq
    title = Column(String(200))
    content = Column(Text, nullable=False)
    source = Column(String(200))  # e.g., "Handbuch S.47"

    # For RAG: store document ID reference
    doc_id = Column(String(100))  # FAISS document ID (hash)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class UserSettings(Base):
    """User preferences and settings"""

    __tablename__ = "user_settings"

    id = Column(Integer, primary_key=True)
    user_name = Column(String(100), unique=True, nullable=False)

    # GUI preferences
    theme = Column(String(20), default="light")
    window_geometry = Column(String(100))

    # Permissions
    role = Column(String(50), default="operator")  # operator, engineer, admin
    can_write_plc = Column(Boolean, default=False)
    can_modify_config = Column(Boolean, default=False)

    settings_json = Column(JSON)  # Additional custom settings

    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime)


# Database initialization
_engine = None
_SessionLocal = None


def get_engine():
    """Get or create database engine"""
    global _engine
    if _engine is None:
        import sys
        from pathlib import Path

        # Add config to path
        sys.path.insert(0, str(Path(__file__).parent.parent.parent / "config"))
        from config import settings

        # Ensure db directory exists
        db_url = settings.database_url
        if db_url.startswith("sqlite:///"):
            db_path = db_url.replace("sqlite:///", "")
            db_dir = Path(db_path).parent
            db_dir.mkdir(parents=True, exist_ok=True)

        _engine = create_engine(
            settings.database_url,
            echo=False,  # Set to True for SQL debugging
            pool_pre_ping=True,
        )
    return _engine


def get_session():
    """Get database session"""
    global _SessionLocal
    if _SessionLocal is None:
        _SessionLocal = sessionmaker(bind=get_engine())
    return _SessionLocal()


def init_database():
    """Initialize database schema"""
    from loguru import logger

    engine = get_engine()
    logger.info("Creating database tables...")
    Base.metadata.create_all(engine)
    logger.info("Database initialized successfully")

    # Create default project if none exists
    session = get_session()
    if session.query(Project).count() == 0:
        default_project = Project(
            name="Default Project", description="Initial PLC monitoring project", is_active=True
        )
        session.add(default_project)
        session.commit()
        logger.info("Created default project")
    session.close()
