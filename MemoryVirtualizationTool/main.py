import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QTabWidget, QVBoxLayout, 
                            QWidget, QToolBar, QAction)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from components.memory_view import MemoryView
from components.paging_view import PagingView
from components.segmentation_view import SegmentationView
from components.system_monitor import SystemMonitor

class MemoryVisualizationApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.is_dark_mode = False
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("Memory Visualization Tool")
        self.setGeometry(100, 100, 1000, 700)
        
        self.toolbar = QToolBar("Main Toolbar")
        self.addToolBar(Qt.TopToolBarArea, self.toolbar)
        
        self.theme_action = QAction("Toggle Theme", self)
        self.theme_action.setIcon(QIcon.fromTheme("weather-clear-night"))
        self.theme_action.triggered.connect(self.toggle_theme)
        self.toolbar.addAction(self.theme_action)
        
        self.main_widget = QWidget()
        self.main_layout = QVBoxLayout()
        self.main_widget.setLayout(self.main_layout)
        
        self.tabs = QTabWidget()
        self.tabs.setTabPosition(QTabWidget.North)
        self.main_layout.addWidget(self.tabs)
        
        self.system_monitor = SystemMonitor()
        self.memory_tab = MemoryView(self.system_monitor)
        self.paging_tab = PagingView(self.system_monitor)
        self.segmentation_tab = SegmentationView(self.system_monitor)
        
        self.tabs.addTab(self.memory_tab, "Memory Allocation")
        self.tabs.addTab(self.paging_tab, "Paging Visualization")
        self.tabs.addTab(self.segmentation_tab, "Segmentation Visualization")
        
        self.setCentralWidget(self.main_widget)
        
        self.apply_theme()
        self.system_monitor.start()

    def toggle_theme(self):
        self.is_dark_mode = not self.is_dark_mode
        self.apply_theme()

    def apply_theme(self):
        if self.is_dark_mode:
            style_sheet = """
            QMainWindow, QWidget { 
                background-color: #2B2B2B; 
                color: #FFFFFF; 
            }
            QTabWidget::pane { 
                border: 1px solid #444444; 
                background: #2B2B2B; 
            }
            QTabBar::tab { 
                background: #3C3C3C; 
                color: #FFFFFF; 
                padding: 8px; 
                margin-right: 2px;
            }
            QTabBar::tab:selected { 
                background: #4CAF50; 
                border-bottom: 2px solid #4CAF50;
            }
            QToolBar { 
                background: #3C3C3C; 
                border: none; 
            }
            QProgressBar { 
                border: 1px solid #444444; 
                background: #333333;
                text-align: center;
                color: #FFFFFF;
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
            }
            QTableWidget { 
                background-color: #333333; 
                color: #FFFFFF; 
                gridline-color: #444444;
                selection-background-color: #555555;
            }
            QHeaderView::section {
                background-color: #3C3C3C;
                color: #FFFFFF;
                padding: 4px;
                border: 1px solid #444444;
            }
            QTableWidget::item {
                background-color: #333333;
                color: #FFFFFF;
            }
            QTableCornerButton::section {
                background-color: #3C3C3C;
                border: 1px solid #444444;
            }
            QLabel {
                color: #FFFFFF;
            }
            QFrame#processCard {
                background-color: #3C3C3C;
                border: 1px solid #444444;
                border-radius: 4px;
            }
            """
            self.theme_action.setIcon(QIcon.fromTheme("weather-clear"))
            matplotlib_style = 'dark_background'
        else:
            style_sheet = """
            QMainWindow, QWidget { 
                background-color: #FFFFFF; 
                color: #000000; 
            }
            QTabWidget::pane { 
                border: 1px solid #CCCCCC; 
                background: #FFFFFF; 
            }
            QTabBar::tab { 
                background: #E0E0E0; 
                color: #000000; 
                padding: 8px; 
                margin-right: 2px;
            }
            QTabBar::tab:selected { 
                background: #4CAF50; 
                border-bottom: 2px solid #4CAF50;
            }
            QToolBar { 
                background: #F0F0F0; 
                border: none; 
            }
            QProgressBar { 
                border: 1px solid #CCCCCC; 
                background: #F0F0F0;
                text-align: center;
                color: #000000;
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
            }
            QTableWidget { 
                background-color: #FFFFFF; 
                color: #000000; 
                gridline-color: #CCCCCC;
                selection-background-color: #DDDDDD;
            }
            QHeaderView::section {
                background-color: #E0E0E0;
                color: #000000;
                padding: 4px;
                border: 1px solid #CCCCCC;
            }
            QTableWidget::item {
                background-color: #FFFFFF;
                color: #000000;
            }
            QTableCornerButton::section {
                background-color: #E0E0E0;
                border: 1px solid #CCCCCC;
            }
            QLabel {
                color: #000000;
            }
            QFrame#processCard {
                background-color: #F0F0F0;
                border: 1px solid #CCCCCC;
                border-radius: 4px;
            }
            """
            self.theme_action.setIcon(QIcon.fromTheme("weather-clear-night"))
            matplotlib_style = 'default'

        QApplication.instance().setStyleSheet(style_sheet)
        self.memory_tab.update_theme(matplotlib_style)
        self.paging_tab.update_theme(matplotlib_style)
        self.segmentation_tab.update_theme(matplotlib_style)

    def closeEvent(self, event):
        self.system_monitor.stop()
        super().closeEvent(event)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MemoryVisualizationApp()
    window.show()
    sys.exit(app.exec_())
