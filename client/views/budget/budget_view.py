from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, 
                               QProgressBar, QPushButton, QDialog, QLineEdit, QDoubleSpinBox, QMessageBox)
from PySide6.QtCore import Qt, QRectF
from PySide6.QtGui import QPainter, QColor, QPen, QFont

from components.saving_item import SavingsItem


# --- דיאלוגים ---

class AddGoalDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("הוספת יעד חיסכון")
        self.setFixedSize(300, 200)
        self.setLayoutDirection(Qt.RightToLeft)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("שם היעד:"))
        self.name_input = QLineEdit()
        layout.addWidget(self.name_input)
        layout.addWidget(QLabel("סכום היעד (₪):"))
        self.amount_input = QDoubleSpinBox()
        self.amount_input.setMaximum(1000000)
        self.amount_input.setButtonSymbols(QDoubleSpinBox.NoButtons)
        layout.addWidget(self.amount_input)
        btn_layout = QHBoxLayout()
        save_btn = QPushButton("שמור")
        save_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton("ביטול")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(save_btn)
        layout.addLayout(btn_layout)

    def get_data(self):
        return self.name_input.text(), self.amount_input.value()

class AddBudgetDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("הוספת קטגוריית תקציב")
        self.setFixedSize(300, 200)
        self.setLayoutDirection(Qt.RightToLeft)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("שם הקטגוריה:"))
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("לדוגמה: ביגוד")
        layout.addWidget(self.name_input)
        layout.addWidget(QLabel("תקרה חודשית (₪):"))
        self.amount_input = QDoubleSpinBox()
        self.amount_input.setMaximum(100000)
        self.amount_input.setButtonSymbols(QDoubleSpinBox.NoButtons)
        layout.addWidget(self.amount_input)
        btn = QPushButton("שמור")
        btn.clicked.connect(self.accept)
        layout.addWidget(btn)

    def get_data(self):
        return self.name_input.text(), self.amount_input.value()

class AddSubDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("הוספת מנוי קבוע")
        self.setFixedSize(300, 200)
        self.setLayoutDirection(Qt.RightToLeft)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("שם המנוי:"))
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("לדוגמה: Apple Music")
        layout.addWidget(self.name_input)
        layout.addWidget(QLabel("עלות חודשית (₪):"))
        self.amount_input = QDoubleSpinBox()
        self.amount_input.setMaximum(10000)
        self.amount_input.setButtonSymbols(QDoubleSpinBox.NoButtons)
        layout.addWidget(self.amount_input)
        btn = QPushButton("שמור")
        btn.clicked.connect(self.accept)
        layout.addWidget(btn)

    def get_data(self):
        return self.name_input.text(), self.amount_input.value()

# --- ווידג'טים ---

class CircularProgress(QWidget):
    def __init__(self, value=0, size=50):
        super().__init__()
        self.value = value
        self.setFixedSize(size, size)

    def set_value(self, value):
        self.value = value
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        rect = QRectF(3, 3, self.width()-6, self.height()-6)
        pen = QPen(QColor("#dfe6e9"), 5)
        pen.setCapStyle(Qt.RoundCap)
        painter.setPen(pen)
        painter.drawEllipse(rect)
        pen.setColor(QColor("#00d2d3"))
        painter.setPen(pen)
        angle = - int(self.value * 3.6 * 16)
        painter.drawArc(rect, 90 * 16, angle)
        painter.setPen(QColor("#2d3436"))
        painter.setFont(QFont("Segoe UI", 9, QFont.Bold))
        painter.drawText(rect, Qt.AlignCenter, f"{int(self.value)}%")

# --- המסך הראשי ---

class BudgetView(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("background-color: #f5f6fa;")
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(10)
        
        header = QLabel("ניהול תקציב ויעדים")
        header.setStyleSheet("font-size: 20px; font-weight: bold; color: #2d3436;")
        main_layout.addWidget(header)

        content_layout = QHBoxLayout()
        
        # --- צד ימין: ניהול תקציב ---
        self.budget_container = QFrame()
        self.budget_container.setStyleSheet("background-color: white; border-radius: 12px; border: 1px solid #e1e1e6;")
        self.budget_layout = QVBoxLayout(self.budget_container)
        self.budget_layout.setAlignment(Qt.AlignTop)
        
        # כותרת + כפתור הוספה
        budget_header = QHBoxLayout()
        lbl_budget = QLabel("תקציב חודשי")
        lbl_budget.setStyleSheet("font-size: 16px; font-weight: bold; color: #333; border: none;")
        self.add_budget_btn = self.create_add_btn()
        
        budget_header.addWidget(lbl_budget)
        budget_header.addStretch()
        budget_header.addWidget(self.add_budget_btn)
        self.budget_layout.addLayout(budget_header)
        
        # אזור לרשימת התקציבים (כדי שנוכל לנקות אותו בנפרד)
        self.budget_list_layout = QVBoxLayout()
        self.budget_layout.addLayout(self.budget_list_layout)
        self.budget_layout.addStretch()
        
        content_layout.addWidget(self.budget_container, 65)

        # --- צד שמאל: מנויים + חיסכון ---
        left_panel = QVBoxLayout()
        left_panel.setSpacing(10)
        
        # 1. מנויים
        self.subs_container = QFrame()
        self.subs_container.setStyleSheet("background-color: white; border-radius: 12px; border: 1px solid #e1e1e6;")
        self.subs_layout = QVBoxLayout(self.subs_container)
        self.subs_layout.setAlignment(Qt.AlignTop)
        
        subs_header = QHBoxLayout()
        lbl_subs = QLabel("מנויים קבועים")
        lbl_subs.setStyleSheet("font-size: 15px; font-weight: bold; border: none;")
        self.add_sub_btn = self.create_add_btn()
        
        subs_header.addWidget(lbl_subs)
        subs_header.addStretch()
        subs_header.addWidget(self.add_sub_btn)
        self.subs_layout.addLayout(subs_header)
        
        self.subs_list_layout = QVBoxLayout()
        self.subs_layout.addLayout(self.subs_list_layout)
        self.subs_layout.addStretch()
        
        left_panel.addWidget(self.subs_container, 1)
        
        # 2. יעדי חיסכון
        self.savings_container = QFrame()
        self.savings_container.setStyleSheet("background-color: white; border-radius: 12px; border: 1px solid #e1e1e6;")
        self.savings_layout = QVBoxLayout(self.savings_container)
        self.savings_layout.setAlignment(Qt.AlignTop)
        
        savings_header = QHBoxLayout()
        lbl_save = QLabel("יעדי חיסכון")
        lbl_save.setStyleSheet("font-size: 15px; font-weight: bold; border: none;")
        self.add_goal_btn = self.create_add_btn()
        
        savings_header.addWidget(lbl_save)
        savings_header.addStretch()
        savings_header.addWidget(self.add_goal_btn)
        self.savings_layout.addLayout(savings_header)
        
        self.goals_list_layout = QVBoxLayout()
        self.savings_layout.addLayout(self.goals_list_layout)
        self.savings_layout.addStretch()
        
        left_panel.addWidget(self.savings_container, 2)
        
        content_layout.addLayout(left_panel, 35)
        main_layout.addLayout(content_layout)

    def create_add_btn(self):
        btn = QPushButton("+")
        btn.setCursor(Qt.PointingHandCursor)
        btn.setFixedSize(25, 25)
        btn.setStyleSheet("""
            QPushButton {
                background-color: #f1f2f6; color: #636e72; border-radius: 12px; font-weight: bold; border: 1px solid #dfe6e9;
            }
            QPushButton:hover { background-color: #00d2d3; color: white; border: none; }
        """)
        return btn

    def add_budget_item(self, name, spent, limit):
        item_widget = QWidget()
        layout = QVBoxLayout(item_widget)
        layout.setSpacing(2)
        layout.setContentsMargins(0, 5, 0, 5)
        
        top_row = QHBoxLayout()
        name_lbl = QLabel(name)
        name_lbl.setStyleSheet("font-weight: bold; font-size: 14px; border: none;")
        amounts_lbl = QLabel(f"₪{spent:,.0f} / ₪{limit:,.0f}")
        amounts_lbl.setStyleSheet("color: #636e72; border: none; font-size: 13px;")
        top_row.addWidget(name_lbl)
        top_row.addStretch()
        top_row.addWidget(amounts_lbl)
        
        progress = QProgressBar()
        progress.setFixedHeight(8)
        progress.setTextVisible(False)
        percent = (spent / limit) * 100 if limit > 0 else 0
        progress.setValue(min(int(percent), 100))
        
        color = "#2ecc71"
        if percent > 75: color = "#f1c40f"
        if percent >= 100: color = "#e74c3c"
        
        progress.setStyleSheet(f"""
            QProgressBar {{ border: none; background-color: #dfe6e9; border-radius: 4px; }}
            QProgressBar::chunk {{ background-color: {color}; border-radius: 4px; }}
        """)
        
        layout.addLayout(top_row)
        layout.addWidget(progress)
        self.budget_list_layout.addWidget(item_widget)

    def add_subscription_item(self, name, amount):
        row = QHBoxLayout()
        name_lbl = QLabel(name)
        name_lbl.setStyleSheet("font-size: 13px; border: none;")
        amt_lbl = QLabel(f"₪{amount}")
        amt_lbl.setStyleSheet("font-weight: bold; font-size: 13px; border: none;")
        row.addWidget(name_lbl)
        row.addStretch()
        row.addWidget(amt_lbl)
        w = QWidget()
        w.setLayout(row)
        self.subs_list_layout.addWidget(w)

    # def add_savings_item(self, name, saved, target):
    #     frame = QFrame()
    #     frame.setStyleSheet("background-color: #f1f2f6; border-radius: 8px; border: none; margin-bottom: 5px;")
    #     layout = QHBoxLayout(frame)
    #     layout.setContentsMargins(10, 5, 10, 5)
    #     text_layout = QVBoxLayout()
    #     name_lbl = QLabel(name)
    #     name_lbl.setStyleSheet("font-weight: bold; font-size: 14px; border: none;")
    #     details_lbl = QLabel(f"נחסך: ₪{saved:,.0f} מתוך ₪{target:,.0f}")
    #     details_lbl.setStyleSheet("color: #636e72; font-size: 12px; border: none;")
    #     text_layout.addWidget(name_lbl)
    #     text_layout.addWidget(details_lbl)
    #     percent = (saved / target) * 100 if target > 0 else 0
    #     circle = CircularProgress(percent, size=40)
    #     layout.addLayout(text_layout)
    #     layout.addStretch()
    #     layout.addWidget(circle)
    #     self.goals_list_layout.addWidget(frame)

    def add_savings_item(self, goal_id, name, current, target):
        item = SavingsItem(goal_id, name, current, target)
        self.savings_layout.addWidget(item)
        return item
    
    def clear_all(self):
        def clear_layout(layout):
            if layout is None:
                return
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()
                elif item.layout() is not None:
                    clear_layout(item.layout())
        
        clear_layout(self.budget_list_layout)
        clear_layout(self.subs_list_layout)
        clear_layout(self.goals_list_layout)