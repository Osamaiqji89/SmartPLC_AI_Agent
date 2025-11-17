"""
Initialize Default PLC Parameters
Creates standard parameters for the SmartPLC system
"""

from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.data.database import get_session, Project, Parameter
from loguru import logger


def init_parameters():
    """Initialize default parameters"""
    logger.info("Initializing default parameters...")

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

        # Default parameters to create
        default_params = [
            # Timer Parameters
            {
                "name": "Motor_Start_Delay",
                "category": "timer",
                "value": 5.0,
                "unit": "s",
                "min_value": 0.0,
                "max_value": 60.0,
                "description": "Delay before motor starts (safety delay)",
            },
            {
                "name": "Pump_Runtime_Max",
                "category": "timer",
                "value": 300.0,
                "unit": "s",
                "min_value": 10.0,
                "max_value": 3600.0,
                "description": "Maximum continuous pump runtime",
            },
            {
                "name": "Drain_Timeout",
                "category": "timer",
                "value": 60.0,
                "unit": "s",
                "min_value": 10.0,
                "max_value": 300.0,
                "description": "Timeout for tank draining operation",
            },
            # Setpoint Parameters
            {
                "name": "Tank_Level_Target",
                "category": "setpoint",
                "value": 75.0,
                "unit": "%",
                "min_value": 0.0,
                "max_value": 100.0,
                "description": "Target tank fill level",
            },
            {
                "name": "Pressure_Setpoint",
                "category": "setpoint",
                "value": 8.5,
                "unit": "bar",
                "min_value": 0.0,
                "max_value": 10.0,
                "description": "Target system pressure",
            },
            {
                "name": "Conveyor_Speed_Target",
                "category": "setpoint",
                "value": 45.0,
                "unit": "m/min",
                "min_value": 0.0,
                "max_value": 100.0,
                "description": "Target conveyor belt speed",
            },
            # Limit Parameters
            {
                "name": "Pressure_Limit_Max",
                "category": "limit",
                "value": 10.0,
                "unit": "bar",
                "min_value": 5.0,
                "max_value": 12.0,
                "description": "Maximum allowed system pressure",
            },
            {
                "name": "Speed_Limit_Max",
                "category": "limit",
                "value": 100.0,
                "unit": "m/min",
                "min_value": 50.0,
                "max_value": 150.0,
                "description": "Maximum conveyor belt speed",
            },
            {
                "name": "Tank_Level_Max",
                "category": "limit",
                "value": 95.0,
                "unit": "%",
                "min_value": 80.0,
                "max_value": 100.0,
                "description": "Maximum safe tank level",
            },
            # Alarm Threshold Parameters
            {
                "name": "Tank_Level_Low_Alarm",
                "category": "alarm",
                "value": 20.0,
                "unit": "%",
                "min_value": 0.0,
                "max_value": 50.0,
                "description": "Low tank level alarm threshold",
            },
            {
                "name": "Pressure_High_Alarm",
                "category": "alarm",
                "value": 9.0,
                "unit": "bar",
                "min_value": 7.0,
                "max_value": 10.0,
                "description": "High pressure alarm threshold",
            },
            {
                "name": "Temperature_Critical",
                "category": "alarm",
                "value": 80.0,
                "unit": "°C",
                "min_value": 60.0,
                "max_value": 100.0,
                "description": "Critical temperature alarm",
            },
        ]

        # Create parameters if they don't exist
        created_count = 0
        updated_count = 0

        for param_data in default_params:
            existing = (
                session.query(Parameter)
                .filter_by(project_id=project.id, name=param_data["name"])
                .first()
            )

            if existing:
                logger.info(f"Parameter '{param_data['name']}' already exists, skipping")
                updated_count += 1
            else:
                param = Parameter(project_id=project.id, **param_data)
                session.add(param)
                created_count += 1
                logger.info(
                    f"Created parameter: {param_data['name']} = {param_data['value']} {param_data['unit']}"
                )

        session.commit()

        logger.success(f"✓ Parameter initialization complete!")
        logger.success(f"  Created: {created_count} new parameters")
        logger.success(f"  Existing: {updated_count} parameters")
        logger.success(f"  Total: {len(default_params)} parameters")

    except Exception as e:
        session.rollback()
        logger.error(f"Error initializing parameters: {e}")
        raise
    finally:
        session.close()


if __name__ == "__main__":
    logger.info("=" * 60)
    logger.info("SmartPLC Parameter Initialization")
    logger.info("=" * 60)

    init_parameters()

    logger.info("=" * 60)
    logger.info("Done! You can now use the Parameter Editor in the GUI")
    logger.info("=" * 60)
