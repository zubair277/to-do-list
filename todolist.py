import sys
import json
import os
from datetime import datetime
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLineEdit, QPushButton, QListWidget, QListWidgetItem, 
                             QLabel, QCheckBox, QMessageBox, QGraphicsDropShadowEffect)
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
        # Helper to fetch colors from the top-level window palette safely
        def palette_color(name, default):
            try:
                win = self.window()
                colors = getattr(win, 'colors', None)
                if isinstance(colors, dict) and name in colors:
                    return colors[name]
            except Exception:
                pass
            return default

        self._palette_color = palette_color
        
        # Pastel card background for each task
        self.setStyleSheet(f"""
            QWidget {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 {self._palette_color('lavender', '#D9B8F2')},
                    stop:1 {self._palette_color('pink', '#F7BFD0')});
                border: 1px solid rgba(196, 154, 133, 0.5);
                border-radius: 12px;
            }}
        """)

        # Subtle glow effect; intensify on hover via enter/leave events
        self._glow = QGraphicsDropShadowEffect(self)
        self._glow.setBlurRadius(10)
        self._glow.setOffset(0, 2)
        self._glow.setColor(QColor(self._palette_color('sky', '#B8D8FF')))
        self.setGraphicsEffect(self._glow)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 3, 5, 3)
        layout.setSpacing(8)
        
        # Checkbox for task completion
        self.checkbox = QCheckBox()
        self.checkbox.setChecked(self.completed)
        self.checkbox.setStyleSheet(f"""
            QCheckBox {{
                background: transparent;
                color: {self._palette_color('taskText', '#F5F3EF')};
                font-size: 13px;
                spacing: 5px;
                font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Display', 'Helvetica Neue', Arial, sans-serif;
            }}
            QCheckBox::indicator {{
                width: 18px;
                height: 18px;
                border: 2px solid {self._palette_color('brown', '#C49A85')};
                background-color: {self._palette_color('cream', '#FFFDF7')};
                border-radius: 9px;
            }}
            QCheckBox::indicator:checked {{
                background-color: {self._palette_color('lavender', '#D9B8F2')};
                border-color: {self._palette_color('brown', '#C49A85')};
                image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTYiIGhlaWdodD0iMTYiIHZpZXdCb3g9IjAgMCAyNCAyNCIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHBhdGggZD0iTTEyIDJMMTQuOTQyIDguODI0N0gyMi4xODZMMTYuMzkyIDEyLjk1MkwxOC45NDIgMjAuMTc1TDEyIDE1Ljc3MUw1LjA1NzcgMjAuMTc1TDcuNjA4NyAxMi45NTJMMC44MTM5NSA4LjgyNDdINy4wNTc4TDEyIDJaIiBmaWxsPSIjRkZGN0ZFIi8+Cjwvc3ZnPgo=);
            }}
            QCheckBox::indicator:hover {{
                border-color: {self._palette_color('yellow', '#FBE89B')};
                background-color: {self._palette_color('pink', '#F7BFD0')};
            }}
        """)
        self.checkbox.stateChanged.connect(self.toggle_completion)
        
        # Task label
        self.task_label = QLabel(f"🐰 {self.task_text}")
        self.task_label.setWordWrap(True)
        self.task_label.setMinimumHeight(20)
        self.task_label.setMaximumHeight(60)
        self.task_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        self.update_label_style()
        
        layout.addWidget(self.checkbox)
        layout.addWidget(self.task_label, 1)  # Give label full space
        
        self.setLayout(layout)

    def enterEvent(self, event):
        if hasattr(self, '_glow'):
            self._glow.setBlurRadius(18)
        super().enterEvent(event)

    def leaveEvent(self, event):
        if hasattr(self, '_glow'):
            self._glow.setBlurRadius(10)
        super().leaveEvent(event)
    
    def toggle_completion(self, state):
        """Toggle task completion status"""
        self.completed = state == Qt.CheckState.Checked.value
        self.update_label_style()
        self.task_changed.emit()
    
    def update_label_style(self):
        """Update label style based on completion status"""
        if self.completed:
            self.task_label.setStyleSheet(f"""
                QLabel {{
                    color: {self._palette_color('taskTextCompleted', '#8A776E')};
                    font-size: 13px;
                    background: transparent;
                    text-decoration: line-through;
                    font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Display', 'Helvetica Neue', Arial, sans-serif;
                    font-weight: normal;
                }}
            """)
        else:
            self.task_label.setStyleSheet(f"""
                QLabel {{
                    color: {self._palette_color('taskText', '#4A3B34')};
                    font-size: 13px;
                    background: transparent;
                    font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Display', 'Helvetica Neue', Arial, sans-serif;
                    font-weight: normal;
                }}
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
        self._allow_close = False
        # Pastel theme palette
        self.colors = {
            "grass": "#B8E2A8",       # soft grass green
            "brown": "#C49A85",       # warm brown (borders/accents)
            "cream": "#FFFDF7",       # creamy white (base)
            "yellow": "#FBE89B",      # gentle yellow (accent/hover)
            "pink": "#F7BFD0",        # pastel pink (accent)
            "lavender": "#D9B8F2",    # light lavender (accent)
            "sky": "#B8D8FF",        # sky blue (accent)
            "textDark": "#4A3B34",    # darker brown for readable text
            "textMuted": "#6B5A52",    # muted brown/gray for secondary
            "taskText": "#F5F3EF",    # soft white for task text
            "taskTextCompleted": "#E8E3DC"  # softer white for completed
        }
        self.init_ui()
        self.load_tasks()
        
    def init_ui(self):
        """Initialize the user interface with nighttime mountain theme"""
        # Window properties
        self.setWindowTitle("🌙 Nighttime To-Do")
        self.setFixedSize(340, 480)  # Slightly larger for better spacing
        
        # Use a normal window type for stability on macOS
        self.setWindowFlags(Qt.WindowType.Window)
        
        # Soft pastel meadow background and base text color
        self.setStyleSheet(f"""
            QWidget {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {self.colors['cream']}, stop:0.5 {self.colors['grass']}, stop:1 {self.colors['pink']});
                color: {self.colors['textDark']};
                font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Display', 'Helvetica Neue', Arial, sans-serif;
                font-size: 11px;
                font-weight: normal;
            }}
        """)
        
        # Position window in bottom-right corner
        self.position_window()
        
        # Create main layout
        layout = QVBoxLayout()
        layout.setSpacing(8)
        layout.setContentsMargins(8, 8, 8, 8)
        
        # Header with title and buttons
        header_layout = QHBoxLayout()
        
        title_label = QLabel("🐰 Latifa's Tasks 🐻")
        title_label.setStyleSheet(f"""
            color: {self.colors['textDark']};
            font-weight: bold;
            font-size: 18px;
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 {self.colors['yellow']}, stop:1 {self.colors['pink']});
            border: 2px solid {self.colors['brown']};
            padding: 8px 12px;
            margin: 1px;
            border-radius: 8px;
            font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Display', 'Helvetica Neue', Arial, sans-serif;
        """)
        
        # Date display
        today = datetime.now().strftime("%B %d, %Y")
        date_label = QLabel(f"🌼 {today}")
        date_label.setStyleSheet(f"""
            color: {self.colors['textMuted']};
            font-weight: normal;
            font-size: 10px;
            background: {self.colors['cream']};
            border: 1px solid {self.colors['brown']};
            padding: 4px 8px;
            margin: 1px;
            border-radius: 6px;
            font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Display', 'Helvetica Neue', Arial, sans-serif;
        """)
        date_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Clear completed tasks button
        clear_button = QPushButton("🧹")
        clear_button.setFixedSize(24, 24)
        clear_button.setToolTip("Clear completed tasks")
        clear_button.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {self.colors['lavender']}, stop:1 {self.colors['pink']});
                border: 2px solid {self.colors['brown']};
                color: {self.colors['textDark']};
                font-weight: bold;
                font-size: 12px;
                border-radius: 6px;
                font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Display', 'Helvetica Neue', Arial, sans-serif;
            }}
            QPushButton:hover {{
                background: {self.colors['yellow']};
                border-color: {self.colors['brown']};
            }}
            QPushButton:pressed {{
                background: {self.colors['lavender']};
            }}
        """)
        clear_button.clicked.connect(self.clear_completed_tasks)
        
        # Close button
        close_button = QPushButton("🌸")
        close_button.setFixedSize(24, 24)
        close_button.setToolTip("Close application")
        close_button.setStyleSheet(f"""
            QPushButton {{
                background: {self.colors['cream']};
                border: 2px solid {self.colors['brown']};
                color: {self.colors['textDark']};
                font-weight: bold;
                font-size: 12px;
                border-radius: 6px;
                font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Display', 'Helvetica Neue', Arial, sans-serif;
            }}
            QPushButton:hover {{
                background: {self.colors['yellow']};
                border-color: {self.colors['brown']};
            }}
            QPushButton:pressed {{
                background: {self.colors['pink']};
            }}
        """)
        close_button.clicked.connect(self.safe_close)
        
        header_layout.addWidget(title_label)
        header_layout.addWidget(date_label)
        header_layout.addStretch()
        header_layout.addWidget(clear_button)
        header_layout.addWidget(close_button)
        
        # Input field for new tasks
        self.task_input = QLineEdit()
        self.task_input.setPlaceholderText("Enter new task... 🌙")
        self.task_input.setStyleSheet(f"""
            QLineEdit {{
                background: {self.colors['cream']};
                border: 2px solid {self.colors['brown']};
                color: {self.colors['textDark']};
                padding: 10px;
                font-size: 13px;
                border-radius: 8px;
                font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Display', 'Helvetica Neue', Arial, sans-serif;
                font-weight: normal;
            }}
            QLineEdit:focus {{
                border-color: {self.colors['lavender']};
                background: {self.colors['yellow']};
            }}
            QLineEdit::placeholder {{
                color: {self.colors['textMuted']};
            }}
        """)
        self.task_input.returnPressed.connect(self.add_task)
        
        # Add button
        add_button = QPushButton("⭐ Add Task ⭐")
        add_button.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {self.colors['grass']}, stop:1 {self.colors['lavender']});
                color: {self.colors['textDark']};
                border: 2px solid {self.colors['brown']};
                padding: 10px;
                font-weight: bold;
                font-size: 12px;
                border-radius: 8px;
                font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Display', 'Helvetica Neue', Arial, sans-serif;
            }}
            QPushButton:hover {{
                background: {self.colors['yellow']};
                border-color: {self.colors['brown']};
            }}
            QPushButton:pressed {{
                background: {self.colors['pink']};
            }}
        """)
        add_button.clicked.connect(self.add_task)
        
        # Task list widget
        self.task_list = QListWidget()
        self.task_list.setStyleSheet(f"""
            QListWidget {{
                background: transparent;
                border: 2px solid {self.colors['brown']};
                border-radius: 8px;
                color: {self.colors['textDark']};
                font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Display', 'Helvetica Neue', Arial, sans-serif;
                outline: none;
            }}
            QListWidget::item {{
                background: transparent;
                border: none;
                margin: 6px 4px;
                padding: 0px;
                border-radius: 12px;
                color: {self.colors['textDark']};
                font-size: 13px;
                font-weight: normal;
            }}
            QListWidget::item:hover {{
                background: transparent;
            }}
            QListWidget::item:selected {{
                background: transparent;
                border: none;
            }}
        """)
        
        # Set background image
        self.set_background_image()
        
        # Optional: disable double-click delete to avoid accidental closures
        # self.task_list.itemDoubleClicked.connect(self.delete_task)
        
        # Task counter
        self.task_counter = QLabel("⭐ 0 tasks total")
        self.task_counter.setStyleSheet(f"""
            color: {self.colors['textDark']};
            font-size: 11px;
            font-weight: bold;
            margin-top: 4px;
            font-family: 'Segoe UI', 'Tahoma', 'Verdana', sans-serif;
            background: {self.colors['cream']};
            border: 1px solid {self.colors['brown']};
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
                                font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Display', 'Helvetica Neue', Arial, sans-serif;
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
                        font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Display', 'Helvetica Neue', Arial, sans-serif;
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
        if old_list:
            self.task_list.setGeometry(old_list.geometry())
        self.task_list.itemDoubleClicked.connect(self.delete_task)
        
        # Replace in layout
        layout = self.layout()
        if layout:
            for i in range(layout.count()):
                item = layout.itemAt(i)
                if item and item.widget() == old_list:
                    layout.removeWidget(old_list)
                    layout.insertWidget(i, self.task_list)
                    break
        
        if old_list:
            old_list.deleteLater()
    
    def _apply_fallback_background(self):
        """Apply fallback CSS background pattern"""
        self.task_list.setStyleSheet(f"""
                    QListWidget {{
                        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                            stop:0 {self.colors['cream']}, stop:0.5 {self.colors['grass']}, stop:1 {self.colors['lavender']}),
                            radial-gradient(circle at 20% 20%, rgba(247, 191, 208, 0.25) 2px, transparent 2px),
                            radial-gradient(circle at 80% 40%, rgba(217, 184, 242, 0.25) 2px, transparent 2px),
                            radial-gradient(circle at 30% 70%, rgba(251, 232, 155, 0.25) 2px, transparent 2px);
                        background-size: 100% 100%, 60px 60px, 80px 80px, 70px 70px;
                        border: 2px solid {self.colors['brown']};
                        border-radius: 8px;
                        color: {self.colors['textDark']};
                        font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Display', 'Helvetica Neue', Arial, sans-serif;
                        outline: none;
                    }}
                    QListWidget::item {{
                        background: rgba(255, 253, 247, 0.8);
                        border: 1px solid rgba(196, 154, 133, 0.7);
                        margin: 2px;
                        padding: 2px;
                        border-radius: 6px;
                        color: {self.colors['textDark']};
                        font-size: 13px;
                        font-weight: normal;
                    }}
                    QListWidget::item:hover {{
                        background: {self.colors['yellow']};
                        border-color: {self.colors['brown']};
                    }}
                    QListWidget::item:selected {{
                        background: {self.colors['lavender']};
                        border-color: {self.colors['brown']};
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
            task_widget = TaskWidget(task_text, completed, self)
            task_widget.task_changed.connect(self.on_task_changed)
            
            # Create list item
            item = QListWidgetItem()
            # Calculate proper size hint for the task widget
            size_hint = task_widget.sizeHint()
            # Ensure minimum height for text visibility
            if size_hint.height() < 30:
                size_hint.setHeight(30)
            item.setSizeHint(size_hint)
            
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
            # Prevent accidental closes; only allow when explicitly requested
            if not self._allow_close:
                event.ignore()
                self.show()
                return
            self.save_tasks()
            event.accept()
        except Exception as e:
            print(f"Error during close: {e}")
            event.accept()  # Still close even if save fails

    def safe_close(self):
        """Allow closing explicitly via close button"""
        self._allow_close = True
        self.close()
    
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