import psutil
from PyQt5.QtCore import QThread, pyqtSignal
import time

class SystemMonitor(QThread):
    memory_updated = pyqtSignal(dict)
    paging_updated = pyqtSignal(dict)
    segmentation_updated = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        self._running = False

    def run(self):
        self._running = True
        while self._running:
            memory_info = self.get_memory_info()
            self.memory_updated.emit(memory_info)
            paging_info = self.get_paging_info()
            self.paging_updated.emit(paging_info)
            segmentation_info = self.get_segmentation_info()
            self.segmentation_updated.emit(segmentation_info)
            time.sleep(1)

    def stop(self):
        self._running = False
        self.wait()

    def get_memory_info(self):
        virtual_mem = psutil.virtual_memory()
        swap_mem = psutil.swap_memory()
        return {
            'total': virtual_mem.total,
            'available': virtual_mem.available,
            'used': virtual_mem.used,
            'free': virtual_mem.free,
            'percent': virtual_mem.percent,
            'swap_total': swap_mem.total,
            'swap_used': swap_mem.used,
            'swap_free': swap_mem.free,
            'swap_percent': swap_mem.percent
        }

    def get_paging_info(self):
        import random
        pages = []
        for i in range(10):
            pages.append({
                'page_id': i,
                'in_physical': random.random() > 0.3,
                'physical_address': random.randint(0, 1000) if random.random() > 0.3 else None,
                'process_id': random.randint(1, 5)
            })
        return {
            'page_size': 4096,
            'total_pages': 100,
            'used_pages': random.randint(30, 70),
            'pages': pages
        }

    def get_segmentation_info(self):
        import random
        segments = []
        for i in range(5):
            segments.append({
                'segment_id': i,
                'base': random.randint(0, 10000),
                'limit': random.randint(100, 1000),
                'type': random.choice(['code', 'data', 'stack', 'heap']),
                'process_id': random.randint(1, 5)
            })
        return {
            'segments': segments,
            'total_memory': 16384,
            'fragmentation': random.random()
        }
