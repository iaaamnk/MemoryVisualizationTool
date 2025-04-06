from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QFrame
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.patches import Rectangle

class PagingView(QWidget):
    def __init__(self, system_monitor):
        super().__init__()
        self.system_monitor = system_monitor
        self.current_style = 'default'
        self.process_cards = {}
        self.init_ui()
        self.system_monitor.paging_updated.connect(self.update_paging_info)

    def init_ui(self):
        self.layout = QVBoxLayout()
        
        self.title_label = QLabel("Paging Visualization")
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
        
        self.page_table = QTableWidget()
        self.page_table.setColumnCount(4)
        self.page_table.setHorizontalHeaderLabels(['Page ID', 'In Physical', 'Physical Address', 'Process ID'])
        self.layout.addWidget(self.page_table)
        
        self.figure, self.ax = plt.subplots(figsize=(10, 6))
        self.canvas = FigureCanvas(self.figure)
        self.layout.addWidget(self.canvas)
        
        self.setLayout(self.layout)

    def update_theme(self, style):
        self.current_style = style
        self.update_paging_info(self.system_monitor.get_paging_info())

    def update_paging_info(self, paging_info):
        self.info_label.setText(
            f"Page Size: {paging_info['page_size']} bytes | "
            f"Total Pages: {paging_info['total_pages']} | "
            f"Used Pages: {paging_info['used_pages']}"
        )
        
        unique_processes = set(page['process_id'] for page in paging_info['pages'])
        current_pids = set(self.process_cards.keys())
        
        for pid in current_pids - unique_processes:
            card = self.process_cards.pop(pid)
            self.process_layout.removeWidget(card)
            card.deleteLater()
        
        colors = plt.cm.tab10.colors
        for pid in unique_processes - current_pids:
            card = QFrame()
            card.setObjectName("processCard")
            card_layout = QVBoxLayout()
            card_label = QLabel(f"Process {pid}")
            card_label.setAlignment(Qt.AlignCenter)
            card_color = QWidget()
            card_color.setFixedSize(20, 20)
            color = colors[pid % len(colors)]
            card_color.setStyleSheet(f"background-color: rgb({int(color[0]*255)}, {int(color[1]*255)}, {int(color[2]*255)});")
            card_layout.addWidget(card_label)
            card_layout.addWidget(card_color)
            card.setLayout(card_layout)
            card.setFixedSize(100, 80)
            self.process_cards[pid] = card
            self.process_layout.addWidget(card)
        self.process_layout.addStretch()
        
        self.page_table.setRowCount(len(paging_info['pages']))
        bg_color = QColor('#333333') if self.current_style == 'dark_background' else QColor('#FFFFFF')
        for row, page in enumerate(paging_info['pages']):
            for col, value in enumerate([str(page['page_id']), str(page['in_physical']),
                                       str(page['physical_address']) if page['physical_address'] is not None else "None",
                                       str(page['process_id'])]):
                item = QTableWidgetItem(value)
                item.setBackground(bg_color)
                self.page_table.setItem(row, col, item)
        
        plt.style.use(self.current_style)
        self.figure.patch.set_facecolor('#2B2B2B' if self.current_style == 'dark_background' else '#FFFFFF')
        self.ax.clear()
        
        bg_color = '#333333' if self.current_style == 'dark_background' else 'lightgray'
        edge_color = '#FFFFFF' if self.current_style == 'dark_background' else 'black'
        text_color = 'white' if self.current_style == 'dark_background' else 'black'
        
        self.ax.add_patch(Rectangle((0, 0), 100, 1, facecolor=bg_color, edgecolor=edge_color))
        
        for page in paging_info['pages']:
            if page['in_physical'] and page['physical_address'] is not None:
                x = page['physical_address'] % 100
                color = colors[page['process_id'] % len(colors)]
                page_rect = Rectangle((x, 0), 8, 0.8, facecolor=color, edgecolor=edge_color, alpha=0.8)
                self.ax.add_patch(page_rect)
                self.ax.text(x + 4, 0.4, str(page['page_id']), 
                           ha='center', va='center', fontsize=8, color=text_color)
        
        self.ax.set_xlim(0, 100)
        self.ax.set_ylim(0, 1)
        self.ax.set_title('Physical Memory Page Allocation', fontsize=14, pad=15)
        self.ax.axis('off')
        
        legend_patches = [Rectangle((0, 0), 1, 1, facecolor=colors[pid % len(colors)], 
                         label=f'Process {pid}') for pid in unique_processes]
        if legend_patches:
            self.ax.legend(handles=legend_patches, loc='upper right', fontsize=10)
        
        self.canvas.draw()
