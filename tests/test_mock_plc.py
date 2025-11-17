"""
Unit Tests for Mock PLC
"""

import time

import pytest

from core.plc.mock_plc import MockPLC, SignalType


class TestMockPLC:
    """Test suite for Mock PLC functionality"""

    def test_plc_initialization(self, mock_plc):
        """Test PLC initializes with correct signals"""
        signals = mock_plc.get_all_signals()

        assert len(signals) > 0
        assert "AI_01_TankLevel" in signals
        assert "AI_02_PressureSensor" in signals
        assert "DO_01_Pump" in signals
        assert "DO_03_Motor" in signals

    def test_read_signal(self, mock_plc):
        """Test reading signal values"""
        value = mock_plc.read_signal("AI_01_TankLevel")
        assert isinstance(value, (int, float))
        assert 0 <= value <= 100

    def test_write_signal_digital(self, mock_plc):
        """Test writing digital signal"""
        # Write TRUE
        success = mock_plc.write_signal("DO_01_Pump", True)
        assert success is True

        # Verify
        value = mock_plc.read_signal("DO_01_Pump")
        assert value is True

        # Write FALSE
        success = mock_plc.write_signal("DO_01_Pump", False)
        assert success is True

        value = mock_plc.read_signal("DO_01_Pump")
        assert value is False

    def test_write_signal_analog(self, mock_plc):
        """Test writing analog signal with range validation"""
        # Valid value
        success = mock_plc.write_signal("AO_01_FlowControl", 75.0)
        assert success is True

        value = mock_plc.read_signal("AO_01_FlowControl")
        assert value == 75.0

        # Out of range - should fail
        success = mock_plc.write_signal("AO_01_FlowControl", 150.0)
        assert success is False

    def test_signal_history(self, mock_plc):
        """Test signal history tracking"""
        # Write multiple values
        mock_plc.write_signal("AI_01_TankLevel", 50.0)
        time.sleep(0.1)
        mock_plc.write_signal("AI_01_TankLevel", 60.0)
        time.sleep(0.1)
        mock_plc.write_signal("AI_01_TankLevel", 70.0)

        # Get history
        history = mock_plc.get_signal_history("AI_01_TankLevel", limit=10)

        assert len(history) >= 3
        assert history[-1]["value"] == 70.0

    def test_tank_filling_simulation(self, mock_plc):
        """Test tank filling process simulation"""
        # Start PLC
        mock_plc.start()

        # Start pump
        mock_plc.write_signal("DO_01_Pump", True)
        initial_level = mock_plc.read_signal("AI_01_TankLevel")

        # Wait for simulation to run
        time.sleep(1.0)

        # Check level increased
        new_level = mock_plc.read_signal("AI_01_TankLevel")
        assert new_level > initial_level

        # Stop pump
        mock_plc.write_signal("DO_01_Pump", False)

    def test_alarm_threshold(self, mock_plc):
        """Test alarm triggering at threshold"""
        alarm_triggered = False

        def alarm_callback(alarm_data):
            nonlocal alarm_triggered
            alarm_triggered = True

        mock_plc.register_alarm_callback(alarm_callback)

        # Set value above threshold
        mock_plc.write_signal("AI_02_PressureSensor", 9.6)  # Threshold is 9.5

        assert alarm_triggered is True

    def test_signal_change_callback(self, mock_plc):
        """Test signal change callbacks"""
        changes = []

        def change_callback(name, old_value, new_value):
            changes.append((name, old_value, new_value))

        mock_plc.register_signal_change_callback(change_callback)

        # Change signal
        mock_plc.write_signal("DO_01_Pump", True)

        assert len(changes) > 0
        assert changes[0][0] == "DO_01_Pump"
        assert changes[0][2] is True

    def test_invalid_signal_name(self, mock_plc):
        """Test reading/writing invalid signal raises error"""
        with pytest.raises(KeyError):
            mock_plc.read_signal("INVALID_SIGNAL")

        success = mock_plc.write_signal("INVALID_SIGNAL", 123)
        assert success is False

    def test_conveyor_simulation(self, mock_plc):
        """Test conveyor belt process"""
        mock_plc.start()

        # Start motor
        mock_plc.write_signal("DO_03_Motor", True)
        initial_speed = mock_plc.read_signal("AI_03_BeltSpeed")

        # Wait for speed to increase
        time.sleep(1.0)

        new_speed = mock_plc.read_signal("AI_03_BeltSpeed")
        assert new_speed > initial_speed

        # Stop motor
        mock_plc.write_signal("DO_03_Motor", False)

        # Wait for speed to decrease
        time.sleep(1.0)

        final_speed = mock_plc.read_signal("AI_03_BeltSpeed")
        assert final_speed < new_speed
