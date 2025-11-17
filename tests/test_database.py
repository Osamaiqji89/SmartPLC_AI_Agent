"""
Unit Tests for Database Models
"""

from datetime import datetime

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from core.data.database import (
    AlarmLog,
    Base,
    ChatHistory,
    Parameter,
    Project,
    Signal,
    SignalDocumentation,
)


@pytest.fixture
def db_session():
    """Create in-memory database session for testing"""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    yield session

    session.close()
    engine.dispose()


class TestDatabaseModels:
    """Test suite for database models"""

    def test_create_project(self, db_session):
        """Test creating a project"""
        project = Project(name="Test Project", description="A test project", is_active=True)

        db_session.add(project)
        db_session.commit()

        assert project.id is not None
        assert project.created_at is not None

    def test_create_signal(self, db_session):
        """Test creating a signal"""
        # Create project first
        project = Project(name="Test Project")
        db_session.add(project)
        db_session.commit()

        # Create signal
        signal = Signal(
            project_id=project.id,
            name="AI_02_PressureSensor",
            address="%IW102",
            type="ANALOG_INPUT",
            unit="bar",
            range_min=0.0,
            range_max=10.0,
            current_value=6.47,
            description="Pressure sensor",
            alarm_threshold=9.5,
        )

        db_session.add(signal)
        db_session.commit()

        assert signal.id is not None
        assert signal.name == "AI_02_PressureSensor"

    def test_signal_history_relationship(self, db_session):
        """Test signal to history relationship"""
        project = Project(name="Test Project")
        db_session.add(project)
        db_session.commit()

        signal = Signal(
            project_id=project.id, name="Test_Signal", type="ANALOG_INPUT", current_value=50.0
        )

        db_session.add(signal)
        db_session.commit()

        # Add to history via relationship
        from core.data.database import SignalHistory

        history_entry = SignalHistory(signal_id=signal.id, timestamp=datetime.utcnow(), value=50.0)

        db_session.add(history_entry)
        db_session.commit()

        # Check relationship
        assert len(signal.history) == 1
        assert signal.history[0].value == 50.0

    def test_create_parameter(self, db_session):
        """Test creating a parameter"""
        project = Project(name="Test Project")
        db_session.add(project)
        db_session.commit()

        param = Parameter(
            project_id=project.id,
            name="Motor_Timer",
            category="timer",
            value=10.0,
            unit="s",
            min_value=0.0,
            max_value=60.0,
            description="Motor run timer",
        )

        db_session.add(param)
        db_session.commit()

        assert param.id is not None

    def test_create_alarm_log(self, db_session):
        """Test creating an alarm log entry"""
        alarm = AlarmLog(
            signal_name="AI_02_PressureSensor",
            alarm_type="threshold_exceeded",
            severity="high",
            message="Pressure exceeded threshold",
            value=9.8,
            threshold=9.5,
        )

        db_session.add(alarm)
        db_session.commit()

        assert alarm.id is not None
        assert alarm.acknowledged is False

    def test_acknowledge_alarm(self, db_session):
        """Test acknowledging an alarm"""
        alarm = AlarmLog(
            signal_name="Test_Signal", alarm_type="warning", severity="medium", message="Test alarm"
        )

        db_session.add(alarm)
        db_session.commit()

        # Acknowledge
        alarm.acknowledged = True
        alarm.acknowledged_at = datetime.utcnow()
        alarm.acknowledged_by = "test_user"

        db_session.commit()

        assert alarm.acknowledged is True
        assert alarm.acknowledged_by == "test_user"

    def test_create_chat_history(self, db_session):
        """Test creating chat history"""
        chat = ChatHistory(
            role="user",
            content="Erkläre Signal AI_02",
            context_signal="AI_02_PressureSensor",
            prompt_tokens=50,
            completion_tokens=200,
        )

        db_session.add(chat)
        db_session.commit()

        assert chat.id is not None
        assert chat.timestamp is not None

    def test_create_signal_documentation(self, db_session):
        """Test creating signal documentation"""
        project = Project(name="Test Project")
        db_session.add(project)
        db_session.commit()

        signal = Signal(project_id=project.id, name="AI_02_PressureSensor", type="ANALOG_INPUT")
        db_session.add(signal)
        db_session.commit()

        doc = SignalDocumentation(
            signal_id=signal.id,
            doc_type="manual",
            title="Pressure Sensor Manual",
            content="This is the manual content...",
            source="Handbuch S.47",
            doc_id="test_doc_id_hash123",
        )

        db_session.add(doc)
        db_session.commit()

        assert doc.id is not None

    def test_cascade_delete(self, db_session):
        """Test cascade deletion of project deletes signals"""
        project = Project(name="Test Project")
        db_session.add(project)
        db_session.commit()

        signal = Signal(project_id=project.id, name="Test_Signal", type="DIGITAL_INPUT")
        db_session.add(signal)
        db_session.commit()

        # Delete project
        db_session.delete(project)
        db_session.commit()

        # Verify signal was also deleted
        assert db_session.query(Signal).filter_by(id=signal.id).first() is None
