#!/usr/bin/env python3
"""
PDSA Games Portal Dashboard
Central hub for accessing all algorithm visualization games
"""
import sys
import os
import logging
import subprocess
import json
import sqlite3
from datetime import datetime
import random
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QGraphicsDropShadowEffect, QScrollArea, QSizePolicy, QGridLayout, 
    QMessageBox, QComboBox, QLineEdit, QInputDialog, QTabWidget, QToolButton,
    QDialog, QFormLayout, QSpacerItem, QCheckBox, QSlider, QMenu, QAction, QColorDialog,
    QStackedWidget, QProgressBar, QTableWidget, QTableWidgetItem, QHeaderView, QGroupBox,
    QRadioButton, QButtonGroup, QStyleFactory, QSystemTrayIcon, QCalendarWidget
)
from PyQt5.QtCore import (
    Qt, QSize, QPropertyAnimation, QEasingCurve, QParallelAnimationGroup, 
    QTimer, QPoint, pyqtSignal, QThread, QSettings, QDate, QSequentialAnimationGroup,
    QVariantAnimation
)
from PyQt5.QtGui import (
    QColor, QFont, QIcon, QPixmap, QPainter, QBrush, QLinearGradient, 
    QPalette, QPen, QCursor, QRadialGradient, QFontDatabase
)

# Try different import approaches for QtChart
try:
    from PyQt5.QtChart import QChart, QChartView, QBarSet, QBarSeries, QValueAxis, QPieSeries
except ImportError:
    try:
        from PyQt5 import QtChart
        QChart = QtChart.QChart
        QChartView = QtChart.QChartView
        QBarSet = QtChart.QBarSet
        QBarSeries = QtChart.QBarSeries
        QValueAxis = QtChart.QValueAxis
        QPieSeries = QtChart.QPieSeries
    except ImportError:
        # Fallback if QtChart is not available - we'll implement alternatives
        class QtChartMissing:
            def __init__(self, *args, **kwargs):
                pass
                
            def __getattr__(self, name):
                return lambda *args, **kwargs: None
                
        QChart = QChartView = QBarSet = QBarSeries = QValueAxis = QPieSeries = QtChartMissing

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='pdsa_games_portal.log',
    filemode='a'
)
logger = logging.getLogger(__name__)

# App settings 
SETTINGS = QSettings("PdsaGamesPortal", "Dashboard")

class GameCard(QFrame):
    """Card widget for displaying a game with its information"""
    def __init__(self, title, icon_text, description, color, launch_function):
        super().__init__()
        # Create a CSS-safe object name without special characters
        safe_name = title.replace(' ', '').replace("'", "").replace('"', '')
        self.setObjectName(f"{safe_name}Card")
        self.setStyleSheet(f"""
            #{safe_name}Card {{
                background-color: rgba(33, 33, 33, 0.7);
                border: 1px solid {color};
                border-radius: 20px;
                padding: 10px;
            }}
            #{safe_name}Card:hover {{
                background-color: rgba(45, 45, 45, 0.8);
                border: 2px solid {color};
            }}
        """)
        
        # Set up for animations
        self.color = color
        self.default_elevation = 5
        self.hover_elevation = 15
        self.elevation = self.default_elevation
        
        self.setup_ui(title, icon_text, description, color, launch_function)
        
        # Apply initial shadow
        self.update_shadow(self.default_elevation)
    
    def setup_ui(self, title, icon_text, description, color, launch_function):
        """Setup the UI components for the game card"""
        card_layout = QVBoxLayout(self)
        card_layout.setContentsMargins(20, 20, 20, 20)
        card_layout.setSpacing(15)
        
        # Game icon with color background
        icon_label = QLabel(icon_text)
        icon_label.setFixedSize(80, 80)
        icon_label.setObjectName("gameIcon")
        icon_label.setStyleSheet(f"""
            #gameIcon {{
                font-size: 36px;
                background-color: {color};
                color: white;
                border-radius: 40px;
                margin-bottom: 10px;
            }}
        """)
        icon_label.setAlignment(Qt.AlignCenter)
        
        # Add shadow effect
        icon_shadow = QGraphicsDropShadowEffect()
        icon_shadow.setBlurRadius(15)
        icon_shadow.setColor(QColor(color))
        icon_shadow.setOffset(0, 0)
        icon_label.setGraphicsEffect(icon_shadow)
        
        card_layout.addWidget(icon_label, 0, Qt.AlignCenter)
        
        # Game title
        title_label = QLabel(title)
        title_label.setObjectName("gameTitle")
        title_label.setStyleSheet("""
            #gameTitle {
                color: white;
                font-size: 18px;
                font-weight: bold;
                margin-top: 5px;
            }
        """)
        title_label.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(title_label)
        
        # Game description
        desc_label = QLabel(description)
        desc_label.setObjectName("gameDescription")
        desc_label.setStyleSheet("""
            #gameDescription {
                color: #BBBBBB;
                font-size: 14px;
            }
        """)
        desc_label.setWordWrap(True)
        desc_label.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(desc_label)
        
        # Spacer to push the button to the bottom
        card_layout.addStretch()
        
        # Launch button
        launch_button = QPushButton("START GAME")
        launch_button.setObjectName("launchButton")
        launch_button.setStyleSheet(f"""
            #launchButton {{
                background-color: {color};
                color: white;
                border: none;
                border-radius: 12px;
                padding: 12px 25px;
                font-size: 14px;
                font-weight: bold;
                letter-spacing: 1px;
            }}
            #launchButton:hover {{
                background-color: {self.lighten_color(color)};
            }}
            #launchButton:pressed {{
                background-color: {self.darken_color(color)};
            }}
        """)
        launch_button.clicked.connect(launch_function)
        card_layout.addWidget(launch_button)
    
    def lighten_color(self, color):
        """Return a lighter version of the color for hover state"""
        if color == "#3D5AFE":
            return "#536DFE"
        elif color == "#00B0FF":
            return "#40C4FF"
        elif color == "#FF6D00":
            return "#FF9E40"
        elif color == "#F50057":
            return "#FF4081"
        elif color == "#00C853":
            return "#69F0AE"
        else:
            return color
    
    def darken_color(self, color):
        """Return a darker version of the color for pressed state"""
        if color == "#3D5AFE":
            return "#303F9F"
        elif color == "#00B0FF":
            return "#0091EA"
        elif color == "#FF6D00":
            return "#E65100"
        elif color == "#F50057":
            return "#C51162"
        elif color == "#00C853":
            return "#00B248"
        else:
            return color
        
    def update_shadow(self, elevation):
        """Update the shadow effect based on elevation"""
        effect = QGraphicsDropShadowEffect(self)
        effect.setBlurRadius(elevation)
        effect.setColor(QColor(0, 0, 0, 100))
        effect.setOffset(0, elevation // 2)
        self.setGraphicsEffect(effect)
        self.elevation = elevation
    
    def enterEvent(self, event):
        """Handle mouse enter events with animation"""
        self.animate_shadow(self.hover_elevation)
        super().enterEvent(event)
    
    def leaveEvent(self, event):
        """Handle mouse leave events with animation"""
        self.animate_shadow(self.default_elevation)
        super().leaveEvent(event)
    
    def animate_shadow(self, target_elevation):
        """Animate the shadow effect"""
        self.animation = QPropertyAnimation(self, b"elevation")
        self.animation.setDuration(150)
        self.animation.setStartValue(self.elevation)
        self.animation.setEndValue(target_elevation)
        self.animation.setEasingCurve(QEasingCurve.OutCubic)
        self.animation.valueChanged.connect(lambda v: self.update_shadow(v))
        self.animation.start()
        
    # Property for animation
    @property
    def elevation(self):
        return self._elevation
        
    @elevation.setter
    def elevation(self, elevation):
        self._elevation = elevation
        
    def pulse_animation(self):
        """Create a pulse animation effect"""
        pulse = QPropertyAnimation(self, b"geometry")
        pulse.setDuration(200)
        current_geometry = self.geometry()
        expanded = current_geometry.adjusted(-5, -5, 5, 5)
        
        pulse.setStartValue(current_geometry)
        pulse.setEndValue(expanded)
        pulse.setEasingCurve(QEasingCurve.InOutQuad)
        
        pulse_reverse = QPropertyAnimation(self, b"geometry")
        pulse_reverse.setDuration(200)
        pulse_reverse.setStartValue(expanded)
        pulse_reverse.setEndValue(current_geometry)
        pulse_reverse.setEasingCurve(QEasingCurve.InOutQuad)
        
        pulse_group = QParallelAnimationGroup(self)
        pulse_group.addAnimation(pulse)
        pulse_group.addAnimation(pulse_reverse)
        pulse_group.start()


class StatsPanel(QFrame):
    """Statistics panel showing game metrics"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("statsPanel")
        self.setStyleSheet("""
            #statsPanel {
                background-color: rgba(33, 33, 33, 0.7);
                border-radius: 15px;
                border: 1px solid #3D5AFE;
            }
        """)
        
        self.init_ui()
        self.load_stats()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("Game Statistics")
        title.setStyleSheet("color: white; font-size: 18px; font-weight: bold;")
        layout.addWidget(title, 0, Qt.AlignCenter)
        
        # Create charts
        self.create_charts(layout)
        
        # Recent activity
        self.activity_table = QTableWidget(5, 2)
        self.activity_table.setHorizontalHeaderLabels(["Game", "Last Played"])
        self.activity_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.activity_table.setStyleSheet("""
            QTableWidget {
                background-color: rgba(33, 33, 33, 0.5);
                color: white;
                border: none;
            }
            QHeaderView::section {
                background-color: #3D5AFE;
                padding: 5px;
                color: white;
                font-weight: bold;
            }
            QTableWidget::item {
                border-bottom: 1px solid rgba(255, 255, 255, 0.1);
                padding: 5px;
            }
        """)
        layout.addWidget(self.activity_table)
        
    def create_charts(self, layout):
        # Create chart for game usage
        usage_chart = QChart()
        usage_chart.setTitle("Games Played")
        usage_chart.setTitleBrush(QColor("white"))
        usage_chart.setBackgroundVisible(False)
        usage_chart.legend().setVisible(True)
        usage_chart.legend().setLabelColor(QColor("white"))
        
        # Wrap the chart in a view
        chart_view = QChartView(usage_chart)
        chart_view.setRenderHint(QPainter.Antialiasing)
        chart_view.setFixedHeight(200)
        chart_view.setStyleSheet("background: transparent;")
        
        layout.addWidget(chart_view)
        
        self.usage_chart = usage_chart
        self.chart_view = chart_view
        
    def load_stats(self):
        """Load game statistics from database files"""
        try:
            # This would be replaced with actual code to load stats from each game's database
            # For now, we'll use random data for demonstration
            
            # Create pie series for games played
            series = QPieSeries()
            series.append("Eight Queens", random.randint(5, 30))
            series.append("Knight's Tour", random.randint(5, 30))
            series.append("Tic Tac Toe", random.randint(15, 50))
            series.append("Tower of Hanoi", random.randint(5, 30))
            series.append("Traveling Salesman", random.randint(5, 30))
            
            # Set colors and make the slices explode slightly
            for i, slice in enumerate(series.slices()):
                colors = ["#F50057", "#00B0FF", "#3D5AFE", "#FF6D00", "#00C853"]
                slice.setBrush(QColor(colors[i]))
                slice.setLabelVisible(True)
                slice.setLabelColor(Qt.white)
                slice.setLabelPosition(QPieSeries.LabelOutside)
                slice.setExploded(True)
                slice.setExplodeDistanceFactor(0.05)
            
            self.usage_chart.removeAllSeries()
            self.usage_chart.addSeries(series)
            
            # Fill recent activity table
            game_names = ["Eight Queens Puzzle", "Knight's Tour", "Tic Tac Toe", 
                         "Tower of Hanoi", "Traveling Salesman"]
            
            # Clear any existing items
            self.activity_table.clearContents()
            
            # Add recent activity (random for demonstration)
            for row in range(5):
                game_item = QTableWidgetItem(game_names[row])
                game_item.setForeground(Qt.white)
                
                date = datetime.now().replace(
                    day=random.randint(1, 28),
                    hour=random.randint(9, 21),
                    minute=random.randint(0, 59)
                )
                date_item = QTableWidgetItem(date.strftime("%b %d, %I:%M %p"))
                date_item.setForeground(Qt.white)
                
                self.activity_table.setItem(row, 0, game_item)
                self.activity_table.setItem(row, 1, date_item)
                
        except Exception as e:
            logger.error(f"Error loading statistics: {e}")


class UserProfileWidget(QFrame):
    """User profile widget for displaying and editing user information"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("userProfileWidget")
        self.setStyleSheet("""
            #userProfileWidget {
                background-color: rgba(33, 33, 33, 0.7);
                border-radius: 15px;
                border: 1px solid #3D5AFE;
            }
        """)
        
        self.init_ui()
        self.load_profile()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Profile title
        title_layout = QHBoxLayout()
        title = QLabel("User Profile")
        title.setStyleSheet("color: white; font-size: 18px; font-weight: bold;")
        edit_btn = QPushButton("Edit")
        edit_btn.setStyleSheet("""
            QPushButton {
                background-color: #3D5AFE;
                color: white;
                border-radius: 10px;
                padding: 5px 10px;
            }
            QPushButton:hover {
                background-color: #536DFE;
            }
        """)
        edit_btn.clicked.connect(self.edit_profile)
        
        title_layout.addWidget(title)
        title_layout.addStretch()
        title_layout.addWidget(edit_btn)
        layout.addLayout(title_layout)
        
        # Profile info
        profile_layout = QFormLayout()
        profile_layout.setVerticalSpacing(10)
        profile_layout.setHorizontalSpacing(15)
        
        self.name_label = QLabel("Guest User")
        self.name_label.setStyleSheet("color: white; font-size: 16px;")
        
        self.level_label = QLabel("Beginner")
        self.level_label.setStyleSheet("color: white; font-size: 16px;")
        
        self.games_label = QLabel("0")
        self.games_label.setStyleSheet("color: white; font-size: 16px;")
        
        # Add labels with colored titles
        name_title = QLabel("Name:")
        name_title.setStyleSheet("color: #3D5AFE; font-weight: bold;")
        profile_layout.addRow(name_title, self.name_label)
        
        level_title = QLabel("Level:")
        level_title.setStyleSheet("color: #3D5AFE; font-weight: bold;")
        profile_layout.addRow(level_title, self.level_label)
        
        games_title = QLabel("Games Played:")
        games_title.setStyleSheet("color: #3D5AFE; font-weight: bold;")
        profile_layout.addRow(games_title, self.games_label)
        
        # Progress bar showing level progress
        progress_title = QLabel("Level Progress:")
        progress_title.setStyleSheet("color: #3D5AFE; font-weight: bold;")
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(25)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                background-color: rgba(255, 255, 255, 0.1);
                border-radius: 5px;
                color: white;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #3D5AFE;
                border-radius: 5px;
            }
        """)
        
        profile_layout.addRow(progress_title, self.progress_bar)
        layout.addLayout(profile_layout)
        
    def load_profile(self):
        """Load user profile from settings"""
        self.name_label.setText(SETTINGS.value("profile/name", "Guest User"))
        self.level_label.setText(SETTINGS.value("profile/level", "Beginner"))
        self.games_label.setText(str(SETTINGS.value("profile/games_played", 0)))
        self.progress_bar.setValue(int(SETTINGS.value("profile/level_progress", 25)))
        
    def edit_profile(self):
        """Show dialog to edit user profile"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Edit Profile")
        dialog.setStyleSheet("""
            QDialog {
                background-color: #1E1E1E;
            }
            QLabel {
                color: white;
            }
            QLineEdit {
                background-color: rgba(255, 255, 255, 0.1);
                color: white;
                border: 1px solid #3D5AFE;
                border-radius: 5px;
                padding: 5px;
            }
            QPushButton {
                background-color: #3D5AFE;
                color: white;
                border-radius: 10px;
                padding: 8px 15px;
            }
            QPushButton:hover {
                background-color: #536DFE;
            }
        """)
        
        layout = QFormLayout(dialog)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setVerticalSpacing(15)
        
        name_edit = QLineEdit(self.name_label.text())
        layout.addRow("Name:", name_edit)
        
        level_combo = QComboBox()
        level_combo.addItems(["Beginner", "Intermediate", "Advanced", "Expert"])
        level_combo.setCurrentText(self.level_label.text())
        level_combo.setStyleSheet("""
            QComboBox {
                background-color: rgba(255, 255, 255, 0.1);
                color: white;
                border: 1px solid #3D5AFE;
                border-radius: 5px;
                padding: 5px;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: url(down_arrow.png);
                width: 10px;
                height: 10px;
            }
        """)
        layout.addRow("Level:", level_combo)
        
        button_box = QHBoxLayout()
        cancel_btn = QPushButton("Cancel")
        save_btn = QPushButton("Save")
        button_box.addWidget(cancel_btn)
        button_box.addWidget(save_btn)
        layout.addRow("", button_box)
        
        cancel_btn.clicked.connect(dialog.reject)
        save_btn.clicked.connect(lambda: self.save_profile(dialog, name_edit.text(), level_combo.currentText()))
        
        dialog.setMinimumWidth(300)
        dialog.exec_()
        
    def save_profile(self, dialog, name, level):
        """Save profile changes"""
        self.name_label.setText(name)
        self.level_label.setText(level)
        
        # Save to settings
        SETTINGS.setValue("profile/name", name)
        SETTINGS.setValue("profile/level", level)
        
        dialog.accept()


class ThemeSwitcher(QWidget):
    """Theme switcher widget for changing app theme"""
    themeChanged = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_theme = SETTINGS.value("theme", "dark")
        self.init_ui()
        
    def init_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)
        
        # Theme label
        theme_label = QLabel("Theme:")
        theme_label.setStyleSheet("color: white;")
        layout.addWidget(theme_label)
        
        # Create theme buttons
        self.dark_btn = QToolButton()
        self.dark_btn.setCheckable(True)
        self.dark_btn.setToolTip("Dark Theme")
        self.dark_btn.setStyleSheet("""
            QToolButton {
                background-color: #121212;
                border: 1px solid #333;
                border-radius: 15px;
                min-width: 30px;
                min-height: 30px;
            }
            QToolButton:checked {
                border: 2px solid #3D5AFE;
            }
        """)
        
        self.light_btn = QToolButton()
        self.light_btn.setCheckable(True)
        self.light_btn.setToolTip("Light Theme")
        self.light_btn.setStyleSheet("""
            QToolButton {
                background-color: #f5f5f5;
                border: 1px solid #ddd;
                border-radius: 15px;
                min-width: 30px;
                min-height: 30px;
            }
            QToolButton:checked {
                border: 2px solid #3D5AFE;
            }
        """)
        
        self.custom_btn = QToolButton()
        self.custom_btn.setCheckable(True)
        self.custom_btn.setToolTip("Custom Theme")
        self.custom_btn.setStyleSheet("""
            QToolButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, 
                                         stop:0 #9C27B0, stop:1 #3D5AFE);
                border: 1px solid #666;
                border-radius: 15px;
                min-width: 30px;
                min-height: 30px;
            }
            QToolButton:checked {
                border: 2px solid white;
            }
        """)
        
        # Set current theme
        if self.current_theme == "dark":
            self.dark_btn.setChecked(True)
        elif self.current_theme == "light":
            self.light_btn.setChecked(True)
        else:
            self.custom_btn.setChecked(True)
        
        # Connect signals
        self.dark_btn.clicked.connect(lambda: self.change_theme("dark"))
        self.light_btn.clicked.connect(lambda: self.change_theme("light"))
        self.custom_btn.clicked.connect(self.open_custom_theme)
        
        # Add to layout
        layout.addWidget(self.dark_btn)
        layout.addWidget(self.light_btn)
        layout.addWidget(self.custom_btn)
        
    def change_theme(self, theme_name):
        """Change the application theme"""
        self.current_theme = theme_name
        SETTINGS.setValue("theme", theme_name)
        
        # Update button states
        self.dark_btn.setChecked(theme_name == "dark")
        self.light_btn.setChecked(theme_name == "light")
        self.custom_btn.setChecked(theme_name == "custom")
        
        # Emit signal
        self.themeChanged.emit(theme_name)
        
    def open_custom_theme(self):
        """Open color picker for custom theme"""
        color = QColorDialog.getColor(QColor("#3D5AFE"), self, "Choose Accent Color")
        if color.isValid():
            SETTINGS.setValue("custom_theme_color", color.name())
            self.change_theme("custom")


class GameFilterWidget(QFrame):
    """Widget for filtering games"""
    filterChanged = pyqtSignal(str, str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("gameFilterWidget")
        self.setStyleSheet("""
            #gameFilterWidget {
                background-color: rgba(33, 33, 33, 0.7);
                border-radius: 15px;
                border: 1px solid #3D5AFE;
                padding: 10px;
            }
        """)
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Title
        title = QLabel("Filter Games")
        title.setStyleSheet("color: white; font-size: 16px; font-weight: bold;")
        layout.addWidget(title)
        
        # Category filter
        category_layout = QHBoxLayout()
        category_label = QLabel("Category:")
        category_label.setStyleSheet("color: white;")
        
        self.category_combo = QComboBox()
        self.category_combo.addItems(["All", "Pathfinding", "Board Games", "Optimization"])
        self.category_combo.setStyleSheet("""
            QComboBox {
                background-color: rgba(255, 255, 255, 0.1);
                color: white;
                border: 1px solid #3D5AFE;
                border-radius: 5px;
                padding: 5px;
            }
        """)
        self.category_combo.currentTextChanged.connect(self.emit_filter_changed)
        
        category_layout.addWidget(category_label)
        category_layout.addWidget(self.category_combo)
        layout.addLayout(category_layout)
        
        # Difficulty filter
        difficulty_layout = QHBoxLayout()
        difficulty_label = QLabel("Difficulty:")
        difficulty_label.setStyleSheet("color: white;")
        
        self.difficulty_combo = QComboBox()
        self.difficulty_combo.addItems(["All", "Easy", "Medium", "Hard"])
        self.difficulty_combo.setStyleSheet("""
            QComboBox {
                background-color: rgba(255, 255, 255, 0.1);
                color: white;
                border: 1px solid #3D5AFE;
                border-radius: 5px;
                padding: 5px;
            }
        """)
        self.difficulty_combo.currentTextChanged.connect(self.emit_filter_changed)
        
        difficulty_layout.addWidget(difficulty_label)
        difficulty_layout.addWidget(self.difficulty_combo)
        layout.addLayout(difficulty_layout)
        
        # Search field
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search games...")
        self.search_input.setStyleSheet("""
            QLineEdit {
                background-color: rgba(255, 255, 255, 0.1);
                color: white;
                border: 1px solid #3D5AFE;
                border-radius: 5px;
                padding: 8px;
            }
        """)
        self.search_input.textChanged.connect(self.emit_filter_changed)
        
        search_layout.addWidget(self.search_input)
        layout.addLayout(search_layout)
        
    def emit_filter_changed(self):
        """Emit signal when filters change"""
        category = self.category_combo.currentText()
        difficulty = self.difficulty_combo.currentText()
        search_text = self.search_input.text()
        
        # Combine filters
        filter_text = search_text
        
        self.filterChanged.emit(filter_text, category)


class DashboardWindow(QMainWindow):
    """Main dashboard window for PDSA Games Portal"""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PDSA Games Portal")
        self.setMinimumSize(1200, 800)  # Increased size for new features
        
        # Load theme from settings
        self.current_theme = SETTINGS.value("theme", "dark")
        self.apply_theme(self.current_theme)
        
        self.setup_ui()
        
        # Start entrance animation after UI is fully set up
        QTimer.singleShot(100, self.animate_cards_entrance)
    
    def apply_theme(self, theme_name):
        """Apply theme to the application"""
        if theme_name == "dark":
            self.setStyleSheet("""
                QMainWindow, QDialog {
                    background-color: #121212;
                }
                QLabel {
                    color: white;
                }
                QPushButton {
                    background-color: #3D5AFE;
                    color: white;
                    border: none;
                    border-radius: 5px;
                    padding: 8px;
                }
                QPushButton:hover {
                    background-color: #536DFE;
                }
                QScrollArea {
                    border: none;
                    background-color: transparent;
                }
                QTabWidget::pane {
                    border: 1px solid #333;
                    background-color: #1E1E1E;
                }
                QTabBar::tab {
                    background-color: #333;
                    color: white;
                    padding: 8px 15px;
                    margin-right: 2px;
                }
                QTabBar::tab:selected {
                    background-color: #3D5AFE;
                }
            """)
        elif theme_name == "light":
            self.setStyleSheet("""
                QMainWindow, QDialog {
                    background-color: #f5f5f5;
                }
                QLabel {
                    color: #333;
                }
                QPushButton {
                    background-color: #3D5AFE;
                    color: white;
                    border: none;
                    border-radius: 5px;
                    padding: 8px;
                }
                QPushButton:hover {
                    background-color: #536DFE;
                }
                QScrollArea {
                    border: none;
                    background-color: transparent;
                }
                QTabWidget::pane {
                    border: 1px solid #ddd;
                    background-color: white;
                }
                QTabBar::tab {
                    background-color: #e0e0e0;
                    color: #333;
                    padding: 8px 15px;
                    margin-right: 2px;
                }
                QTabBar::tab:selected {
                    background-color: #3D5AFE;
                    color: white;
                }
            """)
        else:  # Custom
            accent_color = SETTINGS.value("custom_theme_color", "#3D5AFE")
            self.setStyleSheet(f"""
                QMainWindow, QDialog {{
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, 
                                             stop:0 #121212, stop:1 #1E1E1E);
                }}
                QLabel {{
                    color: white;
                }}
                QPushButton {{
                    background-color: {accent_color};
                    color: white;
                    border: none;
                    border-radius: 5px;
                    padding: 8px;
                }}
                QPushButton:hover {{
                    background-color: {self.lighten_color(accent_color)};
                }}
                QScrollArea {{
                    border: none;
                    background-color: transparent;
                }}
                QTabWidget::pane {{
                    border: 1px solid #333;
                    background-color: rgba(30, 30, 30, 0.7);
                }}
                QTabBar::tab {{
                    background-color: #333;
                    color: white;
                    padding: 8px 15px;
                    margin-right: 2px;
                }}
                QTabBar::tab:selected {{
                    background-color: {accent_color};
                }}
            """)

    def lighten_color(self, color):
        """Helper to lighten a color"""
        # Simple implementation, would normally use QColor directly
        if color == "#3D5AFE":
            return "#536DFE"
        return color
    
    def setup_ui(self):
        """Setup the UI components"""
        # Main central widget
        central_widget = QWidget()
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # Left sidebar for user info, filters, etc.
        sidebar_layout = QVBoxLayout()
        sidebar_layout.setSpacing(15)
        
        # User profile widget
        self.user_profile = UserProfileWidget()
        sidebar_layout.addWidget(self.user_profile)
        
        # Game filter widget
        self.game_filter = GameFilterWidget()
        self.game_filter.filterChanged.connect(self.filter_games)
        sidebar_layout.addWidget(self.game_filter)
        
        # Statistics panel
        self.stats_panel = StatsPanel()
        sidebar_layout.addWidget(self.stats_panel)
        
        # Theme switcher at the bottom
        self.theme_switcher = ThemeSwitcher()
        self.theme_switcher.themeChanged.connect(self.apply_theme)
        sidebar_layout.addWidget(self.theme_switcher)
        
        # Add sidebar to main layout (takes about 30% of width)
        sidebar_container = QWidget()
        sidebar_container.setLayout(sidebar_layout)
        sidebar_container.setFixedWidth(350)
        main_layout.addWidget(sidebar_container)
        
        # Main content area (games, etc.)
        content_layout = QVBoxLayout()
        content_layout.setSpacing(20)
        
        # Header with title and description
        header_frame = QFrame()
        header_frame.setObjectName("headerFrame")
        header_frame.setStyleSheet("""
            #headerFrame {
                background-color: rgba(61, 90, 254, 0.15);
                border-radius: 15px;
            }
        """)
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(20, 15, 20, 15)
        
        # Portal icon
        portal_icon = QLabel("🎮")
        portal_icon.setFixedSize(60, 60)
        portal_icon.setObjectName("portalIcon")
        portal_icon.setStyleSheet("""
            #portalIcon {
                font-size: 30px;
                background-color: #3D5AFE;
                color: white;
                border-radius: 30px;
                margin-right: 15px;
            }
        """)
        portal_icon.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(portal_icon)
        
        # Header text
        header_text = QVBoxLayout()
        header_text.setSpacing(5)
        
        title = QLabel("PDSA GAMES PORTAL")
        title.setObjectName("portalTitle")
        title.setStyleSheet("""
            #portalTitle {
                color: white;
                font-size: 24px;
                font-weight: bold;
                letter-spacing: 1px;
            }
        """)
        header_text.addWidget(title)
        
        subtitle = QLabel("Explore algorithm concepts through interactive games")
        subtitle.setObjectName("portalSubtitle")
        subtitle.setStyleSheet("""
            #portalSubtitle {
                color: #BBBBBB;
                font-size: 14px;
            }
        """)
        header_text.addWidget(subtitle)
        
        header_layout.addLayout(header_text)
        header_layout.addStretch()
        
        content_layout.addWidget(header_frame)
        
        # Stylish separator
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setStyleSheet("""
            background-color: #3D5AFE;
            max-width: 200px;
            height: 3px;
            margin: 5px;
        """)
        content_layout.addWidget(separator, 0, Qt.AlignCenter)
        
        # Container for game cards
        games_container = QWidget()
        self.games_layout = QHBoxLayout(games_container)
        self.games_layout.setContentsMargins(0, 20, 0, 20)
        self.games_layout.setSpacing(20)
        self.games_layout.setAlignment(Qt.AlignCenter)
        
        # Create game cards
        self.create_game_cards(self.games_layout)
        
        # Make the container scrollable for smaller screens
        scroll_area = QScrollArea()
        scroll_area.setObjectName("gamesScrollArea")
        scroll_area.setStyleSheet("""
            #gamesScrollArea {
                background-color: transparent;
                border: none;
            }
        """)
        scroll_area.setWidget(games_container)
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        content_layout.addWidget(scroll_area)
        
        # Footer with attribution
        footer = QLabel("© 2025 PDSA Games Portal - Educational Tool for Algorithm Visualization")
        footer.setObjectName("footer")
        footer.setStyleSheet("""
            #footer {
                color: #777777;
                font-size: 12px;
            }
        """)
        footer.setAlignment(Qt.AlignCenter)
        content_layout.addWidget(footer)
        
        # Add content area to main layout
        content_container = QWidget()
        content_container.setLayout(content_layout)
        main_layout.addWidget(content_container)
        
        # Set the central widget
        self.setCentralWidget(central_widget)
    
    def create_game_cards(self, layout):
        """Create game cards for each game in the portal"""
        # Eight Queens Puzzle
        self.eight_queens_card = GameCard(
            "Eight Queens Puzzle",
            "👑",
            "Place eight queens on a chessboard so that no queen can attack another queen.",
            "#F50057",  # Pink
            self.launch_eight_queens
        )
        self.eight_queens_card.setProperty("category", "Board Games")
        self.eight_queens_card.setProperty("difficulty", "Medium")
        layout.addWidget(self.eight_queens_card)
        
        # Knight's Tour
        self.knights_tour_card = GameCard(
            "Knight's Tour",
            "♞",
            "Find a sequence of moves for a knight to visit every square on a chessboard exactly once.",
            "#00B0FF",  # Light Blue
            self.launch_knights_tour
        )
        self.knights_tour_card.setProperty("category", "Pathfinding")
        self.knights_tour_card.setProperty("difficulty", "Hard")
        layout.addWidget(self.knights_tour_card)
        
        # Tic Tac Toe
        self.tic_tac_toe_card = GameCard(
            "Tic Tac Toe",
            "⭕",
            "Classic game with AI opponents using Minimax and Alpha-Beta pruning algorithms.",
            "#3D5AFE",  # Blue
            self.launch_tic_tac_toe
        )
        self.tic_tac_toe_card.setProperty("category", "Board Games")
        self.tic_tac_toe_card.setProperty("difficulty", "Easy")
        layout.addWidget(self.tic_tac_toe_card)
        
        # Tower of Hanoi
        self.tower_of_hanoi_card = GameCard(
            "Tower of Hanoi",
            "🗼",
            "Move disks from one rod to another following specific rules.",
            "#FF6D00",  # Orange
            self.launch_tower_of_hanoi
        )
        self.tower_of_hanoi_card.setProperty("category", "Optimization")
        self.tower_of_hanoi_card.setProperty("difficulty", "Medium")
        layout.addWidget(self.tower_of_hanoi_card)
        
        # Traveling Salesman
        self.traveling_salesman_card = GameCard(
            "Traveling Salesman",
            "🧭",
            "Find the shortest route to visit all cities and return to the starting point.",
            "#00C853",  # Green
            self.launch_traveling_salesman
        )
        self.traveling_salesman_card.setProperty("category", "Optimization")
        self.traveling_salesman_card.setProperty("difficulty", "Hard")
        layout.addWidget(self.traveling_salesman_card)
        
        # Store cards for filtering
        self.game_cards = [
            self.eight_queens_card,
            self.knights_tour_card, 
            self.tic_tac_toe_card,
            self.tower_of_hanoi_card,
            self.traveling_salesman_card
        ]
    
    def filter_games(self, search_text, category):
        """Filter games based on search text and category"""
        search_text = search_text.lower()
        
        for card in self.game_cards:
            # Get the game title
            title_label = card.findChild(QLabel, "gameTitle")
            if title_label:
                title = title_label.text().lower()
            else:
                title = ""
                
            # Get the description
            desc_label = card.findChild(QLabel, "gameDescription")
            if desc_label:
                desc = desc_label.text().lower()
            else:
                desc = ""
                
            # Check category filter
            card_category = card.property("category")
            category_match = (category == "All" or card_category == category)
                
            # Text search
            text_match = (not search_text or search_text in title or search_text in desc)
                
            # Show or hide the card
            card.setVisible(category_match and text_match)
            
            # If visible, animate it
            if card.isVisible():
                card.pulse_animation()
    
    def launch_game_with_dependencies(self, game_name, script_path, required_modules):
        """Launch a game after checking for dependencies"""
        try:
            # Update games played count in settings
            current_count = int(SETTINGS.value("profile/games_played", 0))
            SETTINGS.setValue("profile/games_played", current_count + 1)
            
            # Path to the Python executable in our virtual environment
            venv_python = os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                                      "pdsa_env", "bin", "python")
            
            # Check if virtual environment exists
            if not os.path.exists(venv_python):
                # Fall back to system Python if virtual environment is not found
                logger.warning(f"Virtual environment not found at {venv_python}, falling back to system Python")
                venv_python = sys.executable
            
            # All dependencies should be in the virtual environment, launch the game
            logger.info(f"Launching {game_name} from {script_path} using {venv_python}")
            subprocess.Popen([venv_python, script_path])
            
            # Update stats if needed
            self.stats_panel.load_stats()
            
            # Update user progress if needed
            current_progress = int(SETTINGS.value("profile/level_progress", 25))
            new_progress = min(100, current_progress + 5)
            SETTINGS.setValue("profile/level_progress", new_progress)
            self.user_profile.progress_bar.setValue(new_progress)
            
            # Check if user leveled up
            if new_progress >= 100 and self.user_profile.level_label.text() == "Beginner":
                SETTINGS.setValue("profile/level", "Intermediate")
                self.user_profile.level_label.setText("Intermediate")
                SETTINGS.setValue("profile/level_progress", 0)
                self.user_profile.progress_bar.setValue(0)
                
                QMessageBox.information(self, "Level Up!", 
                                      "Congratulations! You've advanced to Intermediate level!")
            
        except Exception as e:
            logger.error(f"Error launching {game_name}: {e}")
            from PyQt5.QtWidgets import QMessageBox
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setWindowTitle("Launch Error")
            msg.setText(f"Error launching {game_name}")
            msg.setInformativeText(str(e))
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec_()
    
    def launch_eight_queens(self):
        """Launch the Eight Queens Puzzle game"""
        script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                                  "games", "eight_queen_game", "main.py")
        self.launch_game_with_dependencies("Eight Queens Puzzle", script_path, ["PyQt5"])
    
    def launch_knights_tour(self):
        """Launch the Knight's Tour game"""
        script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                                  "games", "knights_tour_game", "main.py")
        self.launch_game_with_dependencies("Knight's Tour", script_path, ["PyQt5"])
    
    def launch_tic_tac_toe(self):
        """Launch the Tic Tac Toe game"""
        script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                                  "games", "tic_tac_toe_game", "main.py")
        self.launch_game_with_dependencies("Tic Tac Toe", script_path, ["PyQt5", "pandas", "numpy", "matplotlib"])
    
    def launch_tower_of_hanoi(self):
        """Launch the Tower of Hanoi game"""
        script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                                  "games", "tower_of_hanoi_game", "main.py")
        self.launch_game_with_dependencies("Tower of Hanoi", script_path, ["PyQt5", "pygame"])
    
    def launch_traveling_salesman(self):
        """Launch the Traveling Salesman game"""
        script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                                  "games", "traveling_salesman_game", "main.py")
        self.launch_game_with_dependencies("Traveling Salesman", script_path, ["PyQt5"])
    
    def animate_cards_entrance(self):
        """Animate cards entrance when dashboard loads"""
        cards = self.findChildren(GameCard)
        
        for i, card in enumerate(cards):
            # Store original position
            original_pos = card.pos()
            
            # Set initial position (off-screen)
            card.move(card.pos().x() - 300, card.pos().y())
            card.setWindowOpacity(0)
            
            # Create position animation
            pos_anim = QPropertyAnimation(card, b"pos")
            pos_anim.setDuration(300)
            pos_anim.setStartValue(card.pos())
            pos_anim.setEndValue(original_pos)
            pos_anim.setEasingCurve(QEasingCurve.OutCubic)
            
            # Create opacity animation
            opacity_anim = QPropertyAnimation(card, b"windowOpacity")
            opacity_anim.setDuration(300)
            opacity_anim.setStartValue(0.0)
            opacity_anim.setEndValue(1.0)
            opacity_anim.setEasingCurve(QEasingCurve.OutCubic)
            
            # Create animation group
            group = QParallelAnimationGroup(self)
            group.addAnimation(pos_anim)
            group.addAnimation(opacity_anim)
            
            # Start animation with delay based on card index
            QTimer.singleShot(i * 100, group.start)


def main():
    """Main function to start the application"""
    logger.info("Starting PDSA Games Portal")
    
    # Create Qt application
    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # Use Fusion style for consistent look across platforms
    
    # Create and show the dashboard window
    window = DashboardWindow()
    window.show()
    
    # Start the application event loop
    exit_code = app.exec_()
    
    # Log application exit
    logger.info(f"Application exited with code {exit_code}")
    return exit_code


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        logger.exception("Unhandled exception")
        print(f"Error: {str(e)}")
        sys.exit(1)