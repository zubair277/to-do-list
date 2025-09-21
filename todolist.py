import sys
import json
import os
from datetime import datetime
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLineEdit, QPushButton, QListWidget, QListWidgetItem, 
                             QLabel, QCheckBox, QMessageBox)
from PyQt6.QtCore import Qt, QPoint, pyqtSignal
from PyQt6.QtGui import QFont, QFontDatabase, QPixmap, QPainter, QPen, QIcon, QColor

class TaskWidget(QWidget):
    """Custom widget for individual tasks with checkbox functionality"""
    task_changed = pyqtSignal()
    
    def __init__(self, task_text, completed=False, parent=None):
        super().__init__(parent)
        self.task_text = task_text
        self.completed = completed
        self.init_ui()
    
    def init_ui(self):
        """Initialize the task widget UI"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 3, 5, 3)
        layout.setSpacing(8)
        
        # Checkbox for task completion
        self.checkbox = QCheckBox()
        self.checkbox.setChecked(self.completed)
        self.checkbox.setStyleSheet("""
            QCheckBox {
                background: transparent;
                color: #c084fc;
                font-size: 13px;
                spacing: 5px;
            }
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
                border: 2px solid #7c3aed;
                background-color: rgba(30, 27, 75, 0.8);
                border-radius: 6px;
            }
            QCheckBox::indicator:checked {
                background-color: #7c3aed;
                border-color: #8b5cf6;
                image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTIiIGhlaWdodD0iMTIiIHZpZXdCb3g9IjAgMCAxMiAxMiIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHBhdGggZD0iTTEwIDNMNC41IDguNUwyIDYiIHN0cm9rZT0id2hpdGUiIHN0cm9rZS13aWR0aD0iMiIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIiBzdHJva2UtbGluZWpvaW49InJvdW5kIi8+Cjwvc3ZnPgo=);
            }
            QCheckBox::indicator:hover {
                border-color: #a855f7;
                background-color: rgba(120, 58, 237, 0.6);
            }
        """)
        self.checkbox.stateChanged.connect(self.toggle_completion)
        
        # Task label
        self.task_label = QLabel(f"🌙 {self.task_text}")
        self.task_label.setWordWrap(True)
        self.update_label_style()
        
        layout.addWidget(self.checkbox)
        layout.addWidget(self.task_label, 1)  # Give label full space
        
        self.setLayout(layout)
    
    def toggle_completion(self, state):
        """Toggle task completion status"""
        self.completed = state == Qt.CheckState.Checked.value
        self.update_label_style()
        self.task_changed.emit()
    
    def update_label_style(self):
        """Update label style based on completion status"""
        if self.completed:
            self.task_label.setStyleSheet("""
                QLabel {
                    color: #f8fafc;
                    font-size: 13px;
                    background: transparent;
                    text-decoration: line-through;
                    font-family: 'Segoe UI', 'Tahoma', 'Verdana', sans-serif;
                    font-weight: normal;
                }
            """)
        else:
            self.task_label.setStyleSheet("""
                QLabel {
                    color: #c084fc;
                    font-size: 13px;
                    background: transparent;
                    font-family: 'Segoe UI', 'Tahoma', 'Verdana', sans-serif;
                    font-weight: normal;
                }
            """)
    
    def get_task_data(self):
        """Return task data as dictionary"""
        return {
            "text": self.task_text,
            "completed": self.completed
        }

class PixelTodoApp(QWidget):
    def __init__(self):
        super().__init__()
        self.tasks_file = "pixel_todo_tasks.json"
        self.drag_position = QPoint()
        self.init_ui()
        self.load_tasks()
        
    def init_ui(self):
        """Initialize the user interface with nighttime mountain theme"""
        # Window properties
        self.setWindowTitle("🌙 Nighttime To-Do")
        self.setFixedSize(340, 480)  # Slightly larger for better spacing
        
        # Make window frameless and always on top
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | 
                           Qt.WindowType.WindowStaysOnTopHint |
                           Qt.WindowType.Tool)
        
        # Set nighttime mountain themed background
        self.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #1e1b4b, stop:0.3 #312e81, stop:0.7 #4338ca, stop:1 #6366f1);
                color: #c084fc;
                font-family: 'Segoe UI', 'Tahoma', 'Verdana', sans-serif;
                font-size: 11px;
                font-weight: normal;
            }
        """)
        
        # Position window in bottom-right corner
        self.position_window()
        
        # Create main layout
        layout = QVBoxLayout()
        layout.setSpacing(8)
        layout.setContentsMargins(8, 8, 8, 8)
        
        # Header with title and buttons
        header_layout = QHBoxLayout()
        
        title_label = QLabel("🌙 Latifa's Tasks ⭐")
        title_label.setStyleSheet("""
            color: #f8fafc;
            font-weight: bold;
            font-size: 18px;
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 rgba(139, 92, 246, 0.3), stop:1 rgba(236, 72, 153, 0.3));
            border: 2px solid #7c3aed;
            padding: 8px 12px;
            margin: 1px;
            border-radius: 8px;
            font-family: 'Segoe UI', 'Tahoma', 'Verdana', sans-serif;
        """)
        
        # Date display
        today = datetime.now().strftime("%B %d, %Y")
        date_label = QLabel(f"⭐ {today}")
        date_label.setStyleSheet("""
            color: #c084fc;
            font-weight: normal;
            font-size: 10px;
            background: rgba(30, 27, 75, 0.7);
            border: 1px solid #4c1d95;
            padding: 4px 8px;
            margin: 1px;
            border-radius: 6px;
            font-family: 'Segoe UI', 'Tahoma', 'Verdana', sans-serif;
        """)
        date_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Clear completed tasks button
        clear_button = QPushButton("✨")
        clear_button.setFixedSize(24, 24)
        clear_button.setToolTip("Clear completed tasks")
        clear_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(139, 92, 246, 0.4), stop:1 rgba(236, 72, 153, 0.4));
                border: 2px solid #7c3aed;
                color: #f8fafc;
                font-weight: bold;
                font-size: 12px;
                border-radius: 6px;
                font-family: 'Segoe UI', 'Tahoma', 'Verdana', sans-serif;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(139, 92, 246, 0.6), stop:1 rgba(236, 72, 153, 0.6));
                border-color: #8b5cf6;
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(139, 92, 246, 0.8), stop:1 rgba(236, 72, 153, 0.8));
            }
        """)
        clear_button.clicked.connect(self.clear_completed_tasks)
        
        # Close button
        close_button = QPushButton("🌙")
        close_button.setFixedSize(24, 24)
        close_button.setToolTip("Close application")
        close_button.setStyleSheet("""
            QPushButton {
                background: rgba(30, 27, 75, 0.8);
                border: 2px solid #4c1d95;
                color: #c084fc;
                font-weight: bold;
                font-size: 12px;
                border-radius: 6px;
                font-family: 'Segoe UI', 'Tahoma', 'Verdana', sans-serif;
            }
            QPushButton:hover {
                background: rgba(76, 29, 149, 0.8);
                border-color: #7c3aed;
            }
            QPushButton:pressed {
                background: rgba(124, 58, 237, 0.8);
            }
        """)
        close_button.clicked.connect(self.close)
        
        header_layout.addWidget(title_label)
        header_layout.addWidget(date_label)
        header_layout.addStretch()
        header_layout.addWidget(clear_button)
        header_layout.addWidget(close_button)
        
        # Input field for new tasks
        self.task_input = QLineEdit()
        self.task_input.setPlaceholderText("Enter new task... 🌙")
        self.task_input.setStyleSheet("""
            QLineEdit {
                background: rgba(30, 27, 75, 0.8);
                border: 2px solid #4c1d95;
                color: #c084fc;
                padding: 10px;
                font-size: 13px;
                border-radius: 8px;
                font-family: 'Segoe UI', 'Tahoma', 'Verdana', sans-serif;
                font-weight: normal;
            }
            QLineEdit:focus {
                border-color: #7c3aed;
                background: rgba(76, 29, 149, 0.6);
            }
            QLineEdit::placeholder {
                color: rgba(192, 132, 252, 0.6);
            }
        """)
        self.task_input.returnPressed.connect(self.add_task)
        
        # Add button
        add_button = QPushButton("⭐ ADD TASK ⭐")
        add_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(139, 92, 246, 0.4), stop:1 rgba(236, 72, 153, 0.4));
                color: #f8fafc;
                border: 2px solid #7c3aed;
                padding: 10px;
                font-weight: bold;
                font-size: 12px;
                border-radius: 8px;
                font-family: 'Segoe UI', 'Tahoma', 'Verdana', sans-serif;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(139, 92, 246, 0.6), stop:1 rgba(236, 72, 153, 0.6));
                border-color: #8b5cf6;
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(139, 92, 246, 0.8), stop:1 rgba(236, 72, 153, 0.8));
            }
        """)
        add_button.clicked.connect(self.add_task)
        
        # Task list widget
        self.task_list = QListWidget()
        self.task_list.setStyleSheet("""
            QListWidget {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(30, 27, 75, 0.9), stop:0.5 rgba(67, 56, 202, 0.7), stop:1 rgba(30, 27, 75, 0.9));
                border: 2px solid #4c1d95;
                border-radius: 8px;
                color: #c084fc;
                font-family: 'Segoe UI', 'Tahoma', 'Verdana', sans-serif;
                outline: none;
            }
            QListWidget::item {
                background: rgba(30, 27, 75, 0.6);
                border: 1px solid rgba(124, 58, 237, 0.5);
                margin: 2px;
                padding: 2px;
                border-radius: 6px;
                color: #c084fc;
                font-size: 13px;
                font-weight: normal;
            }
            QListWidget::item:hover {
                background: rgba(76, 29, 149, 0.7);
                border-color: #7c3aed;
            }
            QListWidget::item:selected {
                background: rgba(124, 58, 237, 0.6);
                border-color: #8b5cf6;
            }
        """)
        
        # Set background image
        self.set_background_image()
        
        # Add double-click to delete functionality
        self.task_list.itemDoubleClicked.connect(self.delete_task)
        
        # Task counter
        self.task_counter = QLabel("⭐ 0 tasks total")
        self.task_counter.setStyleSheet("""
            color: #f8fafc;
            font-size: 11px;
            font-weight: bold;
            margin-top: 4px;
            font-family: 'Segoe UI', 'Tahoma', 'Verdana', sans-serif;
            background: rgba(30, 27, 75, 0.8);
            border: 1px solid #4c1d95;
            padding: 6px;
            border-radius: 6px;
        """)
        self.task_counter.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Add all widgets to layout
        layout.addLayout(header_layout)
        layout.addWidget(self.task_input)
        layout.addWidget(add_button)
        layout.addWidget(self.task_list)
        layout.addWidget(self.task_counter)
        
        self.setLayout(layout)
        
        # Focus on input field when app starts
        self.task_input.setFocus()
    
    def set_background_image(self):
        """Set a background image for the task list"""
        try:
            # Check for background image files in the same directory
            background_files = [
                "background.png", "background.jpg", "background.jpeg", 
                "bg.png", "bg.jpg", "bg.jpeg",
                "todo_bg.png", "todo_bg.jpg", "todo_bg.jpeg"
            ]
            
            background_image = None
            for bg_file in background_files:
                if os.path.exists(bg_file):
                    background_image = bg_file
                    print(f"Found background image: {bg_file}")
                    break
            
            if background_image:
                # Use the found image file with absolute path
                image_path = os.path.abspath(background_image)
                print(f"Using image path: {image_path}")
                
                # Try using a custom QListWidget with paint event
                try:
                    from PyQt6.QtGui import QPixmap
                    pixmap = QPixmap(image_path)
                    if not pixmap.isNull():
                        # Store the pixmap for custom painting
                        self.background_pixmap = pixmap
                        # Create a custom list widget class
                        self._create_custom_list_widget()
                        print("Background image applied successfully using custom paint!")
                    else:
                        print("Failed to load image with QPixmap")
                        self._apply_fallback_background()
                except Exception as e:
                    print(f"Error applying background image with QPixmap: {e}")
                    # Try CSS approach as fallback
                    try:
                        # Simple CSS approach without complex URL formatting
                        self.task_list.setStyleSheet(f"""
                            QListWidget {{
                                background-color: #1e1b4b;
                                border: 2px solid #4c1d95;
                                border-radius: 8px;
                                color: #c084fc;
                                font-family: 'Segoe UI', 'Tahoma', 'Verdana', sans-serif;
                                outline: none;
                            }}
                            QListWidget::item {{
                                background: rgba(30, 27, 75, 0.85);
                                border: 1px solid rgba(124, 58, 237, 0.6);
                                margin: 2px;
                                padding: 2px;
                                border-radius: 6px;
                                color: #c084fc;
                                font-size: 13px;
                                font-weight: normal;
                            }}
                            QListWidget::item:hover {{
                                background: rgba(76, 29, 149, 0.9);
                                border-color: #7c3aed;
                            }}
                            QListWidget::item:selected {{
                                background: rgba(124, 58, 237, 0.8);
                                border-color: #8b5cf6;
                            }}
                        """)
                        print("Applied fallback CSS styling")
                    except Exception as e2:
                        print(f"Error with CSS fallback: {e2}")
                        self._apply_fallback_background()
            else:
                # Fallback to CSS pattern if no image file found
                print("No background image found. Using CSS pattern.")
                self._apply_fallback_background()
            
        except Exception as e:
            print(f"Error in set_background_image: {e}")
            self._apply_fallback_background()
    
    def _create_custom_list_widget(self):
        """Create a custom QListWidget with background image support"""
        from PyQt6.QtWidgets import QListWidget
        from PyQt6.QtGui import QPainter, QPixmap
        from PyQt6.QtCore import Qt
        
        class CustomListWidget(QListWidget):
            def __init__(self, parent=None, background_pixmap=None):
                super().__init__(parent)
                self.background_pixmap = background_pixmap
                self.setStyleSheet("""
                    QListWidget {
                        border: 2px solid #4c1d95;
                        border-radius: 8px;
                        color: #c084fc;
                        font-family: 'Segoe UI', 'Tahoma', 'Verdana', sans-serif;
                        outline: none;
                    }
                    QListWidget::item {
                        background: rgba(30, 27, 75, 0.85);
                        border: 1px solid rgba(124, 58, 237, 0.6);
                        margin: 2px;
                        padding: 2px;
                        border-radius: 6px;
                        color: #c084fc;
                        font-size: 13px;
                        font-weight: normal;
                    }
                    QListWidget::item:hover {
                        background: rgba(76, 29, 149, 0.9);
                        border-color: #7c3aed;
                    }
                    QListWidget::item:selected {
                        background: rgba(124, 58, 237, 0.8);
                        border-color: #8b5cf6;
                    }
                """)
            
            def paintEvent(self, event):
                painter = QPainter(self.viewport())
                if self.background_pixmap and not self.background_pixmap.isNull():
                    # Scale the pixmap to fit the widget
                    scaled_pixmap = self.background_pixmap.scaled(
                        self.size(), 
                        Qt.AspectRatioMode.KeepAspectRatioByExpanding, 
                        Qt.TransformationMode.SmoothTransformation
                    )
                    # Center the pixmap
                    x = (self.width() - scaled_pixmap.width()) // 2
                    y = (self.height() - scaled_pixmap.height()) // 2
                    painter.drawPixmap(x, y, scaled_pixmap)
                else:
                    # Fallback background
                    painter.fillRect(self.rect(), Qt.GlobalColor.darkBlue)
                super().paintEvent(event)
        
        # Replace the current task_list with custom one
        old_list = self.task_list
        self.task_list = CustomListWidget(self, self.background_pixmap)
        
        # Copy properties from old list
        self.task_list.setGeometry(old_list.geometry())
        self.task_list.itemDoubleClicked.connect(self.delete_task)
        
        # Replace in layout
        layout = self.layout()
        for i in range(layout.count()):
            if layout.itemAt(i).widget() == old_list:
                layout.removeWidget(old_list)
                layout.insertWidget(i, self.task_list)
                break
        
        old_list.deleteLater()
    
    def _apply_fallback_background(self):
        """Apply fallback CSS background pattern"""
        self.task_list.setStyleSheet(f"""
                    QListWidget {{
                        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                            stop:0 rgba(30, 27, 75, 0.9), stop:0.3 rgba(67, 56, 202, 0.7), 
                            stop:0.7 rgba(99, 102, 241, 0.5), stop:1 rgba(30, 27, 75, 0.9)),
                            radial-gradient(circle at 20% 20%, rgba(248, 250, 252, 0.1) 1px, transparent 1px),
                            radial-gradient(circle at 80% 40%, rgba(192, 132, 252, 0.15) 1px, transparent 1px),
                            radial-gradient(circle at 30% 70%, rgba(248, 250, 252, 0.08) 1px, transparent 1px),
                            radial-gradient(circle at 90% 80%, rgba(139, 92, 246, 0.12) 1px, transparent 1px),
                            radial-gradient(circle at 60% 30%, rgba(248, 250, 252, 0.1) 1px, transparent 1px);
                        background-size: 100% 100%, 60px 60px, 80px 80px, 50px 50px, 70px 70px, 90px 90px;
                        border: 2px solid #4c1d95;
                        border-radius: 8px;
                        color: #c084fc;
                        font-family: 'Segoe UI', 'Tahoma', 'Verdana', sans-serif;
                        outline: none;
                    }}
                    QListWidget::item {{
                        background: rgba(30, 27, 75, 0.8);
                        border: 1px solid rgba(124, 58, 237, 0.5);
                        margin: 2px;
                        padding: 2px;
                        border-radius: 6px;
                        color: #c084fc;
                        font-size: 13px;
                        font-weight: normal;
                    }}
                    QListWidget::item:hover {{
                        background: rgba(76, 29, 149, 0.8);
                        border-color: #7c3aed;
                    }}
                    QListWidget::item:selected {{
                        background: rgba(124, 58, 237, 0.7);
                        border-color: #8b5cf6;
                    }}
                """)
    
    def position_window(self):
        """Position the window in the bottom-right corner of the screen"""
        try:
            screen = QApplication.primaryScreen()
            if screen:
                screen_geometry = screen.geometry()
                # Calculate position for bottom-right corner with margin
                x = screen_geometry.width() - self.width() - 20
                y = screen_geometry.height() - self.height() - 80  # Extra margin for taskbar
                self.move(max(0, x), max(0, y))  # Ensure position is not negative
            else:
                # Fallback position if no screen detected
                self.move(100, 100)
        except Exception as e:
            print(f"Error positioning window: {e}")
            self.move(100, 100)  # Fallback position
    
    def add_task(self):
        """Add a new task to the list"""
        task_text = self.task_input.text().strip()
        
        if task_text:  # Only add if text is not empty
            if len(task_text) > 100:  # Limit task length
                QMessageBox.warning(self, "Task Too Long", 
                                  "Please keep tasks under 100 characters.")
                return
            
            self.create_task_item(task_text, False)
            self.task_input.clear()
            self.save_tasks()
            self.update_task_counter()
            self.task_input.setFocus()
        else:
            # Gentle reminder if empty
            self.task_input.setPlaceholderText("Please enter a task first! 🌙")
    
    def create_task_item(self, task_text, completed=False):
        """Create a task item with checkbox functionality"""
        try:
            # Create custom task widget
            task_widget = TaskWidget(task_text, completed)
            task_widget.task_changed.connect(self.on_task_changed)
            
            # Create list item
            item = QListWidgetItem()
            item.setSizeHint(task_widget.sizeHint())
            
            # Add to list
            self.task_list.addItem(item)
            self.task_list.setItemWidget(item, task_widget)
            
        except Exception as e:
            print(f"Error creating task item: {e}")
            QMessageBox.warning(self, "Error", "Failed to create task item.")
    
    def on_task_changed(self):
        """Handle task completion change"""
        self.save_tasks()
        self.update_task_counter()
    
    def delete_task(self, item):
        """Delete a task when double-clicked"""
        try:
            reply = QMessageBox.question(self, "Delete Task", 
                                       "Are you sure you want to delete this task?",
                                       QMessageBox.StandardButton.Yes | 
                                       QMessageBox.StandardButton.No)
            
            if reply == QMessageBox.StandardButton.Yes:
                row = self.task_list.row(item)
                self.task_list.takeItem(row)
                self.save_tasks()
                self.update_task_counter()
        except Exception as e:
            print(f"Error deleting task: {e}")
            QMessageBox.warning(self, "Error", "Failed to delete task.")
    
    def clear_completed_tasks(self):
        """Clear all completed tasks"""
        try:
            completed_count = 0
            for i in range(self.task_list.count() - 1, -1, -1):
                item = self.task_list.item(i)
                task_widget = self.task_list.itemWidget(item)
                if isinstance(task_widget, TaskWidget) and task_widget.completed:
                    self.task_list.takeItem(i)
                    completed_count += 1
            
            if completed_count > 0:
                self.save_tasks()
                self.update_task_counter()
                QMessageBox.information(self, "Tasks Cleared", 
                                      f"Cleared {completed_count} completed task(s)! ✨")
            else:
                QMessageBox.information(self, "No Tasks", 
                                      "No completed tasks to clear! 🌙")
        except Exception as e:
            print(f"Error clearing tasks: {e}")
            QMessageBox.warning(self, "Error", "Failed to clear completed tasks.")
    
    def update_task_counter(self):
        """Update the task counter display"""
        try:
            total_tasks = self.task_list.count()
            completed_tasks = 0
            
            for i in range(total_tasks):
                item = self.task_list.item(i)
                task_widget = self.task_list.itemWidget(item)
                if isinstance(task_widget, TaskWidget) and task_widget.completed:
                    completed_tasks += 1
            
            pending_tasks = total_tasks - completed_tasks
            
            if total_tasks == 0:
                self.task_counter.setText("⭐ 0 tasks total ⭐")
            else:
                self.task_counter.setText(
                    f"⭐ {total_tasks} total • {pending_tasks} pending • {completed_tasks} done ⭐"
                )
        except Exception as e:
            print(f"Error updating counter: {e}")
            self.task_counter.setText("⭐ Task counter error")
    
    def save_tasks(self):
        """Save current tasks to a JSON file"""
        try:
            tasks = []
            for i in range(self.task_list.count()):
                item = self.task_list.item(i)
                task_widget = self.task_list.itemWidget(item)
                
                if isinstance(task_widget, TaskWidget):
                    tasks.append(task_widget.get_task_data())
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(os.path.abspath(self.tasks_file)), exist_ok=True)
            
            with open(self.tasks_file, 'w', encoding='utf-8') as f:
                json.dump(tasks, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            print(f"Error saving tasks: {e}")
            QMessageBox.warning(self, "Save Error", 
                              "Failed to save tasks. Changes may be lost.")
    
    def load_tasks(self):
        """Load tasks from JSON file on startup"""
        if not os.path.exists(self.tasks_file):
            self.update_task_counter()
            return
            
        try:
            with open(self.tasks_file, 'r', encoding='utf-8') as f:
                tasks = json.load(f)
            
            # Handle both old format (strings) and new format (objects)
            for task in tasks:
                if isinstance(task, str):
                    # Old format - just text
                    self.create_task_item(task, False)
                elif isinstance(task, dict):
                    # New format - text and completion status
                    task_text = task.get("text", "").strip()
                    if task_text:  # Only add non-empty tasks
                        self.create_task_item(task_text, task.get("completed", False))
            
            self.update_task_counter()
            
        except json.JSONDecodeError as e:
            print(f"JSON decode error: {e}")
            QMessageBox.warning(self, "Load Error", 
                              "Task file is corrupted. Starting with empty list.")
        except Exception as e:
            print(f"Error loading tasks: {e}")
            QMessageBox.warning(self, "Load Error", 
                              "Failed to load saved tasks.")
    
    # Mouse events for dragging functionality
    def mousePressEvent(self, event):
        """Handle mouse press for dragging"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()
    
    def mouseMoveEvent(self, event):
        """Handle mouse move for dragging"""
        if (event.buttons() == Qt.MouseButton.LeftButton and 
            not self.drag_position.isNull()):
            # Move window to new position
            new_position = event.globalPosition().toPoint() - self.drag_position
            self.move(new_position)
            event.accept()
    
    def closeEvent(self, event):
        """Save tasks when closing the application"""
        try:
            self.save_tasks()
            event.accept()
        except Exception as e:
            print(f"Error during close: {e}")
            event.accept()  # Still close even if save fails
    
    def keyPressEvent(self, event):
        """Handle keyboard shortcuts"""
        if event.key() == Qt.Key.Key_Escape:
            self.close()
        elif event.key() == Qt.Key.Key_Delete:
            # Delete selected task
            current_item = self.task_list.currentItem()
            if current_item:
                self.delete_task(current_item)
        else:
            super().keyPressEvent(event)

def main():
    """Main function to run the application"""
    try:
        app = QApplication(sys.argv)
        
        # Set application properties
        app.setApplicationName("Nighttime To-Do List")
        app.setApplicationVersion("3.0")
        app.setOrganizationName("MountainApps")
        
        # Enable high DPI support (PyQt6 compatible)
        try:
            app.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling, True)
            app.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps, True)
        except AttributeError:
            # These attributes may not be available in all PyQt6 versions
            pass
        
        # Create and show the main window
        window = PixelTodoApp()
        window.show()
        
        # Run the application
        sys.exit(app.exec())
        
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()