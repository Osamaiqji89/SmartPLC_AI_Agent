"""
Mock PLC - Database-Integrated Programmable Logic Controller
Emulates industrial PLC behavior with full database persistence
"""
import random
import threading
import time
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, Optional

from loguru import logger
from core.data.database import get_session, Signal, SignalHistory, AlarmLog, Project


class SignalType(Enum):
    """Signal types in PLC"""
    DI = "DIGITAL_INPUT"      # Digital Input
    DO = "DIGITAL_OUTPUT"     # Digital Output
    AI = "ANALOG_INPUT"       # Analog Input
    AO = "ANALOG_OUTPUT"      # Analog Output


@dataclass
class IOSignal:
    """Represents a PLC I/O signal (in-memory cache)"""
    id: int
    name: str
    type: SignalType  # Changed from str to SignalType enum
    address: str
    value: Any = 0
    unit: str = ""
    description: str = ""
    min_value: float = 0.0
    max_value: float = 100.0
    alarm_threshold: Optional[float] = None
    warning_threshold: Optional[float] = None


class MockPLC:
    """
    Database-integrated PLC Simulator
    
    Features:
    - Loads signals from database
    - Persists signal values to DB
    - Records signal history every 5s
    - Logs alarms to database
    - Thread-safe operations
    """
    
    def __init__(self, update_interval_ms: int = 500, history_interval_s: int = 5):
        self.update_interval = update_interval_ms / 1000.0  # Convert to seconds
        self.history_interval = history_interval_s
        
        # Signal cache (for fast access)
        self.signals: Dict[str, IOSignal] = {}
        
        # Threading
        self._running = False
        self._update_thread: Optional[threading.Thread] = None
        self._history_thread: Optional[threading.Thread] = None
        self._lock = threading.Lock()
        
        # Timing
        self._last_history_save = time.time()
        
        # Callbacks
        self._signal_change_callbacks: list[Callable] = []
        self._alarm_callbacks: list[Callable] = []
        
        # Process state tracking (to prevent duplicate events)
        self._object_detected = False  # Track if object is currently being processed
        
        # Initialize from database
        self._load_signals_from_db()
        
        logger.info(f"Database-integrated PLC initialized with {len(self.signals)} signals")
    
    def _load_signals_from_db(self):
        """Load all signals from database into memory cache"""
        try:
            session = get_session()
            
            # Get active project
            project = session.query(Project).filter_by(is_active=True).first()
            if not project:
                logger.error("No active project found! Run init_signals.py first.")
                session.close()
                return
            
            # Load all signals
            db_signals = session.query(Signal).filter_by(project_id=project.id).all()
            
            # Mapping from DB string to SignalType enum
            type_mapping = {
                "DIGITAL_INPUT": SignalType.DI,
                "DIGITAL_OUTPUT": SignalType.DO,
                "ANALOG_INPUT": SignalType.AI,
                "ANALOG_OUTPUT": SignalType.AO,
                "DI": SignalType.DI,
                "DO": SignalType.DO,
                "AI": SignalType.AI,
                "AO": SignalType.AO
            }
            
            for db_signal in db_signals:
                # Convert string type from DB to SignalType enum
                signal_type = type_mapping.get(db_signal.type)
                if not signal_type:
                    logger.warning(f"Unknown signal type '{db_signal.type}' for {db_signal.name}, defaulting to DI")
                    signal_type = SignalType.DI
                
                # Create in-memory IOSignal from DB Signal
                io_signal = IOSignal(
                    id=db_signal.id,
                    name=db_signal.name,
                    type=signal_type,  # Use enum instead of string
                    address=db_signal.address,
                    value=db_signal.current_value if db_signal.current_value is not None else 0.0,
                    unit=db_signal.unit or "",
                    description=db_signal.description or "",
                    min_value=db_signal.range_min if db_signal.range_min is not None else 0.0,
                    max_value=db_signal.range_max if db_signal.range_max is not None else 100.0,
                    alarm_threshold=db_signal.alarm_threshold,
                    warning_threshold=db_signal.warning_threshold
                )
                
                self.signals[db_signal.name] = io_signal
                logger.debug(f"Loaded signal: {db_signal.name} = {io_signal.value}")
            
            session.close()
            logger.success(f"✓ Loaded {len(self.signals)} signals from database")
            
        except Exception as e:
            logger.error(f"Failed to load signals from database: {e}")
    
    def read_signal(self, name: str) -> Any:
        """Read current value of a signal"""
        with self._lock:
            if name in self.signals:
                return self.signals[name].value
            raise KeyError(f"Signal '{name}' not found")
    
    def write_signal(self, name: str, value: Any) -> bool:
        """
        Write value to a signal
        - Updates in-memory cache
        - Persists to database
        - Triggers callbacks
        - Checks alarms
        """
        with self._lock:
            if name not in self.signals:
                logger.error(f"Signal '{name}' not found")
                return False
            
            signal = self.signals[name]
            
            # Validate analog values
            if signal.type in (SignalType.AI, SignalType.AO):
                try:
                    value = float(value)
                    if not (signal.min_value <= value <= signal.max_value):
                        logger.warning(f"Value {value} out of range [{signal.min_value}, {signal.max_value}] for {name}")
                        value = max(signal.min_value, min(signal.max_value, value))
                except (ValueError, TypeError):
                    logger.error(f"Invalid value type for analog signal {name}: {value}")
                    return False
            
            # Convert digital values to bool/float
            if signal.type in (SignalType.DI, SignalType.DO):
                value = bool(value)
            
            old_value = signal.value
            signal.value = value
            
            # Note: We don't persist every single value change to avoid DB lock issues
            # The history thread will save values every 5 seconds
            # and critical changes (alarms) are logged separately
            
            # Trigger callbacks
            if old_value != value:
                self._trigger_signal_change_callbacks(name, old_value, value)
            
            # Check alarms
            self._check_alarm(signal, value)
            
            return True
    
    def _check_alarm(self, signal: IOSignal, value: Any):
        """Check if signal value exceeds alarm threshold"""
        if not isinstance(value, (int, float)):
            return
        
        # Check alarm threshold (critical)
        if signal.alarm_threshold and value >= signal.alarm_threshold:
            self._log_alarm(
                signal_name=signal.name,
                alarm_type="critical",
                severity="high",
                message=f"{signal.name} exceeded ALARM threshold: {value:.2f} {signal.unit} >= {signal.alarm_threshold} {signal.unit}",
                value=value,
                threshold=signal.alarm_threshold
            )
            # Trigger callback (only once per alarm via DB check)
            self._trigger_alarm_callbacks({
                "signal": signal.name,
                "value": value,
                "threshold": signal.alarm_threshold,
                "type": "alarm"
            })
        
        # Check warning threshold (only if alarm not triggered)
        elif signal.warning_threshold and value >= signal.warning_threshold:
            self._log_alarm(
                signal_name=signal.name,
                alarm_type="warning",
                severity="medium",
                message=f"{signal.name} exceeded WARNING threshold: {value:.2f} {signal.unit} >= {signal.warning_threshold} {signal.unit}",
                value=value,
                threshold=signal.warning_threshold
            )
            # Trigger callback (only once per alarm via DB check)
            self._trigger_alarm_callbacks({
                "signal": signal.name,
                "value": value,
                "threshold": signal.warning_threshold,
                "type": "warning"
            })
        
        # Auto-acknowledge alarm when value drops below threshold
        else:
            self._auto_acknowledge_alarm(signal.name)
    
    def _log_alarm(self, signal_name: str, alarm_type: str, severity: str, message: str, value: float, threshold: float):
        """Log alarm to database"""
        try:
            session = get_session()
            
            # Check if alarm already exists and not acknowledged
            existing = session.query(AlarmLog).filter_by(
                signal_name=signal_name,
                acknowledged=False
            ).first()
            
            if not existing:
                # Create new alarm
                alarm = AlarmLog(
                    signal_name=signal_name,
                    alarm_type=alarm_type,
                    severity=severity,
                    message=message,
                    value=value,
                    threshold=threshold,
                    acknowledged=False
                )
                session.add(alarm)
                session.commit()
                logger.warning(f"🚨 ALARM: {message}")
            
            session.close()
        except Exception as e:
            logger.error(f"Failed to log alarm: {e}")
    
    def _auto_acknowledge_alarm(self, signal_name: str):
        """Auto-acknowledge alarm when value returns to normal"""
        try:
            session = get_session()
            
            # Find unacknowledged alarms for this signal
            alarms = session.query(AlarmLog).filter_by(
                signal_name=signal_name,
                acknowledged=False
            ).all()
            
            if alarms:
                for alarm in alarms:
                    alarm.acknowledged = True
                    alarm.acknowledged_at = datetime.utcnow()
                session.commit()
                logger.info(f"✓ Auto-acknowledged alarm for {signal_name}")
            
            session.close()
        except Exception as e:
            logger.error(f"Failed to auto-acknowledge alarm: {e}")
    
    def get_all_signals(self) -> Dict[str, IOSignal]:
        """Get all signals (returns in-memory cache)"""
        with self._lock:
            return dict(self.signals)
    
    def get_signal_history(self, signal_name: str, limit: int = 100):
        """Get historical values for a signal from database"""
        try:
            if signal_name not in self.signals:
                logger.error(f"Signal '{signal_name}' not found")
                return []
            
            signal = self.signals[signal_name]
            session = get_session()
            
            # Query signal history ordered by timestamp descending
            history = session.query(SignalHistory).filter_by(
                signal_id=signal.id
            ).order_by(SignalHistory.timestamp.desc()).limit(limit).all()
            
            # Convert to list of dicts for easier handling
            result = [
                {
                    'timestamp': h.timestamp,
                    'value': h.value
                }
                for h in reversed(history)  # Reverse to get chronological order
            ]
            
            session.close()
            return result
            
        except Exception as e:
            logger.error(f"Failed to get signal history: {e}")
            return []
    
    def start(self):
        """Start PLC simulation"""
        if self._running:
            logger.warning("PLC already running")
            return
        
        # Initialize default values for analog outputs if not set
        if "AO_01_FlowControl" in self.signals and self.read_signal("AO_01_FlowControl") == 0:
            self.write_signal("AO_01_FlowControl", 50.0)  # Default 50% flow
        
        if "AO_02_MotorSpeed" in self.signals and self.read_signal("AO_02_MotorSpeed") == 0:
            self.write_signal("AO_02_MotorSpeed", 50.0)  # Default 50% motor speed
        
        self._running = True
        
        # Start process simulation thread
        self._update_thread = threading.Thread(target=self._update_loop, daemon=True)
        self._update_thread.start()
        
        # Start history recording thread
        self._history_thread = threading.Thread(target=self._history_loop, daemon=True)
        self._history_thread.start()
        
        logger.info("Mock PLC started (process simulation + history recording)")
    
    def stop(self):
        """Stop PLC simulation"""
        self._running = False
        if self._update_thread:
            self._update_thread.join(timeout=2)
        if self._history_thread:
            self._history_thread.join(timeout=2)
        logger.info("Mock PLC stopped")
    
    def _update_loop(self):
        """Main update loop for process simulation"""
        while self._running:
            try:
                self._simulate_tank_process()
                self._simulate_conveyor_process()
                self._add_noise_to_sensors()
                time.sleep(self.update_interval)
            except Exception as e:
                logger.error(f"Error in PLC update loop: {e}")
    
    def _history_loop(self):
        """Background loop to record signal history"""
        while self._running:
            try:
                time.sleep(self.history_interval)
                self._record_history()
            except Exception as e:
                logger.error(f"Error in history recording loop: {e}")
    
    def _record_history(self):
        """Record current values of all signals to signal_history table"""
        try:
            session = get_session()
            timestamp = datetime.utcnow()
            
            with self._lock:
                for signal_name, signal in self.signals.items():
                    # Update current_value in database (for all signals)
                    db_signal = session.query(Signal).get(signal.id)
                    if db_signal:
                        db_signal.current_value = float(signal.value) if not isinstance(signal.value, bool) else (1.0 if signal.value else 0.0)
                        db_signal.last_update = timestamp
                    
                    # Record history (only for analog signals and digital outputs)
                    if signal.type in (SignalType.AI, SignalType.AO, SignalType.DO):
                        history_entry = SignalHistory(
                            signal_id=signal.id,
                            timestamp=timestamp,
                            value=float(signal.value) if not isinstance(signal.value, bool) else (1.0 if signal.value else 0.0)
                        )
                        session.add(history_entry)
            
            session.commit()
            session.close()
            logger.debug(f"✓ Recorded history for {len(self.signals)} signals")
            
        except Exception as e:
            logger.error(f"Failed to record signal history: {e}")
    
    def _simulate_tank_process(self):
        """Simulate tank filling process"""
        try:
            pump_running = self.read_signal("DO_01_Pump")
            current_level = self.read_signal("AI_01_TankLevel")
            
            # Synchronize drain valve signals (GUI uses DrainValve, simulation uses Drain)
            drain_open = False
            if "DO_02_DrainValve" in self.signals:
                drain_open = self.read_signal("DO_02_DrainValve")
                # Keep DO_02_Drain in sync
                if "DO_02_Drain" in self.signals:
                    if self.read_signal("DO_02_Drain") != drain_open:
                        self.write_signal("DO_02_Drain", drain_open)
            elif "DO_02_Drain" in self.signals:
                drain_open = self.read_signal("DO_02_Drain")
            
            # Get flow control (default to 50% if not set)
            flow_control = self.read_signal("AO_01_FlowControl") if "AO_01_FlowControl" in self.signals else 50.0
            flow_control = max(0.0, min(100.0, flow_control)) / 100.0  # Normalize to 0-1
            # Ensure minimum flow when pump is running (pump can't be completely closed)
            if pump_running and flow_control < 0.1:
                flow_control = 0.1  # Minimum 10% flow
            
            # Calculate fill and drain rates
            fill_rate = 10.0 * flow_control if pump_running else 0.0  # 10% per second max
            drain_rate = 5.0 if drain_open else 0.0  # 5% per second
            
            # Net flow rate (positive = filling, negative = draining, zero = balanced)
            net_rate = fill_rate - drain_rate
            
            # Update tank level based on net flow
            if abs(net_rate) > 0.01:  # Only update if significant change
                new_level = current_level + (net_rate * self.update_interval)
                new_level = max(0.0, min(100.0, new_level))  # Clamp to 0-100%
                self.write_signal("AI_01_TankLevel", new_level)
            else:
                # Rates are balanced, level stays the same
                new_level = current_level
            
            # Auto-stop pump at 95% (always check, regardless of drain state)
            if pump_running and new_level >= 95.0:
                self.write_signal("DO_01_Pump", False)
                logger.info("Tank reached 95%, pump auto-stopped")
            
            # Pressure sensor simulation (correlated with level)
            pressure = 2.0 + (new_level / 100.0) * 6.0  # 2-8 bar range
            self.write_signal("AI_02_PressureSensor", round(pressure, 2))
            
        except KeyError as e:
            logger.debug(f"Signal not found in tank simulation: {e}")
    
    def _simulate_conveyor_process(self):
        """Simulate conveyor belt process"""
        try:
            motor_running = self.read_signal("DO_03_Motor")
            
            if motor_running:
                # Get target speed from AO_02_MotorSpeed (0-100%)
                motor_speed_setpoint = self.read_signal("AO_02_MotorSpeed") if "AO_02_MotorSpeed" in self.signals else 100.0
                motor_speed_setpoint = max(0.0, min(100.0, motor_speed_setpoint))  # Clamp 0-100
                target_speed = motor_speed_setpoint  # Direct mapping: setpoint% = speed in m/min
                
                # Update belt speed (accelerate towards target)
                current_speed = self.read_signal("AI_03_BeltSpeed")
                new_speed = current_speed + (target_speed - current_speed) * 0.1
                self.write_signal("AI_03_BeltSpeed", round(new_speed, 1))
                
                # Simulate object detection (random trigger, but only once per object)
                if not self._object_detected and random.random() < 0.01:  # 1% chance per cycle
                    # New object detected!
                    self._object_detected = True
                    self.write_signal("DI_03_ObjectSensor", True)
                    self.write_signal("DO_04_Stopper", True)
                    
                    # Increment cycle counter (only once per object!)
                    if "AI_04_CycleCounter" in self.signals:
                        current_count = self.read_signal("AI_04_CycleCounter")
                        self.write_signal("AI_04_CycleCounter", current_count + 1)
                    
                    # Limit switch triggers when stopper is active (object at end position)
                    if "DI_04_LimitSwitch" in self.signals:
                        self.write_signal("DI_04_LimitSwitch", True)
                    
                    logger.debug(f"Object detected! Cycle count incremented")
                    
                elif self._object_detected and random.random() < 0.05:  # 5% chance to release object
                    # Object processed and released
                    self._object_detected = False
                    self.write_signal("DI_03_ObjectSensor", False)
                    self.write_signal("DO_04_Stopper", False)
                    
                    # Limit switch deactivates when object is released
                    if "DI_04_LimitSwitch" in self.signals:
                        self.write_signal("DI_04_LimitSwitch", False)
                    
                    logger.debug(f"Object released")
                        
            else:
                # Motor off, speed decreases
                current_speed = self.read_signal("AI_03_BeltSpeed")
                new_speed = max(0.0, current_speed - 10.0 * self.update_interval)
                self.write_signal("AI_03_BeltSpeed", round(new_speed, 1))
                
                # All sensors off when motor stopped, reset state
                self._object_detected = False
                if "DI_04_LimitSwitch" in self.signals:
                    self.write_signal("DI_04_LimitSwitch", False)
                self.write_signal("DI_03_ObjectSensor", False)
                self.write_signal("DO_04_Stopper", False)
                
        except KeyError as e:
            logger.debug(f"Signal not found in conveyor simulation: {e}")
    
    def _add_noise_to_sensors(self):
        """Add realistic noise to analog sensors"""
        analog_signals = ["AI_01_TankLevel", "AI_02_PressureSensor", "AI_03_BeltSpeed"]
        
        for signal_name in analog_signals:
            try:
                if signal_name in self.signals:
                    current_value = self.read_signal(signal_name)
                    if current_value > 0:
                        # Add small random noise (±0.5%)
                        noise = random.uniform(-0.005, 0.005) * current_value
                        new_value = current_value + noise
                        
                        signal = self.signals[signal_name]
                        new_value = max(signal.min_value, min(signal.max_value, new_value))
                        
                        # Update in-memory only (don't trigger full write to avoid spam)
                        with self._lock:
                            signal.value = round(new_value, 2)
            except Exception:
                pass
    
    def register_signal_change_callback(self, callback: Callable):
        """Register callback for signal changes"""
        self._signal_change_callbacks.append(callback)
    
    def register_alarm_callback(self, callback: Callable):
        """Register callback for alarms"""
        self._alarm_callbacks.append(callback)
    
    def _trigger_signal_change_callbacks(self, name: str, old_value: Any, new_value: Any):
        """Trigger all signal change callbacks"""
        for callback in self._signal_change_callbacks:
            try:
                callback(name, old_value, new_value)
            except Exception as e:
                logger.error(f"Error in signal change callback: {e}")
    
    def _trigger_alarm_callbacks(self, alarm_data: dict):
        """Trigger alarm callbacks"""
        for callback in self._alarm_callbacks:
            try:
                callback(alarm_data)
            except Exception as e:
                logger.error(f"Error in alarm callback: {e}")


# Global PLC instance
_plc_instance: Optional[MockPLC] = None


def get_plc() -> MockPLC:
    """Get or create global PLC instance"""
    global _plc_instance
    if _plc_instance is None:
        import sys
        from pathlib import Path
        # Add config to path
        sys.path.insert(0, str(Path(__file__).parent.parent.parent / "config"))
        from config import settings
        _plc_instance = MockPLC(
            update_interval_ms=settings.plc_update_interval_ms,
            history_interval_s=5  # Record history every 5 seconds
        )
    return _plc_instance
