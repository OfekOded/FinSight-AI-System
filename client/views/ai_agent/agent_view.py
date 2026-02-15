# agent_view.py - מציג את ממשק הצ'אט: רשימת הבועות (Bubbles), תיבת הטקסט וכפתורי ההצעות המהירות.
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QLineEdit, QPushButton
from PySide6.QtCore import Qt

class AgentView(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setStyleSheet("background-color: white; font-size: 16px; padding: 10px;")
        self.layout.addWidget(self.chat_display)
        
        self.input_layout = QHBoxLayout()
        self.question_input = QLineEdit()
        self.question_input.setFixedHeight(40)
        self.question_input.setStyleSheet("font-size: 16px; padding: 5px;")
        
        self.send_btn = QPushButton("שלח")
        self.send_btn.setFixedHeight(40)
        self.send_btn.setStyleSheet("background-color: #00d2d3; color: white; font-weight: bold; font-size: 16px;")
        
        self.input_layout.addWidget(self.question_input)
        self.input_layout.addWidget(self.send_btn)
        
        self.layout.addLayout(self.input_layout)

    def append_message(self, sender: str, message: str):
        self.chat_display.append(f"<b>{sender}:</b> {message}<br><br>")

    def get_question(self) -> str:
        return self.question_input.text()

    def clear_input(self):
        self.question_input.clear()