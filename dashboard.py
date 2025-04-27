#!/usr/bin/env python3
"""
PDSA Games Portal Dashboard
Central hub for accessing all algorithm visualization games
"""
import sys
import os
import logging
import subprocess
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QGraphicsDropShadowEffect, QScrollArea, QSizePolicy
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QColor, QFont, QIcon, QPixmap

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='pdsa_games_portal.log',
    filemode='a'
)
logger = logging.getLogger(__name__)

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
        
        self.setup_ui(title, icon_text, description, color, launch_function)
    
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


class DashboardWindow(QMainWindow):
    """Main dashboard window for PDSA Games Portal"""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PDSA Games Portal")
        self.setMinimumSize(1000, 700)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #121212;
            }
        """)
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the UI components"""
        # Main central widget
        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(20)
        
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
        
        main_layout.addWidget(header_frame)
        
        # Stylish separator
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setStyleSheet("""
            background-color: #3D5AFE;
            max-width: 200px;
            height: 3px;
            margin: 5px;
        """)
        main_layout.addWidget(separator, 0, Qt.AlignCenter)
        
        # Container for game cards
        games_container = QWidget()
        games_layout = QHBoxLayout(games_container)
        games_layout.setContentsMargins(0, 20, 0, 20)
        games_layout.setSpacing(20)
        games_layout.setAlignment(Qt.AlignCenter)
        
        # Create game cards
        self.create_game_cards(games_layout)
        
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
        main_layout.addWidget(scroll_area)
        
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
        main_layout.addWidget(footer)
        
        self.setCentralWidget(central_widget)
    
    def create_game_cards(self, layout):
        """Create game cards for each game in the portal"""
        # Eight Queens Puzzle
        eight_queens_card = GameCard(
            "Eight Queens Puzzle",
            "👑",
            "Place eight queens on a chessboard so that no queen can attack another queen.",
            "#F50057",  # Pink
            self.launch_eight_queens
        )
        layout.addWidget(eight_queens_card)
        
        # Knight's Tour
        knights_tour_card = GameCard(
            "Knight's Tour",
            "♞",
            "Find a sequence of moves for a knight to visit every square on a chessboard exactly once.",
            "#00B0FF",  # Light Blue
            self.launch_knights_tour
        )
        layout.addWidget(knights_tour_card)
        
        # Tic Tac Toe
        tic_tac_toe_card = GameCard(
            "Tic Tac Toe",
            "⭕",
            "Classic game with AI opponents using Minimax and Alpha-Beta pruning algorithms.",
            "#3D5AFE",  # Blue
            self.launch_tic_tac_toe
        )
        layout.addWidget(tic_tac_toe_card)
        
        # Tower of Hanoi
        tower_of_hanoi_card = GameCard(
            "Tower of Hanoi",
            "🗼",
            "Move disks from one rod to another following specific rules.",
            "#FF6D00",  # Orange
            self.launch_tower_of_hanoi
        )
        layout.addWidget(tower_of_hanoi_card)
        
        # Traveling Salesman
        traveling_salesman_card = GameCard(
            "Traveling Salesman",
            "🧭",
            "Find the shortest route to visit all cities and return to the starting point.",
            "#00C853",  # Green
            self.launch_traveling_salesman
        )
        layout.addWidget(traveling_salesman_card)
    
    def launch_game_with_dependencies(self, game_name, script_path, required_modules):
        """Launch a game after checking for dependencies"""
        try:
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