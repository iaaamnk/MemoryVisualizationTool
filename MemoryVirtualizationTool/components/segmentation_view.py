from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QFrame
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.patches import Rectangle

class SegmentationView(QWidget):
    def __init__(self, system_monitor):
        super().__init__()
        self.system_monitor = system_monitor
        self.current_style = 'default'
        self.process_cards = {}
        self.init_ui()
        self.system_monitor.segmentation_updated.connect(self.update_segmentation_info)

    def init_ui(self):
        self.layout = QVBoxLayout()
        
        self.title_label = QLabel("Segmentation Visualization")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("font-size: 16px; font-weight: bold; margin: 10px;")
        self.layout.addWidget(self.title_label)
        
        self.info_label = QLabel()
        self.info_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.info_label)
        
        self.process_container = QWidget()
        self.process_layout = QHBoxLayout()
        self.process_container.setLayout(self.process_layout)
        self.layout.addWidget(self.process_container)
        
        self.segment_table = QTableWidget()
        self.segment_table.setColumnCount(5)
        self.segment_table.setHorizontalHeaderLabels(['Segment ID', 'Base', 'Limit', 'Type', 'Process ID'])
        self.layout.addWidget(self.segment_table)
        
        self.figure, self.ax = plt.subplots(figsize=(10, 6))
        self.canvas = FigureCanvas(self.figure)
        self.layout.addWidget(self.canvas)
        
        self.setLayout(self.layout)

    def update_theme(self, style):
        self.current_style = style
        self.update_segmentation_info(self.system_monitor.get_segmentation_info())

    def update_segmentation_info(self, segmentation_info):
        self.info_label.setText(
            f"Total Memory: {segmentation_info['total_memory']} KB | "
            f"Fragmentation: {segmentation_info['fragmentation']:.2f}"
        )
        
        unique_processes = set(segment['process_id'] for segment in segmentation_info['segments'])
        current_pids = set(self.process_cards.keys())
        
        for pid in current_pids - unique_processes:
            card = self.process_cards.pop(pid)
            self.process_layout.removeWidget(card)
            card.deleteLater()
        
        colors = {'code': '#4CAF50', 'data': '#2196F3', 'stack': '#F44336', 'heap': '#FF9800'}
        for pid in unique_processes - current_pids:
            card = QFrame()
            card.setObjectName("processCard")
            card_layout = QVBoxLayout()
            card_label = QLabel(f"Process {pid}")
            card_label.setAlignment(Qt.AlignCenter)
            card_color = QWidget()
            card_color.setFixedSize(20, 20)
            card_color.setStyleSheet(f"background-color: #4CAF50;")
            card_layout.addWidget(card_label)
            card_layout.addWidget(card_color)
            card.setLayout(card_layout)
            card.setFixedSize(100, 80)
            self.process_cards[pid] = card
            self.process_layout.addWidget(card)
        self.process_layout.addStretch()
        
        self.segment_table.setRowCount(len(segmentation_info['segments']))
        bg_color = QColor('#333333') if self.current_style == 'dark_background' else QColor('#FFFFFF')
        for row, segment in enumerate(segmentation_info['segments']):
            for col, value in enumerate([str(segment['segment_id']), str(segment['base']),
                                       str(segment['limit']), segment['type'], str(segment['process_id'])]):
                item = QTableWidgetItem(value)
                item.setBackground(bg_color)
                self.segment_table.setItem(row, col, item)
        
        plt.style.use(self.current_style)
        self.figure.patch.set_facecolor('#2B2B2B' if self.current_style == 'dark_background' else '#FFFFFF')
        self.ax.clear()
        
        total_memory = segmentation_info['total_memory']
        bg_color = '#333333' if self.current_style == 'dark_background' else 'lightgray'
        edge_color = '#FFFFFF' if self.current_style == 'dark_background' else 'black'
        text_color = 'white' if self.current_style == 'dark_background' else 'black'
        
        self.ax.add_patch(Rectangle((0, 0), total_memory, 1, facecolor=bg_color, edgecolor=edge_color))
        
        for segment in segmentation_info['segments']:
            segment_rect = Rectangle(
                (segment['base'], 0), segment['limit'], 0.8,
                facecolor=colors.get(segment['type'], 'gray'),
                edgecolor=edge_color, alpha=0.8
            )
            self.ax.add_patch(segment_rect)
            self.ax.text(
                segment['base'] + segment['limit']/2, 0.4,
                f"PID:{segment['process_id']}\n{segment['type']}\n{segment['limit']}K",
                ha='center', va='center', fontsize=8, color=text_color
            )
        
        self.ax.set_xlim(0, total_memory)
        self.ax.set_ylim(0, 1)
        self.ax.set_title('Memory Segmentation', fontsize=14, pad=15)
        self.ax.axis('off')
        
        legend_patches = [Rectangle((0, 0), 1, 1, facecolor=color, label=seg_type) 
                         for seg_type, color in colors.items()]
        if legend_patches:
            self.ax.legend(handles=legend_patches, loc='upper right', fontsize=10)
        
        self.canvas.draw()
