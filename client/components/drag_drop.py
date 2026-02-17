from PySide6.QtWidgets import QLabel
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QDragEnterEvent, QDropEvent

class DragDropArea(QLabel):
    # סיגנל שמודיע כשהמשתמש בחר קובץ
    file_dropped = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAlignment(Qt.AlignCenter)
        self.setText("\n\nגרור קובץ קבלה לכאן\nאו לחץ לבחירה\n\n")
        self.setStyleSheet("""
            QLabel {
                border: 3px dashed #b2bec3;
                border-radius: 15px;
                background-color: #f1f2f6;
                color: #636e72;
                font-size: 18px;
                font-weight: bold;
            }
            QLabel:hover {
                background-color: #e6e9ed;
                border-color: #0984e3;
                color: #0984e3;
            }
        """)
        self.setAcceptDrops(True)
        self.file_path = None
        self.clicked_callback = None

    def mousePressEvent(self, event):
        if self.clicked_callback:
            self.clicked_callback()

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        urls = event.mimeData().urls()
        if urls and urls[0].isLocalFile():
            file_path = urls[0].toLocalFile()
            self.set_file(file_path)

    def set_file(self, path):
        """פונקציה לעדכון התצוגה אחרי בחירת קובץ"""
        self.file_path = path
        filename = path.split('/')[-1]
        self.setText(f"\nקובץ נבחר:\n{filename}\n\n")
        self.setStyleSheet("""
            QLabel {
                border: 3px solid #00b894;
                border-radius: 15px;
                background-color: #e3fcf7;
                color: #00b894;
                font-size: 16px;
                font-weight: bold;
            }
        """)
        self.file_dropped.emit(path)