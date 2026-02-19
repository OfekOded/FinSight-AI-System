from PySide6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel, QProgressBar
from PySide6.QtCore import Qt, Signal

class SavingsItem(QFrame):
    clicked = Signal(int, str, float, float) 

    def __init__(self, goal_id, name, current, target):
        super().__init__()
        self.goal_id = goal_id
        self.name = name
        self.current = current
        self.target = target
        
        self.setCursor(Qt.PointingHandCursor)
        self.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #dfe6e9;
                border-radius: 10px;
            }
            QFrame:hover {
                border: 1px solid #6c5ce7;
                background-color: #fcfcfc;
            }
        """)
        
        layout = QVBoxLayout(self)
        
        # כותרת וסכומים
        header = QHBoxLayout()
        title = QLabel(f"{name}")
        title.setStyleSheet("font-weight: bold; font-size: 14px; border: none; background: transparent;")
        
        amounts = QLabel(f"{current:,.0f} / {target:,.0f} ₪")
        amounts.setStyleSheet("color: #636e72; font-weight: 500; border: none; background: transparent;")
        
        header.addWidget(title)
        header.addStretch()
        header.addWidget(amounts)
        layout.addLayout(header)
        
        # פרוגרס בר 
        # מי יודע איך קוראים לזה בעברית? חחחחחחח
        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        
        # חישוב אחוזים
        if target > 0:
            percent = int((current / target) * 100)
        else:
            percent = 0
            
        self.progress.setValue(percent)
        self.progress.setTextVisible(True)
        self.progress.setFormat("%p%")
        
        # שינוי צבע אם הושלם
        if percent >= 100:
            self.progress.setStyleSheet("""
                QProgressBar {
                    border: 1px solid #dfe6e9;
                    border-radius: 5px;
                    text-align: center;
                    background: transparent;
                }
                QProgressBar::chunk {
                    background-color: #00b894; /* ירוק */
                    border-radius: 5px;
                }
            """)
        else:
            self.progress.setStyleSheet("""
                QProgressBar {
                    border: 1px solid #dfe6e9;
                    border-radius: 5px;
                    text-align: center;
                    background: transparent;
                }
                QProgressBar::chunk {
                    background-color: #fdcb6e; /* כתום/צהוב */
                    border-radius: 5px;
                }
            """)
            
        layout.addWidget(self.progress)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.goal_id, self.name, self.current, self.target)
        super().mousePressEvent(event)