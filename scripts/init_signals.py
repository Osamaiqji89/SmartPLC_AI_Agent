"""
Initialize PLC Signals in Database
Creates all 13 signals from MockPLC in the database
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from loguru import logger  # noqa: E402

from core.data.database import Project, Signal, get_session  # noqa: E402


def init_signals():
    """Initialize all PLC signals in database"""
    logger.info("Initializing PLC signals...")

    session = get_session()

    try:
        # Get or create default project
        project = session.query(Project).filter_by(is_active=True).first()
        if not project:
            project = Project(
                name="Default Project", description="SmartPLC Simulation Project", is_active=True
            )
            session.add(project)
            session.commit()
            logger.info(f"Created project: {project.name}")

        # Define all signals from MockPLC
        signals_config = [
            # Digital Inputs
            {
                "name": "DI_01_StartButton",
                "address": "%IX0.0",
                "type": "DIGITAL_INPUT",
                "description": "Start button for process",
                "range_min": 0.0,
                "range_max": 1.0,
            },
            {
                "name": "DI_02_StopButton",
                "address": "%IX0.1",
                "type": "DIGITAL_INPUT",
                "description": "Stop button for process",
                "range_min": 0.0,
                "range_max": 1.0,
            },
            {
                "name": "DI_03_ObjectSensor",
                "address": "%IX0.2",
                "type": "DIGITAL_INPUT",
                "description": "Object detection sensor on conveyor belt",
                "range_min": 0.0,
                "range_max": 1.0,
            },
            {
                "name": "DI_04_LimitSwitch",
                "address": "%IX0.3",
                "type": "DIGITAL_INPUT",
                "description": "Limit switch for position detection",
                "range_min": 0.0,
                "range_max": 1.0,
            },
            # Digital Outputs
            {
                "name": "DO_01_Pump",
                "address": "%QX0.0",
                "type": "DIGITAL_OUTPUT",
                "description": "Main tank filling pump",
                "range_min": 0.0,
                "range_max": 1.0,
            },
            {
                "name": "DO_02_Drain",
                "address": "%QX0.1",
                "type": "DIGITAL_OUTPUT",
                "description": "Tank drain valve",
                "range_min": 0.0,
                "range_max": 1.0,
            },
            {
                "name": "DO_02_DrainValve",
                "address": "%QX0.1",
                "type": "DIGITAL_OUTPUT",
                "description": "Tank drain valve (alternative name)",
                "range_min": 0.0,
                "range_max": 1.0,
            },
            {
                "name": "DO_03_Motor",
                "address": "%QX0.2",
                "type": "DIGITAL_OUTPUT",
                "description": "Conveyor belt motor",
                "range_min": 0.0,
                "range_max": 1.0,
            },
            {
                "name": "DO_04_Stopper",
                "address": "%QX0.3",
                "type": "DIGITAL_OUTPUT",
                "description": "Conveyor belt stopper",
                "range_min": 0.0,
                "range_max": 1.0,
            },
            # Analog Inputs
            {
                "name": "AI_01_TankLevel",
                "address": "%IW0",
                "type": "ANALOG_INPUT",
                "unit": "%",
                "description": "Tank fill level sensor",
                "range_min": 0.0,
                "range_max": 100.0,
                "sensor_type": "Ultrasonic Level Sensor",
                "alarm_threshold": 95.0,
                "warning_threshold": 90.0,
            },
            {
                "name": "AI_02_PressureSensor",
                "address": "%IW1",
                "type": "ANALOG_INPUT",
                "unit": "bar",
                "description": "System pressure sensor",
                "range_min": 0.0,
                "range_max": 10.0,
                "sensor_type": "Pressure Transmitter",
                "alarm_threshold": 9.5,
                "warning_threshold": 9.0,
            },
            {
                "name": "AI_03_BeltSpeed",
                "address": "%IW2",
                "type": "ANALOG_INPUT",
                "unit": "m/min",
                "description": "Conveyor belt speed sensor",
                "range_min": 0.0,
                "range_max": 100.0,
                "sensor_type": "Rotary Encoder",
                "alarm_threshold": 95.0,
            },
            {
                "name": "AI_04_CycleCounter",
                "address": "%IW3",
                "type": "ANALOG_INPUT",
                "unit": "cycles",
                "description": "Production cycle counter",
                "range_min": 0.0,
                "range_max": 99999.0,
                "sensor_type": "Counter",
            },
            # Analog Outputs
            {
                "name": "AO_01_FlowControl",
                "address": "%QW0",
                "type": "ANALOG_OUTPUT",
                "unit": "%",
                "description": "Flow control valve position",
                "range_min": 0.0,
                "range_max": 100.0,
            },
            {
                "name": "AO_02_MotorSpeed",
                "address": "%QW1",
                "type": "ANALOG_OUTPUT",
                "unit": "%",
                "description": "Motor speed control (frequency converter)",
                "range_min": 0.0,
                "range_max": 100.0,
            },
            {
                "name": "AO_03_HeatingPower",
                "address": "%QW2",
                "type": "ANALOG_OUTPUT",
                "unit": "%",
                "description": "Heating element power control",
                "range_min": 0.0,
                "range_max": 100.0,
            },
        ]

        # Create signals if they don't exist
        created_count = 0
        updated_count = 0

        for signal_data in signals_config:
            existing = (
                session.query(Signal)
                .filter_by(project_id=project.id, name=signal_data["name"])
                .first()
            )

            if existing:
                # Update existing signal
                for key, value in signal_data.items():
                    if key != "name":
                        setattr(existing, key, value)
                updated_count += 1
                logger.info(f"Updated signal: {signal_data['name']}")
            else:
                # Create new signal
                signal = Signal(
                    project_id=project.id, current_value=0.0, **signal_data  # Initial value
                )
                session.add(signal)
                created_count += 1
                logger.info(f"Created signal: {signal_data['name']} ({signal_data['type']})")

        session.commit()

        logger.success("✓ Signal initialization complete!")
        logger.success(f"  Created: {created_count} new signals")
        logger.success(f"  Updated: {updated_count} signals")
        logger.success(f"  Total: {len(signals_config)} signals")

    except Exception as e:
        session.rollback()
        logger.error(f"Error initializing signals: {e}")
        raise
    finally:
        session.close()


if __name__ == "__main__":
    logger.info("=" * 60)
    logger.info("SmartPLC Signal Initialization")
    logger.info("=" * 60)

    init_signals()

    logger.info("=" * 60)
    logger.info("Done! Signals are now in the database")
    logger.info("=" * 60)
