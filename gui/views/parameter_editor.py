"""
Parameter Editor View - Configure PLC parameters with database persistence
"""
from typing import Optional, Dict, Any
from PySide6.QtCore import Qt, QSize
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QPushButton,
    QHeaderView,
    QMessageBox,
    QDialog,
    QFormLayout,
    QLineEdit,
    QDoubleSpinBox,
    QDialogButtonBox
)
from PySide6.QtGui import QFont, QIcon
from loguru import logger

from core.data.database import get_session, Parameter


class ParameterDialog(QDialog):
    """Dialog for adding/editing parameters"""
    
    def __init__(self, parameter=None, parent=None):
        super().__init__(parent)
        self.parameter = parameter
        self.is_edit = parameter is not None
        
        self.setWindowTitle("Edit Parameter" if self.is_edit else "Add Parameter")
        self.setMinimumWidth(400)
        
        self._setup_ui()
        
        if self.is_edit:
            self._load_parameter()
    
    def _setup_ui(self) -> None:
        """Setup dialog UI"""
        layout = QVBoxLayout()
        
        # Form
        form = QFormLayout()
        
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("e.g., Motor_Timer")
        form.addRow("Parameter Name:", self.name_input)
        
        self.value_input = QDoubleSpinBox()
        self.value_input.setRange(-999999, 999999)
        self.value_input.setDecimals(2)
        form.addRow("Value:", self.value_input)
        
        self.unit_input = QLineEdit()
        self.unit_input.setPlaceholderText("e.g., s, %, bar")
        form.addRow("Unit:", self.unit_input)
        
        self.min_input = QDoubleSpinBox()
        self.min_input.setRange(-999999, 999999)
        self.min_input.setDecimals(2)
        form.addRow("Min Value:", self.min_input)
        
        self.max_input = QDoubleSpinBox()
        self.max_input.setRange(-999999, 999999)
        self.max_input.setDecimals(2)
        self.max_input.setValue(100)
        form.addRow("Max Value:", self.max_input)
        
        self.description_input = QLineEdit()
        self.description_input.setPlaceholderText("Description of the parameter")
        form.addRow("Description:", self.description_input)
        
        layout.addLayout(form)
        
        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        buttons.accepted.connect(self._validate_and_accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
        self.setLayout(layout)
    
    def _load_parameter(self) -> None:
        """Load parameter data into form"""
        if self.parameter:
            self.name_input.setText(self.parameter.name)
            self.value_input.setValue(self.parameter.value)
            self.unit_input.setText(self.parameter.unit or "")
            self.min_input.setValue(self.parameter.min_value or 0.0)
            self.max_input.setValue(self.parameter.max_value or 100.0)
            self.description_input.setText(self.parameter.description or "")
    
    def _validate_and_accept(self) -> None:
        """Validate input and accept dialog"""
        # Validate name
        name = self.name_input.text().strip()
        if not name:
            QMessageBox.warning(self, "Validation Error", "Parameter name is required!")
            return
        
        # Validate range
        min_val = self.min_input.value()
        max_val = self.max_input.value()
        if min_val >= max_val:
            QMessageBox.warning(self, "Validation Error", "Min value must be less than Max value!")
            return
        
        # Validate value in range
        value = self.value_input.value()
        if not (min_val <= value <= max_val):
            QMessageBox.warning(
                self, 
                "Validation Error", 
                f"Value must be between {min_val} and {max_val}!"
            )
            return
        
        self.accept()
    
    def get_data(self) -> Dict[str, Any]:
        """Get form data as dictionary"""
        return {
            'name': self.name_input.text().strip(),
            'value': self.value_input.value(),
            'unit': self.unit_input.text().strip(),
            'min_value': self.min_input.value(),
            'max_value': self.max_input.value(),
            'description': self.description_input.text().strip()
        }


class ParameterEditorView(QWidget):
    """Parameter configuration view with database persistence"""
    
    def __init__(self):
        super().__init__()
        self._setup_ui()
        self._load_parameters()
    
    def _setup_ui(self) -> None:
        """Setup UI"""
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("Parameter Configuration")
        title.setFont(QFont("Roboto", 16, QFont.Bold))
        layout.addWidget(title)
        
        # Info
        info = QLabel("Configure process timers, setpoints, and control parameters")
        info.setStyleSheet("color: gray; font-style: italic;")
        layout.addWidget(info)
        
        # Parameters table
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.verticalHeader().setDefaultSectionSize(40)
        self.table.setHorizontalHeaderLabels([
            "Parameter", "Value", "Unit", "Range", "Description", "Actions"
        ])
        
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(4, QHeaderView.Stretch)
        header.setSectionResizeMode(5, QHeaderView.Fixed)
        header.setDefaultSectionSize(120)
        
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.table)
        
        # Buttons
        btn_layout = QHBoxLayout()
        
        add_btn = QPushButton("Add Parameter")
        add_btn.setMinimumWidth(150)
        add_btn.setIcon(QIcon(":/icons/icons/add.png"))
        add_btn.clicked.connect(self._add_parameter)
        btn_layout.addWidget(add_btn)
        
        reload_btn = QPushButton("Reload")
        reload_btn.setMinimumWidth(150)
        reload_btn.setIcon(QIcon(":/icons/icons/reload.png"))
        reload_btn.clicked.connect(self._load_parameters)
        btn_layout.addWidget(reload_btn)
        
        export_btn = QPushButton("Export CSV")
        export_btn.setMinimumWidth(150)
        export_btn.setIcon(QIcon(":/icons/icons/share.png"))
        export_btn.clicked.connect(self._export_csv)
        btn_layout.addWidget(export_btn)
        
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
        
        self.setLayout(layout)
    
    def _load_parameters(self) -> None:
        """Load parameters from database"""
        try:
            session = get_session()
            parameters = session.query(Parameter).order_by(Parameter.name).all()
            
            self.table.setRowCount(len(parameters))
            
            for row, param in enumerate(parameters):
                # Parameter name
                self.table.setItem(row, 0, QTableWidgetItem(param.name))
                
                # Value
                self.table.setItem(row, 1, QTableWidgetItem(str(param.value)))
                
                # Unit
                self.table.setItem(row, 2, QTableWidgetItem(param.unit or ""))
                
                # Range
                range_str = f"{param.min_value or 0}-{param.max_value or 100}"
                self.table.setItem(row, 3, QTableWidgetItem(range_str))
                
                # Description
                self.table.setItem(row, 4, QTableWidgetItem(param.description or ""))
                
                # Action buttons
                action_widget = QWidget()
                action_layout = QHBoxLayout(action_widget)
                action_layout.setContentsMargins(2, 2, 2, 2)
                
                edit_btn = QPushButton("")
                edit_btn.setIconSize(QSize(23, 23))
                edit_btn.setIcon(QIcon(":/icons/icons/engineering.png"))
                edit_btn.clicked.connect(lambda checked=False, p=param: self._edit_parameter(p))
                action_layout.addWidget(edit_btn)
                
                delete_btn = QPushButton("")
                delete_btn.setIconSize(QSize(23, 23))
                delete_btn.setIcon(QIcon(":/icons/icons/bin.png"))
                delete_btn.clicked.connect(lambda checked=False, p=param: self._delete_parameter(p))
                action_layout.addWidget(delete_btn)
                
                self.table.setCellWidget(row, 5, action_widget)
            
            session.close()
            logger.info(f"Loaded {len(parameters)} parameters from database")
            
        except Exception as e:
            logger.error(f"Error loading parameters: {e}")
            QMessageBox.critical(
                self,
                "Database Error",
                f"Failed to load parameters:\n{str(e)}"
            )
    
    def _add_parameter(self) -> None:
        """Add new parameter"""
        dialog = ParameterDialog(parent=self)
        
        if dialog.exec() == QDialog.Accepted:
            data = dialog.get_data()
            
            try:
                session = get_session()
                
                # Get or create default project
                from core.data.database import Project
                project = session.query(Project).filter_by(is_active=True).first()
                if not project:
                    project = Project(name="Default Project", is_active=True)
                    session.add(project)
                    session.commit()
                
                # Check if parameter already exists
                existing = session.query(Parameter).filter_by(name=data['name']).first()
                if existing:
                    QMessageBox.warning(
                        self,
                        "Duplicate Parameter",
                        f"Parameter '{data['name']}' already exists!"
                    )
                    session.close()
                    return
                
                # Create new parameter
                param = Parameter(
                    project_id=project.id,
                    name=data['name'],
                    value=data['value'],
                    unit=data['unit'],
                    min_value=data['min_value'],
                    max_value=data['max_value'],
                    description=data['description']
                )
                
                session.add(param)
                session.commit()
                session.close()
                
                logger.info(f"Added parameter: {data['name']}")
                QMessageBox.information(
                    self,
                    "Success",
                    f"Parameter '{data['name']}' added successfully!"
                )
                
                # Reload table
                self._load_parameters()
                
            except Exception as e:
                logger.error(f"Error adding parameter: {e}")
                QMessageBox.critical(
                    self,
                    "Database Error",
                    f"Failed to add parameter:\n{str(e)}"
                )
    
    def _edit_parameter(self, parameter: Parameter) -> None:
        """Edit existing parameter"""
        dialog = ParameterDialog(parameter=parameter, parent=self)
        
        if dialog.exec() == QDialog.Accepted:
            data = dialog.get_data()
            
            try:
                session = get_session()
                
                # Get fresh instance
                param = session.query(Parameter).get(parameter.id)
                
                if param:
                    param.name = data['name']
                    param.value = data['value']
                    param.unit = data['unit']
                    param.min_value = data['min_value']
                    param.max_value = data['max_value']
                    param.description = data['description']
                    
                    session.commit()
                    session.close()
                    
                    logger.info(f"Updated parameter: {data['name']}")
                    QMessageBox.information(
                        self,
                        "Success",
                        f"Parameter '{data['name']}' updated successfully!"
                    )
                    
                    # Reload table
                    self._load_parameters()
                else:
                    session.close()
                    QMessageBox.warning(self, "Error", "Parameter not found!")
                
            except Exception as e:
                logger.error(f"Error updating parameter: {e}")
                QMessageBox.critical(
                    self,
                    "Database Error",
                    f"Failed to update parameter:\n{str(e)}"
                )
    
    def _delete_parameter(self, parameter: Parameter) -> None:
        """Delete parameter"""
        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Are you sure you want to delete parameter '{parameter.name}'?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                session = get_session()
                
                # Get fresh instance and delete
                param = session.query(Parameter).get(parameter.id)
                if param:
                    session.delete(param)
                    session.commit()
                    
                    logger.info(f"Deleted parameter: {parameter.name}")
                    QMessageBox.information(
                        self,
                        "Success",
                        f"Parameter '{parameter.name}' deleted successfully!"
                    )
                    
                    # Reload table
                    self._load_parameters()
                
                session.close()
                
            except Exception as e:
                logger.error(f"Error deleting parameter: {e}")
                QMessageBox.critical(
                    self,
                    "Database Error",
                    f"Failed to delete parameter:\n{str(e)}"
                )
    
    def _export_csv(self) -> None:
        """Export parameters to CSV"""
        try:
            from datetime import datetime
            import csv
            from pathlib import Path
            
            # Create export directory
            export_dir = Path("data/exports")
            export_dir.mkdir(parents=True, exist_ok=True)
            
            # Generate filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = export_dir / f"parameters_{timestamp}.csv"
            
            # Get parameters from database
            session = get_session()
            parameters = session.query(Parameter).order_by(Parameter.name).all()
            
            # Write CSV
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['Parameter', 'Value', 'Unit', 'Min', 'Max', 'Description'])
                
                for param in parameters:
                    writer.writerow([
                        param.name,
                        param.value,
                        param.unit or '',
                        param.min_value or 0,
                        param.max_value or 100,
                        param.description or ''
                    ])
            
            session.close()
            
            logger.info(f"Exported {len(parameters)} parameters to {filename}")
            QMessageBox.information(
                self,
                "Export Successful",
                f"Exported {len(parameters)} parameters to:\n{filename}"
            )
            
        except Exception as e:
            logger.error(f"Error exporting parameters: {e}")
            QMessageBox.critical(
                self,
                "Export Error",
                f"Failed to export parameters:\n{str(e)}"
            )

