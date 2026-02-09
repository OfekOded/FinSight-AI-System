# dashboard_view.py - אחראי על ציור הגרפים (QtCharts), עדכון הטקסטים (Labels) וסידור האלמנטים במסך הבית.

# client/views/dashboard/dashboard_view.py
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, 
                               QTableWidget, QTableWidgetItem, QHeaderView, QDateEdit, 
                               QSizePolicy, QToolTip)
from PySide6.QtCharts import (QChart, QChartView, QSplineSeries, QScatterSeries, QPieSeries, 
                              QPieSlice, QValueAxis, QBarCategoryAxis, QLegend)
from PySide6.QtGui import QPainter, QColor, QFont, QBrush, QPen, QCursor
from PySide6.QtCore import Qt, QDate, QSize, QMargins

class DashboardView(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("background-color: #f5f6fa;")
        
        # משתנה עזר לשמירת התאריכים של הגרף (עבור ה-Hover)
        self.current_chart_categories = []

        # --- Layout ראשי ---
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setSpacing(20)

        # 1. כותרת + KPIs
        self.header_layout = QHBoxLayout()
        
        title_box = QVBoxLayout()
        self.title = QLabel("לוח בקרה פיננסי")
        self.title.setStyleSheet("font-size: 26px; font-weight: bold; color: #2c3e50;")
        self.subtitle = QLabel("סיכום פעילות חודשי")
        self.subtitle.setStyleSheet("font-size: 16px; color: #7f8c8d;")
        title_box.addWidget(self.title)
        title_box.addWidget(self.subtitle)
        
        self.header_layout.addLayout(title_box)
        self.header_layout.addStretch()
        
        self.balance_card = self.create_kpi_card("יתרה נוכחית", "₪0.00", "#2ecc71")
        self.expense_card = self.create_kpi_card("הוצאות החודש", "₪0.00", "#e74c3c")
        
        self.header_layout.addWidget(self.balance_card)
        self.header_layout.addWidget(self.expense_card)
        
        self.layout.addLayout(self.header_layout)

        # 2. אזור הגרפים (פיצול ימין ושמאל)
        self.content_layout = QHBoxLayout()
        
        # --- צד ימין: גרף מגמה + סינון תאריך ---
        self.right_panel = QFrame()
        self.right_panel.setStyleSheet("background-color: white; border-radius: 12px; border: 1px solid #e1e1e6;")
        self.right_layout = QVBoxLayout(self.right_panel)
        
        # כותרת ופילטר תאריך
        self.chart_header = QHBoxLayout()
        lbl_chart = QLabel("מגמת הוצאות יומית")
        lbl_chart.setStyleSheet("font-weight: bold; font-size: 16px; color: #333; border: none;")
        
        self.date_filter = QDateEdit()
        self.date_filter.setDisplayFormat("MM/yyyy")
        self.date_filter.setDate(QDate.currentDate())
        self.date_filter.setCalendarPopup(True)
        self.date_filter.setMinimumWidth(130)
        self.date_filter.setFixedHeight(35)
        self.date_filter.setStyleSheet("""
            QDateEdit {
                border: 1px solid #dfe6e9; border-radius: 5px; padding: 5px; color: #2d3436;
            }
            QDateEdit::drop-down { border: none; }
        """)
        
        self.chart_header.addWidget(lbl_chart)
        self.chart_header.addStretch()
        self.chart_header.addWidget(QLabel("הצג לפי:"))
        self.chart_header.addWidget(self.date_filter)
        
        self.right_layout.addLayout(self.chart_header)
        
        self.chart_spline_view = QChartView()
        self.chart_spline_view.setRenderHint(QPainter.Antialiasing)
        self.chart_spline_view.setStyleSheet("background: transparent; border: none;")
        self.right_layout.addWidget(self.chart_spline_view)
        
        self.content_layout.addWidget(self.right_panel, 2) 

        # --- צד שמאל: דונאט + טבלה ---
        self.left_panel_layout = QVBoxLayout()
        
        # א. גרף דונאט
        self.donut_container = self.create_container("התפלגות הוצאות")
        self.chart_donut_view = QChartView()
        self.chart_donut_view.setRenderHint(QPainter.Antialiasing)
        self.chart_donut_view.setMinimumHeight(280)
        self.chart_donut_view.setStyleSheet("background: transparent; border: none;")
        self.donut_container.layout().addWidget(self.chart_donut_view)
        
        # ב. טבלת עסקאות אחרונות
        self.table_container = self.create_container("עסקאות אחרונות")
        self.recent_table = self.create_recent_table()
        self.table_container.layout().addWidget(self.recent_table)

        self.left_panel_layout.addWidget(self.donut_container)
        self.left_panel_layout.addWidget(self.table_container)
        
        self.content_layout.addLayout(self.left_panel_layout, 1)

        self.layout.addLayout(self.content_layout)

    def create_kpi_card(self, title, value, color):
        frame = QFrame()
        frame.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border-radius: 12px;
                border: 1px solid #e1e1e6;
                min-width: 180px;
            }}
        """)
        layout = QVBoxLayout(frame)
        lbl_title = QLabel(title)
        lbl_title.setStyleSheet("color: #7f8c8d; font-size: 14px; border: none;")
        lbl_value = QLabel(value)
        lbl_value.setStyleSheet(f"color: {color}; font-size: 24px; font-weight: bold; border: none;")
        
        layout.addWidget(lbl_title)
        layout.addWidget(lbl_value)
        return frame

    def create_container(self, title):
        frame = QFrame()
        frame.setStyleSheet("background-color: white; border-radius: 12px; border: 1px solid #e1e1e6;")
        layout = QVBoxLayout(frame)
        lbl = QLabel(title)
        lbl.setStyleSheet("font-weight: bold; font-size: 16px; color: #333; margin-bottom: 5px; border: none;")
        layout.addWidget(lbl)
        return frame

    def create_recent_table(self):
        table = QTableWidget()
        table.setColumnCount(3)
        table.setRowCount(5) 
        table.verticalHeader().setVisible(False)
        table.horizontalHeader().setVisible(False)
        table.setShowGrid(False)
        table.setFocusPolicy(Qt.NoFocus) 
        table.setSelectionMode(QTableWidget.NoSelection) 
        
        fixed_height = (5 * 55) + 10
        table.setFixedHeight(fixed_height)
        
        table.setStyleSheet("""
            QTableWidget {
                border: none;
                background-color: transparent;
            }
            QTableWidget::item {
                padding-right: 10px;
                border-bottom: 1px solid #f0f0f0;
            }
        """)
        
        header = table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        return table

    # --- עדכונים ---

    def update_kpi(self, balance, expenses):
        self.balance_card.findChildren(QLabel)[1].setText(f"₪{balance:,.2f}")
        self.expense_card.findChildren(QLabel)[1].setText(f"₪{expenses:,.2f}")

    def update_spline_chart(self, daily_data):
        chart = QChart()
        chart.legend().hide()
        chart.setBackgroundBrush(Qt.NoBrush)
        chart.setAnimationOptions(QChart.SeriesAnimations)
        
        chart.setMargins(QMargins(10, 10, 10, 30)) 

        series = QSplineSeries()
        series.setColor(QColor("#0984e3"))
        series.setPen(QPen(QColor("#0984e3"), 3)) 
        
        scatter = QScatterSeries()
        scatter.setMarkerSize(12)
        scatter.setColor(QColor("white"))
        scatter.setBorderColor(QColor("#0984e3"))
        
        scatter.hovered.connect(self.on_scatter_hover)
        
        # איפוס הרשימה ל-Hover
        self.current_chart_categories = []
        max_val = 100
        
        sorted_dates = sorted(daily_data.keys())
        
        for i, date_str in enumerate(sorted_dates):
            amount = daily_data[date_str]
            try:
                display_date = date_str[8:] + "/" + date_str[5:7] 
            except:
                display_date = date_str
            
            # --- התיקון כאן: הוספה לרשימה של המחלקה ---
            self.current_chart_categories.append(display_date)
            
            series.append(i, amount)
            scatter.append(i, amount)
            
            if amount > max_val: max_val = amount

        chart.addSeries(series)
        chart.addSeries(scatter)

        # ציר X
        axis_x = QBarCategoryAxis()
        axis_x.append(self.current_chart_categories) # שימוש ברשימה המתוקנת
        axis_x.setLabelsFont(QFont("Segoe UI", 9))
        axis_x.setLabelsAngle(-90) # טקסט אנכי
        chart.addAxis(axis_x, Qt.AlignBottom)
        series.attachAxis(axis_x)
        scatter.attachAxis(axis_x)

        # ציר Y
        axis_y = QValueAxis()
        axis_y.setRange(0, max_val * 1.2)
        axis_y.setLabelFormat("%.0f") 
        chart.addAxis(axis_y, Qt.AlignLeft)
        series.attachAxis(axis_y)
        scatter.attachAxis(axis_y)

        self.chart_spline_view.setChart(chart)

    def on_scatter_hover(self, point, state):
        if state:
            index = int(point.x())
            if 0 <= index < len(self.current_chart_categories):
                date_label = self.current_chart_categories[index]
                amount = point.y()
                text = f"תאריך: {date_label}\nסכום: ₪{amount:,.0f}"
                QToolTip.showText(QCursor.pos(), text)
        else:
            QToolTip.hideText()

    def update_donut_chart(self, category_data):
        chart = QChart()
        chart.setBackgroundBrush(Qt.NoBrush)
        chart.setAnimationOptions(QChart.SeriesAnimations)
        chart.setLayoutDirection(Qt.RightToLeft)
        
        chart.legend().setVisible(True)
        chart.legend().setAlignment(Qt.AlignBottom)
        chart.legend().setFont(QFont("Segoe UI", 9))
        chart.legend().setMarkerShape(QLegend.MarkerShapeCircle) 

        series = QPieSeries()
        series.setHoleSize(0.45) 
        
        total_sum = sum([amount for _, amount in category_data])
        if total_sum == 0: total_sum = 1

        colors = ["#00cec9", "#ff7675", "#74b9ff", "#ffeaa7", "#a29bfe", "#636e72"]
        
        for i, (cat, amount) in enumerate(category_data):
            percent = (amount / total_sum) * 100
            label = f"{cat} ({percent:.1f}%)" 
            
            slice_ = series.append(label, amount)
            slice_.setBrush(QColor(colors[i % len(colors)]))
            
            slice_.hovered.connect(lambda is_hovered, s=slice_: self.on_slice_hover(s, is_hovered))
            slice_.setLabelVisible(False) 

        chart.addSeries(series)
        self.chart_donut_view.setChart(chart)

    def on_slice_hover(self, slice_, is_hovered):
        slice_.setExploded(is_hovered)
        slice_.setExplodeDistanceFactor(0.1) 
        
        if is_hovered:
            percent = (slice_.percentage() * 100)
            text = f"{slice_.label().split('(')[0].strip()}\n{percent:.1f}%"
            QToolTip.showText(QCursor.pos(), text)
        else:
            QToolTip.hideText() # תוקן: שימוש ב-QToolTip הגלובלי

    def update_recent_table(self, transactions):
        self.recent_table.clearContents()
        
        icons = {
            "מזון": "🍔", "אוכל": "🍔", "מסעדות": "🍕",
            "תחבורה": "🚗", "דלק": "⛽", "מונית": "🚕",
            "בילויים": "🎉", "סרט": "🎬",
            "קניות": "🛍️", "ביגוד": "👕",
            "שכר דירה": "🏠", "חשבונות": "💡",
            "אחר": "📄"
        }

        for i in range(5):
            if i < len(transactions):
                t = transactions[i]
                
                cat = t.get("category", "אחר")
                icon_item = QTableWidgetItem(icons.get(cat, "📄"))
                icon_item.setTextAlignment(Qt.AlignCenter)
                icon_item.setFlags(Qt.ItemIsEnabled) 
                self.recent_table.setItem(i, 0, icon_item)
                
                date_short = t.get('date', '')[5:] 
                desc = f"{t.get('title')} ({date_short})"
                desc_item = QTableWidgetItem(desc)
                desc_item.setFont(QFont("Segoe UI", 10))
                desc_item.setFlags(Qt.ItemIsEnabled)
                self.recent_table.setItem(i, 1, desc_item)
                
                amount = t.get("amount_in_ils", 0)
                amount_item = QTableWidgetItem(f"₪{amount:,.0f}")
                amount_item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                amount_item.setForeground(QColor("#e74c3c"))
                amount_item.setFont(QFont("Segoe UI", 10, QFont.Bold))
                amount_item.setFlags(Qt.ItemIsEnabled)
                self.recent_table.setItem(i, 2, amount_item)
            else:
                self.recent_table.setItem(i, 0, QTableWidgetItem(""))
                self.recent_table.setItem(i, 1, QTableWidgetItem(""))
                self.recent_table.setItem(i, 2, QTableWidgetItem(""))

            self.recent_table.setRowHeight(i, 55)