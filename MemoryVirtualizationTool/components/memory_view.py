from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QProgressBar
from PyQt5.QtCore import Qt
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import numpy as np

class MemoryView(QWidget):
    def __init__(self, system_monitor):
        super().__init__()
        self.system_monitor = system_monitor
        self.current_style = 'default'
        self.init_ui()
        self.system_monitor.memory_updated.connect(self.update_memory_info)

    def init_ui(self):
        self.layout = QVBoxLayout()
        
        self.memory_label = QLabel("Memory Information")
        self.memory_label.setAlignment(Qt.AlignCenter)
        self.memory_label.setStyleSheet("font-size: 16px; font-weight: bold; margin: 10px;")
        self.layout.addWidget(self.memory_label)
        
        self.ram_progress = QProgressBar()
        self.ram_progress.setFormat("RAM Usage: %p%")
        self.layout.addWidget(self.ram_progress)
        
        self.swap_progress = QProgressBar()
        self.swap_progress.setFormat("Swap Usage: %p%")
        self.layout.addWidget(self.swap_progress)
        
        self.figure, self.ax = plt.subplots(figsize=(10, 6))
        self.canvas = FigureCanvas(self.figure)
        self.layout.addWidget(self.canvas)
        
        self.setLayout(self.layout)

    def update_theme(self, style):
        self.current_style = style
        self.update_memory_info(self.system_monitor.get_memory_info())

    def update_memory_info(self, memory_info):
        self.ram_progress.setValue(int(memory_info['percent']))
        self.swap_progress.setValue(int(memory_info['swap_percent']))
        
        plt.style.use(self.current_style)
        self.figure.patch.set_facecolor('#2B2B2B' if self.current_style == 'dark_background' else '#FFFFFF')
        self.ax.clear()
        self.ax.set_facecolor('#2B2B2B' if self.current_style == 'dark_background' else '#FFFFFF')
        
        labels = ['Used', 'Free', 'Available']
        ram_values = [memory_info['used'] / (1024 ** 3), 
                     memory_info['free'] / (1024 ** 3), 
                     memory_info['available'] / (1024 ** 3)]
        swap_values = [memory_info['swap_used'] / (1024 ** 3), 
                      memory_info['swap_free'] / (1024 ** 3), 
                      0]
        
        x = np.arange(len(labels))
        width = 0.35
        
        self.ax.bar(x - width/2, ram_values, width, label='RAM', color='#4CAF50')
        self.ax.bar(x + width/2, swap_values, width, label='Swap', color='#2196F3')
        
        text_color = 'white' if self.current_style == 'dark_background' else 'black'
        self.ax.set_ylabel('GB', fontsize=12, color=text_color)
        self.ax.set_title('Memory Allocation', fontsize=14, pad=15, color=text_color)
        self.ax.set_xticks(x)
        self.ax.set_xticklabels(labels, fontsize=10, color=text_color)
        self.ax.legend(fontsize=10)
        
        for i, v in enumerate(ram_values + swap_values[:2]):
            if v > 0:
                self.ax.text(i % 3 + (i // 3 - 0.5) * width, v, f'{v:.2f}',
                            ha='center', va='bottom', fontsize=9, color=text_color)
        
        self.ax.grid(True, linestyle='--', alpha=0.7, color='#666666' if self.current_style == 'dark_background' else '#CCCCCC')
        self.canvas.draw()
